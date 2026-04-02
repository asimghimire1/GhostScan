@echo off
REM ============================================
REM MCQ Screen Assistant - Setup Script
REM ============================================

echo.
echo ==========================================
echo     MCQ Screen Assistant Setup
echo ==========================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Install requirements
echo Installing dependencies (this may take a minute)...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Setup Complete!
echo ==========================================
echo.
echo Before running the app, make sure:
echo.
echo 1. Ollama is installed from https://ollama.ai
echo 2. In Command Prompt, run: ollama pull mistral
echo 3. Tesseract is installed from:
echo    https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo Then run the app:
echo   python main.py
echo   or
echo   run.bat
echo.
pause
