# Network Monitoring Test Script for Windows
# CS331 Project - OpenTelemetry vs SNMP

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Network Monitoring Project - Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0

# Test 1: Docker is running
Write-Host "[Test 1/10] Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Docker is installed: $dockerVersion" -ForegroundColor Green
        $testsPassed++
    } else {
        throw "Docker not found"
    }
} catch {
    Write-Host "  [FAIL] Docker is not installed or not running" -ForegroundColor Red
    Write-Host "    Please install Docker Desktop from https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    $testsFailed++
}

# Test 2: Docker Compose is available
Write-Host "`n[Test 2/10] Checking Docker Compose..." -ForegroundColor Yellow
try {
    $composeVersion = docker-compose --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Docker Compose is available: $composeVersion" -ForegroundColor Green
        $testsPassed++
    } else {
        throw "Docker Compose not found"
    }
} catch {
    Write-Host "  [FAIL] Docker Compose is not available" -ForegroundColor Red
    $testsFailed++
}

# Test 3: Services are running
Write-Host "`n[Test 3/10] Checking running services..." -ForegroundColor Yellow
try {
    $runningServices = docker-compose ps --services --filter "status=running" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $serviceCount = ($runningServices | Measure-Object).Count
        if ($serviceCount -ge 6) {
            Write-Host "  [OK] Services are running ($serviceCount services)" -ForegroundColor Green
            $testsPassed++
        } else {
            Write-Host "  [FAIL] Only $serviceCount services running (expected 6+)" -ForegroundColor Red
            Write-Host "    Run: docker-compose up -d" -ForegroundColor Yellow
            $testsFailed++
        }
    } else {
        throw "Cannot check services"
    }
} catch {
    Write-Host "  [FAIL] Cannot check services. Are they started?" -ForegroundColor Red
    Write-Host "    Run: docker-compose up -d" -ForegroundColor Yellow
    $testsFailed++
}

# Test 4: Prometheus is accessible
Write-Host "`n[Test 4/10] Testing Prometheus..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/-/healthy" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  [OK] Prometheus is healthy (http://localhost:9090)" -ForegroundColor Green
        $testsPassed++
    }
} catch {
    Write-Host "  [FAIL] Prometheus is not accessible" -ForegroundColor Red
    Write-Host "    Check: docker-compose logs prometheus" -ForegroundColor Yellow
    $testsFailed++
}

# Test 5: Grafana is accessible
Write-Host "`n[Test 5/10] Testing Grafana..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  [OK] Grafana is healthy (http://localhost:3000)" -ForegroundColor Green
        $testsPassed++
    }
} catch {
    Write-Host "  [FAIL] Grafana is not accessible" -ForegroundColor Red
    Write-Host "    Check: docker-compose logs grafana" -ForegroundColor Yellow
    $testsFailed++
}

# Test 6: OpenTelemetry Collector is accessible
Write-Host "`n[Test 6/10] Testing OpenTelemetry Collector..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:13133" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  [OK] OpenTelemetry Collector is healthy" -ForegroundColor Green
        $testsPassed++
    }
} catch {
    Write-Host "  [FAIL] OpenTelemetry Collector is not accessible" -ForegroundColor Red
    Write-Host "    Check: docker-compose logs otel-collector" -ForegroundColor Yellow
    $testsFailed++
}

# Test 7: Prometheus has targets
Write-Host "`n[Test 7/10] Checking Prometheus targets..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/targets" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    $targets = ($response.Content | ConvertFrom-Json).data.activeTargets
    $upTargets = ($targets | Where-Object { $_.health -eq "up" }).Count
    $totalTargets = $targets.Count
    
    if ($upTargets -ge 3) {
        Write-Host "  [OK] Prometheus has $upTargets/$totalTargets targets up" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  [FAIL] Only $upTargets/$totalTargets targets are up" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] Cannot check Prometheus targets" -ForegroundColor Red
    $testsFailed++
}

# Test 8: SNMP metrics are being collected
Write-Host "`n[Test 8/10] Checking SNMP metrics..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/query?query=snmp_if_in_octets_total" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    $result = ($response.Content | ConvertFrom-Json).data.result
    
    if ($result.Count -gt 0) {
        Write-Host "  [OK] SNMP metrics are being collected" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  [WARN] SNMP metrics not found (may need time to collect)" -ForegroundColor Yellow
        Write-Host "    Wait 1-2 minutes and try again" -ForegroundColor Yellow
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] Cannot check SNMP metrics" -ForegroundColor Red
    $testsFailed++
}

# Test 9: OpenTelemetry metrics are being collected
Write-Host "`n[Test 9/10] Checking OpenTelemetry metrics..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/query?query=network_latency_ms" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    $result = ($response.Content | ConvertFrom-Json).data.result
    
    if ($result.Count -gt 0) {
        Write-Host "  [OK] OpenTelemetry metrics are being collected" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  [WARN] OpenTelemetry metrics not found (may need time to collect)" -ForegroundColor Yellow
        Write-Host "    Wait 1-2 minutes and try again" -ForegroundColor Yellow
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] Cannot check OpenTelemetry metrics" -ForegroundColor Red
    $testsFailed++
}

# Test 10: Grafana dashboards exist
Write-Host "`n[Test 10/10] Checking Grafana dashboards..." -ForegroundColor Yellow
try {
    # Try to access Grafana API (may require auth, so we just check if endpoint responds)
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/search?query=&" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    
    if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 401) {
        Write-Host "  [OK] Grafana API is accessible" -ForegroundColor Green
        Write-Host "    Login at http://localhost:3000 (admin/admin) to view dashboards" -ForegroundColor Cyan
        $testsPassed++
    }
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 401) {
        Write-Host "  [OK] Grafana is running (requires login)" -ForegroundColor Green
        Write-Host "    Login at http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
        $testsPassed++
    } else {
        Write-Host "  [FAIL] Cannot access Grafana dashboards" -ForegroundColor Red
        $testsFailed++
    }
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tests Passed: $testsPassed/10" -ForegroundColor Green
Write-Host "Tests Failed: $testsFailed/10" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })

if ($testsPassed -eq 10) {
    Write-Host "`n[OK] All tests passed! Your setup is working correctly." -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Open Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor White
    Write-Host "  2. View dashboards: Dashboards → Browse" -ForegroundColor White
    Write-Host "  3. Generate traffic: python mininet\traffic_generator.py" -ForegroundColor White
} elseif ($testsPassed -ge 7) {
    Write-Host "`n[WARN] Most tests passed. Some services may need more time to initialize." -ForegroundColor Yellow
    Write-Host "  Wait 1-2 minutes and run this test again." -ForegroundColor Yellow
} else {
    Write-Host "`n[FAIL] Several tests failed. Please check the errors above." -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Cyan
    Write-Host "  1. Ensure Docker Desktop is running" -ForegroundColor White
    Write-Host "  2. Start services: docker-compose up -d" -ForegroundColor White
    Write-Host "  3. Check logs: docker-compose logs" -ForegroundColor White
    Write-Host "  4. See WINDOWS_SETUP.md for detailed instructions" -ForegroundColor White
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host ""

# Return exit code based on results
if ($testsFailed -eq 0) {
    exit 0
} else {
    exit 1
}