# Build stage for qemu-system-arm
FROM debian:stable-slim AS qemu-builder

RUN apt-get update
RUN apt-get -y install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libreadline-dev libffi-dev curl libbz2-dev
RUN apt-get -y install curl wget tk-dev liblzma-dev git xz-utils libnss3-dev libssl-dev libsqlite3-dev
RUN curl -O https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tar.xz
RUN tar xf Python-3.8.10.tar.xz
WORKDIR "Python-3.8.10"
RUN ./configure --enable-optimizations
RUN make -j 8
RUN make altinstall
RUN alias python=python3.8
RUN alias pip=pip3.8
WORKDIR ~
RUN git clone https://github.com/Jchuk99/python_socket_test.git

#venv setup
#pip install --user wheel
#pip install dronekit
#pip install dronekit-sitl
#pip uninstall pymavlink
#pip install pymavlink==2.4.8
#pip install rplidar
#pip install numpy
