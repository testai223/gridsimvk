#!/usr/bin/env python3
"""
Test script to demonstrate noise-free vs noisy measurement modes
"""

from grid_state_estimator import GridStateEstimator

def test_both_modes():
    """Test both noise-free and noisy modes"""
    
    print("="*70)
    print("TESTING NOISE-FREE vs NOISY MEASUREMENT MODES")
    print("="*70)
    
    # Set random seed for reproducible results
    import numpy as np
    np.random.seed(42)
    
    # Create estimator
    estimator = GridStateEstimator()
    
    # Create grid
    print("\n1. Creating IEEE 9-bus grid model...")
    estimator.create_ieee9_grid()
    
    # Test noise-free mode
    print("\n" + "="*50)
    print("MODE 1: PERFECT MEASUREMENTS (No Noise)")
    print("="*50)
    
    estimator.simulate_measurements(noise_level=0.0)
    estimator.run_state_estimation()
    
    # Show only the measurement comparison table
    measurement_comparison = []
    
    # Get voltage measurements comparison
    for i, bus_idx in enumerate(estimator.net.bus.index):
        true_value = estimator.net.res_bus.vm_pu.iloc[bus_idx]
        v_measurements = estimator.net.measurement[
            (estimator.net.measurement.element == bus_idx) & 
            (estimator.net.measurement.measurement_type == 'v')
        ]
        measured_value = v_measurements['value'].iloc[0] if not v_measurements.empty else true_value
        estimated_value = estimator.estimation_results['bus_voltages'].vm_pu.iloc[bus_idx]
        
        measurement_comparison.append({
            'Bus': f'Bus {bus_idx}',
            'Load Flow': true_value,
            'Measurement': measured_value,
            'Estimated': estimated_value,
            'Meas Error (%)': ((measured_value - true_value) / true_value * 100),
            'Est Error (%)': ((estimated_value - true_value) / true_value * 100)
        })
    
    import pandas as pd
    df_perfect = pd.DataFrame(measurement_comparison)
    print("\nVOLTAGE MEASUREMENTS COMPARISON (Perfect):")
    print(df_perfect.round(6))
    print(f"Mean measurement error: {df_perfect['Meas Error (%)'].abs().mean():.6f}%")
    print(f"Mean estimation error: {df_perfect['Est Error (%)'].abs().mean():.6f}%")
    
    # Test noisy mode
    print("\n" + "="*50)
    print("MODE 2: NOISY MEASUREMENTS (2% Noise)")
    print("="*50)
    
    estimator.simulate_measurements(noise_level=0.02)
    estimator.run_state_estimation()
    
    # Show measurement comparison for noisy mode
    measurement_comparison = []
    
    for i, bus_idx in enumerate(estimator.net.bus.index):
        true_value = estimator.net.res_bus.vm_pu.iloc[bus_idx]
        v_measurements = estimator.net.measurement[
            (estimator.net.measurement.element == bus_idx) & 
            (estimator.net.measurement.measurement_type == 'v')
        ]
        measured_value = v_measurements['value'].iloc[0] if not v_measurements.empty else true_value
        estimated_value = estimator.estimation_results['bus_voltages'].vm_pu.iloc[bus_idx]
        
        measurement_comparison.append({
            'Bus': f'Bus {bus_idx}',
            'Load Flow': true_value,
            'Measurement': measured_value,
            'Estimated': estimated_value,
            'Meas Error (%)': ((measured_value - true_value) / true_value * 100),
            'Est Error (%)': ((estimated_value - true_value) / true_value * 100)
        })
    
    df_noisy = pd.DataFrame(measurement_comparison)
    print("\nVOLTAGE MEASUREMENTS COMPARISON (Noisy):")
    print(df_noisy.round(6))
    print(f"Mean measurement error: {df_noisy['Meas Error (%)'].abs().mean():.6f}%")
    print(f"Mean estimation error: {df_noisy['Est Error (%)'].abs().mean():.6f}%")
    
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    print("Perfect measurements:")
    print(f"  - Measurement error: ~0% (perfect)")
    print(f"  - Estimation error: ~{df_perfect['Est Error (%)'].abs().mean():.4f}% (numerical precision)")
    print("\nNoisy measurements:")
    print(f"  - Measurement error: ~{df_noisy['Meas Error (%)'].abs().mean():.2f}% (added noise)")
    print(f"  - Estimation error: ~{df_noisy['Est Error (%)'].abs().mean():.2f}% (filtered by state estimation)")
    print(f"\nState estimation reduces error by: {(df_noisy['Meas Error (%)'].abs().mean() / df_noisy['Est Error (%)'].abs().mean()):.1f}x")

if __name__ == "__main__":
    test_both_modes()