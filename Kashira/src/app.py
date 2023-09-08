import random
from kubernetes import config, client
from kubernetes.stream import stream
from flask import Flask
import os
import zipfile
import subprocess
import pyinotify
import threading
import re
import subprocess

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

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        filepath = event.pathname
        regex = r"/kashira_(\w+)\.tar\.gz$" 
        match = re.search(regex, filepath)
        if match:
                NameOfChallenge = match.group(1)
                cmd=["setup",NameOfChallenge]
                subprocess.run(cmd)
        else:
            print("Challenge name does not match specified format: ",filepath)

def start_notifier():
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_MODIFY
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch("/opt/kashira/", mask, rec=False)
    notifier.loop()

# TODO: Add metrics/monitoring functionality
if __name__ == "__main__":
    os.chmod("setup-script.sh", 0o755)
    os.system("bash ./setup-script.sh")
    os.system("rm -rf setup-script.sh")
    os.system("rm -rf /opt/kashira/app.py")
    t = threading.Thread(target=start_notifier)
    t.start()
    app.run('0.0.0.0', os.environ['DAEMON_PORT'])
