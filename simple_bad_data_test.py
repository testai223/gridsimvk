#!/usr/bin/env python3
"""
Simple test of bad data detection with manual verification
"""

from grid_state_estimator import GridStateEstimator
import numpy as np

# Create estimator
estimator = GridStateEstimator()
estimator.create_ieee9_grid()
estimator.simulate_measurements(noise_level=0.01)  # Very low noise

print("🔍 SIMPLE BAD DATA TEST")
print("="*40)
print(f"Grid: IEEE 9-bus")
print(f"Measurements: {len(estimator.net.measurement)}")

# Show some original measurements
print(f"\n📊 Sample original measurements:")
for i in range(3):
    meas = estimator.net.measurement.iloc[i]
    print(f"  [{i}] {meas['measurement_type'].upper()}: {meas['value']:.4f} (element {meas['element']})")

# Manually introduce obvious bad data
print(f"\n🚨 Introducing bad data:")
bad_idx = 0
original_value = estimator.net.measurement.loc[bad_idx, 'value']
bad_value = original_value * 10  # 10x the original value - very bad!

estimator.net.measurement.loc[bad_idx, 'value'] = bad_value

print(f"Corrupted measurement {bad_idx}:")
print(f"  Original: {original_value:.6f}")
print(f"  Bad:      {bad_value:.6f}")
print(f"  Ratio:    {bad_value/original_value:.1f}x")

# Run state estimation to see the impact
print(f"\n⚡ Running state estimation with bad data...")
estimator.run_state_estimation()

if estimator.estimation_results:
    print("✅ State estimation converged (but accuracy may be poor)")
else:
    print("❌ State estimation failed")

# Now test bad data detection
print(f"\n🔍 Testing bad data detection...")

# Override input for non-interactive testing
import builtins
original_input = builtins.input
builtins.input = lambda prompt: 'n'  # Don't restore measurements automatically

try:
    results = estimator.detect_bad_data(confidence_level=0.95, max_iterations=3)
    
    if results:
        print(f"\n📊 DETECTION RESULTS:")
        print(f"Final status: {results.get('final_status')}")
        
        bad_measurements = results.get('bad_measurements', [])
        if bad_measurements:
            print(f"Bad measurements found: {len(bad_measurements)}")
            for bad_meas in bad_measurements:
                idx = bad_meas['measurement_index']
                norm_residual = bad_meas['normalized_residual']
                print(f"  Index {idx}: normalized residual = {norm_residual:.3f}")
                
                if idx == bad_idx:
                    print(f"  🎯 Correctly identified the corrupted measurement!")
        else:
            print(f"No bad measurements detected")
            print(f"This might indicate:")
            print(f"  - Detection thresholds need adjustment")
            print(f"  - Bad data was not severe enough")
            print(f"  - Algorithm needs tuning")
    else:
        print(f"Detection failed")

finally:
    builtins.input = original_input

print(f"\n✅ Test completed")