# DOCKER DIRECTIONS
1. Install Docker Desktop
    if most up to date version doesn't recognize WSL 2 on desktop, install v3.5.2

2. RUN these commands from python_socket_test(drone main later) directory: 
    docker buildx create --name mybuilder
    docker buildx use mybuilder
    docker buildx inspect --bootstrap
    docker buildx build --platform linux/arm64 -t debian_slim --load . 
    