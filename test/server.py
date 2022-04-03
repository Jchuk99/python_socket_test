import sys
sys.path.append(r"../pydrone")
sys.path.append(r"../pydrone/clients")
import utils
from DroneVehicle import DroneVehicle
from DroneServer import DroneServer
from DroneMap import DroneMap
from queue import Queue
from time import sleep


def main():

    drone_map = DroneMap()  # thread-safe map object
    message_queue = Queue()  # thread-safe message queue class 

    # drone server will pass command through message queue, and 
    # will give map/telemetry data through map and telemetry data structures
 
    drone_vehicle = DroneVehicle(drone_map)
    drone_server = DroneServer(drone_map, drone_vehicle, message_queue,"192.168.1.111", 5050)
    #drone_server = DroneServer(drone_map, drone_vehicle, message_queue, "10.0.0.39", 5050)
    
    drone_map.run()
    drone_server.run()
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            if message == 'START':
                # AKA we start a new thread to get the drone to hover, and run obstacle avoidance
                # give this thread: 
                # drone_map to run obstacle avoidance using provided info,
                print('drone is starting')
                drone_vehicle.run()
            elif message == 'STOP':
                print('drone is stopping')
            elif message == 'ARM':
                print('drone is arming')
            elif message == 'DISARM':
                print('drone is disarming')
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
