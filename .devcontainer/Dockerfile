FROM mcr.microsoft.com/devcontainers/base:ubuntu26.04

ENV DEBIAN_FRONTEND=noninteractive
# Install packages. Ubuntu 26.04 (Resolute) ships Python 3.14 as the default
# `python3` (python3.14 3.14.4 in main), so no deadsnakes PPA is needed.
# Node.js 24 comes from the NodeSource apt repo configured manually — no setup
# script piped to a shell; apt verifies every package against the NodeSource
# signing key via `Signed-By`.
# https://github.com/nodesource/distributions/wiki/Repository-Manual-Installation
# ffmpeg is here for agent-browser (`record` needs it on PATH).
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg python3 python3-pip python3-venv git gh openjdk-17-jdk gnuplot fd-find ripgrep && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    chmod 644 /etc/apt/keyrings/nodesource.gpg && \
    printf 'Types: deb\nURIs: https://deb.nodesource.com/node_24.x/\nSuites: nodistro\nComponents: main\nSigned-By: /etc/apt/keyrings/nodesource.gpg\n' > /etc/apt/sources.list.d/nodesource.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends nodejs ffmpeg && \
    npm install -g agent-browser && \
    npm cache clean --force && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# `python` alias = plain symlink to python3 — no python-is-python3 package, so
# no alternatives re-registration can ever flip the default away from 3.14.
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Fresh pip: distro pip is deb-managed (no RECORD file) and refuses normal
# `--upgrade` uninstall. `--ignore-installed` skips the uninstall step; the new
# pip lands first on sys.path (/usr/local/lib/python3.14/dist-packages) and wins.
RUN python3 -m pip install --ignore-installed --break-system-packages pip

# Python tooling: repo shared tooling comes from PEP 735 [dependency-groups]
# in pyproject.toml (single source of truth — matches CI's `--group dev`;
# import-linter + vulture land here automatically).
COPY pyproject.toml /tmp/pyproject.toml
RUN cd /tmp && \
    python3 -m pip install --break-system-packages --group dev && \
    rm /tmp/pyproject.toml

# Install maelstrom. Pin both version and tarball digest: `curl -fL` alone
# trusts whatever the release URL serves today.
ARG MAELSTROM_VERSION=v0.2.4
ARG MAELSTROM_SHA256=301ec71d6b12af0d765edb413f5cf5aa1046b5609bd4e31376a0b549548e5799
RUN mkdir -p /opt/maelstrom && \
    curl -fL -o /tmp/maelstrom.tar.bz2 "https://github.com/jepsen-io/maelstrom/releases/download/${MAELSTROM_VERSION}/maelstrom.tar.bz2" && \
    echo "${MAELSTROM_SHA256}  /tmp/maelstrom.tar.bz2" | sha256sum -c - && \
    tar -xjf /tmp/maelstrom.tar.bz2 -C /opt/maelstrom --strip-components=1 && \
    rm /tmp/maelstrom.tar.bz2
ENV PATH="/opt/maelstrom:${PATH}"
EXPOSE 8080

# Pi Coding Agent + agent-browser runtime — user scope, installed AS `vscode`.
ARG PI_VERSION=v0.87.1

USER vscode
RUN npm install -g --ignore-scripts --prefix "$HOME/.local" @earendil-works/pi-coding-agent@${PI_VERSION} && \
    agent-browser install --with-deps && \
    npm cache clean --force && \
    sudo rm -rf /var/lib/apt/lists/*
