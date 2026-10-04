@echo off
TITLE Food Delivery Analytics & Operations Intelligence Server
CLS

echo ====================================================================
echo  FOOD DELIVERY ANALYTICS & OPERATIONS INTELLIGENCE PLATFORM
echo ====================================================================
echo.
echo [1/3] Running Data Cleaning & Feature Engineering Pipeline...
python src/data_cleaning.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Data cleaning failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/3] Building Relational SQLite Warehouse & KPI Engine...
python src/feature_engineering.py
python src/db_manager.py
python src/kpi_engine.py
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Data pipeline processing failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Launching Operations Web Dashboard...
echo Opening http://localhost:3000 in your browser...
start http://localhost:3000

echo.
echo Server running on http://localhost:3000 (Press Ctrl+C to stop)
echo ====================================================================
echo.

node server.js
pause
