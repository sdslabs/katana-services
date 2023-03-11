from flask import Flask, request
import os
import zipfile
import subprocess
import pyinotify
import threading
import re

app = Flask(__name__)

@app.route("/deploy", methods = ["POST"])
def grab():
    try:
        file_name = list(request.files)[0]
        challenge_name = request.form["challenge_name"]
        challenge_artifact = request.files[file_name]
        challenge_root = os.path.join(os.environ['CHALLENGE_DIR'], challenge_name)
        artifact_path = os.path.join(os.environ['TMP_DIR'], file_name)
        challenge_artifact.save(artifact_path)
        with zipfile.ZipFile(artifact_path, 'r') as zip_ref:
            zip_ref.extractall(challenge_root)
        os.remove(artifact_path)
        assert (os.environ['INIT_FILE'] in os.listdir(challenge_root))
        os.chmod(os.path.join(challenge_root, os.environ['INIT_FILE']), 0o755)
        outlog = open(os.path.join(challenge_root, "out.log"), "w")
        errlog = open(os.path.join(challenge_root, "err.log"), "w")
        subprocess.Popen(
            [os.path.join(challenge_root, os.environ['INIT_FILE'])],
            cwd=challenge_root,
            stdout=outlog,
            stderr=errlog,
        )
        return {"success": True}
    except Exception as err:
        return {"success": False, "error": str(err)}
    
class EventHandler(pyinotify.ProcessEvent):
    def process_IN_MODIFY(self, event):
        filepath = event.pathname
        regex = r"/katana_(\w+)_(\w+)\.tar\.gz$" # Matches two groups of word characters separated by underscores
        match = re.search(regex, filepath)
        if match:
                typ = match.group(1)
                name = match.group(2)
                cmd="setup "+name+" "+typ
                os.system(cmd)
        else:
            print("recieved file of name: ",filepath)
        
def start_notifier():
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_MODIFY
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch('/opt/katana/', mask, rec=False)
    notifier.loop()

# TODO: add metrics/monitoring functionality
if __name__ == "__main__":
    os.system("chmod +x setup_script.sh")
    os.system("bash ./setup_script.sh")
    os.system("rm -rf setup_script.sh")
    t = threading.Thread(target=start_notifier)
    t.start()
    app.run('0.0.0.0', 3004)
    
