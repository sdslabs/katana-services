import random
from kubernetes import config, client
from kubernetes.stream import stream
from flask import Flask

app = Flask(__name__)

flag_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

def generate_flag():
    # Random length of flag between 10 and 20
    length_of_flag = random.randint(15, 20)

    flag = 'katana{' + ''.join(random.choice(flag_chars) for _ in range(length_of_flag)) + '}'
    return flag

def pod_executor(command, pod_name, pod_namespace):
    config.load_incluster_config()
    api = client.CoreV1Api()
    resp = api.read_namespaced_pod(name=pod_name, namespace=pod_namespace)
    exec_command = [
        '/bin/sh',
        '-c',
        ' '.join(command)]
    resp = stream(api.connect_get_namespaced_pod_exec,
                  pod_name,
                  pod_namespace,
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False)
    return resp

@app.route('/')
def hello():
    return "Hello, world!"

if __name__ == '__main__':
    app.run()
