import sys
from time import sleep
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from threading import Thread
import pyqtgraph as pg
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.animation as animation

sys.path.append(r"../pydrone")
sys.path.append(r"../pydrone/clients")
from PyLidar import PyLidar
from DroneClients import DroneClients

class GroundStation:

    def __init__(self):
        Form, Window = uic.loadUiType("main.ui")		
        map = 0  # get_map
        telemetry = 0 #get_telemetry

        self.app = QApplication([])
        self.window = Window()
        self.drone_clients = DroneClients("10.0.0.101", 5050)
        # self.lidar = PyLidar("COM5", 115200)
        # # connects the lidar using the default port (tty/USB0)
        # self.lidar.connect()
        # # Starts the lidar motor
        # self.lidar.start_motor()
        self.connected = False

        self.form = Form()
        self.form.setupUi(self.window)

        self.canvas = FigureCanvas(plt.Figure())
        self.form.lidarGraph.addWidget(self.canvas)
        self.ax = self.canvas.figure.add_subplot(projection='polar')
        self.ax.set_rmax(8000)
        self.ax.grid(True)

        self.form.connectButton.clicked.connect(self.connectDrone)

        self.lidar_render_thread = Thread(target = self.update_lidar_render)

    def start(self):
        self.window.show()
        self.app.exec_()
    
    def update_lidar_render(self):
        while self.connected:
            arr = self.drone_clients.get_lidar_scan()
            #arr = self.lidar.get_lidar_scans_as_np(True)
            self.ax.clear()
           # print(arr)
            theta = np.radians(arr[:, 1])
            self.ax.scatter(theta, arr[:, 2], s = 1)
            self.canvas.draw()
            sleep(.1)


    def connectDrone(self):
        if not self.connected:
            self.connected = True
            self.drone_clients.run()
            self.lidar_thread = Thread(target = self.update_lidar_render)
            self.lidar_thread.start()
        else:
            self.connected = False
            self.drone_clients.stop()
            self.lidar_thread.join()

def main():
    gs = GroundStation()
    gs.start()

if __name__ == "__main__":
    main()