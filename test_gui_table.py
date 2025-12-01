#!/usr/bin/env python3
"""
Test script for GUI table functionality.

The test relies on a Tk GUI backend. In headless environments (like CI) we
gracefully skip to avoid ImportErrors from unavailable display backends.
"""

import os
import sys

import numpy as np
import pytest

import matplotlib

HAS_DISPLAY = bool(os.environ.get("DISPLAY")) or sys.platform.startswith("win")
if HAS_DISPLAY:
    matplotlib.use("TkAgg")
else:  # Headless execution
    matplotlib.use("Agg")

try:
    import tkinter as tk
except Exception as exc:  # pragma: no cover - environment-dependent
    pytest.skip(f"Tkinter unavailable: {exc}", allow_module_level=True)

if not HAS_DISPLAY:  # pragma: no cover - environment-dependent
    pytest.skip("No display available for Tk GUI tests", allow_module_level=True)

from simple_gui import PowerSystemGUI
from grid_state_estimator import GridStateEstimator

def test_table_functionality():
    """Test the table display functionality"""
    print("Testing GUI table functionality...")
    
    # Create a minimal GUI for testing
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        # Create estimator and run a complete workflow
        estimator = GridStateEstimator()
        estimator.create_ieee9_grid()
        print("✅ IEEE 9-bus grid created")
        
        # Set seed for reproducible results
        np.random.seed(42)
        estimator.simulate_measurements(noise_level=0.02)
        print("✅ Measurements generated")
        
        # Run state estimation
        estimator.run_state_estimation()
        print("✅ State estimation completed")
        
        # Test data extraction for table
        app = PowerSystemGUI(root)
        app.estimator = estimator
        
        # Test measurement comparison data extraction
        comparison_data = app.get_measurement_comparison_data()
        
        if comparison_data:
            print(f"✅ Successfully extracted {len(comparison_data)} measurement comparisons")
            
            # Show sample data
            print("\nSample table data:")
            print("-" * 80)
            print(f"{'Measurement':<25} {'Unit':<8} {'Load Flow':<12} {'Measured':<12} {'Est Error %':<12}")
            print("-" * 80)
            
            for i, data in enumerate(comparison_data[:5]):  # Show first 5 rows
                print(f"{data['Measurement']:<25} "
                      f"{data['Unit']:<8} "
                      f"{data['Load Flow Result']:<12.4f} "
                      f"{data['Simulated Measurement']:<12.4f} "
                      f"{data['Est vs True (%)']:<12.2f}")
            
            if len(comparison_data) > 5:
                print(f"... and {len(comparison_data) - 5} more rows")
            
            print("\n✅ Table functionality test completed successfully!")
            return True
        else:
            print("❌ Failed to extract measurement comparison data")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        root.destroy()

if __name__ == "__main__":
    success = test_table_functionality()
    sys.exit(0 if success else 1)