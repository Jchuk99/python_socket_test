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

from networking.DroneClients import DroneClients

class GroundStation:

	def __init__(self):
		Form, Window = uic.loadUiType("main.ui")		
		map = 0  # get_map
		telemetry = 0 #get_telemetry

		self.app = QApplication([])
		self.window = Window()
		self.drone_clients = DroneClients(map, telemetry,"192.168.1.107", 5050 )
		self.connected = False

		self.form = Form()
		self.form.setupUi(self.window)

		self.canvas = FigureCanvas(plt.Figure())
		self.form.lidarGraph.addWidget(self.canvas)
		self.ax = self.canvas.figure.add_subplot(projection='polar')
		self.ax.set_rmax(4000)
		self.ax.grid(True)

		self.form.connectButton.clicked.connect(self.connectDrone)

		self.lidar_render_thread = Thread(target = self.update_lidar_render)

	def start(self):
		self.window.show()
		self.app.exec_()

	def update_lidar_render(self):
		while self.connected:
			arr = self.drone_clients.current_lidar_reading
			self.ax.clear()
			self.ax.scatter(np.radians(arr[:, 0]), arr[:, 1], s = 1)
			
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
