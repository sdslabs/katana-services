## import stmnt
import os
import requests

from app import app

def test_deployment():
    # Set environment variables
    os.environ['CHALLENGE_DIR'] = '/opt/challenges/'
    os.environ['TMP_DIR'] = '/tmp/'
    os.environ['DAEMON_PORT'] = '3004'
    os.environ['INIT_FILE'] = 'run.sh'

    client = app.test_client()

    # Request
    with open('tests/run.zip', 'rb') as f:
        uploadbase = client.post('/deploy',
                                data=f,
                                headers={'X-File-Name': 'run.zip',
                                        'Content-Disposition': 'form-data; name="{0}"; filename="{0}"'.format('run.zip'),
                                        'content-type': 'multipart/form-data'})
        assert(uploadbase.status_code == 200)


