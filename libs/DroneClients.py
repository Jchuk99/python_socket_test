import sys
sys.path.append(".")
import utils
from time import sleep
from threading import Thread
import threading, queue
import socket
import pickle
import numpy as np

class DroneClients:
    # needs to have a thread-safe map (currently is lidar_reading), thread-safe telemetry data, 
    # requires server to be running first
    def __init__(self, env_map, telemetry_data, server, port):
        self.env_map = env_map
        self.telemetry_data = telemetry_data
        self.lock = threading.Lock()
        self.is_running = False

        # self.ADDR = (server, port number)
        self.ADDR = (server, port)
        
        #this np array is currently serving as thread-safe drone_map object
        self.current_lidar_reading = utils.LockedObject()
        self.current_lidar_reading = np.empty((1, 3))

    def start(self):
        self.telemetry_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.telemetry_client.connect(self.ADDR)

        self.map_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.map_client.connect(self.ADDR)

        self.command_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.command_client.connect(self.ADDR)

        # make this a dictionary 
        self.clients = {
            self.telemetry_client : "TELEMETRY".encode('utf-8'),
            self.map_client : "MAP".encode('utf-8'),
            self.command_client : "COMMAND".encode('utf-8')
        }

        for client, msg in self.clients.items():
            # initializing the client types
            utils.send_message(client, str(len(msg)).encode('utf-8'), msg)
         
        self.request_clients = [self.telemetry_client, self.map_client]

    def run(self):
        self.start()
        self.lock.acquire()
        try:
            self.is_running = True
        finally:
            self.lock.release()

        thread = Thread(target = self.run_requests)
        thread.start()
 
    def run_requests(self):
        for client in self.request_clients:
            thread = Thread(target = self.request_data, args=(client, self.clients.get(client)))
            thread.start()
        while True:
            sleep(1)
            if not self.running():
                print('exiting')
                break

    def stop(self):
        self.lock.acquire()
        try:
            self.is_running = False
        finally:
            self.lock.release()

        for client in self.clients:
            client.close()

    def request_data(self, client, msg):
        connected = True
        while connected:
            try:
                # dont have to send this everytime, think bout it later
                utils.send_message(client, str(len(msg)).encode('utf-8'), msg )
                data_length = int(client.recv(utils.HEADER).decode('utf-8').strip())
                
                if (msg == b'MAP'):
                    arr = pickle.loads(client.recv(data_length))

                    if arr.size % 3 == 0:
                        new = np.reshape(arr, (int(arr.size / 3), 3))
                        self.current_lidar_reading = new
                # else:
                #     print(client.recv(2048).decode('utf-8'))
                sleep(.1)
            except (ConnectionAbortedError, OSError) as e:
                print("user is breaking client connection.")
                break
        return

    def running(self):
        is_running = None
        self.lock.acquire()
        try:
            is_running = self.is_running
        finally:
            self.lock.release()
        return is_running

    # will be called on GUI event
    def send_command(self, msg):
        utils.send_message(
            self.command_client, 
            str(len(msg)).encode('utf-8'), 
            msg.encode('utf-8')
        )
        return 
