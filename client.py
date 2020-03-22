import socket
import pickle

host = "192.168.1.66"
port = 5555
HEADERSIZE = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

while True : 
    full_msg = b''
    new_msg = True
    while True:
        msg = s.recv(2048)
        