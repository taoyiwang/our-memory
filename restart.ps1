# One-click restart for the "Our Story" dev server (PowerShell core).
# Called by restart.bat (double-click). Can also be run directly:
#   powershell -NoProfile -ExecutionPolicy Bypass -File restart.ps1
#
# Note: keep ALL output ASCII-only so the window never shows mojibake
# regardless of PowerShell 5.1 / code-page handling.

$ErrorActionPreference = 'SilentlyContinue'
Set-Location $PSScriptRoot

$port = if ($env:PORT_OVERRIDE) { $env:PORT_OVERRIDE } else { '5000' }
$logDir = Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
# Start-Process requires stdout / stderr to be different files
$outLog = Join-Path $logDir 'dev.log'
$errLog = Join-Path $logDir 'dev.err.log'

Write-Host '==> Stopping old process...'
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*app.py*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Write-Host '==> Freeing the port...'
$netstat = (netstat -ano | Where-Object { $_ -match ":$port\s" -and $_ -match 'LISTENING' })
if ($netstat) {
    $netstat | ForEach-Object { ($_ -split '\s+')[-1] } | Sort-Object -Unique |
        ForEach-Object { Stop-Process -Id $_ -Force }
}

Start-Sleep -Seconds 1

Write-Host "==> Starting server (port $port)..."
$proc = Start-Process -FilePath (Join-Path $PSScriptRoot 'venv\Scripts\python.exe') `
    -ArgumentList 'app.py' `
    -WorkingDirectory $PSScriptRoot `
    -RedirectStandardOutput $outLog -RedirectStandardError $errLog `
    -WindowStyle Hidden -PassThru

Write-Host '==> Waiting for the server to be ready...'
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$port/login" -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Milliseconds 500 }
}

if ($ready) {
    Write-Host ""
    Write-Host "OK! Server is running at: http://localhost:$port"
    Write-Host "    (default password: 123456)"
    Write-Host "    Logs: logs\dev.log"
} else {
    Write-Host '==> Timed out. Recent log output:'
    Get-Content $outLog -Tail 20 -ErrorAction SilentlyContinue
    if (Test-Path $errLog) { Write-Host '--- stderr ---'; Get-Content $errLog -Tail 20 -ErrorAction SilentlyContinue }
    exit 1
}
