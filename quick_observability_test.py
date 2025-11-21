#!/usr/bin/env python3

from grid_state_estimator import GridStateEstimator

# Quick test
estimator = GridStateEstimator()
estimator.create_ieee9_grid()
estimator.simulate_measurements(noise_level=0.0)

print("Running observability test...")
obs_results = estimator.test_observability()

print("\nQuick Summary:")
print(f"Measurements: {obs_results['n_measurements']}")
print(f"States: {obs_results['n_states']}")  
print(f"Redundancy: {obs_results['redundancy']:.2f}")
print(f"Status: {obs_results['status']}")
print(f"Coverage: {obs_results['coverage_percentage']:.1f}% of buses")