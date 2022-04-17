import sys
sys.path.append(".")
import utils
from time import sleep
import threading, queue
import pickle
import socket
import logging


# this class is meant to be run in a seperate thread
class DroneServer:
    # needs to have a thread-safe map, thread-safe telemetry data, and a message_queue to
    # communicate with drone
    def __init__(self, drone_map, drone_vehicle, message_queue, server, port):
        # an already running drone map
        self.drone_map = drone_map
        self.drone_vehicle = drone_vehicle
        self.message_queue = message_queue
        self.clients = list()
  
        self.ADDR = (server, port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)


    def run(self):
        thread = threading.Thread(target = self.start)
        thread.start()
 
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
        logging.info('Closing server')
        self.server.close()


    def handle_client(self, conn, addr):
        logging.info("[NEW CONNECTION] %s connected.", addr)
        init = False
        connected = True
        client_type = None

        while connected:
            try:
                msg = conn.recv(utils.HEADER).decode('utf-8')
                # blank message is sent the first time we connect, make sure we get actual message
                if msg:
                    # strip padded part of buffer away
                    #first msg dictates length, second msg is contents
                    msg_length = int(msg.strip())
                    msg = conn.recv(msg_length).decode('utf-8').strip()

                    #first message will always contain client type
                    if not init:
                        client_type = self.get_client_type(msg)
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
        logging.info('Sendig map info')

        # get data
        map_data = self.drone_map.get_map_data()
        
        # construct header message/transform numpy lidar readings to byte array
        byte_map_data = pickle.dumps(map_data)
        #print(f"drone lidar data: {byte_lidar_data}")
        
        header = str(len(byte_map_data)).encode('utf-8')
        utils.send_message(conn, header, byte_map_data)

    def handle_telemetry_client(self, conn):
        logging.info("Sending telemetry data")

        # get data
        telemetry = self.drone_vehicle.telemetry
        #print(telemetry)

        # construct header message/transform numpy lidar readings to byte array
        byte_telemetry_data = pickle.dumps(telemetry)
        #print(f"telemetry data: {byte_telemetry_data}")
       
        header = str(len(byte_telemetry_data)).encode('utf-8')
        utils.send_message(conn, header, byte_telemetry_data)


    def handle_command_client(self, conn, msg):
        logging.info("Command %s was receivied from the client", msg) 
        self.message_queue.put(msg)
  

