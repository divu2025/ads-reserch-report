# setup_env.ps1

# 1. Clean existing environment
if (Test-Path '.venv') {
    Write-Host 'Removing existing .venv...' -ForegroundColor Cyan
    Remove-Item -Recurse -Force '.venv'
}

# 2. Recreate virtual environment
# Note: This will use the default 'python' in your PATH. 
# Ensure you are using Python 3.11 or 3.12 for best results.
Write-Host 'Creating fresh virtual environment...' -ForegroundColor Cyan
python -m venv .venv

# 3. Upgrade pip and install dependencies
Write-Host 'Installing dependencies from requirements.txt...' -ForegroundColor Cyan
& '.\.venv\Scripts\python.exe' -m pip install --upgrade pip
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt

Write-Host '----------------------------------------' -ForegroundColor Green
Write-Host 'Installation Complete!' -ForegroundColor Green
Write-Host 'To start the application, run .\start_agent.ps1' -ForegroundColor Yellow
Write-Host '----------------------------------------' -ForegroundColor Green
