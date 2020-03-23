import socket
from _thread import *
import sys
import pickle
import select

HEADERSIZE = 10

d = {1: "hey", 2: "there"}

host = "192.168.1.66"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen()

print("Listening on port 5555 ...")
while True:
    conn, addr = s.accept()
    print(f"Connection from {addr} has been established !")
    msg = pickle.dumps(d)
    conn.send(msg)
    print("Sent an object : ", d)
    received = conn.recv(2048)
    obj = pickle.loads(received)
    print("Received an object : ", obj)


