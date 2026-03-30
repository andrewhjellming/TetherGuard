@echo off
title TetherGuard iOS Connection Stabilizer
echo [TetherGuard] Initializing boot sequence...

:: 1. Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python 3.10 or higher and try again.
    pause
    exit /b
)

:: 2. Create an isolated virtual environment if it doesn't exist
if not exist venv (
    echo [TetherGuard] First run detected. Creating virtual environment...
    python -m venv venv
)

:: 3. Activate the environment
call venv\Scripts\activate

:: 4. Verify/Install dependencies
echo [TetherGuard] Verifying core dependencies...
pip install -r requirements.txt -q
:: Install colorama for the terminal monitor
pip install colorama -q

:: 5. Launch the Application Monitor
echo [TetherGuard] Booting Application Monitor...
echo.
python logger.py

pause
