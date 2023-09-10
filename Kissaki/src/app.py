from flask import Flask, request
import os
import zipfile
import subprocess
import pyinotify
import threading
import re
import subprocess

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, world!"

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        filepath = event.pathname
        regex = r"/kissaki_(\w+)\.tar\.gz$" #checks for file type to be kissaki_<type-of-challenge>_<name>.tar.gz
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
    wdd = wm.add_watch("/opt/kissaki/", mask, rec=False)
    notifier.loop()

# TODO: Add metrics/monitoring functionality
if __name__ == "__main__":
    os.chmod("setup-script.sh", 0o755)
    os.system("bash ./setup-script.sh")
    os.system("rm -rf setup-script.sh")
    os.system("rm -rf /opt/kissaki/app.py")
    t = threading.Thread(target=start_notifier)
    t.start()
    app.run('0.0.0.0', os.environ['DAEMON_PORT'])    