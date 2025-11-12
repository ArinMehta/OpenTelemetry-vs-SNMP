#!/bin/bash

# Network Monitoring Project Setup Script
# This script sets up the environment for the project

set -e

echo "=========================================="
echo "Network Monitoring Project Setup"
echo "OpenTelemetry vs SNMP"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_warning "This script is designed for Linux. Some features may not work on other systems."
fi

# Check for Docker
echo "Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
print_status "Docker found"

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
print_status "Docker Compose found"

# Check for Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi
print_status "Python 3 found"

# Optional: Check for Mininet
if command -v mn &> /dev/null; then
    print_status "Mininet found"
else
    print_warning "Mininet not found. Network topology simulation will not be available."
    echo "To install Mininet: sudo apt-get install mininet"
fi

echo ""
echo "Setting up project directories..."

# Create necessary directories
mkdir -p prometheus
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards
mkdir -p grafana/dashboards
mkdir -p opentelemetry
mkdir -p snmp
mkdir -p mininet
mkdir -p docs
mkdir -p logs

print_status "Directories created"

# Set permissions
echo ""
echo "Setting permissions..."
chmod +x scripts/*.sh 2>/dev/null || true
chmod +x mininet/*.py 2>/dev/null || true
chmod +x opentelemetry/*.py 2>/dev/null || true
chmod +x snmp/*.py 2>/dev/null || true

print_status "Permissions set"

# Pull Docker images
echo ""
echo "Pulling Docker images (this may take a few minutes)..."
docker-compose pull

print_status "Docker images pulled"

# Build custom images
echo ""
echo "Building custom Docker images..."
docker-compose build

print_status "Custom images built"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cat > .env << EOF
# Network Monitoring Project Configuration

# SNMP Configuration
SNMP_TARGET=snmp-simulator
SNMP_COMMUNITY=public
SNMP_VERSION=2c
SNMP_INTERVAL=15

# OpenTelemetry Configuration
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_SERVICE_NAME=network-monitor
OTEL_SERVICE_VERSION=1.0.0
OTEL_DEPLOYMENT_ENV=development

# Grafana Configuration
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin

# Prometheus Configuration
PROMETHEUS_RETENTION=15d
EOF
    print_status ".env file created"
else
    print_status ".env file already exists"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start the services: ./scripts/start.sh"
echo "2. Access Grafana: http://localhost:3000 (admin/admin)"
echo "3. Access Prometheus: http://localhost:9090"
echo "4. (Optional) Run Mininet topology: sudo python mininet/topology.py"
echo "5. Generate traffic: python mininet/traffic_generator.py"
echo ""
echo "For more information, see README.md"
echo ""

