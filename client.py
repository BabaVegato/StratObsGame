import socket
import pickle

class Client : 
    def __init__(self):
        self.state_rcvd = None
        self.server_socket = None
        self.socket = None

    def create_client(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def wait_for_object(self):
        #d = None
        while True:
            msg = self.socket.recv(2048)
            d = pickle.loads(msg)
            self.state_rcvd = d
            print("Object received : ", d)

    def send_obj(self, obj):
        msg = pickle.dumps(obj)
        self.server_socket.send(msg)