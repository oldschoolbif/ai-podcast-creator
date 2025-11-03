# AI Podcast Creator - Docker Image
# Optimized for GPU utilization with CUDA 12.1
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install system dependencies including build tools for PyAV (audiocraft)
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-dev \
    ffmpeg \
    git \
    wget \
    pkg-config \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    && rm -rf /var/lib/apt/lists/*

# Set CUDA environment variables for optimal GPU utilization
ENV CUDA_VISIBLE_DEVICES=0
ENV NVIDIA_VISIBLE_DEVICES=0
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/scripts data/outputs data/cache data/models logs

# Initialize database
RUN python3 -m src.cli.main init || true

# Set entrypoint
ENTRYPOINT ["python3", "-m", "src.cli.main"]

# Default command
CMD ["--help"]

