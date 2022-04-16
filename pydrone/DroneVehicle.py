
#from ssl import VERIFY_X509_PARTIAL_CHAIN
from dronekit import VehicleMode, connect, LocationGlobalRelative
import sys
sys.path.append(".")
import utils
from pymavlink import mavutil
import matplotlib.pyplot as plt
import threading
import numpy as np
import os
import time
from time import sleep


import logging
import socket
import argparse
import math

# responsible for running code that moves the vehicle
class DroneVehicle:

	def __init__(self, drone_map = None, connected = True, debug = False):
		#THIS SHOULD BE THE EXACT SAME OBJECT THAT DRONE SERVER IS TALKING TO
		self.debug = debug
		self.connected = connected
		self.drone_map = drone_map
		self.isRunning = utils.LockedObject()
		self.isRunning = False
		self.telemetry = utils.LockedObject()
		self.telemetry = utils.Telemetry()
  
		self.vx = None
		self.vy = None 

		self.telemetry_thread = threading.Thread(target=self.read)
		self.vehicle_thread = threading.Thread(target=self.start)

		if self.connected:
			self.vehicle = connect('udp:127.0.0.1:14550', wait_ready=True)

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
				self.vehicle.mode.name,
				self.vx,
				self.vy
			)
			sleep(2)


	def run(self):
		msg = self.vehicle.message_factory.command_long_encode(
			0, 0,    # target system, target component
			mavutil.mavlink.MAV_CMD_DO_SET_HOME, #command
			0,    #confirmation
			0,    # param 1, (1=use current location, 0=use specified location)
			0,    # param 2, unused
			0,    # param 3,unused
			0,    # param 4, unused
			40.4435249, -79.9547351, 0)    # param 5 ~ 7 latitude, longitude, altitude

		self.vehicle.send_mavlink(msg)
		self.vehicle.flush()

		self.vehicle_thread = threading.Thread(target=self.start, args=(.75,))
		self.vehicle_thread.start()


	def start(self, targetAlt):

		self.running = True
		#find drone heading, adjust to face east and convert negative angles to positive
		self.delta_theta = self.vehicle.heading - 90
		if self.delta_theta < 0:
			self.delta_theta = 360 + self.delta_theta
		
		self.telemetry_thread.start()

		if self.debug:
			self.obstacle_detection()
		else:
      
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
			self.vehicle.simple_takeoff(.75) # Take off to target altitude

			# Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
			#  after Vehicle.simple_takeoff will execute immediately).
			while True:
				print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
				#Break and return from function just below target altitude.
				if self.vehicle.location.global_relative_frame.alt>=targetAlt*0.95:
					print("Reached target altitude")
					break
				time.sleep(3)
			self.obstacle_detection()
    
	def obstacle_detection(self):
		print("starting obstacle detection")
		while self.running:
			#self.vehicle.mode = VehicleMode("LAND")
			# obstacle detection goes here
			env_map = self.drone_map.map
			if env_map.mapbytes:
				self.parseMapData(env_map.x, env_map.y, env_map.theta, env_map.get_occupancy_grid())
    
	def testMov(self):
		#north
		self.setV(.35,0,0)
		time.sleep(2)
		self.stopMov()
		time.sleep(2)
		#south
		self.setV(-.35,0,0)
		time.sleep(2)
		self.stopMov()
		time.sleep(2)
		#east
		self.setV(0,.35,0)
		time.sleep(2)
		self.stopMov()
		time.sleep(2)
		#west
		self.setV(0,-.35,0)
		time.sleep(2)
		self.stopMov()
		time.sleep(2)

	def stop(self):
		self.running = False
		sleep(.01)
		self.vehicle.mode = VehicleMode("LAND")

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
	

	def compassAdj(self,hyp,dx,dy):
		orig = math.degrees(math.tan(-dy/-dx))

		new_angle = orig - self.delta_theta

		if new_angle < 0:
			new_angle = 360 + new_angle

		new_dx = hyp*math.acos(new_angle)
		new_dy = hyp*math.asin(new_angle)

		if new_angle > 90 and new_angle <= 180:
			new_dx = -new_dx
		elif new_angle > 180 and new_angle <= 270:
			new_dx = -new_dx
			new_dy = -new_dy
		elif new_angle > 270 and new_angle < 360:
			new_dy = -new_dy

		return new_dx,new_dy

		
	def foundObj(self,dx,dy,theta,x_orig,y_orig):
    
		print("dy: "+ str(dy)+" dx: "+str(dx)+" x_orig: "+str(x_orig)+" y_orig: "+str(y_orig))


		if(dx > 0 and dy > 0):
			quad = 1
		elif(dx < 0 and dy > 0):
			quad = 2
		elif(dx < 0 and dy < 0):
			quad = 3
		else:
			quad = 4

		print(quad)
		#negative
		if theta < 0:
			theta = theta*-1
			#mod and convert to positive
			theta = theta % 360
			theta = 360 - theta
		#positive
		else :
			#mod
			theta = theta % 360
		
		#find angles between points
		#angle = math.degrees(math.atan(dy/dx))
		hyp = math.sqrt((dx*dx)+(dy*dy))
		if hyp == 0:
			self.stopMov()
			print("\n no velocity is being sent")
			self.stopMov()
			return

		red = .45

		#function to adjust for drone heading
		#dx, dy = self.compassAdj(hyp,dx,dy)

		#may need to uninvert dx and dy below when adding in the compass adjustment
		print("vx before red : {}".format(-dx/hyp))
		vx = (-dx/hyp)*red
		vy = (-dy/hyp)*red
  
		self.vx = vx
		self.vy = vy

		#set velocity
		if not self.debug:
			self.setV(vy,vx,0)
			pass

		print("\nvelociy is:" + str(round(vy,2))+ ", " + str(round(vx, 2)))
		if(vx < 0):
			print('west')
		elif(vx > 0):
			print('east')

		if(vy < 0):
			print('south')
		elif(vy > 0):
			print('north')
			
	def returnToBase(self):
		self.vehicle.mode = VehicleMode("RTL")
	
	def stopMov(self):
		self.setV(0,0,0)
		
	def land(self):
		self.vehicle.mode = VehicleMode("LAND")
	
	def parseMapData(self,x_mm,y_mm,theta,data):
		print("x_old :" + str(x_mm) + "\ny_old: " + str(y_mm))

		x,y,x_min,x_max,y_min,y_max = utils.find_radius(x_mm, y_mm)

		print("x :" + str(x) + "\ny: " + str(y))
		if self.debug:
			# plt.imshow(map_data, cmap='gray', vmin=0, vmax=1)
			# plt.plot(x,y,'ro') 
			# plt.show()
			pass

		print("x_max:{} x_min: {}y_max: {} y_min: {}".format(x_max,x_min, y_max,y_min))
		if self.debug:
			# plt.imshow(map_data[y_min:y_max, x_min:x_max], cmap='gray', vmin=0, vmax=1)
			# plt.show()
			pass

		#iterators
		i = int(x_min)
		j = int(y_min)
		
		sum_dx = 0.0
		sum_dy = 0.0

		#check range of pixels
		while(j < y_max):
			i = int(x_min)
			while (i < x_max):
				if data[j, i] == 1:
					# i represents y here (rows), j represents x (cols)
					dx = i - x
					dy = j - y
					hyp = math.sqrt((dx*dx)+(dy*dy))
					if hyp > 0:
						#print("x: {} y {} dx: {} dy: {}".format(i, j, dx, dy))
						sum_dx += dx/hyp
						sum_dy += dy/hyp	
				i += 1
			j += 1
		
		print("\nsum_dx:{} sum_dy:{}".format(sum_dx, sum_dy))

		self.foundObj(sum_dx, sum_dy, theta, x, y)
				


if __name__ == "__main__":
    
	files = ['1', '2', '3','4', '90', '180', '270', 'North']
	file_base = '../test/data/map_data'
	map_data = None
	x = None
	y = None
	theta = None
	drone_vehicle = DroneVehicle(connected=False, debug=True)
	print(os.getcwd())

	for file_tag in files:
    	
		position_file = '{}/position_{}.txt'.format(file_base, file_tag)
		map_file = '{}/map_data_{}.txt'.format(file_base, file_tag) 

		with open(position_file, "r") as f:	
			position = f.readline().split(" ")	
			print(position)
			x = float(position[0])
			y = float(position[1])
			theta = float(position[2])

		map_data = np.loadtxt(map_file, dtype=np.uint8, delimiter=' ')
		drone_vehicle.parseMapData(x, y, theta, map_data)




 
