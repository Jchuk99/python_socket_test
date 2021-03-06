from dronekit import VehicleMode, connect, LocationGlobalRelative
from pymavlink import mavutil
import threading
import time
import socket
import argparse
import math


# responsible for running code that moves the vehicle
class DroneVehicle:

	def __init__(self):#, telemetry_data, server, port):
		#self.addr = f'tcp:{server}:{port}'
		self.addr = f'tcp:127.0.0.1:5760'
		
		#'tcp:127.0.0.1:5760'
		#connect to flight controller
		#THIS SHOULD BE THE EXACT SAME OBJECT THAT DRONE SERVER IS TALKING TO
		#self.isRunning = utils.LockedObject()
		self.isRunning = False
		#self.telemetry = telemetry_data
		self.vehicle = connect(self.addr, wait_ready=True)
		#vehicle = connect('tcp:192.168.1.1:5760', wait_ready=True)

	def read(self):
		while True:
			telemetry = utils.Telemetry(
				vehicle.location.global_relative_frame.alt,
				vehicle.attitude.pitch,
				vehicle.attiude.yaw,
				vehicle.attiude.roll,
				vehicle.velocity,
				vehicle.airspeed,
				vehicle.groundspeed,
				vehicle.mode.name
			)

			sleep(1)
			if not self.running:
				break


	def start(targetAlt):
		
		
		self.running = True

		thread = threading.Thread(target=self.read)
		thread.start()

		print("Basic pre-arm checks")
		# Don't try to arm until autopilot is ready
		while not vehicle.is_armable:
			print(" Waiting for vehicle to initialise...")
			time.sleep(1)

		print("Arming motors")
		# Copter should arm in GUIDED mode
		self.vehicle.mode    = VehicleMode("GUIDED")
		self.vehicle.armed   = True

		# Confirm vehicle armed before attempting to take off
		while not vehicle.armed:
			print(" Waiting for arming...")
			time.sleep(1)

		print("Taking off!")
		self.vehicle.simple_takeoff(targetAlt) # Take off to target altitude

		# Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
		#  after Vehicle.simple_takeoff will execute immediately).
		while True:
			print(" Altitude: ", self.vehicle.location.global_relative_frame.alt)
			#Break and return from function just below target altitude.
			if self.vehicle.location.global_relative_frame.alt>=targetAlt*0.95:
				print("Reached target altitude")
				break
			time.sleep(1)

	def setV(Vx, Vy, Vz):
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
	
	def foundObjT(self,y,y,theta):
		#fix theta
		if theta > 360:
			while theta > 360:
				theta = theta-360
		elif theta < 0:
			theta = theta*-1
			
		newX = (-math.cos(math.radians(theta)))*2
		newY = (0math.sin(math.radians(theta)))*2
		
		self.setV(newY, newX, 0)
	
	def foundObj(self, x,y,theta):
		#checks edge cases
		if x==0:
			if y>0:
				self.setV(-1,0,0)
			elif y<0:
				self.setV(1,0,0)
		elif y==0:
			if x>0:
				self.setV(0,-1,0)
			elif x<0:
				self.setV(0,1,0)
		#take constant ratio and reduce
		elif y!=0 and x!=0:			
			if abs(x) > abs(y):
				k = y/x
			else:
				k = x/y
			
			if k < 0:
				k = k*(-1)
			
			if abs(x) > abs(y):
				newX = 1						
				newY = newX*k
			else:
				newY = 1
				newX = newY*k
			
			if x > 0:
				newX = newX*(-1)
			
			if y > 0:
				newY = newY*(-1)
			
			self.setV(newY,newX,0)
			
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
		
		s = math.sqrt(data.size)
		
		x_min = x-25
		x_max = x+25
		y_min = y-25
		y_max = y+25
		
		if x_min < 0:
			x_min = 0
			
		if y_min < 0:
			y_min = 0
		
		if x_max > s:
			x_max = s
		
		if y_max > s:
			y_max = s
		
		i = x_min
		y = y_min
		
		while(j < y_max):
			while (i < x_max):
				if data[i,j] > 127:
					foundObj(i,j,theta)
					time.sleep(5)
					#revisit this to solve for drone returning to base only after objec is gone
					break
					
			
		

start(2)
print(" Altitude: ", vehicle.location.global_relative_frame.alt)
print("Velocity: %s" % vehicle.velocity)

'''c = 0
while c<2:
	setV(1,0,0)
	print("Direction: NORTH relative to heading of drone")
	print("Velocity: %s" % vehicle.velocity)
	time.sleep(1)
	c=c+1


c = 0
while c<2:
	setV(-1,0,0)
	print("Direction: SOUTH relative to heading of drone")
	print("Velocity: %s" % vehicle.velocity)
	time.sleep(1)
	c=c+1


c = 0
while c<2:
	setV(0,1,0)
	print("Direction: EAST relative to heading of drone")
	print("Velocity: %s" % vehicle.velocity)
	time.sleep(1)
	c=c+1


c = 0
while c<2:
	setV(0,-1,0)
	print("Direction: WEST relative to heading of drone")
	print("Velocity: %s" % vehicle.velocity)
	time.sleep(1)
	c=c+1

print("Velocity: %s" % vehicle.velocity)
'''
