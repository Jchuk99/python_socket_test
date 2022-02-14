import sys
sys.path.append(".")
from python_socket_test.DroneServer import DroneServer
from time import sleep


from rplidar import RPLidar

def main():
    map = 0  #get mutable/thread-safe map object
    telemetry = 0 #get mutable/thread-safe telemetry object
    message_queue = list()
    # drone server will pass command through message queue, and 
    # will give map/telemetry data through map and telemetry data structures
    drone_server = DroneServer(map, telemetry, message_queue)
    drone_server.run()
    while True:
        try:
            # print("drone server is not blocking")
            sleep(1)
        except KeyboardInterrupt:
            print('interrupt')
            drone_server.stop()
            break


if __name__ == "__main__":
    main()