# Quick setup and test script for local testing
# Run this script to verify everything is set up correctly

Write-Host "=== Incident Tracker Local Test Setup ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Activate virtual environment
Write-Host "Step 1: Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    exit 1
}

# Step 2: Install/update dependencies
Write-Host ""
Write-Host "Step 2: Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Step 3: Test imports
Write-Host ""
Write-Host "Step 3: Testing imports..." -ForegroundColor Yellow
$env:PYTHONPATH = "."
python -c "from app import create_app; app = create_app('dev'); print('App imports successful')"
if ($LASTEXITCODE -eq 0) {
    Write-Host "All imports successful" -ForegroundColor Green
} else {
    Write-Host "ERROR: Import errors detected" -ForegroundColor Red
    exit 1
}

# Step 4: Check migrations
Write-Host ""
Write-Host "Step 4: Checking database migrations..." -ForegroundColor Yellow
flask db current
if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration check complete" -ForegroundColor Green
} else {
    Write-Host "WARNING: Migration check had issues - this might be OK if database doesn't exist yet" -ForegroundColor Yellow
}

# Step 5: Run type checking
Write-Host ""
Write-Host "Step 5: Running type checks..." -ForegroundColor Yellow
mypy app --no-error-summary *>&1 | Select-Object -First 10
if ($LASTEXITCODE -eq 0) {
    Write-Host "Type checking passed" -ForegroundColor Green
} else {
    Write-Host "WARNING: Type checking found some issues - check output above" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run migrations: flask db upgrade" -ForegroundColor White
Write-Host "2. Run tests: pytest -v" -ForegroundColor White
Write-Host "3. Start server: python run.py" -ForegroundColor White
Write-Host ""

