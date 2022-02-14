from dronekit import VehicleMode, connect, LocationGlobalRelative
from pymavlink import mavutil
import time
import socket
import argparse

vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True)
#vehicle = connect('tcp:192.168.1.1:5760', wait_ready=True)

def armAndTakeoff(targetAlt):
	
	print("Basic pre-arm checks")
	# Don't try to arm until autopilot is ready
	while not vehicle.is_armable:
		print(" Waiting for vehicle to initialise...")
		time.sleep(1)

	print("Arming motors")
	# Copter should arm in GUIDED mode
	vehicle.mode    = VehicleMode("GUIDED")
	vehicle.armed   = True

	# Confirm vehicle armed before attempting to take off
	while not vehicle.armed:
		print(" Waiting for arming...")
		time.sleep(1)

	print("Taking off!")
	vehicle.simple_takeoff(targetAlt) # Take off to target altitude

	# Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
	#  after Vehicle.simple_takeoff will execute immediately).
	while True:
		print(" Altitude: ", vehicle.location.global_relative_frame.alt)
		#Break and return from function just below target altitude.
		if vehicle.location.global_relative_frame.alt>=targetAlt*0.95:
			print("Reached target altitude")
			break
		time.sleep(1)

def setV(Vx, Vy, Vz):
	msg = vehicle.message_factory.set_position_target_local_ned_encode(
			0,
			0,0,
			mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED,
			0b0000111111000111,
			0,0,0,
			Vx, Vy, Vz,
			0,0,0,
			0,0)
	vehicle.send_mavlink(msg)
	vehicle.flush()

armAndTakeoff(2)
print(" Altitude: ", vehicle.location.global_relative_frame.alt)
print("Velocity: %s" % vehicle.velocity)

c = 0
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
