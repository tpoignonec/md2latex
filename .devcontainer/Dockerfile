FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    # LaTeX and document processing
    texlive-full \
    pandoc \
    inotify-tools \
    librsvg2-bin \
    # Python development
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    # Additional utilities
    git \
    make \
    curl \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies for md2latex
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Install development dependencies
RUN pip3 install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    pre-commit \
    sphinx \
    sphinx-rtd-theme

# Set up working directory
WORKDIR /workspace

# Copy the library source (this will be overridden by volume mount in development)
COPY src/ /workspace/src/
COPY pyproject.toml /workspace/
COPY README.md /workspace/

# Install md2latex in development mode
RUN pip3 install -e .

# Set up entrypoint
ENV PATH="/workspace/src:${PATH}"
ENV PYTHONPATH="/workspace/src:${PYTHONPATH}"
