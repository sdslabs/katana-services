from flask import Flask, request
import os
import zipfile
from conf import *
import subprocess

app = Flask(__name__)

@app.route("/deploy", methods = ["POST"])
def grab():
    try:
        file_name = list(request.files)[0]
        challenge_name = request.form["challenge_name"]
        challenge_artifact = request.files[file_name]
        challenge_root = os.path.join(challenge_dir, challenge_name)
        artifact_path = os.path.join(tmp_dir, file_name)
        challenge_artifact.save(artifact_path)
        with zipfile.ZipFile(artifact_path, 'r') as zip_ref:
            zip_ref.extractall(challenge_root)
        os.remove(artifact_path)
        assert (init_file in os.listdir(challenge_root))
        os.chmod(os.path.join(challenge_root, init_file), 0o755)
        outlog = open(os.path.join(challenge_root, "out.log"), "w")
        errlog = open(os.path.join(challenge_root, "err.log"), "w")
        subprocess.Popen(
            [os.path.join(challenge_root, init_file)],
            cwd=challenge_root,
            stdout=outlog,
            stderr=errlog,
            shell=True
        )
        return {"success": True}
    except Exception as err:
        return {"success": False, "error": str(err)}

# TODO: add metrics/monitoring functionality

app.run('0.0.0.0', 3004)
