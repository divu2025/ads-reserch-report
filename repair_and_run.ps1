# repair_and_run.ps1

Write-Host 'Searching for a stable Python version (3.11 or 3.12)...' -ForegroundColor Cyan

$stablePython = $null

# Check for py launcher (best way on Windows)
if (Get-Command 'py' -ErrorAction SilentlyContinue) {
    if (& py -3.12 --version 2>$null) {
        $stablePython = 'py -3.12'
        Write-Host 'Found Python 3.12 via py launcher.' -ForegroundColor Green
    } elseif (& py -3.11 --version 2>$null) {
        $stablePython = 'py -3.11'
        Write-Host 'Found Python 3.11 via py launcher.' -ForegroundColor Green
    }
}

# Check direct python commands
if (-not $stablePython) {
    if (Get-Command 'python3.12' -ErrorAction SilentlyContinue) {
        $stablePython = 'python3.12'
    } elseif (Get-Command 'python3.11' -ErrorAction SilentlyContinue) {
        $stablePython = 'python3.11'
    } elseif (Get-Command 'python' -ErrorAction SilentlyContinue) {
        $ver = & python --version 2>&1
        if ($ver -like '*3.12*' -or $ver -like '*3.11*') {
            $stablePython = 'python'
        }
    }
}

if (-not $stablePython) {
    Write-Host 'ERROR: No stable Python version (3.11 or 3.12) found.' -ForegroundColor Red
    Write-Host 'Your current Python is likely too new (3.14+) or missing.'
    Write-Host 'Please ensure Python 3.12 is in your PATH.'
    exit 1
}

Write-Host "Proceeding with $stablePython..." -ForegroundColor Yellow

# 1. Clean existing environment
if (Test-Path '.venv') {
    Write-Host 'Cleaning old environment...'
    Remove-Item -Recurse -Force '.venv'
}

# 2. Create fresh .venv with STABLE version
Write-Host "Creating fresh .venv with $stablePython..."
if ($stablePython -eq 'py -3.12') {
    & py -3.12 -m venv .venv
} elseif ($stablePython -eq 'py -3.11') {
    & py -3.11 -m venv .venv
} else {
    & $stablePython -m venv .venv
}

# 3. Install dependencies
Write-Host 'Installing dependencies...'
& '.\.venv\Scripts\python.exe' -m pip install --upgrade pip
& '.\.venv\Scripts\python.exe' -m pip install -r requirements.txt

Write-Host '----------------------------------------' -ForegroundColor Green
Write-Host 'REPAIR COMPLETE!' -ForegroundColor Green
Write-Host 'Run .\start_agent.ps1 to start the application.' -ForegroundColor Yellow
Write-Host '----------------------------------------' -ForegroundColor Green
