from dronekit import connect, VehicleMode, mavutil
import time
from pymavlink import mavutil

vehicle = connect("127.0.0.1:14550", wait_ready=True)

print("connected")

msg = vehicle.message_factory.command_long_encode(
			0, 0,    # target system, target component
			mavutil.mavlink.SET_GPS_GLOBAL_ORIGIN, #command
			0,    #confirmation
			0,    # param 1, (1=use current location, 0=use specified location)
			0,    # param 2, unused
			0,    # param 3,unused
			0,    # param 4, unused
			40.4435249, -79.9547351, 0)    # param 5 ~ 7 latitude, longitude, altitude

vehicle.send_mavlink(msg)
vehicle.flush()

print("msg sent")
 