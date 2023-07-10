import random
from kubernetes import config, client, watch
from kubernetes.stream import stream

flag_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

config.load_incluster_config()
api = client.CoreV1Api()

def generate_flag():
    # Random length of flag between 10 and 20
    length_of_flag = random.randint(15, 20)

    flag = 'katana{' + ''.join(random.choice(flag_chars) for _ in range(length_of_flag)) + '}'
    return flag

def pod_executor(command, pod_name, pod_namespace):
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

def update_flag():
    pass
    
if __name__ == '__main__':
    w = watch.Watch()
    namespace = 'katana'
    statefulset_name = 'kashira'
    for event in w.stream(api.list_namespaced_stateful_set, namespace=namespace):
        if event['object'].metadata.name == statefulset_name and 'tick' in event['object'].metadata.annotations:
            update_flag()

            statefulset = api.read_namespaced_stateful_set(name=statefulset_name, namespace=namespace)
            statefulset.metadata.annotations['tick'] = 'false'
            api.patch_namespaced_stateful_set(name=statefulset_name, namespace=namespace, body=statefulset)