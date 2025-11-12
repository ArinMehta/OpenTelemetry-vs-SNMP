# Network Monitoring: OpenTelemetry vs SNMP

## CS331 Project - IIT Gandhinagar

**Team Members:**
- Vedant Chichmalkar (22110282) - SNMP Implementation & Prometheus Integration
- Arin Mehta (23110038) - OpenTelemetry Implementation & Prometheus Integration
- Bhavya Parmar (23110059) - Integration Testing & Performance Comparison

## Project Overview

This project compares and integrates two key observability tools: OpenTelemetry and Simple Network Management Protocol (SNMP), to monitor and assess the performance and health of a network system.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Network Topology                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  Host 1  │────│ Switch 1 │────│  Host 2  │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│       │               │                │                     │
│       └───────────────┴────────────────┘                     │
│                       │                                      │
└───────────────────────┼──────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
   ┌────▼─────┐                  ┌─────▼────┐
   │   SNMP   │                  │OpenTelem │
   │  Agent   │                  │  Agent   │
   └────┬─────┘                  └─────┬────┘
        │                               │
        └───────────────┬───────────────┘
                        │
                  ┌─────▼──────┐
                  │ Prometheus │
                  └─────┬──────┘
                        │
                  ┌─────▼──────┐
                  │  Grafana   │
                  └────────────┘
```

## Features

- **SNMP Monitoring**: Traditional network device monitoring using SNMP v2/v3
- **OpenTelemetry Monitoring**: Modern observability with metrics, traces, and logs
- **Prometheus Integration**: Centralized metrics storage and querying
- **Grafana Dashboards**: Real-time visualization and comparison
- **Network Emulation**: Mininet-based network topology for testing

## Directory Structure

```
.
├── docker-compose.yml          # Docker services orchestration
├── mininet/                    # Network topology scripts
│   ├── topology.py            # Mininet network setup
│   └── traffic_generator.py   # Network traffic simulation
├── snmp/                       # SNMP monitoring setup
│   ├── snmpd.conf             # SNMP daemon configuration
│   ├── snmp_exporter.yml      # SNMP exporter for Prometheus
│   └── collect_snmp.py        # SNMP data collection script
├── opentelemetry/             # OpenTelemetry setup
│   ├── otel-collector-config.yaml
│   ├── instrumentation.py     # Application instrumentation
│   └── network_monitor.py     # Network metrics collection
├── prometheus/                 # Prometheus configuration
│   └── prometheus.yml
├── grafana/                    # Grafana dashboards
│   ├── dashboards/
│   │   ├── snmp-dashboard.json
│   │   ├── otel-dashboard.json
│   │   └── comparison-dashboard.json
│   └── provisioning/
├── scripts/                    # Utility scripts
│   ├── setup.sh               # Environment setup
│   ├── start.sh               # Start all services
│   └── test.sh                # Run tests
└── docs/                       # Documentation
    ├── setup-guide.md
    ├── comparison-analysis.md
    └── presentation.md
```

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Mininet (for network emulation)
- Linux environment (Ubuntu 20.04+ recommended)

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
./scripts/setup.sh

# Start all services
./scripts/start.sh
```

### 2. Access Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **OpenTelemetry Collector**: http://localhost:4317 (gRPC), http://localhost:4318 (HTTP)

### 3. Run Network Simulation

```bash
# Start Mininet topology
sudo python mininet/topology.py

# Generate traffic
python mininet/traffic_generator.py
```

## Monitoring Metrics

### SNMP Metrics
- Interface statistics (ifInOctets, ifOutOctets)
- Bandwidth utilization
- Packet loss and errors
- Device uptime
- CPU and memory usage

### OpenTelemetry Metrics
- Network latency (RTT)
- Throughput
- Packet loss rate
- Connection states
- Application-level metrics

## Timeline

- **Week 1**: Planning, Setup and Research ✓
- **Week 2**: Environment Setup
- **Week 3**: Implementation and Data Collection
- **Week 4**: Analysis, Visualization & Documentation

## Expected Outcomes

1. Working setup demonstrating network monitoring using both SNMP and OpenTelemetry
2. Grafana dashboards showing real-time data from both tools
3. Performance comparison analysis
4. Insights into combining SNMP and OpenTelemetry for comprehensive monitoring

## License

MIT License - Academic Project

## Contact

For questions or issues, contact the team members at their IIT Gandhinagar email addresses.

