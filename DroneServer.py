import sys
from time import sleep
import numpy as np
import threading, queue
import socket
import subprocess
from rplidar import RPLidar

# this class is meant to be run in a seperate thread
class DroneServer:
    # needs to have a thread-safe map, thread-safe telemetry data, and a message_queue to
    # communicate with drone
    def __init__(self, env_map, telemetry_data, message_queue):
        self.env_map = env_map
        self.telemetry_data = telemetry_data
        self.message_queue = message_queue
        self.lock = threading.Lock()
        self.is_running = False
        # self.ADDR = (server, port number)
        self.clients = list()
        self.HEADER = 64
    #  self.ADDR = (socket.gethostbyname(socket.gethostname()), 5050)
        self.ADDR = ('192.168.1.107', 5050) #temp
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)

        # lidar stuff
        self.lidar = RPLidar('/dev/ttyUSB0')
        self.current_reading = np.empty((0, 0))

        info = self.lidar.get_info()
        print(info)

        health = self.lidar.get_health()
        print(health)

    def read_lidar(self):
        for scan in self.lidar.iter_scans():
            self.current_reading = np.array(scan)
            # np.save('temp.npy', np.array([self.current_reading]))

    def run(self):
        thread = threading.Thread(target = self.start)
        thread.start()
        self.lidar_thread = threading.Thread(target = self.read_lidar)
        self.lidar_thread.start()
 
    def start(self):
        self.server.listen()
        print(f"[LISTENING] server is listening on {self.ADDR}")
        while True:
            try:
                conn, addr = self.server.accept()
                self.clients.append(conn)
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.start()
                print("[ACTIVE CONNECTIONS] {}".format(threading.activeCount() - 1))
            except OSError:
                for conn in self.clients:
                    conn.close()
                break

    def stop(self):
        print('closing server')
        self.lidar.stop()
        self.lidar.disconnect()
        self.server.close()
        self.lidar_thread.join()

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        init = False
        connected = True
        client_type = None

        while connected:
            try:
                msg = conn.recv(self.HEADER).decode('utf-8')
                # blank message is sent the first time we connect, make sure we get actual message
                if msg:
                    # strip padded part of buffer away
                    #first msg dictates length, second msg is contents
                    msg_length = int(msg.strip())
                    msg = conn.recv(msg_length).decode('utf-8').strip()

                    #first message will always contain client type
                    if not init:
                        client_type = self.get_client_type(msg)
                        print(client_type)
                        init = True
                    else:
                        if client_type == 'TELEMETRY':
                            self.handle_telemetry_client(conn)
                        elif client_type == 'MAP':
                            self.handle_map_client(conn)
                        elif client_type == 'COMMAND':
                            self.handle_command_client(conn, msg)
                        else:
                            print('this is illegal, should never happen')
            except OSError:
                break

    def get_client_type(self, msg):
        client_type = None
        if msg == 'TELEMETRY':
            client_type = 'TELEMETRY'
        elif msg == 'MAP':
            client_type = 'MAP'
        elif msg == 'COMMAND':
            client_type = 'COMMAND'
        else:
            print('this client type is not supported')
        return client_type
            

    def handle_map_client(self, conn):
        print("Sending map data.")
        # conn.send("Map data:".encode('utf-8')) 
        print(self.current_reading.shape)
        temp = np.array(self.current_reading).tostring()
        conn.send(temp)
        pass

    def handle_telemetry_client(self, conn):
        print("Sending telemetry data")
        conn.send("Telemetry data:".encode('utf-8')) 
        pass

    def handle_command_client(self, conn, msg):
        print(f"Command {msg} was receivied from the client") 
        pass

