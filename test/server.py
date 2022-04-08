import sys
sys.path.append(r"../pydrone")
sys.path.append(r"../pydrone/clients")
import argparse
import utils
from DroneVehicle import DroneVehicle
from DroneServer import DroneServer
from DroneMap import DroneMap
from queue import Queue
from time import sleep


def main(args):

    print(args)
    drone_map = DroneMap(run=args.no_lidar)  # thread-safe map object
    message_queue = Queue()  # thread-safe message queue class 

    # drone server will pass command through message queue, and 
    # will give map/telemetry data through map and telemetry data structures
    
    if args.no_gui:
        message_queue.put('START')
 
    drone_vehicle = DroneVehicle(drone_map, connected = args.no_connect_drone)
    drone_server = DroneServer(drone_map, drone_vehicle, message_queue,"172.20.10.5", 5050)
    #drone_server = DroneServer(drone_map, drone_vehicle, message_queue, "10.0.0.39", 5050)

    drone_map.run()
    drone_server.run()


    
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            if message == 'START':
                # AKA we start a new thread to get the drone to hov`er, and run obstacle avoidance
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
                drone_vehicle.stop()
                drone_server.stop()
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument( '--no_lidar', default = True, action='store_false')
    parser.add_argument( '--no_connect_drone', default = True, action='store_false')
    parser.add_argument( '--no_gui', default = False, action='store_true')
    args = parser.parse_args()
    main(args)
