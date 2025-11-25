#!/usr/bin/env python3
"""
Simple demonstration of measurement modification functionality
Shows how to modify specific measurements like "bus a = 1.2 p.u."
"""

from grid_state_estimator import GridStateEstimator

def demo_measurement_modification():
    """Demonstrate measurement modification as requested"""
    print("MEASUREMENT MODIFICATION DEMO")
    print("="*50)
    print("Demonstrating: 'measurement bus a = 1.2 p.u.'")
    print("="*50)
    
    # Create estimator
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.02)
    
    # Show original measurements for bus voltages only
    print("\n1. Original bus voltage measurements:")
    voltage_measurements = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'v']
    for idx, row in voltage_measurements.iterrows():
        bus_id = row['element']
        value = row['value']
        print(f"   Bus {bus_id}: {value:.4f} p.u.")
    
    # Modify specific bus voltage (example: Bus 1 = 1.2 p.u.)
    print(f"\n2. Modifying Bus 1 voltage to 1.2 p.u. (as requested)...")
    success = estimator.modify_bus_voltage_measurement(bus_id=1, new_voltage_pu=1.2)
    
    if success:
        print(f"   ✅ Successfully modified Bus 1 voltage measurement")
    else:
        print(f"   ❌ Failed to modify Bus 1 voltage measurement")
    
    # Show updated measurements
    print(f"\n3. Updated bus voltage measurements:")
    voltage_measurements = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'v']
    for idx, row in voltage_measurements.iterrows():
        bus_id = row['element']
        value = row['value']
        print(f"   Bus {bus_id}: {value:.4f} p.u.")
    
    # Run state estimation with modified measurement
    print(f"\n4. Running state estimation with modified measurement...")
    estimator.run_state_estimation()
    
    if estimator.estimation_results:
        print(f"   ✅ State estimation completed successfully")
        
        # Show estimated voltages
        if hasattr(estimator.net, 'res_bus_est'):
            print(f"\n5. Estimated bus voltages:")
            for i in range(len(estimator.net.res_bus_est)):
                est_voltage = estimator.net.res_bus_est.vm_pu.iloc[i]
                print(f"   Bus {i}: {est_voltage:.4f} p.u. (estimated)")
        
        # Show the impact of the modification
        print(f"\n6. Impact analysis:")
        print(f"   Modified Bus 1 measurement: 1.2000 p.u.")
        if hasattr(estimator.net, 'res_bus_est') and len(estimator.net.res_bus_est) > 1:
            estimated_bus1 = estimator.net.res_bus_est.vm_pu.iloc[1]
            print(f"   Estimated Bus 1 voltage: {estimated_bus1:.4f} p.u.")
            print(f"   Difference: {abs(1.2 - estimated_bus1):.4f} p.u.")
    else:
        print(f"   ❌ State estimation failed")
    
    # Reset and show comparison
    print(f"\n7. Resetting measurements and comparing...")
    estimator.reset_measurements(noise_level=0.02)
    estimator.run_state_estimation()
    
    if estimator.estimation_results and hasattr(estimator.net, 'res_bus_est'):
        original_bus1 = estimator.net.res_bus_est.vm_pu.iloc[1]
        print(f"   Original estimated Bus 1: {original_bus1:.4f} p.u.")
        print(f"   Modified estimated Bus 1: {estimated_bus1:.4f} p.u.")
        print(f"   Impact of measurement change: {abs(estimated_bus1 - original_bus1):.4f} p.u.")

def show_available_methods():
    """Show all available measurement modification methods"""
    print("\n" + "="*60)
    print("AVAILABLE MEASUREMENT MODIFICATION METHODS")
    print("="*60)
    
    print("\n1. List all measurements:")
    print("   estimator.list_measurements()")
    print("   # Shows all measurements with indices, types, and values")
    
    print("\n2. Modify bus voltage measurement:")
    print("   estimator.modify_bus_voltage_measurement(bus_id, voltage_pu)")
    print("   # Example: estimator.modify_bus_voltage_measurement(1, 1.2)")
    print("   # Sets Bus 1 voltage measurement to 1.2 p.u.")
    
    print("\n3. Modify line power measurement:")
    print("   estimator.modify_line_power_measurement(line_id, side, type, value)")
    print("   # Example: estimator.modify_line_power_measurement(0, 'from', 'p', 150.0)")
    print("   # Sets Line 0 active power (from side) to 150 MW")
    
    print("\n4. Modify by measurement index:")
    print("   estimator.modify_measurement(index, new_value, new_std_dev=None)")
    print("   # Example: estimator.modify_measurement(5, 1.05)")
    print("   # Sets measurement at index 5 to 1.05")
    
    print("\n5. Reset all measurements:")
    print("   estimator.reset_measurements(noise_level=0.02)")
    print("   # Restores original simulated measurements")
    
    print("\n6. Create interactive scenario:")
    print("   estimator.create_measurement_scenario('my_test')")
    print("   # Shows measurements and helper information")

if __name__ == "__main__":
    print("🔧 POWER SYSTEM MEASUREMENT MODIFICATION")
    print("="*60)
    print("This demonstrates how to modify specific measurements")
    print("like setting 'bus a = 1.2 p.u.' as requested")
    print("="*60)
    
    # Run the main demonstration
    demo_measurement_modification()
    
    # Show available methods
    show_available_methods()
    
    print(f"\n🎯 DEMONSTRATION COMPLETE!")
    print("="*60)
    print("Key takeaway: You can now easily modify any measurement:")
    print("• estimator.modify_bus_voltage_measurement(1, 1.2)  # Bus 1 = 1.2 p.u.")
    print("• estimator.modify_line_power_measurement(0, 'from', 'p', 100)  # Line 0 = 100 MW")
    print("• estimator.list_measurements()  # See all available measurements")
    print("• estimator.run_state_estimation()  # Test impact on state estimation")