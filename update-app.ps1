# update-app.ps1 - Update only archana_app container
# Usage: .\update-app.ps1

$ErrorActionPreference = "Stop"

$APP_NAME = "archana"
$COMPOSE_CMD = $null

# Detect docker-compose command
if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
    $COMPOSE_CMD = "docker-compose"
} elseif (docker compose version 2>&1 | Select-String "compose" -Quiet) {
    $COMPOSE_CMD = "docker compose"
} else {
    Write-Host "[ERROR] Docker Compose not found." -ForegroundColor Red
    exit 1
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Update Archana App Container" -ForegroundColor Cyan
Write-Host "============================================"
Write-Host ""

# Check if containers are running
Write-Host "Checking container status..."
$composeStatus = & $COMPOSE_CMD ps --format table
Write-Host $composeStatus
Write-Host ""

# Rebuild only app image
Write-Host "Rebuilding app image..." -ForegroundColor Yellow
& $COMPOSE_CMD build --no-cache app

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Build completed" -ForegroundColor Green
Write-Host ""

# Stop and remove old app container
Write-Host "Stopping old app container..." -ForegroundColor Yellow
docker stop "${APP_NAME}_app" 2>$null | Out-Null
docker rm "${APP_NAME}_app" 2>$null | Out-Null

# Start new container
Write-Host "Starting new app container..." -ForegroundColor Cyan
& $COMPOSE_CMD up -d app

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to start app container." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] App container started" -ForegroundColor Green
Write-Host ""

# Wait for container to be healthy
Write-Host "Waiting for app to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Show status
Write-Host "Container status:" -ForegroundColor Cyan
& $COMPOSE_CMD ps app

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "App updated successfully!" -ForegroundColor Green
Write-Host "============================================"
Write-Host ""
Write-Host "App logs: $COMPOSE_CMD logs -f app"
Write-Host ""
