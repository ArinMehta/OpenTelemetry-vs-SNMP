#!/bin/bash

# Test script to verify monitoring setup

set -e

echo "=========================================="
echo "Network Monitoring Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0

test_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED++))
}

test_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test 1: Check if Prometheus is accessible
echo "Test 1: Prometheus accessibility"
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    test_pass "Prometheus is accessible"
else
    test_fail "Prometheus is not accessible"
fi

# Test 2: Check if Grafana is accessible
echo "Test 2: Grafana accessibility"
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    test_pass "Grafana is accessible"
else
    test_fail "Grafana is not accessible"
fi

# Test 3: Check if OpenTelemetry Collector is running
echo "Test 3: OpenTelemetry Collector health"
if curl -s http://localhost:13133 > /dev/null 2>&1; then
    test_pass "OpenTelemetry Collector is healthy"
else
    test_fail "OpenTelemetry Collector is not healthy"
fi

# Test 4: Check if SNMP Exporter is running
echo "Test 4: SNMP Exporter accessibility"
if curl -s http://localhost:9116/metrics > /dev/null 2>&1; then
    test_pass "SNMP Exporter is accessible"
else
    test_fail "SNMP Exporter is not accessible"
fi

# Test 5: Check if Prometheus is scraping targets
echo "Test 5: Prometheus targets"
TARGETS=$(curl -s http://localhost:9090/api/v1/targets | grep -o '"health":"up"' | wc -l)
if [ "$TARGETS" -gt 0 ]; then
    test_pass "Prometheus has $TARGETS healthy targets"
else
    test_warn "Prometheus has no healthy targets yet (may need more time)"
fi

# Test 6: Check if metrics are being collected
echo "Test 6: Metrics collection"
METRICS=$(curl -s http://localhost:9090/api/v1/label/__name__/values | grep -o '"network' | wc -l)
if [ "$METRICS" -gt 0 ]; then
    test_pass "Network metrics are being collected"
else
    test_warn "No network metrics found yet (may need more time)"
fi

# Test 7: Check if Grafana datasource is configured
echo "Test 7: Grafana datasource"
DATASOURCE=$(curl -s -u admin:admin http://localhost:3000/api/datasources | grep -o '"name":"Prometheus"' | wc -l)
if [ "$DATASOURCE" -gt 0 ]; then
    test_pass "Grafana Prometheus datasource is configured"
else
    test_fail "Grafana Prometheus datasource is not configured"
fi

# Test 8: Check if dashboards are loaded
echo "Test 8: Grafana dashboards"
DASHBOARDS=$(curl -s -u admin:admin http://localhost:3000/api/search | grep -o '"type":"dash-db"' | wc -l)
if [ "$DASHBOARDS" -gt 0 ]; then
    test_pass "$DASHBOARDS Grafana dashboards are loaded"
else
    test_warn "No Grafana dashboards found (may need to be imported manually)"
fi

# Test 9: Check Docker containers
echo "Test 9: Docker containers status"
RUNNING=$(docker-compose ps | grep "Up" | wc -l)
if [ "$RUNNING" -ge 5 ]; then
    test_pass "$RUNNING containers are running"
else
    test_fail "Only $RUNNING containers are running (expected at least 5)"
fi

# Test 10: Check network connectivity
echo "Test 10: Network connectivity"
if docker-compose exec -T prometheus wget -q -O- http://grafana:3000/api/health > /dev/null 2>&1; then
    test_pass "Inter-container networking is working"
else
    test_fail "Inter-container networking is not working"
fi

echo ""
echo "=========================================="
echo "Test Results"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All critical tests passed!${NC}"
    echo ""
    echo "You can now:"
    echo "  1. Access Grafana: http://localhost:3000"
    echo "  2. View dashboards: SNMP, OpenTelemetry, Comparison"
    echo "  3. Generate traffic: python mininet/traffic_generator.py"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check the logs:${NC}"
    echo "  docker-compose logs"
    exit 1
fi

