@echo off
REM ============================================
REM MCQ Screen Assistant - Run Script
REM ============================================

echo.
echo ==========================================
echo   MCQ Screen Assistant
echo ==========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import PyQt5, mss, pytesseract, anthropic" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        pause
        exit /b 1
    )
)

REM Run the application
echo Starting MCQ Assistant...
echo.
python main.py

pause
