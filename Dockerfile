# Build stage for qemu-system-arm
FROM debian:stable-slim AS qemu-builder
RUN su
RUN apt-get update
WORKDIR /home
RUN apt-get install -y make build-essential git
RUN apt-get install -y libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm  \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv
ENV HOME="/root"
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"
RUN eval "$(pyenv init --path)"
RUN eval "$(pyenv init -)"
RUN git clone https://github.com/pyenv/pyenv-virtualenv.git $PYENV_ROOT/plugins/pyenv-virtualenv
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
RUN pyenv install 3.8.10
RUN pyenv global 3.8.10
RUN git clone https://github.com/Jchuk99/python_socket_test.git
RUN git clone https://github.com/ArduPilot/ardupilot
pip install virtualenv
WORKDIR /home/python_socket_test
RUN python -m virtualenv venv
RUN . ./venv/bin/activate
WORKDIR /home/ardupilot
RUN git submodule update --init --recursive
RUN ./waf configure --board sitl
RUN ./waf copter
RUN export LD_LIBRARY_PATH="/home/pi/python_socket_test/pydrone/libs/Linux/ARM64"
