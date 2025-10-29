# AI Podcast Creator - Docker Image
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

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

