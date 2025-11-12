# Windows Setup Guide

Complete guide to run the Network Monitoring project on Windows.

---

## 📋 Prerequisites

### Required Software

1. **Docker Desktop for Windows**
   - Download: https://www.docker.com/products/docker-desktop/
   - Minimum: Windows 10 64-bit (Pro, Enterprise, or Education)
   - Or: Windows 11
   - Requires: WSL 2 (Windows Subsystem for Linux)

2. **Python 3.8+** ✅ (Already installed - Python 3.13.7)
   - Download: https://www.python.org/downloads/

3. **Git** (Optional, for version control)
   - Download: https://git-scm.com/download/win

---

## 🚀 Step-by-Step Setup

### Step 1: Install Docker Desktop

1. **Download Docker Desktop**
   ```
   https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
   ```

2. **Install Docker Desktop**
   - Run the installer
   - Follow the installation wizard
   - Enable WSL 2 when prompted
   - Restart your computer if required

3. **Start Docker Desktop**
   - Launch Docker Desktop from Start Menu
   - Wait for Docker to start (whale icon in system tray)
   - Accept the service agreement

4. **Verify Installation**
   ```powershell
   docker --version
   docker-compose --version
   ```

### Step 2: Configure Docker

1. **Open Docker Desktop Settings**
   - Right-click Docker icon in system tray
   - Click "Settings"

2. **Allocate Resources** (Recommended)
   - Go to "Resources" → "Advanced"
   - CPUs: 4 (minimum 2)
   - Memory: 4 GB (minimum 2 GB)
   - Click "Apply & Restart"

3. **Enable WSL 2 Integration** (if using WSL)
   - Go to "Resources" → "WSL Integration"
   - Enable integration with your WSL distros

### Step 3: Install Python Dependencies

```powershell
# Navigate to project directory
cd "d:\7th_Sem\Computer Networks\Project"

# Install Python packages
pip install -r requirements.txt
```

### Step 4: Setup Project

Since the setup script is for Linux/Mac, we'll do it manually on Windows:

```powershell
# Create necessary directories (if not exist)
New-Item -ItemType Directory -Force -Path "prometheus-data"
New-Item -ItemType Directory -Force -Path "grafana-data"

# Pull Docker images
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest
docker pull otel/opentelemetry-collector:latest
docker pull prom/snmp-exporter:latest
docker pull prom/node-exporter:latest
```

### Step 5: Start Services

```powershell
# Start all services
docker-compose up -d

# Wait 30 seconds for services to initialize
Start-Sleep -Seconds 30

# Check status
docker-compose ps
```

### Step 6: Verify Services

```powershell
# Check if services are running
docker-compose ps

# View logs
docker-compose logs

# Check specific service
docker-compose logs grafana
```

---

## 🌐 Access Services

Once all services are running:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **OpenTelemetry Collector** | http://localhost:13133 | - |

---

## 🧪 Testing

### Quick Health Check

```powershell
# Test Prometheus
Invoke-WebRequest -Uri "http://localhost:9090/-/healthy" -UseBasicParsing

# Test Grafana
Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing

# Test OpenTelemetry Collector
Invoke-WebRequest -Uri "http://localhost:13133" -UseBasicParsing
```

### Generate Test Traffic

```powershell
# Install Python dependencies first
pip install -r requirements.txt

# Run traffic generator
python mininet\traffic_generator.py --mode mixed
```

---

## 📊 View Dashboards

1. **Open Grafana**
   - Navigate to http://localhost:3000
   - Login: `admin` / `admin`
   - Skip password change (or set new password)

2. **Access Dashboards**
   - Click "Dashboards" (left sidebar)
   - Click "Browse"
   - You should see 3 dashboards:
     - SNMP Network Monitoring
     - OpenTelemetry Network Monitoring
     - SNMP vs OpenTelemetry Comparison

3. **View Metrics**
   - Click on any dashboard
   - Set time range to "Last 1 hour" (top-right)
   - Click refresh button

---

## 🛠️ Common Windows Issues

### Issue 1: Docker Desktop won't start

**Solution:**
1. Enable Hyper-V and Containers features:
   ```powershell
   # Run as Administrator
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   Enable-WindowsOptionalFeature -Online -FeatureName Containers -All
   ```
2. Restart computer
3. Start Docker Desktop

### Issue 2: WSL 2 not installed

**Solution:**
```powershell
# Run as Administrator
wsl --install
wsl --set-default-version 2
```
Restart computer after installation.

### Issue 3: Port already in use

**Solution:**
```powershell
# Find process using port (e.g., 3000)
netstat -ano | findstr :3000

# Kill process by PID
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

### Issue 4: Permission denied errors

**Solution:**
- Run PowerShell as Administrator
- Or add your user to docker-users group:
  ```powershell
  net localgroup docker-users "YOUR_USERNAME" /add
  ```
- Logout and login again

### Issue 5: Containers exit immediately

**Solution:**
```powershell
# Check logs
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔧 Windows-Specific Commands

### PowerShell Equivalents

| Linux/Mac | Windows PowerShell |
|-----------|-------------------|
| `ls -la` | `Get-ChildItem` or `dir` |
| `cat file.txt` | `Get-Content file.txt` |
| `chmod +x script.sh` | Not needed for .ps1 scripts |
| `./script.sh` | `.\script.ps1` |
| `grep pattern` | `Select-String pattern` |

### Useful PowerShell Commands

```powershell
# View all containers
docker ps -a

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# View logs (follow mode)
docker-compose logs -f

# Remove all containers and volumes
docker-compose down -v

# Check Docker disk usage
docker system df

# Clean up Docker
docker system prune -a
```

---

## 📝 Windows Testing Script

Create a file `test.ps1`:

```powershell
# Network Monitoring Test Script for Windows

Write-Host "Testing Network Monitoring Services..." -ForegroundColor Green

# Test 1: Docker is running
Write-Host "`n[1/5] Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running" -ForegroundColor Red
    exit 1
}

# Test 2: Services are running
Write-Host "`n[2/5] Checking services..." -ForegroundColor Yellow
$services = docker-compose ps --services --filter "status=running"
if ($services.Count -ge 6) {
    Write-Host "✓ Services are running ($($services.Count) services)" -ForegroundColor Green
} else {
    Write-Host "✗ Not all services are running" -ForegroundColor Red
}

# Test 3: Prometheus
Write-Host "`n[3/5] Testing Prometheus..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/-/healthy" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Prometheus is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Prometheus is not accessible" -ForegroundColor Red
}

# Test 4: Grafana
Write-Host "`n[4/5] Testing Grafana..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Grafana is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Grafana is not accessible" -ForegroundColor Red
}

# Test 5: OpenTelemetry Collector
Write-Host "`n[5/5] Testing OpenTelemetry Collector..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:13133" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ OpenTelemetry Collector is healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ OpenTelemetry Collector is not accessible" -ForegroundColor Red
}

Write-Host "`n" -NoNewline
Write-Host "Testing complete!" -ForegroundColor Green
Write-Host "`nAccess Grafana at: http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
```

Run it:
```powershell
.\test.ps1
```

---

## 🎯 Quick Start for Windows

**Complete setup in 5 steps:**

```powershell
# 1. Install Docker Desktop (manual download and install)
# Download from: https://www.docker.com/products/docker-desktop/

# 2. Navigate to project
cd "d:\7th_Sem\Computer Networks\Project"

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Start services
docker-compose up -d

# 5. Wait and access
Start-Sleep -Seconds 30
Start-Process "http://localhost:3000"
```

---

## 📚 Additional Resources

- **Docker Desktop Docs**: https://docs.docker.com/desktop/windows/
- **WSL 2 Setup**: https://docs.microsoft.com/en-us/windows/wsl/install
- **PowerShell Guide**: https://docs.microsoft.com/en-us/powershell/

---

## ✅ Verification Checklist

Before demo/presentation:

- [ ] Docker Desktop installed and running
- [ ] All services started: `docker-compose ps`
- [ ] Grafana accessible: http://localhost:3000
- [ ] Prometheus accessible: http://localhost:9090
- [ ] Dashboards visible in Grafana
- [ ] Metrics being collected (wait 2-3 minutes)
- [ ] Test script passes: `.\test.ps1`

---

## 🎓 For Your Presentation

**What to show:**

1. **Architecture** - Explain the diagram
2. **Running Services** - Show `docker-compose ps`
3. **Grafana Dashboards** - Live metrics
4. **Comparison** - Side-by-side analysis
5. **Understanding** - Explain how each component works

**Be ready to explain:**
- How SNMP polling works
- How OpenTelemetry push model works
- Why Prometheus is used for storage
- Trade-offs between the two approaches
- When to use each tool

---

## 🆘 Need Help?

1. Check logs: `docker-compose logs`
2. Review troubleshooting: `docs\troubleshooting.md`
3. Restart services: `docker-compose restart`
4. Clean restart: `docker-compose down && docker-compose up -d`

---

**Good luck with your project!** 🚀

