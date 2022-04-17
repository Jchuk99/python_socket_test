from dataclasses import dataclass
import numpy as np
import pandas as pd
import threading
import copy
MAP_SIZE_PIXELS         = 500
MAP_SIZE_METERS         = 20
MAP_SCALE_METERS_PER_PIXEL = MAP_SIZE_METERS / float(MAP_SIZE_PIXELS)
RADIUS = .75
HEADER = 64

# MESSAGE PROTOCOL:
# 1st message to server must contain client type
# Messages have two parts:
#   first: sending the length of the message so
#   the server knows how much mem to allocate
#   second: the actual message contents
def send_message(client, header_msg, msg):
        padded_header_msg = header_msg + b' ' * (HEADER - len(header_msg))
        client.send(padded_header_msg)
        client.send(msg)

def find_radius(x_mm,y_mm):
    #mm -> m
    x = x_mm/1000
    y = y_mm/1000
    # flip, so x = y, y = x (for indexing into data)

    #m => pixels
    x = x/MAP_SCALE_METERS_PER_PIXEL
    y = y/MAP_SCALE_METERS_PER_PIXEL

    x = round(x)
    y = round(y)

    #max range
    s = MAP_SIZE_PIXELS
    #radius in meters
    rad = RADIUS
    #m -> pixels
    ran = rad/MAP_SCALE_METERS_PER_PIXEL
        
    #radius of drone detection
    x_min = int(x-ran)
    x_max = int(x+ran)
    y_min = int(y-ran)
    y_max = int(y+ran)
        
    #adjust for out of bounds
    if x_min < 0:
        x_min = 0
        
    if y_min < 0:
        y_min = 0

    if x_max > s:
        x_max = s

    if y_max > s:
        y_max = s

    return x,y,x_min,x_max,y_min,y_max
    

@dataclass
class Telemetry:
    altitude : float = 0.0
    pitch : float = 0.0
    yaw : float = 0.0
    roll : float = 0.0
    velocity : float = 0.0
    airspeed : float = 0.0
    groundspeed : float = 0.0
    flight_mode : str = ""
    vx : float = 0.0
    vy : float = 0.0

    def __str__(self):
        string = """altitude: {} m, pitch: {}, yaw: {}, roll: {},
            velocity: {}, airspeed: {}, groundspeed: {}, flight_mode: {}
            vx: {}. vy:{}
            """.format(
            self.altitude, self.pitch, self.yaw, self.roll,
            self.velocity, self.airspeed, self.groundspeed, 
            self.flight_mode, self.vx, self.vy
        )
        return string

@dataclass
class MapData:
    lidar_data : np.ndarray = np.empty((1, 3))
    mapbytes:  bytearray = bytearray()
    x : float = 0.0 # mm
    y : float = 0.0 # mm
    theta : float = 0.0 # degrees

    def get_map_as_np(self):
        map_arr = np.frombuffer(self.mapbytes, dtype=np.uint8, count=-1)
        map_arr = map_arr.reshape(MAP_SIZE_PIXELS, MAP_SIZE_PIXELS)
        return map_arr
    
    def get_occupancy_grid(self):
        map_arr = self.get_map_as_np()
        map_arr = map_arr < 128
        map_arr = map_arr.astype(int)
        return map_arr
    
    def get_x_pixel(self):
        meters = self.x / 1000.0
        return meters/MAP_SCALE_METERS_PER_PIXEL

    def get_y_pixel(self):
        meters = self.y / 1000.0
        return meters/MAP_SCALE_METERS_PER_PIXEL


    def __str__(self):
        string = '{} {} {}'.format(self.x, self.y, self.theta)
        return string


# haven't tested on non numpy objects
class LockedObject(object):
    """
    Thread safe object
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.val = None

    def __get__(self, obj, objtype):
        self.lock.acquire()
        if self.val != None:
            # return a copy of the data could be slowing us down but safer
            if isinstance(ret_val, np.ndarray):
                ret_val = self.val.copy()
            else:
                ret_val = copy.deep_copy(self.val)
        else:
            ret_val = None
        self.lock.release()
        # print('getting', ret_val)
        return ret_val

    def __set__(self, obj, val):
        self.lock.acquire()
        # print('setting', val)
        # speed up for nparrays
        if isinstance(val, np.ndarray):
            self.val = val.copy()
        else:
            self.val = copy.deep_copy(val)
        self.lock.release()
