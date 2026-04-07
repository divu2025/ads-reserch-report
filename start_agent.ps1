# start_agent.ps1

Write-Host 'Starting Jewelry Ads Intel Agent...' -ForegroundColor Cyan

# Check if .venv exists
if (-not (Test-Path '.venv')) {
    Write-Host 'ERROR: .venv not found! Please run .\repair_and_run.ps1 first.' -ForegroundColor Red
    exit 1
}

# Start Backend in a separate process
Write-Host 'Starting FastAPI Backend (Port 8000)...' -ForegroundColor Yellow
Start-Process powershell -ArgumentList '-NoExit', '-Command', "& '.\.venv\Scripts\python.exe' -m uvicorn main:app --reload --port 8000 --host 127.0.0.1"

# Wait for backend to initialize
Write-Host 'Waiting for backend...' -ForegroundColor Gray
Start-Sleep -Seconds 3

# Start Frontend in the current process
Write-Host 'Starting Streamlit Frontend...' -ForegroundColor Green
$streamlitPath = ".\.venv\Scripts\streamlit.exe"
& $streamlitPath run app.py
