import socket
import threading
from threading import Event
from time import sleep
import time

# 64 byte header is sent before every message, dictating how long the next message will be
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

event = Event()

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        try:
            msg = conn.recv(HEADER).decode('utf-8')
            # blank message is sent the first time we connect, make sure we get actual message
            if msg:
                # strip padded part of buffer away
                header = msg.strip().split('|', 1)
                msg_length = int(header[0])
                msg_type = header[1]

                if msg_type == 'TEL':
                    print("sending telemetry data")
                    conn.send("Telemetry data:".encode('utf-8'))    
                elif msg_type == 'MAP':
                    print("sending map data")
                    conn.send("Map data:".encode('utf-8'))    

                if msg == DISCONNECT_MESSAGE:
                    connected = False
        except OSError:
            break

        

def start():
    clients = list()
    server.listen()
    print(f"[LISTENING] server is listening on {SERVER}")
    while True:
        try:
            conn, addr = server.accept()
            clients.append(conn)
            thread = threading.Thread(target = handle_client, args=(conn, addr))
            thread.start()
            print("[ACTIVE CONNECTIONS] {}".format(threading.activeCount() - 1))
        except OSError:
            for conn in clients:
                conn.close()
            break

def main():
    thread = threading.Thread(target = start)
    thread.start()
    while True:
        try:
            sleep(1)
        except KeyboardInterrupt:
            server.close()
            break
if __name__ == "__main__":
    main()