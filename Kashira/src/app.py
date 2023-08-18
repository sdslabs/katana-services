from flask import Flask
from kubernetes import config, client, watch
from kubernetes.stream import stream
from pymongo import MongoClient
import random
import threading

app = Flask(__name__)
flag_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

config.load_incluster_config()
api = client.CoreV1Api()
api_instance = client.AppsV1Api()

def establish_mongo_connection(username, password):
    service_name = "mongo-nodeport-svc"
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
                update_flag(mongo,"katana-team-0","notekeeper")
                annotations['tick'] = 'false'  # Set annotation to 'false'
                statefulset = api_instance.read_namespaced_stateful_set(statefulset_name, namespace)
                statefulset.metadata.annotations = annotations
                updated_statefulset = api_instance.patch_namespaced_stateful_set(statefulset_name, namespace, statefulset)

def run_watch_statefulset():
    with app.app_context():
        watch_statefulset()


if __name__ == '__main__':
    t = threading.Thread(target=run_watch_statefulset)
    t.start()
    app.run()
