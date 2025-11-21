#!/usr/bin/env python3
"""
Demo script showcasing grid visualization features
"""

from grid_state_estimator import GridStateEstimator
import numpy as np

def demo_grid_visualization():
    """Demonstrate grid visualization with different scenarios"""
    
    print("GRID VISUALIZATION DEMO")
    print("="*60)
    print("This demo shows how state estimation results are visualized on the grid")
    print("="*60)
    
    # Set seed for consistent results
    np.random.seed(123)
    
    # Create estimator
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    
    print(f"\nIEEE 9-Bus System Layout:")
    print(f"  Generators at buses: 0, 1, 2 (green)")
    print(f"  Loads at buses: 4, 5, 7 (red)")  
    print(f"  Transfer buses: 3, 6, 8 (blue)")
    print(f"  Total: 9 buses, 9 transmission lines")
    
    # Test with moderate noise to show visible differences
    print(f"\nGenerating measurements with 3% noise...")
    estimator.simulate_measurements(noise_level=0.03)
    
    print(f"Running state estimation...")
    estimator.run_state_estimation()
    
    # Show some key results
    print(f"\nKey Results Preview:")
    vm_true = estimator.net.res_bus.vm_pu.values
    vm_est = estimator.estimation_results['bus_voltages'].vm_pu.values
    errors = ((vm_est - vm_true) / vm_true) * 100
    
    print(f"  Average estimation error: {np.mean(np.abs(errors)):.3f}%")
    print(f"  Max estimation error: {np.max(np.abs(errors)):.3f}%")
    print(f"  Buses with highest errors: {np.argsort(np.abs(errors))[-3:]}")
    
    print(f"\nThe grid visualization will show:")
    print(f"  🎨 Plot 1: Voltage Magnitudes - Color-coded voltage levels")
    print(f"  📊 Plot 2: Estimation Errors - Red (over) / Blue (under) estimated")
    print(f"  🔄 Plot 3: Power Flows - Arrows showing direction and magnitude")
    print(f"  📍 Plot 4: Measurement Locations - Where sensors are placed")
    
    print(f"\nGenerating visualizations...")
    
    # Generate the grid plots
    estimator.plot_grid_results()
    
    print(f"\n✅ Demo completed!")
    print(f"The visualizations help operators:")
    print(f"  - Identify voltage problems across the network")
    print(f"  - See where estimation errors are largest") 
    print(f"  - Monitor power flow patterns")
    print(f"  - Verify sensor placement adequacy")

if __name__ == "__main__":
    demo_grid_visualization()