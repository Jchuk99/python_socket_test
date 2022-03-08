MAP_SIZE_PIXELS         = 500
MAP_SIZE_METERS         = 10
LIDAR_DEVICE            = '/dev/ttyUSB0'

# Ideally we could use all 250 or so samples that the RPLidar delivers in one 
# scan, but on slower computers you'll get an empty map and unchanging position
# at that rate.
MIN_SAMPLES   = 200

from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel

import sys
sys.path.append(".")
from PyLidar import PyLidar
from utils import LockedObject
import subprocess
import numpy as np
import threading
from time import sleep
import time



class DroneMap:
    def __init__(self):
        # lidar stuff
        try:
            self.lidar = PyLidar(LIDAR_DEVICE, 115200)
            # Create an RMHC SLAM object with a laser model and optional robot model
            self.slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
            # connects the lidar using the default port (tty/USB0)
            self.lidar.connect()
            # Starts the lidar motor
            self.lidar.start_motor()
        except OSError:
            print("Lidar is not properly connected.")
            sys.exit()
        
        self.current_reading = LockedObject()
        self.current_reading = np.empty((0, 0))

        self.map = LockedObject()
        self.map = np.empty((0, 0))

        #info = self.lidar.get_info()
        #print(info)

        #health = self.lidar.get_health()
        #print(health)

        # ultrasonic stuff?

    def read(self):
        #TODO: this is  where the SLAM algorithm should go 
    
        self.slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

        # We will use these to store previous scan in case current scan is inadequate
        previous_distances = None
        previous_angles    = None

        # Initialize empty map
        mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
        while True:
            items = self.lidar.get_lidar_scans_as_np(True)
            self.current_reading = items
             # Extract distances and angles from triples
            distances = items[:,2].tolist()
            print(distances)
            angles    = items[:,1].tolist()
            print(angles)
            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > MIN_SAMPLES:
                self.slam.update(distances, scan_angles_degrees=angles)
                previous_distances = distances.copy()
                previous_angles    = angles.copy()
                # If not adequate, use previous
            elif previous_distances is not None:
                self.slam.update(previous_distances, scan_angles_degrees=previous_angles)
                 # Get current robot position
            x, y, theta = self.slam.getpos()

            # Get current map bytes as grayscale
            self.slam.getmap(mapbytes)
            self.map = np.reshape(
                np.frombuffer(mapbytes, dtype=np.int8),
                newshape=(MAP_SIZE_PIXELS, MAP_SIZE_PIXELS)
            )
            print(str(self.map))
            sleep(.1)
        pass

    def run(self):
        self.lidar_thread = threading.Thread(target = self.read)
        self.lidar_thread.start()

    def stop(self):
        print('stopping lidar')
       # self.lidar.stopmotor()
        self.lidar.disconnect()
        self.lidar_thread.join()

    def get_lidar_data(self):
         print(self.current_reading.shape)
         data = self.current_reading
         return data
    
    def get_map(self):
         data = self.map
         return data
         
