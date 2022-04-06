
from dronekit import VehicleMode, connect, LocationGlobalRelative
import sys
sys.path.append(".")
import utils
from pymavlink import mavutil
import threading
import numpy as np
import time
from time import sleep

import socket
import argparse
import math

# responsible for running code that moves the vehicle
class DroneVehicle:

	def __init__(self, drone_map = None, connect = True):
		#connect to flight controller
		#THIS SHOULD BE THE EXACT SAME OBJECT THAT DRONE SERVER IS TALKING TO
		self.drone_map = drone_map
		self.isRunning = utils.LockedObject()
		self.isRunning = False
		self.telemetry = utils.LockedObject()
		self.telemetry = utils.Telemetry()

		self.telemetry_thread = threading.Thread(target=self.read)
		self.vehicle_thread = threading.Thread(target=self.start)

		if connect:
			self.vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)
		#self.vehicle = connect(self.addr, wait_ready=True)
		#vehicle = connect('tcp:192.168.1.1:5760', wait_ready=True)

	def read(self):
		while self.running:
			self.telemetry = utils.Telemetry(
				self.vehicle.location.global_relative_frame.alt,
				self.vehicle.attitude.pitch,
				self.vehicle.attitude.yaw,
				self.vehicle.attitude.roll,
				self.vehicle.velocity,
				self.vehicle.airspeed,
				self.vehicle.groundspeed,
				self.vehicle.mode.name
			)
			sleep(2)


	def run(self):
		self.vehicle_thread = threading.Thread(target=self.start, args=(1,))
		self.vehicle_thread.start()

	def start(self, targetAlt):

		self.running = True

		self.telemetry_thread.start()

		print("Arming motors")
		# Copter should arm in GUIDED mode
		self.vehicle.mode    = VehicleMode("GUIDED")
		self.vehicle.armed   = True

		# Confirm vehicle armed before attempting to take off
		while not self.vehicle.armed:
			print(" Waiting for arming...")
			time.sleep(1)

		print(f'vehicle.mode: {self.vehicle.mode}')
		print("Taking off!")
		self.vehicle.simple_takeoff(1) # Take off to target altitude

		# Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
		#  after Vehicle.simple_takeoff will execute immediately).
		while True:
			print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
			#Break and return from function just below target altitude.
			if self.vehicle.location.global_relative_frame.alt>=targetAlt*0.95:
				print("Reached target altitude")
				break
			time.sleep(1)

		print("attempting to land")
		while self.running:
			self.vehicle.mode = VehicleMode("LAND")
			# obstacle detection goes here
			
			
			parseMapData(self.drone_map.map.x,self.drone_map.map.y,self.drone_map.map.theta,self.drone_map.map.get_map_as_np())
	
	
	
	def stop(self):
		self.vehicle.mode = VehicleMode("LAND")
		self.running = False


	def setV(self, Vx, Vy, Vz):
		msg = self.vehicle.message_factory.set_position_target_local_ned_encode(
				0,
				0,0,
				mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
				0b0000111111000111,
				0,0,0,
				Vx, Vy, Vz,
				0,0,0,
				0,0)
		self.vehicle.send_mavlink(msg)
		self.vehicle.flush()
		
	def foundObjT(self,x,y,theta):
		#fix theta
		if theta > 360:
			while theta > 360:
				theta = theta-360
		elif theta < 0:
			theta = theta*-1
			
		newX = (-math.cos(math.radians(theta)))*2
		newY = (-math.sin(math.radians(theta)))*2
		
		#self.setV(newY, newX, 0)
	
	def foundObj(self,s_x,s_y,theta,x_max,y_max,r):
		x_orig = x_max - r
		y_orig = y_max - r
		
		#negative
		if theta < 0:
			theta = theta*-1
			#mod and convert to positive
			theta = theta%360
			theta = 360-theta
		#positive
		else :
			#mod
			theta = theta%360
		
		#east
		if theta <= 45 or theta >= 315:
			y = s_y - (2*y_orig)
			x = s_x
		#north
		elif theta <= 135:
			y = s_y
			x = s_x
		#west
		elif theta <= 225:
			y = s_y
			x = s_x - (2*x_orig)
		#south
		else:
			y = s_y - (2*y_orig)
			x = s_x - (2*x_orig)
		
		#checks edge cases
		if x==0:
			if y>0:
				#self.setV(-0.25,0,0)
				#time.sleep(1)
				#self.stopMov()
				print("\nvelociy is:" + str(-0.25)+ ", " + str(0))
			elif y<0:
				#self.setV(0.25,0,0)
				#time.sleep(1)
				#self.stopMov()
				print("\nvelociy is:" + str(0.25)+ ", " + str(0))
		elif y==0:
			if x>0:
				#self.setV(0,-0.25,0)
				#time.sleep(1)
				#self.stopMov()
				print("\nvelociy is:" + str(0)+ ", " + str(newX))
			elif x<0:
				#self.setV(0,0.25,0)
				#time.sleep(1)
				#self.stopMov()
				print("\nvelociy is:" + str(0)+ ", " + str(newX))
		#take constant ratio and reduce
		elif y!=0 and x!=0:			
			if abs(x) > abs(y):
				k = y/x
			else:
				k = x/y
			
			if k < 0:
				k = k*(-1)
			
			#create new velocities
			if abs(x) > abs(y):
				newX = 0.35						
				newY = newX*k
			else:
				newY = 0.35
				newX = newY*k
			
			#set correct sign
			if x > 0:
				newX = newX*(-1)
			
			if y > 0:
				newY = newY*(-1)
			
			#set velocity
			#self.setV(newY,newX,0)
			#time.sleep(1)
			#self.stopMov()
			print("\nvelociy is:" + str(newY)+ ", " + str(newX))
			
		def returnToBase(self):
			self.vehicle.mode = VehicleMode("RTL")
		
		def stopMov(self):
			self.setV(0,0,0)
			
		def land(self):
			self.vehicle.mode = VehicleMode("LAND")
	
	def parseMapData(self,x_old,y_old,theta,data):
		#mm -> m
		x = y_old/1000
		y = x_old/1000
		
		#m => pixels
		x = x/0.02
		y = y/0.02
		
		print("x :" + str(x) + "\ny:" + str(y))
		#max range
		s = math.sqrt(data.size)
		#radius in meters
		rad = .5
		#m -> pixels
		ran = rad/.02
		
		#radius of drone detection
		x_min = x-rad
		x_max = x+rad
		y_min = y-rad
		y_max = y+rad
		
		#adjust for out of bounds
		if x_min < 0:
			x_min = 0
			
		if y_min < 0:
			y_min = 0
		
		if x_max > s:
			x_max = s
		
		if y_max > s:
			y_max = s
		
		#iterators
		i = int(x_min)
		j = int(y_min)
		
		#check range of pixels
		while(j < y_max):
			i = int(x_min)
			while (i < x_max):
				if data[i, j] == 1:
					print(data[i,j])
					print("\ni: " + str(i) + "\nj: " + str(j))
					self.foundObj(i,j,theta,x_max,y_max,ran)
					time.sleep(5)
					#revisit this to solve for drone returning to base only after object is gone
					#current idea, just let loop run and see what happens
					break
				i = i + 1

			j = j + 1
				


if __name__ == "__main__":
	map_data = None
	x = None
	y = None
	theta = None
	drone_vehicle = DroneVehicle(connect=False)
	with open("../test/data/map_data/position_1.txt", "r") as f:	
		position = f.readline().split(" ")	
		print(position)
		x = float(position[0])
		y = float(position[1])
		theta = float(position[2])
	map_data = np.loadtxt("../test/data/map_data/map_data_1.txt", dtype=np.uint8, delimiter=' ')
	#map_data = np.random.random_integers(0, 255, (500, 500))
	print(map_data.shape)
	drone_vehicle.parseMapData(x, y, theta, map_data)





