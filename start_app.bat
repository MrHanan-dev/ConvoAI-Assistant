@echo off
echo.
echo ===============================================
echo   AI Conversation Assistant - Python Edition
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

echo Python version:
python --version

echo.
echo Starting AI Conversation Assistant...
echo.

REM Run the Python launcher
python start_python_app.py

echo.
echo Application has stopped.
pause
