FROM nvidia/cuda:10.1-base-ubuntu16.04

# Install some basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    sudo \
    git \
    bzip2 \
    libx11-6 \
    tmux \
    htop \
    nano \
    vim \
    wget \
    locales \
    libgl1-mesa-glx \
    python3 \
    python3-pip \ 
    python3-dev \ 
    build-essential \ 
 && rm -rf /var/lib/apt/lists/*
RUN pip3 install --upgrade pip
RUN locale-gen en_US.UTF-8
RUN update-locale en_US.UTF-8
#Set ascii environment
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
COPY . /ganilla
WORKDIR /ganilla
RUN ["python3", "-m", "pip", "install", "-r", "requirements.txt"]
