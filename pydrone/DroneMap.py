MAP_SIZE_PIXELS         = 500
MAP_SIZE_METERS         = 15
LIDAR_DEVICE            = '/dev/ttyUSB0'

# Ideally we could use all 250 or so samples that the RPLidar delivers in one 
# scan, but on slower computers you'll get an empty map and unchanging position
# at that rate.
MIN_SAMPLES   = 200

from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from scipy.interpolate import interp1d


import sys
sys.path.append(".")
from PyLidar import PyLidar
from utils import LockedObject
from utils import MapData
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
            # connects the lidar using the default port (tty/USB0)
            self.lidar.connect()
            # Starts the lidar motor
            self.lidar.start_motor()
        except OSError:
            print("Lidar is not properly connected.")
            sys.exit()

        self.map = LockedObject()
        self.map = MapData()

        self.current_lidar_reading = LockedObject()
        self.current_lidar_reading = np.empty((1,3))

        #info = self.lidar.get_info()
        #print(info)

        #health = self.lidar.get_health()
        #print(health)

        # ultrasonic stuff?

    def read_lidar_data(self):
        while True:
            self.current_lidar_reading = self.lidar.get_lidar_scans_as_np(True)
            sleep(.05)
  
    def update_map(self):
        #TODO: this is  where the SLAM algorithm should go 
    
        self.slam = RMHC_SLAM(
            LaserModel(), 
            MAP_SIZE_PIXELS, 
            MAP_SIZE_METERS, 
            map_quality=50, 
            hole_width_mm=2000,
            max_search_iter=3000
            )

        # We will use these to store previous scan in case current scan is inadequate
        previous_distances = None
        previous_angles    = None

        # Initialize empty map
        mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

        while True:
            items = self.current_lidar_reading
             # Extract distances and angles from triples
            distances = items[:,2].tolist()
            angles = items[:,1].tolist()
           # print(len(distances))
            f = interp1d(angles, distances, fill_value='extrapolate')
            distances = list(f(np.arange(360)))
            #print(len(distances))
            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > MIN_SAMPLES:
                self.slam.update(distances)
                previous_distances = distances.copy()
                # If not adequate, use previous
            elif previous_distances is not None:
                self.slam.update(previous_distances)
                 # Get current robot position
            x, y, theta = self.slam.getpos()
            # print(
            #     'x:{}, y:{}, theta:{}'.format(
            #         x,y,theta
            #     )
            # )
            # Get current map bytes as grayscale
            self.slam.getmap(mapbytes)
            self.map = MapData(
                items,mapbytes,x,y,theta
            )

        pass

    def run(self):
        self.lidar_thread = threading.Thread(target = self.read_lidar_data)
        self.map_thread = threading.Thread(target = self.update_map)
        self.lidar_thread.start()
        self.map_thread.start()

    def stop(self):
        print('stopping lidar')
       # self.lidar.stopmotor()
        self.lidar.disconnect()
        self.lidar_thread.join()
        self.map_thread.join()

    def get_map_data(self):
         data = self.map
         return data
         
