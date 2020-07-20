FROM nvidia/cuda:11.0-base-ubuntu20.04

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    libatlas-base-dev \
    gfortran \
    curl \
    sudo \
    git \
    bzip2 \
    libx11-6 \
    tmux \
    htop \
    vim \
    wget \
    locales \
    libgl1-mesa-glx \
    libssl-dev \ 
    libpcre3 \
    libpcre3-dev \ 
    python3 \
    python3-pip \ 
    python3-dev \ 
    build-essential \ 
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip
RUN pip3 install flask
RUN pip3 install flask_cors

RUN locale-gen en_US.UTF-8
RUN update-locale en_US.UTF-8
#Set ascii environment
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
COPY . /ganilla
WORKDIR /ganilla
RUN ["python3", "-m", "pip", "install", "-r", "requirements.txt"]
