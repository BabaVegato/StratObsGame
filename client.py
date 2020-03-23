import socket
import pickle


def create_client(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s

def wait_for_object():
    while True:
        msg = s.recv(2048)
        d = pickle.loads(msg)
        print(d)

def send_obj(socket, obj):
    msg = pickle.dumps(obj)
    socket.send(msg)