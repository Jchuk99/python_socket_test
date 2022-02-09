import socket
import threading


HEADER = 64
PORT = 5050
SERVER = "10.0.0.101"
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"

tel_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tel_client.connect(ADDR)

map_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
map_client.connect(ADDR)

def send(msg):
    message = msg.encode('utf-8')
    msg_length = len(message)
    send_length = str(msg_length).encode('utf-8')
    padded_send_length = send_length + b' ' * (HEADER - len(send_length))
    client.send(padded_send_length)
    client.send(message)
    print(client.recv(2048).decode('utf-8'))

def request_tele(client):
    while True:
        request_msg = f"{str(0)}|TEL".encode('utf-8')
        padded_request_msg = request_msg + b' ' * (HEADER - len(request_msg))
        client.send(padded_request_msg)
        print(client.recv(2048).decode('utf-8'))

def request_map(client):
    while True:
        request_msg = f"{str(0)}|MAP".encode('utf-8')
        padded_request_msg = request_msg + b' ' * (HEADER - len(request_msg))
        client.send(padded_request_msg)
        print(client.recv(2048).decode('utf-8'))

thread = threading.Thread(target = request_tele, args=(tel_client,))
thread.start()
thread = threading.Thread(target = request_map, args=(map_client,))
thread.start()

print('done')
