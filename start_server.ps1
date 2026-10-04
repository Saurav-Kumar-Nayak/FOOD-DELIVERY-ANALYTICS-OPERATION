Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host " FOOD DELIVERY ANALYTICS & OPERATIONS INTELLIGENCE PLATFORM" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Running Data Ingestion & Pipeline..." -ForegroundColor Yellow
python src/data_cleaning.py
python src/feature_engineering.py
python src/db_manager.py
python src/kpi_engine.py

Write-Host ""
Write-Host "[2/3] Opening Dashboard in browser..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "[3/3] Starting Server at http://localhost:3000 ..." -ForegroundColor Cyan
Write-Host "(Press Ctrl+C to stop server)" -ForegroundColor Gray
Write-Host "====================================================================" -ForegroundColor Cyan

node server.js
