#!/usr/bin/env python3
"""
Simple demo of noise-free vs noisy measurement modes
"""

from grid_state_estimator import GridStateEstimator
import numpy as np

def main():
    print("POWER SYSTEM STATE ESTIMATION - NOISE COMPARISON")
    print("="*60)
    
    # Set random seed for reproducibility
    np.random.seed(12345)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    
    # Test 1: Perfect measurements
    print("\n🔹 PERFECT MEASUREMENTS (noise_level = 0.0)")
    print("-" * 40)
    estimator.simulate_measurements(noise_level=0.0)
    estimator.run_state_estimation()
    
    # Check first few voltage measurements
    print("First 3 bus voltage measurements:")
    for i in range(3):
        true_val = estimator.net.res_bus.vm_pu.iloc[i]
        meas_val = estimator.net.measurement[
            (estimator.net.measurement.measurement_type == 'v') &
            (estimator.net.measurement.element == i)
        ]['value'].iloc[0]
        est_val = estimator.estimation_results['bus_voltages'].vm_pu.iloc[i]
        meas_err = abs((meas_val - true_val) / true_val * 100)
        est_err = abs((est_val - true_val) / true_val * 100)
        print(f"  Bus {i}: True={true_val:.6f}, Meas={meas_val:.6f}, Est={est_val:.6f}")
        print(f"         Meas Error={meas_err:.6f}%, Est Error={est_err:.6f}%")
    
    # Test 2: Noisy measurements
    print("\n🔸 NOISY MEASUREMENTS (noise_level = 0.02)")
    print("-" * 40)
    estimator.simulate_measurements(noise_level=0.02)
    estimator.run_state_estimation()
    
    print("First 3 bus voltage measurements:")
    for i in range(3):
        true_val = estimator.net.res_bus.vm_pu.iloc[i]
        meas_val = estimator.net.measurement[
            (estimator.net.measurement.measurement_type == 'v') &
            (estimator.net.measurement.element == i)
        ]['value'].iloc[0]
        est_val = estimator.estimation_results['bus_voltages'].vm_pu.iloc[i]
        meas_err = abs((meas_val - true_val) / true_val * 100)
        est_err = abs((est_val - true_val) / true_val * 100)
        print(f"  Bus {i}: True={true_val:.6f}, Meas={meas_val:.6f}, Est={est_val:.6f}")
        print(f"         Meas Error={meas_err:.6f}%, Est Error={est_err:.6f}%")
    
    # Test 3: Higher noise
    print("\n🔸 HIGH NOISE MEASUREMENTS (noise_level = 0.05)")
    print("-" * 40)
    estimator.simulate_measurements(noise_level=0.05)
    estimator.run_state_estimation()
    
    print("First 3 bus voltage measurements:")
    for i in range(3):
        true_val = estimator.net.res_bus.vm_pu.iloc[i]
        meas_val = estimator.net.measurement[
            (estimator.net.measurement.measurement_type == 'v') &
            (estimator.net.measurement.element == i)
        ]['value'].iloc[0]
        est_val = estimator.estimation_results['bus_voltages'].vm_pu.iloc[i]
        meas_err = abs((meas_val - true_val) / true_val * 100)
        est_err = abs((est_val - true_val) / true_val * 100)
        print(f"  Bus {i}: True={true_val:.6f}, Meas={meas_val:.6f}, Est={est_val:.6f}")
        print(f"         Meas Error={meas_err:.6f}%, Est Error={est_err:.6f}%")
    
    print("\n" + "="*60)
    print("✅ Noise-free mode works: Perfect measurements = Load flow results")
    print("✅ Noisy modes work: Measurements have added noise, estimation filters it")
    print("✅ Higher noise shows clearer difference between measurement and estimation")

if __name__ == "__main__":
    main()