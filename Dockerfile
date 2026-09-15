# ==============================================================================
# VisionGuard Enterprise Production Dockerfile
# ==============================================================================
FROM python:3.11-slim

# Install system multimedia and OpenCV runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose web dashboard port
EXPOSE 8000

# Run FastAPI web dashboard by default
CMD ["python", "-m", "visionguard.cli", "--web", "--host", "0.0.0.0", "--port", "8000"]
