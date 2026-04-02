@echo off
REM ============================================
REM MCQ Screen Assistant - Build Script
REM ============================================

echo.
echo ==========================================
echo   Building MCQ Screen Assistant
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

REM Install PyInstaller if needed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

echo.
echo Building executable...
echo.

REM Build using spec file
pyinstaller --clean MCQAssistant.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   BUILD SUCCESSFUL!
echo ==========================================
echo.
echo Executable location: dist\MCQAssistant.exe
echo.
echo IMPORTANT:
echo - Ensure Tesseract OCR is installed on target machine
echo - Set ANTHROPIC_API_KEY environment variable
echo.

pause
