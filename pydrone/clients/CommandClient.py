import sys
sys.path.append(".")
import utils
import socket
import pickle
import numpy as np

class CommandClient:
    def __init__(self, ip_type, protocol, addr):
        self.map = {
            "IPV4" : socket.AF_INET,
            "TCP" : socket.SOCK_STREAM
        }
        self.init_msg = "COMMAND".encode('utf-8')
        self.init_msg_size = str(len(self.init_msg)).encode('utf-8')
        self.ADDR = addr

        self.client = socket.socket(
            self.map[ip_type.upper()], 
            self.map[protocol.upper()]
        )


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

    def send_command(self, msg):
        utils.send_message(
            self.client, 
            str(len(msg)).encode('utf-8'),
            msg.encode('utf-8')
        )
        return 