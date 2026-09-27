# init-grafana.ps1 - Initialize Grafana with Prometheus datasource
# Usage: .\init-grafana.ps1

$ErrorActionPreference = "Stop"

$GF_URL = "http://localhost:3000"

# Read .env file
$envFile = ".env"
$envVars = @{}
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([^#=]+)=(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim('"').Trim("'")
            $envVars[$key] = $value
        }
    }
}

$GF_USER = if ($envVars["GF_ADMIN_USER"]) { $envVars["GF_ADMIN_USER"] } else { "admin" }
$GF_PASSWORD = if ($envVars["GF_ADMIN_PASSWORD"]) { $envVars["GF_ADMIN_PASSWORD"] } else { "trooperQ@3p" }

Write-Host "Initializing Grafana..." -ForegroundColor Cyan

# Try to login with cookie-based auth
Write-Host "Logging in to Grafana..."
$loginBody = @{
    user     = $GF_USER
    password = $GF_PASSWORD
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
}

$loginResponse = $null
try {
    $loginResponse = Invoke-RestMethod -Uri "$GF_URL/api/auth/login" -Method POST -Headers $headers -Body $loginBody
    Write-Host "[OK] Logged in successfully" -ForegroundColor Green
    $authHeader = @{
        "Authorization" = "Bearer $($loginResponse.token)"
    }
} catch {
    Write-Host "[WARN] Token login failed, trying cookie-based auth..." -ForegroundColor Yellow
    
    # Use cookie-based authentication
    $loginUrl = "$GF_URL/login"
    $loginData = "user=$([System.Uri]::EscapeDataString($GF_USER))&password=$([System.Uri]::EscapeDataString($GF_PASSWORD))&redirectUrl=/"
    
    $webClient = New-Object System.Net.WebClient
    $webClient.Headers.Add("Content-Type", "application/x-www-form-urlencoded")
    
    try {
        $cookies = New-Object System.Net.CookieContainer
        $webClient.Headers.Add("CookieContainer", $cookies)
        
        $responseBytes = $webClient.UploadString($loginUrl, "POST", $loginData)
        $responseText = [System.Text.Encoding]::UTF8.GetString($responseBytes)
        
        if ($responseText -match '"name"') {
            Write-Host "[OK] Logged in with cookie auth" -ForegroundColor Green
            $authHeader = @{
                "Authorization" = "Bearer admin-token"
            }
        } else {
            throw "Cookie login failed"
        }
    } catch {
        Write-Host "[ERROR] Login failed. Grafana requires password change on first login." -ForegroundColor Red
        Write-Host ""
        Write-Host "  Manual fix required:" -ForegroundColor Yellow
        Write-Host "  1. Open http://localhost:3000" -ForegroundColor Yellow
        Write-Host "  2. Login with user='$GF_USER' password='$GF_PASSWORD'" -ForegroundColor Yellow
        Write-Host "  3. Change password when prompted" -ForegroundColor Yellow
        Write-Host "  4. Update GF_ADMIN_PASSWORD in .env file" -ForegroundColor Yellow
        Write-Host "  5. Run .\init-grafana.ps1 again" -ForegroundColor Yellow
        exit 1
    }
}

# Add Prometheus datasource
$dsBody = @{
    orgId     = 1
    name      = "Prometheus"
    type      = "prometheus"
    url       = "http://prometheus:9090"
    access    = "proxy"
    isDefault = $true
    version   = 1
    editable  = $true
    jsonData = @{
        timeInterval = "15s"
    }
} | ConvertTo-Json -Depth 10

try {
    $result = Invoke-RestMethod -Uri "$GF_URL/api/datasources" -Method POST -ContentType "application/json" -Body $dsBody
    Write-Host "[OK] Prometheus datasource added" -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode.value__ -eq 409) {
        Write-Host "[WARN] Prometheus datasource already exists" -ForegroundColor Yellow
    } else {
        Write-Host "[ERROR] Failed to add datasource: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Grafana initialized!" -ForegroundColor Green
Write-Host "Open: http://localhost:3000" -ForegroundColor Cyan
Write-Host "User: $GF_USER" -ForegroundColor Cyan
Write-Host "Password: $GF_PASSWORD" -ForegroundColor Cyan
Write-Host ""
