#!/bin/bash

# Start all monitoring services

set -e

echo "=========================================="
echo "Starting Network Monitoring Services"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true
print_status "Existing containers stopped"

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

# Check Prometheus
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    print_status "Prometheus is running"
else
    print_warning "Prometheus may not be ready yet"
fi

# Check Grafana
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    print_status "Grafana is running"
else
    print_warning "Grafana may not be ready yet"
fi

# Check OpenTelemetry Collector
if curl -s http://localhost:13133 > /dev/null 2>&1; then
    print_status "OpenTelemetry Collector is running"
else
    print_warning "OpenTelemetry Collector may not be ready yet"
fi

# Display running containers
echo ""
echo "Running containers:"
docker-compose ps

echo ""
echo "=========================================="
echo -e "${GREEN}Services started successfully!${NC}"
echo "=========================================="
echo ""
echo "Access the following services:"
echo "  • Grafana:              http://localhost:3000 (admin/admin)"
echo "  • Prometheus:           http://localhost:9090"
echo "  • SNMP Exporter:        http://localhost:9116"
echo "  • OpenTelemetry:        http://localhost:4317 (gRPC)"
echo "  • Node Exporter:        http://localhost:9100"
echo ""
echo "View logs:"
echo "  docker-compose logs -f [service-name]"
echo ""
echo "Stop services:"
echo "  docker-compose down"
echo ""

