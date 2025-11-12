# Quick Start Guide

Get the Network Monitoring project up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ installed
- 4GB RAM available
- Linux/macOS (Windows with WSL2)

## Quick Setup (3 Steps)

### Step 1: Setup Environment

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run setup
./scripts/setup.sh
```

### Step 2: Start Services

```bash
# Start all monitoring services
./scripts/start.sh
```

Wait about 30 seconds for all services to initialize.

### Step 3: Access Dashboards

Open your browser:

- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`
  
- **Prometheus**: http://localhost:9090

## View Dashboards

In Grafana:

1. Click on "Dashboards" (left sidebar)
2. Click "Browse"
3. You'll see three dashboards:
   - **SNMP Network Monitoring** - Traditional network metrics
   - **OpenTelemetry Network Monitoring** - Modern application metrics
   - **SNMP vs OpenTelemetry Comparison** - Side-by-side comparison

## Generate Traffic (Optional)

To see metrics in action:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate network traffic
python mininet/traffic_generator.py --mode mixed
```

Press `Ctrl+C` to stop.

## Verify Everything Works

```bash
./scripts/test.sh
```

This runs automated tests to verify all components are working.

## Common Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# View running containers
docker-compose ps
```

## Troubleshooting

### Services not starting?

```bash
# Check Docker is running
docker info

# View detailed logs
docker-compose logs
```

### No metrics in Grafana?

1. Wait 1-2 minutes for data collection
2. Check time range (top-right, set to "Last 1 hour")
3. Click refresh button
4. Verify Prometheus has data: http://localhost:9090/graph

### Port already in use?

```bash
# Stop conflicting services
docker-compose down

# Or change ports in docker-compose.yml
```

## What's Running?

After starting, you'll have:

- **Prometheus** (port 9090) - Metrics storage
- **Grafana** (port 3000) - Visualization
- **OpenTelemetry Collector** (ports 4317, 4318) - Metrics collection
- **SNMP Exporter** (port 9116) - SNMP to Prometheus bridge
- **Network Monitor** (port 8080) - Custom network monitoring
- **SNMP Collector** (port 8000) - SNMP data collector

## Next Steps

1. ✓ Explore the three Grafana dashboards
2. ✓ Generate traffic and watch metrics update
3. ✓ Read the full documentation in `docs/setup-guide.md`
4. ✓ Review the comparison analysis in `docs/comparison-analysis.md`
5. ✓ Check the presentation outline in `docs/presentation.md`

## Project Structure

```
.
├── docker-compose.yml          # Service orchestration
├── prometheus/                 # Prometheus config
├── grafana/                    # Grafana dashboards
├── opentelemetry/             # OpenTelemetry setup
├── snmp/                      # SNMP monitoring
├── mininet/                   # Network simulation
├── scripts/                   # Utility scripts
└── docs/                      # Documentation
```

## Support

For detailed information, see:
- `README.md` - Project overview
- `docs/setup-guide.md` - Detailed setup instructions
- `docs/comparison-analysis.md` - Technical comparison
- `docs/presentation.md` - Presentation outline

## Team

- Vedant Chichmalkar (22110282) - SNMP Implementation
- Arin Mehta (23110038) - OpenTelemetry Implementation
- Bhavya Parmar (23110059) - Integration & Comparison

---

**Enjoy monitoring!** 🚀

