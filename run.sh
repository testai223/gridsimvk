#!/bin/bash
# Simple launcher script for the Power System State Estimation Application

echo "🔌 Power System State Estimation Application Launcher"
echo "======================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup first:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if pandapower is installed
if ! python3 -c "import pandapower" 2>/dev/null; then
    echo "❌ pandapower not installed!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the main application
echo "🚀 Starting application..."
echo ""
python3 main.py

echo ""
echo "👋 Application finished."