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

flag_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

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


def pod_executor(file_path, pod_name, pod_namespace):
    pod2_list = api.list_namespaced_pod(namespace=pod_namespace, label_selector=pod_name)
    exec_command = ["sh",file_path]
    if pod2_list.items:
        pod2 = pod2_list.items[0]
        pod2_name = pod2.metadata.name
        try:
            resp = api.connect_get_namespaced_pod_exec(
                name=pod2_name,
                namespace=pod_namespace,
                command=exec_command,
                stderr=True, stdin=False,
                stdout=True, tty=False
            )
            print("Command executed. Response: " + resp)
        except:
            print("Error executing command")
    else:
        print("No pod found with label selector in team namespace.")

def update_all_challenges():
    mongo_db = mongo['katana']
    mongo_collection = mongo_db['teams']
    for team in mongo_collection.find():
        for challenge in team['challenges']:
            update_flag(mongo, team['username'], challenge['challengename'])
            challenge_name = challenge['challengename']
            checker_path = f"updaters/{challenge_name}/flag_updater.sh"
            if os.path.exists(checker_path):
                flag = pod_executor(checker_path, team['podname'], team["username"]+"-ns")
                print(flag)

def flag_checker():
    mongo_db = mongo['katana']
    mongo_collection = mongo_db['teams']
    for team in mongo_collection.find():
        for challenge in team['challenges']:
            challenge_name = challenge['challengename']
            checker_path = f"checkers/{challenge_name}/checker.sh"
            if os.path.exists(checker_path):
                command = ["sh", checker_path]
                flag = pod_executor(command, team['podname'], team["username"]+"-ns")
                if(flag == challenge['flag']):
                    print(flag)
                    print("Flag is correct")
                else:
                    print(flag)
                    print("Flag is incorrect")

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

if __name__ == '__main__':
    t1 = threading.Thread(target=run_watch_statefulset)
    t2 = threading.Thread(target=run_commands_randomly)
    t1.start()
    t2.start()
    app.run(host='0.0.0.0',port = 80)

