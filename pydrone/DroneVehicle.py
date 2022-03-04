from dronekit import VehicleMode, connect, LocationGlobalRelative
import sys
sys.path.append(".")
import utils
from pymavlink import mavutil
import threading
import time
from time import sleep

import socket
import argparse


# responsible for running code that moves the vehicle
class DroneVehicle:

	def __init__(self, server, port):
		self.addr = f'tcp:{server}:{port}'
		#'tcp:127.0.0.1:5760'
		#connect to flight controller
		#THIS SHOULD BE THE EXACT SAME OBJECT THAT DRONE SERVER IS TALKING TO
		self.isRunning = utils.LockedObject()
		self.isRunning = False
		self.telemetry = utils.LockedObject()
		self.telemetry = utils.Telemetry()
		print(self.addr)
		self.vehicle = connect('udp:127.0.0.1:14551', wait_ready=True)
		#self.vehicle = connect(self.addr, wait_ready=True)
		#vehicle = connect('tcp:192.168.1.1:5760', wait_ready=True)

	def read(self):
		while True:
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
			if not self.running:
				break


	def start(self, targetAlt):
		
		
		self.running = True

		thread = threading.Thread(target=self.read)
		thread.start()

		print("Basic pre-arm checks")
		# Don't try to arm until autopilot is ready
		while not self.vehicle.is_armable:
			print(" Waiting for vehicle to initialise...")
			time.sleep(1)

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

