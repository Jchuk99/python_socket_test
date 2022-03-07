import sys
sys.path.append(".")
import utils
import socket
import pickle
from time import sleep
import numpy as np

class MapClient:
    def __init__(self, ip_type, protocol, addr):
        self.map = {
            "IPV4" : socket.AF_INET,
            "TCP" : socket.SOCK_STREAM
        }
        self.init_msg = "MAP".encode('utf-8')
        self.init_msg_size = str(len(self.init_msg)).encode('utf-8')
        self.ADDR = addr

        self.client = socket.socket(
            self.map[ip_type.upper()], 
            self.map[protocol.upper()]
        )

        #this np array is currently serving as thread-safe drone_map object
        self.current_lidar_reading = utils.LockedObject()
        self.current_lidar_reading = np.empty((1, 3))

    def connect(self):
        self.client.connect(self.ADDR)

    def init(self):
        utils.send_message(
            self.client, 
            self.init_msg_size, 
            self.init_msg
        )

    def close(self):
        self.client.close()

    
    def request_data(self):
        connected = True
        while connected:
            try:
                utils.send_message(
                    self.client, 
                    self.init_msg_size, 
                    self.init_msg
                )

                data_length = int(self.client.recv(utils.HEADER).decode('utf-8').strip())
                arr = pickle.loads(self.client.recv(data_length))

                if  arr.size % 3 == 0:
                    new = np.reshape(arr, (int(arr.size / 3), 3))
                    self.current_lidar_reading = new
                #print("Map data: " + np.array_str(self.current_lidar_reading))
                sleep(.05)
            except (ConnectionAbortedError, OSError) as e:
                print("user is breaking client connection.")
                break
