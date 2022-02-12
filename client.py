import socket
from threading import Thread, Event
from time import sleep


HEADER = 64
PORT = 5050
SERVER = "10.0.0.101"
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"

tel_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tel_client.connect(ADDR)

map_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
map_client.connect(ADDR)

event = Event()

def request_data(client, msg):
    while True:
        try:
            request_msg = msg.encode('utf-8')
            padded_request_msg = request_msg + b' ' * (HEADER - len(request_msg))
            client.send(padded_request_msg)
            print(client.recv(2048).decode('utf-8'))
        except (ConnectionAbortedError, OSError) as e:
            print("user is breaking client connection.")
            break

print('starting threads')
telemetry_msg = f"{str(0)}|TEL"
map_msg = f"{str(0)}|MAP"

thread = Thread(target = request_data, args=(tel_client, telemetry_msg))
thread.start()
thread = Thread(target = request_data, args=(map_client, map_msg))
thread.start()
print('threads started')

while True:
    try:
        sleep(1)
    except KeyboardInterrupt:
        print('keyboard interrupt')
        tel_client.close()
        map_client.close()
        break
