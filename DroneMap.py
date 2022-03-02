import sys
sys.path.append(".")
from utils import LockedObject
import subprocess
import numpy as np
import threading
from rplidar import RPLidar
#from FastestRplidar.source.fastestrplidar import FastestRplidar


class DroneMap:
    def __init__(self):
        # lidar stuff
        self.lidar = PyLidar("COM5", 115200)
         # connects the lidar using the default port (tty/USB0)
        self.lidar.connect()
         # Starts the lidar motor
        self.lidar.start_motor()

        self.current_reading = LockedObject()
        self.current_reading = np.empty((0, 0))

        #info = self.lidar.get_info()
        #print(info)

        #health = self.lidar.get_health()
        #print(health)

        # ultrasonic stuff?

    def read(self):
        #TODO: this is  where the SLAM algorithm should go 
        # methods/objects outside of the map should not have any idea about lidar,
        # lidar scans should be passed into BreezySLAM algorithim to generate map
        # right now the lidar readings are using lockedObject class, which makes underlying
        # data collection thread-safe, will want to change that with the actual map object in the futre
        # unless we want to keep the possiblility of getting botht the map and the lidar readings.
        while True:
                self.current_reading = self.lidar.get_scan_as_np(True)
                sleep(.1)
        pass

    def run(self):
        self.lidar_thread = threading.Thread(target = self.read)
        self.lidar_thread.start()

    def stop(self):
        print('stopping lidar')
       # self.lidar.stopmotor()
        self.lidar_thread.join()

    def get_lidar_data(self):
         print(self.current_reading.shape)
         data = self.current_reading
         return data
         
