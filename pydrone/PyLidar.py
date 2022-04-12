from ctypes import *
import numpy as np
import time
import pathlib
import platform

if platform.system() == 'Windows':
    lib_path = pathlib.Path(__file__).parent.resolve()
    lib_path = pathlib.Path(lib_path, 'libs', 'Windows', 'x64', 'pylidar.dll')
else:
    lib_path = 'pylidar.so'
lib = cdll.LoadLibrary(str(lib_path))

#TODO: mem leaks present because pointers aren't being freed
class LidarScan(Structure):
    _fields_ = [("data", POINTER(POINTER(c_double))),
                ("size", c_int)]

class PyLidar(object):
    def __init__(self, port, baud_rate):
        lib.createLidar.restype = c_void_p
        lib.createLidar.argtypes = [c_char_p, c_int]
        print(str.encode(port))
        self.obj = c_void_p(lib.createLidar(str.encode(port), c_int(115200)))
    
    def free(self, ptr):
        lib.freeMem.argtypes = [c_void_p]
        lib.freeMem(c_void_p(ptr))
    
    def connect(self):
        lib.connect.argtypes = [c_void_p]
        lib.connect(self.obj)

    def disconnect(self):
        lib.disconnect.argtypes = [c_void_p]
        lib.disconnect(self.obj)
    
    def reset(self, timeout):
        lib.reset.argtypes = [c_void_p, c_uint32]
        lib.reset(self.obj, timeout)

    def start_motor(self):
        lib.startMotor.argtypes = [c_void_p]
        lib.startMotor(self.obj)
    
    def stop_motor(self):
        lib.stopMotor.argtypes = [c_void_p]
        lib.stopMotor(self.obj)
    
    def is_connected(self):
        lib.isConnected.argtypes = [c_void_p]
        lib.get_lidar_scan.restype = c_bool
        return lib.isConnected(self.obj)
    
    def check_health(self):
        lib.checkHealth.argtypes = [c_void_p]
        lib.get_lidar_scan.restype = c_bool
        return lib.checkHealth(self.obj)
    
    def get_frequency(self):
        lib.getFrequency.argtypes = [c_void_p]
        lib.getFrequency.restype = c_float
        return lib.getFrequency(self.obj)

    def get_lidar_scans(self, filter_quality):
        lib.get_lidar_scan.argtypes = [c_void_p, c_bool]
        lib.get_lidar_scan.restype = POINTER(LidarScan)
        lidar_scans = lib.get_lidar_scan(self.obj, c_bool(filter_quality)).contents
        return lidar_scans

    def get_lidar_scans_as_np(self, filter_quality):
        lib.get_lidar_scan.argtypes = [c_void_p, c_bool]
        lib.get_lidar_scan.restype = POINTER(LidarScan)
        lidar_scans = lib.get_lidar_scan(self.obj, c_bool(filter_quality)).contents
        data = np.zeros((lidar_scans.size, 3))
        if lidar_scans.size > 0:
            with np.nditer(data, flags=['multi_index'], op_flags=['readwrite']) as it:
                for x in it:
                    x[...] = lidar_scans.data[it.multi_index[0]][it.multi_index[1]]
        # find way to free data
        # or self.free(lidar_scans)
        #lib.free(c_void_p(lidar_scans))
        return data


if __name__ == "__main__":
    lidar = PyLidar("COM7", 115200)
    print("Connected: {} ".format(lidar.is_connected()))
    lidar.connect()
    print("Connected: {} ".format(lidar.is_connected()))
    lidar.start_motor()
    # write one scan to file
    with open("lidar_scan_2.txt", "w") as file1:
        lidar_scans = lidar.get_lidar_scans(True)
        frequency = lidar.get_frequency()
        print("Frequency (Hz): {}".format(frequency))

        for i in range(0, lidar_scans.size, 1):
            file1.write(
                "quality: {} angle: {} distance: {}\n".format(
                    lidar_scans.data[i][0],
                    lidar_scans.data[i][1],
                    lidar_scans.data[i][2]
                )
            )
    lidar.stop_motor()
    time.sleep(10)
    with open("lidar_scan_2_np.txt", "w") as file1:
        lidar_scans = lidar.get_lidar_scans_as_np(True)
        np.savetxt("lidar_scan_2_np.txt", lidar_scans)
    print(str(np.loadtxt("lidar_scan_2_np.txt")))

