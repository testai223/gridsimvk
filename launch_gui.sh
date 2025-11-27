#!/bin/bash
# Launch script for Power System GUI

echo "🔌 Launching Power System State Estimation GUI..."
echo "Please wait for the window to appear..."

# Check if virtual environment exists
if [ -f "venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Launch GUI
python3 simple_gui.py