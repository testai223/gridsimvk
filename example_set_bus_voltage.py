#!/usr/bin/env python3
"""
Simple example showing how to set a specific bus voltage measurement
Example: "measurement bus a = 1.2 p.u."
"""

from grid_state_estimator import GridStateEstimator

# Create power system
estimator = GridStateEstimator()
estimator.create_ieee9_grid()
estimator.simulate_measurements(noise_level=0.02)

print("EXAMPLE: Setting bus voltage measurement")
print("="*45)

# Show original bus voltage
voltage_meas = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'v']
bus1_original = voltage_meas[voltage_meas['element'] == 1]['value'].iloc[0]
print(f"Bus 1 original voltage: {bus1_original:.4f} p.u.")

# Set bus voltage as requested: "measurement bus a = 1.2 p.u."
# (using bus 1 as example for "bus a")
estimator.modify_bus_voltage_measurement(bus_id=1, new_voltage_pu=1.2)

# Confirm the change
voltage_meas = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'v']
bus1_new = voltage_meas[voltage_meas['element'] == 1]['value'].iloc[0]
print(f"Bus 1 new voltage:      {bus1_new:.4f} p.u.")

# Run state estimation to see the impact
print(f"\nRunning state estimation...")
estimator.run_state_estimation()

if estimator.estimation_results and hasattr(estimator.net, 'res_bus_est'):
    estimated_voltage = estimator.net.res_bus_est.vm_pu.iloc[1]
    print(f"Estimated Bus 1 voltage: {estimated_voltage:.4f} p.u.")
    print(f"✅ Successfully modified and estimated with new measurement!")
else:
    print(f"❌ State estimation failed")

print(f"\nUsage examples:")
print(f"• estimator.modify_bus_voltage_measurement(1, 1.2)    # Set Bus 1 = 1.2 p.u.")
print(f"• estimator.modify_bus_voltage_measurement(0, 1.05)   # Set Bus 0 = 1.05 p.u.")
print(f"• estimator.modify_bus_voltage_measurement(3, 0.98)   # Set Bus 3 = 0.98 p.u.")