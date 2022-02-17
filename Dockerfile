# Build stage for qemu-system-arm
FROM debian:stable-slim AS qemu-builder
su -s
apt-get update
apt-get -y install sudo
apt-get -y install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libreadline-dev libffi-dev curl libbz2-dev
apt-get -y install curl wget tk-dev liblzma-dev git xz-utils libnss3-dev libssl-dev libsqlite3-dev pip
curl -O https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tar.xz
tar xf Python-3.8.10.tar.xz
cd Python-3.8.10
./configure --enable-optimizations
make -j 4
make altinstall
alias python=python3.8
alias pip=pip3.8
cd ~
git clone https://github.com/Jchuk99/python_socket_test.git

#venv setup
#pip install --user wheel
#pip install dronekit
#pip install dronekit-sitl
#pip uninstall pymavlink
#pip install pymavlink==2.4.8
#pip install rplidar
#pip install numpy
