#!/usr/bin/env python3

from grid_state_estimator import GridStateEstimator
import numpy as np

# Set random seed
np.random.seed(42)

estimator = GridStateEstimator()
estimator.create_ieee9_grid()

print("Testing noise implementation...")

# Test with clear noise
print("\n1. Adding 5% noise:")
estimator.simulate_measurements(noise_level=0.05)

print("Voltage measurements:")
v_measurements = estimator.net.measurement[estimator.net.measurement.measurement_type == 'v']
for i, row in v_measurements.iterrows():
    bus_idx = int(row['element'])
    true_val = estimator.net.res_bus.vm_pu.iloc[bus_idx] 
    measured_val = row['value']
    error = (measured_val - true_val) / true_val * 100
    print(f"Bus {bus_idx}: True={true_val:.6f}, Measured={measured_val:.6f}, Error={error:.3f}%")

print("\n2. Testing perfect measurements:")
estimator.simulate_measurements(noise_level=0.0)

v_measurements = estimator.net.measurement[estimator.net.measurement.measurement_type == 'v']
print("Perfect voltage measurements:")
for i, row in v_measurements.iterrows():
    bus_idx = int(row['element'])
    true_val = estimator.net.res_bus.vm_pu.iloc[bus_idx] 
    measured_val = row['value']
    error = (measured_val - true_val) / true_val * 100
    print(f"Bus {bus_idx}: True={true_val:.6f}, Measured={measured_val:.6f}, Error={error:.6f}%")