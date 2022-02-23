# DOCKER DIRECTIONS
1. Install Docker Desktop
    if most up to date version doesn't recognize WSL 2 on desktop, install v3.5.2

2. RUN these commands from python_socket_test(drone main later) directory: 
    docker buildx create --name mybuilder
    docker buildx use mybuilder
    docker buildx inspect --bootstrap
    docker buildx build --platform linux/arm64 -t debian_slim --load . 
    
    clone ardupilot
    build ardupilot
    
    python sim_vehicle.py -v ArduCopter
    param load /home/ardupilot/Tools/autotest/default_params/copter-heli.parm
    #x86
    dronekit-sitl copter
    dronekit-sitl /home/ardupilot/build/sitl/bin/arducopter
    mavproxy.py --master tcp:127.0.0.1:5760 --out udp:127.0.0.1:14551