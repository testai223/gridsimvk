@echo off
REM Power System State Estimation Web Application Launcher (Windows)
REM Quick launch script for the Flask web interface

echo ⚡ Power System State Estimation Web App Launcher
echo ==================================================

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo 🔍 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  No virtual environment found - using system Python
)

REM Check if web app exists
if not exist "web_ui\web_app.py" (
    echo ❌ Web app not found at web_ui\web_app.py
    pause
    exit /b 1
)

echo ✅ Web app found

REM Set Flask environment variables
set FLASK_APP=web_ui.web_app
set FLASK_ENV=development
set FLASK_DEBUG=1
set MPLBACKEND=Agg

REM Check Flask installation
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Flask not installed. Installing requirements...
    pip install -r requirements.txt
)

echo.
echo 🚀 Starting web application...
echo 📍 URL: http://127.0.0.1:8000
echo 🛑 Press Ctrl+C to stop
echo ==================================================

REM Start the web application
python run_web_app.py

echo.
echo 👋 Web application stopped
pause