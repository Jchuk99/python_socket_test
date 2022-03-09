import sys
sys.path.append(".")
import utils
import socket
import pickle
from time import sleep
import numpy as np

class MapClient:
    def __init__(self, ip_type, protocol, addr):
        self.socket_map = {
            "IPV4" : socket.AF_INET,
            "TCP" : socket.SOCK_STREAM
        }
        self.init_msg = "MAP".encode('utf-8')
        self.init_msg_size = str(len(self.init_msg)).encode('utf-8')
        self.ADDR = addr

        self.client = socket.socket(
            self.socket_map[ip_type.upper()], 
            self.socket_map[protocol.upper()]
        )

        #this np array is currently serving as thread-safe drone_map object
        self.current_lidar_reading = utils.LockedObject()
        self.current_lidar_reading = np.empty((1, 3))

        self.position_map = utils.LockedObject()
        self.position_map = utils.PositionMap()

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
                
                #TODO: refactor into two different clients?
                #get lidar data

                data_length = int(self.client.recv(utils.HEADER).decode('utf-8').strip())
                print(data_length)
                data = b''
                while len(data) < data_length:
                    packet = self.client.recv(4096)
                    if not packet: break
                    data += packet
                arr = pickle.loads(data)
                print(arr)
                #get map data
                data_length = int(self.client.recv(utils.HEADER).decode('utf-8').strip())
                print(data_length)
                data = b''
                while len(data) < data_length:
                    packet = self.client.recv(4096)
                    if not packet: break
                    data += packet
                self.position_map = pickle.loads(data)

                if  arr.size % 3 == 0:
                    new = np.reshape(arr, (int(arr.size / 3), 3))
                    self.current_lidar_reading = new
                sleep(.05)
            except (ConnectionAbortedError, OSError) as e:
                print("user is breaking client connection.")
                break
