#!/usr/bin/env python3
"""
Test script for grid visualization functionality
"""

from grid_state_estimator import GridStateEstimator
import numpy as np

def test_grid_visualization():
    """Test the new grid visualization features"""
    
    print("TESTING GRID VISUALIZATION")
    print("="*50)
    
    # Set random seed for reproducible results
    np.random.seed(42)
    
    # Create estimator and run analysis
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    
    print("\n1. Testing with noisy measurements...")
    estimator.simulate_measurements(noise_level=0.02)
    estimator.run_state_estimation()
    
    print("\n2. Showing tabular results...")
    print("First few voltage results:")
    for i in range(3):
        true_val = estimator.net.res_bus.vm_pu.iloc[i]
        est_val = estimator.estimation_results['bus_voltages'].vm_pu.iloc[i]
        error = (est_val - true_val) / true_val * 100
        print(f"  Bus {i}: True={true_val:.4f}, Est={est_val:.4f}, Error={error:.3f}%")
    
    print("\n3. Generating grid visualizations...")
    print("This will show 4 plots:")
    print("  - Voltage magnitudes on grid (color-coded)")
    print("  - Voltage estimation errors (red/blue)")  
    print("  - Power flows with arrows")
    print("  - Measurement locations")
    
    # This will trigger the grid visualization
    estimator.plot_grid_results()
    
    print("\n✅ Grid visualization test completed!")
    print("Check the plot windows for the visual results.")

if __name__ == "__main__":
    test_grid_visualization()