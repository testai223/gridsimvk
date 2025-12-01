#!/bin/bash

# Power System State Estimation Web Application Launcher
# Quick launch script for the Flask web interface

echo "⚡ Power System State Estimation Web App Launcher"
echo "=================================================="

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "🔍 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found - using system Python"
fi

# Check if web app exists
if [ ! -f "web_ui/web_app.py" ]; then
    echo "❌ Web app not found at web_ui/web_app.py"
    exit 1
fi

echo "✅ Web app found"

# Set Flask environment variables
export FLASK_APP=web_ui.web_app
export FLASK_ENV=development
export FLASK_DEBUG=1
export MPLBACKEND=Agg

# Check Flask installation
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ Flask not installed. Installing requirements..."
    pip install -r requirements.txt
fi

echo ""
echo "🚀 Starting web application..."
echo "📍 URL: http://127.0.0.1:8000"
echo "🛑 Press Ctrl+C to stop"
echo "=================================================="

# Start the web application
python run_web_app.py

echo ""
echo "👋 Web application stopped"