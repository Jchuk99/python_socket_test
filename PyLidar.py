from ctypes import *
lib = cdll.LoadLibrary(r'C:\Users\Udoka\Desktop\Projects\rplidar_sdk\workspaces\vc14\x64\Release\sdk_test.dll')

class PyLidar(object):
    def __init__(self):
        lib.createLidar.restype = c_void_p
        lib.createLidar.argtypes = [c_char_p, c_int]
        self.obj = c_void_p(lib.createLidar(c_char_p(b'COM5'), c_int(115200)))

    def connect(self):
        lib.connect.argtypes = [c_void_p]
        lib.connect(self.obj)

    def start_motor(self):
        lib.startMotor.argtypes = [c_void_p]
        lib.startMotor(self.obj)
    
    def stop_motor(self):
        lib.stopMotor.argtypes = [c_void_p]
        lib.stopMotor(self.obj)

    def get_lidar_samples(self):
        lib.get_scan_as_vectors.argtypes = [c_void_p, c_bool]
        lib.get_scan_as_vectors.restype = POINTER(POINTER(c_double))
        lidar_samples =  lib.get_scan_as_vectors(self.obj, c_bool(1))
        print("\nPython")
        print("angle: " +  str(lidar_samples[0][0]))
        print("distance: " + str(lidar_samples[0][1]))
        print("quality: " + str(lidar_samples[0][2]))
        print("\n")
        


lidar = PyLidar()
lidar.connect()
lidar.start_motor()
while True:
    lidar.get_lidar_samples()
