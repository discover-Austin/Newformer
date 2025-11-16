# Chrysalis-Transformer X (CT-X) Production Dockerfile
FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

# Metadata
LABEL maintainer="Claude & Austin"
LABEL description="CT-X: The Last Transformer You'll Ever Need"
LABEL version="2.0.0"

# Non-root user (security best practices)
RUN groupadd -r ctx && useradd -r -g ctx -u 1001 ctxuser

# System dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=ctxuser:ctx . /app

# Create directories for models and logs
RUN mkdir -p /models /logs && chown -R ctxuser:ctx /models /logs

# Model download script (placeholder - would download from model hub in production)
COPY scripts/download_model.py /app/scripts/
RUN chmod +x /app/scripts/download_model.py

# Security: Run as non-root
USER ctxuser

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/models/ct-x-70b
ENV DEVICE=auto
ENV PORT=8000

# Start API server
CMD ["python3", "api_server.py"]
