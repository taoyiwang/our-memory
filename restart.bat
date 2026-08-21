@echo off
rem One-click restart for Windows (double-click to run).
rem All real logic lives in restart.ps1 (ASCII-only output, no mojibake).

cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0restart.ps1"

echo.
echo Press any key to close this window...
pause >nul
