#!/bin/bash
# Script to activate virtual environment and install dependencies

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Virtual environment ready!"
echo "To activate manually: source venv/bin/activate"
echo "To run application: python grid_state_estimator.py"