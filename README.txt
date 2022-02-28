# BUILDING TEST ENVIRONMENT FOR WINDOWS
1. https://ardupilot.org/dev/docs/building-setup-windows-cygwin.html#building-setup-windows-cygwin
   Install Cygwin, follow this link for right setting and libraries to add.
2. Install pyenv for windows: https://github.com/pyenv-win/pyenv-win
3. setup python3.8.10:
	pyenv install 3.8.10
    pyenv global 3.8.10
	python --version
		- If python version hasn't changed, 
		  you have to add %USERPROFILE%\.pyenv\pyenv-win\shims 
		  ahead of your python version in your PATH system variable.
3. pip install virtualenv
4. cd to home directory ( of this repository)
5  create virtualenv: python -m virtualenv venv
6. activate virtualenv: .\venv\Scripts\activate.bat	  
7. pip install -r requirements.txt
8. git submodule update --init --recursive
9. Download Windows Subsystem for Linux, can be done by downloading Ubunutu from microsoft store.
10. Open up the cygwin terminal and run: 'cd c:/' to get to base c drive. Navigate to ardupilot
11. https://github.com/ArduPilot/ardupilot/blob/master/BUILD.md details how to build ardupilot on cygwin terminal
	./waf configure
	./waf copter
	will also need to install pexpect, empy, and future, you can do this at the cygwin installation.



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