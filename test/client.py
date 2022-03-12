import sys
sys.path.append(r"../pydrone")
sys.path.append(r"../pydrone/clients")
from DroneClients import DroneClients
from roboviz import MapVisualizer
from time import sleep

MAP_SIZE_PIXELS         = 500
MAP_SIZE_METERS         = 10


def main():
    # map object, telemetry object, SERVER, PORT
    #drone_clients = DroneClients(map, telemetry,"192.168.1.107", 5050 )
    drone_clients = DroneClients("10.0.0.118", 5050)
    #drone_clients = DroneClients(map, telemetry,"10.0.2.15", 5050 )
    # Set up a SLAM display
    viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')
    drone_clients.run()
    drone_clients.send_command("START")
    while True:
        try:
            position_map = drone_clients.get_map_data()
            x = position_map.x
            y = position_map.y
            theta = position_map.thetagit pu
            mapbytes = position_map.mapbytes
            #print("clients are not blocking main thread")
            # Display map and robot pose, exiting gracefully if user closes it
            if mapbytes:
                if not viz.display(x/1000., y/1000., theta, mapbytes):
                    exit(0)
            sleep(1)
        except KeyboardInterrupt:
            print('interrupt')
            drone_clients.stop()
            break

    print('done')
    

if __name__ == "__main__":
    main()
