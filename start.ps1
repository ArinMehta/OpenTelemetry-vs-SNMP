# start.ps1 - Safe Windows start script (no special characters)
param(
    [switch]$NoPrompt
)

function Info($m)  { Write-Host "[INFO]  $m" -ForegroundColor Cyan }
function Warn($m)  { Write-Host "[WARN]  $m" -ForegroundColor Yellow }
function Err($m)   { Write-Host "[ERROR] $m" -ForegroundColor Red }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Network Monitoring Project - Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Info "Checking Docker..."
try {
    & docker info > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker CLI or daemon not available"
    }
    Info "Docker CLI and daemon are available"
} catch {
    Err "Docker is not running or not available. Start Docker Desktop and retry."
    Write-Host "Download: https://www.docker.com/products/docker-desktop/" -ForegroundColor Cyan
    exit 1
}

# Stop existing containers
Info "Stopping existing containers (if any)..."
& docker compose down --remove-orphans 2>&1 | Out-Null

# Ensure data dirs exist
Info "Ensuring data directories exist..."
New-Item -ItemType Directory -Force -Path "prometheus-data" | Out-Null
New-Item -ItemType Directory -Force -Path "grafana-data" | Out-Null

# Start services
Info "Starting services with 'docker compose up -d'..."
& docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Err "docker compose up -d failed. Run 'docker compose up' manually to see errors."
    exit 2
}

# Wait a short time for services to initialize
$wait = 20
for ($i = $wait; $i -gt 0; $i--) {
    Write-Host -NoNewline "`r  Waiting... $i seconds remaining "
    Start-Sleep -Seconds 1
}
Write-Host "`r"

# Show container status
Info "Docker containers:"
& docker compose ps

# Detect restarting containers and print last logs
$psOut = & docker ps --format '{{.Names}}|{{.Status}}'
$restarting = @()
foreach ($line in $psOut) {
    if ($line -match '^(?<name>[^|]+)\|(?<status>.*Restarting.*)$') {
        $restarting += $Matches['name']
    }
}

if ($restarting.Count -gt 0) {
    Warn ("Found container(s) in Restarting state: {0}" -f ($restarting -join ', '))
    foreach ($c in $restarting) {
        Write-Host ""
        Write-Host "---- Last 200 lines of logs for container: $c ----" -ForegroundColor Yellow
        & docker logs --tail 200 $c
        Write-Host "---- End logs for $c ----" -ForegroundColor Yellow
    }
    Warn "Inspect the logs above for errors (config, env, or runtime exceptions)."
} else {
    Info "No restarting containers detected."
}

# Basic HTTP health checks
function Check-Http($name, $url) {
    Write-Host -NoNewline ("  Checking {0}..." -f $name)
    try {
        $resp = Invoke-WebRequest -Uri $url -TimeoutSec 5 -ErrorAction Stop
        if ($null -ne $resp -and $resp.StatusCode -eq 200) {
            Write-Host " OK" -ForegroundColor Green
            return $true
        } else {
            Write-Host " FAIL" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host " FAIL" -ForegroundColor Red
        return $false
    }
}

Write-Host ""
Write-Host "Performing simple health checks..."
Check-Http "Prometheus" "http://localhost:9090/-/healthy"
Check-Http "Grafana" "http://localhost:3000/api/health"
Check-Http "OTel Collector" "http://localhost:13133/"

# Access info
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Access the services (if running):" -ForegroundColor White
Write-Host "  Grafana: http://localhost:3000  (default admin/admin)" -ForegroundColor White
Write-Host "  Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "  OTel Collector: http://localhost:13133" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not $NoPrompt) {
    $open = Read-Host "Open Grafana in browser now? (Y/N)"
    if ($open -match '^[Yy]') {
        Start-Process "http://localhost:3000"
        Info "Opening Grafana in browser..."
    }
}

Write-Host ""
Write-Host "Startup complete. Monitoring stack initiated." -ForegroundColor Green
Write-Host ""
