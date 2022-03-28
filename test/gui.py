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
        Form, Window = uic.loadUiType("test.ui")		

        self.app = QApplication([])
        self.window = Window()
        self.drone_clients = DroneClients("192.168.1.106", 5050)
        self.lidar = PyLidar("COM5", 115200)
        # connects the lidar using the default port (tty/USB0)
        self.lidar.connect()
        # Starts the lidar motor
        self.lidar.start_motor()
        self.connected = False

        self.form = Form()
        self.form.setupUi(self.window)

        self.map_viz = MapVisualizer(
            MAP_SIZE_PIXELS, MAP_SIZE_METERS, 
            'SLAM', show_trajectory=True 
        )

        self.canvas = FigureCanvas(plt.Figure())

        self.form.lidarGraph.addWidget(self.canvas)
        self.form.mapGraph.addWidget(self.map_viz.canvas)

        self.ax = self.canvas.figure.add_subplot(projection='polar')
        self.ax.set_rmax(8000)
        self.ax.grid(True)

        self.form.tabWidget.currentChanged.connect(self.tabChanged)
        self.form.connectButton.clicked.connect(self.connectDrone)

        self.lidar_render_thread = Thread(target = self.update_lidar_render)
        self.map_render_thread = Thread(target = self.update_map_render)

    def tabChanged(self):
        print("Tab was changed to", self.form.tabWidget.currentIndex())

    def start(self):
        self.window.show()
        self.app.exec_()
    
    def update_lidar_render(self):
        while self.connected:
            #arr = self.drone_clients.get_map_data().lidar_data
            arr = self.lidar.get_lidar_scans_as_np(filter_quality=True)
            self.ax.clear()
            theta = np.radians(arr[:, 1])
            self.ax.scatter(theta, arr[:, 2], s = 1)
            self.canvas.draw()
            sleep(.1)
    
    def update_map_render(self):
        while self.connected:
            env_map = self.drone_clients.get_map_data()
            # Display map and robot pose, exiting gracefully if user closes it
            if env_map.mapbytes:
                if not self.map_viz.display(
                    env_map.x/1000., env_map.y/1000., 
                    env_map.theta, env_map.mapbytes
                ):
                    exit(0)


    def connectDrone(self):
        if not self.connected:
            self.connected = True
            #self.drone_clients.run()
            self.lidar_render_thread.start()
            self.map_render_thread.start()
        else:
            self.connected = False
           # self.drone_clients.stop()
            self.lidar_render_thread.join()
            self.map_render_thread.join()

def main():
    gs = GroundStation()
    gs.start()

if __name__ == "__main__":
    main()