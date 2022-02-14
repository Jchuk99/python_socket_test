import sys
sys.path.append(".")
from DroneServer import DroneServer
from DroneMap import DroneMap
from queue import Queue
from time import sleep


def main():
    telemetry = utils.LockedObject()
    telemetry = Telemetry()

    drone_map = DroneMap()  # thread-safe map object
    # telemetry = DroneVehicle() #get mutable/thread-safe telemetry object
    telemetry = 0
    message_queue = Queue()  # thread-safe message queue class 
    # drone server will pass command through message queue, and 
    # will give map/telemetry data through map and telemetry data structures

    drone_server = DroneServer(drone_map, telemetry, message_queue, '192.168.1.107', 5050)
   # drone_server = DroneServer(drone_map, telemetry, message_queue, ,"10.0.0.101", 5050)

    drone_vehicle = DroneVehicle(telemetry, '127.0.0.1:5760', 5760)

    drone_map.run()
    drone_server.run()
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            if message == 'START':
                # AKA we start a new thread to get the drone to hover, and run obstacle avoidance
                # give this thread: 
                # drone_map to run obstacle avoidance using provided info,
                # drone_telemetry
                # a shutdown signal that we can use to stop whenever the stop command starts
                drone_vehicle.start(2)
                print(" Altitude: ", vehicle.location.global_relative_frame.alt)
                print("Velocity: %s" % vehicle.velocity)

                c = 0
                while c<2:
                    drone_vehicle.setV(1,0,0)
                    print("Direction: NORTH relative to heading of drone")
                    print("Velocity: %s" % vehicle.velocity)
                    time.sleep(1)
                    c=c+1

                
                print('drone is starting')
            elif message == 'STOP':
                print('drone is stopping')
        else:
            try:
                #print("drone server is not blocking")
                sleep(1)
            except KeyboardInterrupt:
                print('interrupt')
                drone_server.stop()
                break


if __name__ == "__main__":
    main()