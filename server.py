import socket
import threading
import time

# 64 byte header is sent before every message, dictating how long the next message will be
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
print(SERVER)
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode('utf-8')
        # blank message is sent the first time we connect, make sure we get actual message
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode('utf-8')
            print(f"[{addr}] {msg}")
            conn.send("Msg received".encode('utf-8'))
            if msg == DISCONNECT_MESSAGE:
                connected = False

    conn.close()
        

def start():
    server.listen()
    print(f"[LISTENING] server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target = handle_client, args=(conn, addr))
        thread.start()
        print("[ACTIVE CONNECTIONS] {}".format(threading.activeCount() - 1))

def main():
    print("[STARTING] server is starting...")
    start()

if __name__ == "__main__":
    main()