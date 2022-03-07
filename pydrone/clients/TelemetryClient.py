import sys
sys.path.append(".")
import utils
import socket
import pickle
from time import sleep
import numpy as np

class TelemetryClient:
    def __init__(self, ip_type, protocol, addr):
        self.map = {
            "IPV4" : socket.AF_INET,
            "TCP" : socket.SOCK_STREAM
        }
        self.init_msg = "TELEMETRY".encode('utf-8')
        self.init_msg_size = str(len(self.init_msg)).encode('utf-8')
        self.ADDR = addr
        self.client = socket.socket(
            self.map[ip_type.upper()], 
            self.map[protocol.upper()]
        )
        self.telemetry = utils.LockedObject()
        self.telemetry = utils.Telemetry()

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
                self.telemetry = pickle.loads(self.client.recv(data_length))
               # print(self.telemetry)
                sleep(.1)
            except (ConnectionAbortedError, OSError) as e:
                print("user is breaking client connection.")
                break
        return
    

 