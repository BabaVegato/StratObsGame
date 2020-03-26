import socket
import pickle

class Client : 
    def __init__(self):
        self.info_rcvd = None
        self.socket = None

    def create_client(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def wait_for_object(self):
        while True:
            msg = self.socket.recv(4096)
            d = pickle.loads(msg)
            self.info_rcvd = d
            print("Object received : ", d)
            print("----------------------")

    def send_obj(self, obj):
        msg = pickle.dumps(obj)
        self.socket.send(msg)
        print("Sent an object : ", obj)
        print("----------------------")