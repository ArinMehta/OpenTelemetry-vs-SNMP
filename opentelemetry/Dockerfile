FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including gcc for psutil
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    iputils-ping \
    net-tools \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY network_monitor.py .
COPY instrumentation.py .

# Expose Prometheus metrics port
EXPOSE 8080

# Run the network monitor
CMD ["python", "network_monitor.py"]
