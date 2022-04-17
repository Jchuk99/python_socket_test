import sys
import os
import utils

from TelemetryClient import TelemetryClient
from CommandClient import CommandClient
from MapClient import MapClient
from time import sleep
from threading import Thread
import threading, queue
import socket
import pickle
import numpy as np

class DroneClients:
    # needs to have a thread-safe map (currently is lidar_reading), thread-safe telemetry data, 
    # requires server to be running first
    def __init__(self, server, port):
        self.lock = threading.Lock()
        self.is_running = False

        # self.ADDR = (server, port number)
        self.ADDR = (server, port)
        

    def start(self):
        self.telemetry_client = TelemetryClient("IPv4", "TCP", self.ADDR)

        self.map_client = MapClient("IPv4", "TCP", self.ADDR)

        self.command_client = CommandClient("IPv4", "TCP", self.ADDR)

        # make this a dictionary 
        self.clients = [
            self.telemetry_client,
            self.map_client,
            self.command_client 
        ]

        for client in self.clients:
            # initializing the client types
            client.connect()
            client.init()
         
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
            thread = Thread(target = client.request_data)
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

    def running(self):
        is_running = None
        self.lock.acquire()
        try:
            is_running = self.is_running
        finally:
            self.lock.release()
        return is_running

    def get_lidar_scan(self):
        #print(np.array_str(self.current_lidar_reading))
        return self.map_client.current_lidar_reading
    
    def get_map_data(self):
        return self.map_client.map
    
    def get_calculated_velocity(self):
        return self.telemetry_client.telemetry.vx, self.telemetry_client.telemetry.vy
   
    # will be called on GUI event
    def send_command(self, msg):
        self.command_client.send_command(msg)
        return 
