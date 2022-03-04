from ctypes import *
import numpy as np
import time
lib = cdll.LoadLibrary(r'C:\Users\Udoka\Desktop\Projects\rplidar_sdk\workspaces\vc14\x64\Release\sdk_test.dll')

#TODO: mem leaks present because pointers aren't being freed
class LidarScan(Structure):
    _fields_ = [("data", POINTER(POINTER(c_double))),
                ("size", c_int)]

class PyLidar(object):
    def __init__(self, port, baud_rate):
        lib.createLidar.restype = c_void_p
        lib.createLidar.argtypes = [c_char_p, c_int]
        self.obj = c_void_p(lib.createLidar(c_char_p(str.encode(port)), c_int(115200)))

    def connect(self):
        lib.connect.argtypes = [c_void_p]
        lib.connect(self.obj)

    def start_motor(self):
        lib.startMotor.argtypes = [c_void_p]
        lib.startMotor(self.obj)
    
    def stop_motor(self):
        lib.stopMotor.argtypes = [c_void_p]
        lib.stopMotor(self.obj)

    def get_lidar_scans(self, filter_quality):
        lib.get_lidar_scan.argtypes = [c_void_p, c_bool]
        lib.get_lidar_scan.restype = POINTER(LidarScan)
        start = time.time()
        lidar_scans = lib.get_lidar_scan(self.obj, c_bool(filter_quality)).contents
        end = time.time()
        print("Elapsed time: {}".format(end - start))
        print("Frequency (Hz): {}".format(1/(end-start)))

        return lidar_scans

    def get_lidar_scans_as_np(self, filter_quality):
        lib.get_lidar_scan.argtypes = [c_void_p, c_bool]
        lib.get_lidar_scan.restype = POINTER(LidarScan)
        lidar_scans = lib.get_lidar_scan(self.obj, c_bool(filter_quality)).contents
        data = np.zeros((lidar_scans.size, 3))
        with np.nditer(data, flags=['multi_index'], op_flags=['readwrite']) as it:
            for x in it:
                x[...] = lidar_scans.data[it.multi_index[0]][it.multi_index[1]]
        # find way to free data
        # or self.free(lidar_scans)
        #lib.free(c_void_p(lidar_scans))
        return data


if __name__ == "__main__":
    lidar = PyLidar("COM5", 115200)
    lidar.connect()
    lidar.start_motor()
    # write one scan to file
    with open("lidar_scan_2.txt", "w") as file1:
        lidar_scans = lidar.get_lidar_scans(True)

        for i in range(0, lidar_scans.size, 1):
            file1.write(
                "angle: {} distance: {} quality: {}\n".format(
                    lidar_scans.data[i][0],
                    lidar_scans.data[i][1],
                    lidar_scans.data[i][2]
                )
            )
    with open("lidar_scan_2_np.txt", "w") as file1:
        lidar_scans = lidar.get_lidar_scans_as_np(True)
        np.savetxt("lidar_scan_2_np.txt", lidar_scans)
    print(str(np.loadtxt("lidar_scan_2_np.txt")))

