# syntax=docker/dockerfile:1.4
FROM ubuntu:22.04

# Install OS-level packages
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    # Ubuntu image is configured to delete cached files.
    # We're using a cache mount, so we remove that config.
    rm --force /etc/apt/apt.conf.d/docker-clean && \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache && \
    # Tell apt-get we're never going to be able to give manual feedback
    export DEBIAN_FRONTEND=noninteractive && \
    # Update the package listing, so we know what packages exist
    apt-get update && \
    # Install security updates
    apt-get --yes upgrade && \
    # Add deadsnakes ppa to install other versions of Python
    apt-get --yes install --no-install-recommends software-properties-common gpg-agent && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    # Install packages, without unnecessary recommended packages
    apt-get --yes install --no-install-recommends \
    python3.8 python3.8-distutils \
    python3.9 python3.9-distutils \
    python3.10 \
    python3.11 python3.11-venv \
    python3.12 \
    git tini curl && \
    # Install Github CLI
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
    dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
    tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get --yes install --no-install-recommends gh

# Create and activate virtual environment
ENV VIRTUAL_ENV="/root/.venv"
RUN python3.11 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Setup root home directory
WORKDIR /root/pysparkplug

# Install nox
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install nox==2023.04.22

# Trust repo directory
RUN git config --global --add safe.directory /root/pysparkplug

ENV XDG_CACHE_HOME="/root/pysparkplug/.cache"

ENTRYPOINT ["tini", "-v", "--"]
