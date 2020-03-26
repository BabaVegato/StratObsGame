import socket
import threading
import pickle
import select

class Server:
    def __init__(self):
        self.host = "192.168.1.68"
        self.port = 5555
        self.socket = None
        self.running = False
        self.conn = None

    def create_server(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen()
        self.running = True
        self.conn_addr = None
        self.conn = None
        self.state_rcvd = None
        print("Listening on port 5555 ...")

    def wait_for_a_connection(self):
        while self.conn_addr is None :
            self.conn, self.conn_addr = self.socket.accept()
            print(f"Connection from {self.conn_addr} has been established !")

    def send_obj(self, conn, obj):
        msg = pickle.dumps(obj)
        self.conn.send(msg)
        print("Sent an object : ", obj)
        

    def wait_for_object(self, conn):
        while True:
            msg = self.conn.recv(4096)
            d = pickle.loads(msg)
            self.state_rcvd = d
            print("Object received : ", d)

