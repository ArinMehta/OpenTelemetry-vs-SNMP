# snmp/Dockerfile (corrected paths for build context ./snmp)
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies needed for SNMP and building Python extensions
RUN apt-get update && apt-get install -y \
    snmp \
    snmpd \
    libsnmp-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the snmp-specific requirements and install them
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Safety: ensure these packages are present even if requirements file was missed
RUN pip install --no-cache-dir pysnmp pyasn1 pyasn1-modules

# Copy the collector code (relative to ./snmp build context)
COPY collect_snmp.py ./collect_snmp.py

CMD ["python", "collect_snmp.py"]