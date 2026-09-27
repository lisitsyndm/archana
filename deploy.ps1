# deploy.ps1 - Deploy Archana project in Docker (Windows)
# Usage: .\deploy.ps1

$ErrorActionPreference = "Stop"

$APP_NAME = "archana"
$DB_NAME = "knowledge"
$DB_USER = "dima"
$DB_PASSWORD = "trooperQ@1"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Archana - Docker Deployment Script (Windows)"
Write-Host "============================================"
Write-Host ""

# Check Docker
Write-Host "Checking Docker..."
try {
    $dockerVersion = docker --version
    Write-Host "[OK] Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Docker is not installed. Install Docker Desktop for Windows and try again." -ForegroundColor Red
    exit 1
}

# Detect docker-compose command
$COMPOSE_CMD = $null
if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
    $COMPOSE_CMD = "docker-compose"
    $composeVersion = docker-compose --version
    Write-Host "[OK] docker-compose found: $composeVersion" -ForegroundColor Green
} elseif (docker compose version 2>&1 | Select-String "compose" -Quiet) {
    $COMPOSE_CMD = "docker compose"
    Write-Host "[OK] 'docker compose' (plugin) found" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Docker Compose not found. Make sure Docker Desktop is installed and running." -ForegroundColor Red
    exit 1
}

# Check .env file
Write-Host ""
if (-not (Test-Path ".env")) {
    Write-Host "[WARN] .env file not found. Creating with default settings..." -ForegroundColor Yellow
    
    $lines = @(
        "DB_HOST=localhost",
        "DB_PORT=5432",
        "DB_NAME=$DB_NAME",
        "DB_USERNAME=$DB_USER",
        "DB_PASSWORD=$DB_PASSWORD",
        "GF_ADMIN_USER=admin",
        "GF_ADMIN_PASSWORD=admin"
    )
    $lines | Out-File -FilePath ".env" -Encoding utf8
    Write-Host "[OK] .env file created" -ForegroundColor Green
} else {
    Write-Host "[OK] .env file found" -ForegroundColor Green
}

# Cleanup previous containers
Write-Host ""
Write-Host "Cleaning up previous containers..." -ForegroundColor Yellow

$existing = docker ps -a --format "{{.Names}}"
if ($existing -contains "${APP_NAME}_app") {
    docker rm -f "${APP_NAME}_app" | Out-Null
}
if ($existing -contains "${APP_NAME}_postgres") {
    docker rm -f "${APP_NAME}_postgres" | Out-Null
}
if ($existing -contains "${APP_NAME}_prometheus") {
    docker rm -f "${APP_NAME}_app" | Out-Null
}
if ($existing -contains "${APP_NAME}_grafana") {
    docker rm -f "${APP_NAME}_postgres" | Out-Null
}

# Remove volumes (optional, commented out for safety)
# docker volume rm "${APP_NAME}_postgres_data" 2>$null | Out-Null

Write-Host "[OK] Cleanup completed" -ForegroundColor Green

# Build images
Write-Host ""
Write-Host "Building Docker images..." -ForegroundColor Yellow
& $COMPOSE_CMD build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker image build failed." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Build completed successfully" -ForegroundColor Green

# Start services
Write-Host ""
Write-Host "Starting services..." -ForegroundColor Cyan
& $COMPOSE_CMD up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to start services." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Services started" -ForegroundColor Green

# Wait for PostgreSQL readiness
Write-Host ""
Write-Host "Waiting for PostgreSQL readiness (10 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check container health
Write-Host ""
Write-Host "Checking container status..." -ForegroundColor Cyan
& $COMPOSE_CMD ps

# Run database migrations
Write-Host ""
Write-Host "Running database migrations..." -ForegroundColor Cyan
docker exec ${APP_NAME}_app python migrations/db_0000.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Database migration failed." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Database migration completed" -ForegroundColor Green

# Initialize Grafana datasource
Write-Host ""
Write-Host "Initializing Grafana datasource..." -ForegroundColor Cyan
Start-Sleep -Seconds 15
& $PSScriptRoot\init-grafana.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] Grafana initialization failed. You can run it manually: .\init-grafana.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "============================================"
Write-Host ""
Write-Host "Services available:" -ForegroundColor Cyan
Write-Host "  - Application:    http://localhost:8000"
Write-Host "  - PostgreSQL:     localhost:5432"
Write-Host "  - Prometheus:     http://localhost:9090"
Write-Host "  - Grafana:        http://localhost:3000"
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  App logs:         $COMPOSE_CMD logs -f app"
Write-Host "  DB logs:          $COMPOSE_CMD logs -f postgres"
Write-Host "  Prometheus logs:  $COMPOSE_CMD logs -f prometheus"
Write-Host "  Grafana logs:     $COMPOSE_CMD logs -f grafana"
Write-Host "  Stop services:    $COMPOSE_CMD down"
Write-Host "  Stop + remove data: $COMPOSE_CMD down -v"
Write-Host ""
