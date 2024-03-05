from flask import Flask, request, jsonify
import logging
from kubernetes import client, config
import time
import random
import requests
import threading


app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

try:
    config.load_incluster_config()
except config.config_exception.ConfigException:
    try:
        config.load_kube_config()
    except config.config_exception.ConfigException:
        raise

v1 = client.CoreV1Api()

cc_svc_ns = "katana"
current_thread = None


def service_port(svc, ns):
    service = v1.read_namespaced_service(name=svc, namespace=ns)
    # cluster_ip = service.spec.cluster_ip
    ports = service.spec.ports
    port = ports[0].port
    return port


checkers = set()


@app.route("/")
def hello():
    return "Hello, world!"


@app.route("/register", methods=["POST"])
def register_checker():
    checker_info = request.get_json()
    # here chall_name is harcoded
    checkers.add(checker_info["ccName"])
    logging.info(checkers)
    return jsonify({"message": "Registered successfully"})


@app.route("/status")
def handle_status():
    global current_thread

    # stop already running thread
    if current_thread is not None:
        current_thread.do_run = False
        current_thread.join()

    # start a new thread
    current_thread = threading.Thread(target=run_loop)
    current_thread.do_run = True
    current_thread.start()

    return "started a new loop\n"


def run_loop():
    with app.app_context():
        t = threading.current_thread()
        interval = 10  # in sec
        while getattr(t, "do_run", True):
            start_time = time.time()
            sleep_time = random.randint(1, interval - 3)
            time.sleep(sleep_time)
            data = []
            for checker in checkers:
                svc = checker + "-svc"
                # port = service_port(svc, cc_svc_ns)
                port = 80  # ------------hardcoded----------------------
                url = f"http://{svc}.{cc_svc_ns}.svc.cluster.local:{port}/checker"
                try:
                    response = requests.get(url)
                    logging.info(f"Received response from {url}:{response}")
                    data.append(response.json())
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error making request to {url}:{str(e)}")

            # post request to kashira

            kashira_svc = "kashira-svc"
            kashira_ns = "katana"
            kashira_port = "80"
            url = f"http://{kashira_svc}.{kashira_ns}.svc.cluster.local:{kashira_port}/kissaki"
            headers = {"Content-Type": "application/json"}
            # url = "http://10.61.81.227:5000"
            try:
                # Send all the data as JSON in the POST request
                response = requests.post(url, json=data, headers=headers)
                response.raise_for_status()
                logging.info(f"Made POST request to {url}:{response.status_code}")
            except requests.exceptions.HTTPError as errh:
                logging.error(
                    f"HTTP Error occurred while making POST request to {url}:{str(errh)}"
                )
            except requests.exceptions.RequestException as e:
                logging.error(f"Error making POST request to {url}:{str(e)}")
            # waiting unless next 30 sec starts
            rem_time = time.time() - start_time
            if rem_time < interval:
                time.sleep(rem_time)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
