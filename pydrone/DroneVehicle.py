
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
		
	def foundObj(self,s_x,s_y,theta,x_orig,y_orig,r):
  		#find quad
		dx = s_x - x_orig
		dy = y_orig - s_y

		print("dy: "+ str(dy)+" dx: "+str(dx)+"\ns_x: "+str(s_x)+" x_orig: "+str(x_orig)+"\ns_y: "+str(s_y)+" y_orig: "+str(y_orig))

		#TODO add edge cases
		#if(s_x == x_orig):
    			
		if(dx > 0 and dy > 0):
			quad = 1
		elif(dx < 0 and dy > 0):
			quad = 2
		elif(dx < 0 and dy < 0):
			quad = 3
		else:
			quad = 4

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
		
		#set bool for whether x and or y should be flipped based on quad and where the drone is facing
		#east
		if theta <= 45 or theta >= 315:
			print("east")
			if(quad == 2 or quad == 4):
				print("quad 2 or 4")
				fx = 1
				fy = 0
			else:
				print("quad 1 or 3")
				fx = 0
				fy = 1
		#north
		elif theta <= 135:
			fx = 0
			fy = 0
		#west
		elif theta <= 225:
			if(quad == 2 or quad == 4):
				fx = 0
				fy = 1
			else:
				fx = 1
				fy = 0
		#south
		else:
			fx = 0
			fy = 0
		
		
		#find angles between points
		angle = math.degrees(math.atan(dy/dx))
		
		#larger value set to 0.35
		if(dy > dx):
			vy = 0.35
			vx = vy/math.tan(angle+180)
		else:
			vx = 0.35
			vy = vx/math.tan(angle+180)
		
		if(fx):
			print("flip x")
			vx = vx*-1
		
		if(fy):
			print("flip y")
			vy = vy*-1

		##################################################################
		#take constant ratio and reduce
		#if y!=0 and x!=0:			
			#if abs(x) > abs(y):
				#k = y/x
			#else:
				#k = x/y
			
			#if k < 0:
				#k = k*(-1)
			
			#create new velocities
			#if abs(x) > abs(y):
				#newX = 0.35						
				#newY = newX*k
			#else:
				#newY = 0.35
				#newX = newY*k
			
			#set correct sign
			#if x > 0:
				#newX = newX*(-1)
			
			#if y > 0:
				#newY = newY*(-1)
			
		#############################################################
		#set velocity
		#self.setV(vy,vx,0)
		#time.sleep(1)
		#self.stopMov()
		print("\nvelociy is:" + str(vy)+ ", " + str(vx))
			
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

		x = int(x)
		y = int(y)

		print("x :" + str(x) + "\ny: " + str(y))
		#max range
		s = math.sqrt(data.size)
		#radius in meters
		rad = .75
		#m -> pixels
		ran = rad/.02
		
		#radius of drone detection
		x_min = x-ran
		x_max = x+ran
		y_min = y-ran
		y_max = y+ran
		
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
		
		#print(x_max)
		#print(x_min)
		#print(y_max)
		#rint(y_min)
		z = 0
		#check range of pixels
		while(j < y_max):
			i = int(x_min)
			while (i < x_max):
				#print(data[i, j])
				if data[i, j] == 1:
					print(data[i,j])
					print("\ny: " + str(i) + " x: " + str(j))
					self.foundObj(i, j,theta,x,y,ran)
					time.sleep(.1)
					#revisit this to solve for drone returning to base only after object is gone
					#current idea, just let loop run and see what happens
				i = i + 1

			j = j + 1
			z = z+1
		print(z)
				


if __name__ == "__main__":
	map_data = None
	x = None
	y = None
	theta = None
	drone_vehicle = DroneVehicle(connect=False)
	print(os.getcwd())
	with open("test/data/map_data/position_north.txt", "r") as f:	
		position = f.readline().split(" ")	
		print(position)
		x = float(position[0])
		y = float(position[1])
		theta = float(position[2])
	map_data = np.loadtxt("test/data/map_data/map_data_north.txt", dtype=np.uint8, delimiter=' ')
	plt.imshow(map_data, cmap='gray', vmin=0, vmax=1)
	plt.show()
	drone_vehicle.parseMapData(x, y, theta, map_data)





