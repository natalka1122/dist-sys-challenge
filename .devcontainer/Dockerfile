FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ENV DEBIAN_FRONTEND=noninteractive
# Install packages
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt install -y python3.14 python3-pip python3-venv git gh openjdk-17-jdk fd-find ripgrep && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Make Python 3.14 default (--set: deterministic, no auto-mode tie with 3.12).
# `python` alias = plain symlink to python3 — no python-is-python3 package, so
# no alternatives re-registration can ever flip the default back to 3.12.
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.14 1 && \
    update-alternatives --set python3 /usr/bin/python3.14 && \
    ln -sf /usr/bin/python3 /usr/bin/python

# Fresh pip: distro pip 24.0 is deb-managed (no RECORD file) and refuses normal
# `--upgrade` uninstall. `--ignore-installed` skips the uninstall step; the new
# pip lands first on sys.path (/usr/local/lib/python3.14/dist-packages) and wins.
RUN python3.14 -m pip install --ignore-installed --break-system-packages pip

# Python tooling: repo shared tooling comes from PEP 735 [dependency-groups]
# in pyproject.toml (single source of truth — matches CI's `--group dev`;
# import-linter + vulture land here automatically).
COPY pyproject.toml /tmp/pyproject.toml
RUN cd /tmp && \
    python3.14 -m pip install --break-system-packages --group dev && \
    rm /tmp/pyproject.toml

# Install maelstrom
RUN mkdir -p /opt/maelstrom && \
    curl -fL -o /tmp/maelstrom.tar.bz2 https://github.com/jepsen-io/maelstrom/releases/download/v0.2.4/maelstrom.tar.bz2 && \
    tar -xjf /tmp/maelstrom.tar.bz2 -C /opt/maelstrom --strip-components=1 && \
    rm /tmp/maelstrom.tar.bz2
ENV PATH="/opt/maelstrom:${PATH}"

# Node.js 24 + Pi Coding Agent
ARG PI_VERSION=v0.86.1
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g --ignore-scripts @earendil-works/pi-coding-agent@${PI_VERSION} && \
    npm install -g agent-browser && \
    HOME=/home/vscode agent-browser install --with-deps && \
    apt-get install -y --no-install-recommends ffmpeg && \
    npm cache clean --force && \
    rm -rf /var/lib/apt/lists/*

# Pi default model + packages come from the mounted workspace
# /home/vscode/.pi/agent/settings.json (gitignored; initialize_command.sh
# overwrites it from the versioned .devcontainer/pi-settings.json on every
# start — canonical wins). pi auto-installs missing `packages` at startup
# (unpinned = latest).
# The mkdir pre-creates bind-mount target dirs so Docker doesn't fabricate
# root-owned ones that would block vscode writes.
RUN mkdir -p /home/vscode/.pi/agent/sessions && \
    chown -R vscode:vscode /home/vscode/.pi /home/vscode/.agent-browser

EXPOSE 8080
