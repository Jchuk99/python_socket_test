# Build stage for qemu-system-arm
FROM debian:stable-slim AS qemu-builder
RUN apt-get update
RUN apt-get install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm git \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
WORKDIR /home
RUN su
RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv
RUN export PYENV_ROOT="$HOME/.pyenv"
RUN export PATH="$PYENV_ROOT/bin:$PATH"    # if `pyenv` is not already on PATH
RUN eval "$(pyenv init --path)"
RUN eval "$(pyenv init -)"
RUN git clone https://github.com/pyenv/pyenv-virtualenv.git $PYENV_ROOT/plugins/pyenv-virtualenv
RUN $ echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
export PATH="$PYENV_ROOT/shims:$PATH"
RUN git clone https://github.com/Jchuk99/python_socket_test.git
RUN pyenv install 3.8.10
