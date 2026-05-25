FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Install packages
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt install -y python3.14 python3-pip python3-venv git python-is-python3 iputils-ping net-tools telnet tcpdump redis-tools netcat-openbsd openjdk-17-jdk xxd graphviz gnuplot gh && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.14 1

RUN pip install --break-system-packages --upgrade argcomplete mypy pytest pytest-cov pytest-asyncio black wemake-python-styleguide cohesion dlint pytest-xdist vulture isort jupyter uv

# Install maelstrom
RUN mkdir -p /opt/maelstrom && \
    curl -fL -o /tmp/maelstrom.tar.bz2 https://github.com/jepsen-io/maelstrom/releases/download/v0.2.4/maelstrom.tar.bz2 && \
    tar -xjf /tmp/maelstrom.tar.bz2 -C /opt/maelstrom --strip-components=1 && \
    rm /tmp/maelstrom.tar.bz2
ENV PATH="/opt/maelstrom:${PATH}"

# Node.js 22 + Pi Coding Agent
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g @mariozechner/pi-coding-agent && \
    npm cache clean --force && \
    rm -rf /var/lib/apt/lists/*
RUN pi update && \
    pi install npm:pi-subagents && \
    pi install npm:pi-mcp-adapter

ARG MY_OPENROUTER_API_KEY
ENV MY_OPENROUTER_API_KEY=${MY_OPENROUTER_API_KEY}

EXPOSE 8080
