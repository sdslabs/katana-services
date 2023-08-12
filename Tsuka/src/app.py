from flask import Flask, request
import os
import zipfile
import subprocess
import pyinotify
import threading
import re
import subprocess
import paramiko

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
        regex = r"/katana_(\w+)_(\w+)\.tar\.gz$" #checks for file type to be katana_<type-of-challenge>_<name>.tar.gz
        match = re.search(regex, filepath)
        if match:
                TypeOfChallenge = match.group(1)
                Name = match.group(2)
                cmd=["setup",Name,TypeOfChallenge]
                subprocess.run(cmd)
        else:
            print("Challenge name does not match specified format: ",filepath)

        
def start_notifier():
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_MODIFY
    handler = EventHandler()
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch("/opt/katana/", mask, rec=False)
    notifier.loop()

class SSHServer(paramiko.ServerInterface):
    def check_auth_password(self, username, password):
        # In this simple example, we allow authentication with any username and password
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        # We allow all channel requests
        return paramiko.OPEN_SUCCEEDED
        
def start_ssh_server():
    server = paramiko.Transport(('0.0.0.0', 22))
    server.add_server_key(paramiko.RSAKey.generate(2048))
    server.set_subsystem_handler('sftp', paramiko.SFTPServer)

    try:
        server.start_server(server=SSHServer())
        print("SSH server is running...")
        server.accept()
    except Exception as e:
        print("An error occurred:", str(e))
    finally:
        server.close()

# TODO: add metrics/monitoring functionality
if __name__ == "__main__":
    os.chmod("setup-script.sh", 0o755)
    os.system("bash ./setup-script.sh")
    os.system("rm -rf setup-script.sh")
    t = threading.Thread(target=start_notifier)
    t.start()
    # Start the SSH server in a separate thread
    ssh_thread = threading.Thread(target=start_ssh_server)
    ssh_thread.start()
    app.run('0.0.0.0', os.environ['DAEMON_PORT'])    
