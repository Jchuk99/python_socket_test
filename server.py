import sys
sys.path.append(".")
from DroneServer import DroneServer
from DroneMap import DroneMap
from queue import Queue
from time import sleep


def main():
    drone_map = DroneMap()  # thread-safe map object
    telemetry = 0 #get mutable/thread-safe telemetry object
    message_queue = Queue()  # thread-safe message queue class 
    # drone server will pass command through message queue, and 
    # will give map/telemetry data through map and telemetry data structures

    drone_server = DroneServer(drone_map, telemetry, message_queue)
    drone_map.run()
    drone_server.run()
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            if message == 'START':
                # AKA we start a new thread to get the drone to hover, and run obstacle avoidance
                # give this thread the drone_map to run obstacle avoidance, also need a to give it
                # a shutdown signal that we can use to stop whenever the stop command starts
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