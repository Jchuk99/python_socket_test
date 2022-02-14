import sys
sys.path.append(".")
from DroneClients import DroneClients
from time import sleep


def main():
    map = 0  #get_map
    telemetry = 0 #get_telemetry

    # map object, telemetry object, SERVER, PORT
    #drone_clients = DroneClients(map, telemetry,"192.168.1.107", 5050 )
   # drone_clients = DroneClients(map, telemetry,"10.0.0.101", 5050
    drone_clients = DroneClients(map, telemetry,"10.0.0.39", 5050 ))

    drone_clients.run()
    drone_clients.send_command("START")
    while True:
        try:
            #print("clients are not blocking main thread")
            sleep(1)
        except KeyboardInterrupt:
            print('interrupt')
            drone_clients.stop()
            break

    print('done')
    

if __name__ == "__main__":
    main()