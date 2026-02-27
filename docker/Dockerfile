# Use a lightweight base image with Python
FROM python:3.12-slim

# Install any OS-level dependencies needed for building common Python libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    gfortran \
    libblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
RUN pip install --no-cache-dir \
    numpy \
    scipy \
    sympy \
    pandas

# (Optional) Create a non-root user. Running as root is *not* recommended in production.
RUN useradd -m sandboxuser
USER sandboxuser

# The container will run whatever command we pass via `docker run ...`
CMD ["python"]