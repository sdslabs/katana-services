from flask import Flask, request
from kubernetes import config, client, watch
from kubernetes.stream import stream
from pymongo import MongoClient
import random
import threading
import os
import time
import binascii
import base64
import hashlib
from Crypto.Cipher import AES    

app = Flask(__name__)

flag_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

config.load_incluster_config()
api = client.CoreV1Api()
api_instance = client.AppsV1Api()

submissions = {}


def establish_mongo_connection(username, password):
    service_name = "mongo-svc"
    namespace = "katana"
    service = api.read_namespaced_service(name=service_name, namespace=namespace)
    mongo_ip = service.spec.cluster_ip
    mongo_uri = f"mongodb://{username}:{password}@{mongo_ip}"
    mongo_client = MongoClient(mongo_uri)
    print("Connected to MongoDB.")
    return mongo_client


mongo = establish_mongo_connection("adminuser", "password123")

status_getter = {}
status_setter = {}

challenge_statuses = {}
down_deduction = 10


config.load_incluster_config()
api = client.CoreV1Api()
api_instance = client.AppsV1Api()

def establish_mongo_connection(username, password):
    service_name = "mongo-svc"
    namespace = "katana"
    service = api.read_namespaced_service(name=service_name, namespace=namespace)
    mongo_ip = service.spec.cluster_ip
    mongo_uri = f"mongodb://{username}:{password}@{mongo_ip}"
    mongo_client = MongoClient(mongo_uri)
    print("Connected to MongoDB.")
    return mongo_client

mongo = establish_mongo_connection("adminuser","password123")

status_getter = {}
status_setter = {}

def generate_flag():
    length_of_flag = random.randint(15, 20)
    
    flag = 'katana{' + ''.join(random.choice(flag_chars) for _ in range(length_of_flag)) + '}'
    return flag

def update_flag(mongo_client, team_name, challenge_name):
    flag = generate_flag()  
    mongo_db = mongo_client['katana']
    mongo_collection = mongo_db['teams']
    
    query = {
        'username': team_name,
        'challenges.challengename': challenge_name
    }
    
    update = {
        '$set': {
            'challenges.$.flag': flag
        }
    }
    mongo_collection.update_one(query, update)

def watch_statefulset():
    namespace = 'katana'
    statefulset_name = 'kashira'
    w = watch.Watch()
    for event in w.stream(api_instance.list_namespaced_stateful_set, namespace=namespace):
        if event['object'].metadata.name == statefulset_name:
            annotations = event['object'].metadata.annotations
            if annotations and annotations.get('tick') == 'true':
                update_all_challenges()
                annotations['tick'] = 'false'  # Set annotation to 'false'
                statefulset = api_instance.read_namespaced_stateful_set(statefulset_name, namespace)
                statefulset.metadata.annotations = annotations
                updated_statefulset = api_instance.patch_namespaced_stateful_set(statefulset_name, namespace, statefulset)

def run_watch_statefulset():
    with app.app_context():
        watch_statefulset()


def pod_executor(file_path, real_flag, pod_name, pod_namespace, is_getter):
    api_new = client.CoreV1Api()
    
    _ = api_new.read_namespaced_pod(name=pod_name, namespace=pod_namespace)
    resp = stream(api_new.connect_get_namespaced_pod_exec,
                    pod_name, pod_namespace,
                    command='/bin/sh',
                    stderr = True, stdin = True , stdout = True, tty = False,
                    _preload_content = False)
    commands = ''
    with open(file_path, 'r') as file:
        commands = file.read()
    try:
        resp.write_stdin(commands)
        while True:
            if resp.peek_stdout() != '':
                break
        output = resp.read_stdout()
        resp.close()
        if is_getter:
            return output
        else:
            global status_setter
            if not pod_namespace in status_setter:
                status_setter[pod_namespace] = {}
            status_setter[pod_namespace][pod_name] = output
            return None
    except:
        return None
      
def get_exact_name(challenge_name, namespace):
    api = client.CoreV1Api()
    data_json = api.list_namespaced_pod(namespace, label_selector = 'app=' + challenge_name)
    if len(data_json.items) == 0:
        print(f'Error: No pod for challenge {challenge_name} exists in namespace: {namespace}')
        return None
    else:
        return data_json.items[0].metadata.name

def exec_setter_script(team):
    team_namespace = team['username'] + '-ns'
    for challenge in team['challenges']:
        challenge_name = challenge['challengename']
        update_flag(mongo, team['username'], challenge_name)
        setter_path = f"./flag-data/{challenge_name}/flag_setter.sh"
        if os.path.exists(setter_path):
            pod_name = get_exact_name(challenge_name, team_namespace)
            pod_executor(setter_path, pod_name, team_namespace, False)

def update_all_challenges():
    mongo_db = mongo['katana']
    mongo_collection = mongo_db['teams']
    for team in mongo_collection.find():
        thr = threading.Thread(target=exec_setter_script, args=(team, ))
        thr.daemon = True
        thr.start()

def exec_getter_script(team):
    team_namespace = team['username'] + '-ns'
    for  challenge in team['challenges']:
        challenge_name = challenge['challengename']
        getter_path = f"./flag-data/{challenge_name}/flag_getter.sh"
        if os.path.exists(getter_path):
            pod_name = get_exact_name(challenge_name, team_namespace)
            output = pod_executor(getter_path, pod_name, team_namespace, True)
            global status_getter
            if output == challenge['flag']:
                status_getter[team_namespace][pod_name] = True
            else:
                status_getter[team_namespace][pod_name] = False

def flag_checker():
    mongo_db = mongo['katana']
    mongo_collection = mongo_db['teams']
    for team in mongo_collection.find():
        thr = threading.Thread(target=exec_getter_script, args=(team, ))
        thr.daemon = True
        thr.start()

def run_commands_randomly():
    while True:
        flag_checker()
        time.sleep(random.randint(0, 600))

@app.route('/receive-flag',methods=['POST'])
def receive_flag():
    if request.method == 'POST':
        data = request.get_json()
        encrypted_flag = data.get("encrypted_flag")
        team_name = data.get("team_name")
        challenge_name = data.get("challenge_name")       
        mongo_db = mongo["katana"]
        mongo_collection = mongo_db['teams']
        team = mongo_collection.find_one({"username": team_name})
    
        if team:
            password = team["password"]
        else:
            return "Team not found"
        
        iterations = 10000
        outputbytes = base64.b64decode(encrypted_flag)
        passwordbytes = password.encode('utf-8')
        salt = outputbytes[8:16]
        derivedkey = hashlib.pbkdf2_hmac('sha256', passwordbytes, salt, iterations, 48)
        key = derivedkey[0:32]
        iv = derivedkey[32:48]
        ciphertext = outputbytes[16:]
        decryptor = AES.new(key, AES.MODE_CBC, iv)
        flag = decryptor.decrypt(ciphertext)
        flag = flag[:-flag[-1]].decode('utf-8')
       
        teams = mongo_collection.find()
    
        for team in teams:
            for challenge in team["challenges"]:
                if challenge["challengename"] == challenge_name:
                    true_flag = challenge["flag"]
                    if true_flag == flag:
                        if team["username"] == team_name :
                            return "Can not submit your own flag"
                        else:
                            mongo_collection.update_one({"username": team_name}, {"$inc": {"score": challenge["points"]}})
                            return "Flag submitted successfully\n"
        return "Wrong flag or challenge name.\n"
    else:
        return "Wrong request method"

# @app.route("/kissaki", methods=["POST"])
# def receive_json():
#     json = request.json
#     for info in json["data"]:
#         parse_json(info)
#     return "OK", 200

# ------------code for testing----------------
import logging

logging.basicConfig(level=logging.INFO)

@app.route("/kissaki", methods=["POST"])
def receive_json():
    json = request.json
    logging.info(f"Received data:\n{json}")
    return "ok", 200
# ------------code for testing----------------

if __name__ == '__main__':
    t1 = threading.Thread(target=run_watch_statefulset)
    t2 = threading.Thread(target=run_commands_randomly)
    t1.start()
    t2.start()
    app.run(host='0.0.0.0',port = 80)
