#!/usr/bin/env python3
"""
Test script for measurement modification functionality
Demonstrates how to modify specific measurements and test impact on state estimation
"""

from grid_state_estimator import GridStateEstimator
import numpy as np

def test_basic_measurement_modification():
    """Test basic measurement modification functionality"""
    print("MEASUREMENT MODIFICATION TEST")
    print("="*60)
    
    # Create estimator with IEEE 9-bus system
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    
    # Generate initial measurements
    print("\n1. Generating initial measurements...")
    estimator.simulate_measurements(noise_level=0.02)
    
    # List all measurements
    print("\n2. Original measurements:")
    estimator.list_measurements()
    
    # Modify a specific bus voltage measurement
    print("\n3. Modifying bus voltage measurement...")
    print("Setting Bus 1 voltage to 1.2 p.u. (significantly different from normal ~1.05)")
    estimator.modify_bus_voltage_measurement(bus_id=1, new_voltage_pu=1.2)
    
    # Modify a line power measurement
    print("\n4. Modifying line power measurement...")
    print("Setting Line 0 active power (from side) to 50 MW")
    estimator.modify_line_power_measurement(line_id=0, side='from', measurement_type='p', new_value=50.0)
    
    # Run state estimation with modified measurements
    print("\n5. Running state estimation with modified measurements...")
    estimator.run_state_estimation()
    
    if estimator.estimation_results:
        print("✅ State estimation completed with modified measurements")
        print("\nEstimated voltage results:")
        if hasattr(estimator.net, 'res_bus_est'):
            for i, bus_name in enumerate(estimator.net.bus.name):
                est_voltage = estimator.net.res_bus_est.vm_pu.iloc[i]
                print(f"  Bus {i} ({bus_name}): {est_voltage:.4f} p.u.")
        else:
            print("  State estimation results not available in expected format")
    else:
        print("❌ State estimation failed")
    
    # Reset measurements and test again
    print("\n6. Resetting measurements to original values...")
    estimator.reset_measurements(noise_level=0.02)
    
    print("\n7. Running state estimation with reset measurements...")
    estimator.run_state_estimation()
    
    if estimator.estimation_results:
        print("✅ State estimation completed with reset measurements")
    else:
        print("❌ State estimation failed with reset measurements")
    
    return True

def test_bad_data_scenario():
    """Test bad data detection scenario"""
    print("\n" + "="*60)
    print("BAD DATA SCENARIO TEST")
    print("="*60)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.01)  # Low noise for better baseline
    
    print("\n1. Creating bad data scenario...")
    
    # Create scenario with bad measurements
    estimator.create_measurement_scenario("bad_data")
    
    # Introduce several bad measurements
    print("\n2. Introducing bad measurements:")
    
    # Very high voltage (should be around 1.05, setting to 1.5)
    print("   • Setting Bus 2 voltage to 1.5 p.u. (unrealistic high voltage)")
    estimator.modify_bus_voltage_measurement(bus_id=2, new_voltage_pu=1.5)
    
    # Very high power flow (setting to unrealistic value)
    print("   • Setting Line 1 active power to 1000 MW (unrealistic for this system)")
    estimator.modify_line_power_measurement(line_id=1, side='from', measurement_type='p', new_value=1000.0)
    
    # Negative reactive power where it shouldn't be
    print("   • Setting Line 2 reactive power to -500 Mvar (unrealistic)")
    estimator.modify_line_power_measurement(line_id=2, side='to', measurement_type='q', new_value=-500.0)
    
    # Run state estimation with bad data
    print("\n3. Running state estimation with bad data...")
    estimator.run_state_estimation()
    
    # Show the impact
    if estimator.estimation_results:
        print("\n4. Results with bad data:")
        print("   (Note: State estimator may converge but with poor accuracy)")
        if hasattr(estimator.net, 'res_bus_est'):
            for i in range(min(3, len(estimator.net.res_bus_est))):
                true_voltage = estimator.net.res_bus.vm_pu.iloc[i] if hasattr(estimator.net, 'res_bus') else 'N/A'
                est_voltage = estimator.net.res_bus_est.vm_pu.iloc[i]
                print(f"   Bus {i}: Estimated = {est_voltage:.4f} p.u.")
                if true_voltage != 'N/A':
                    error = abs(est_voltage - true_voltage) / true_voltage * 100
                    print(f"            Error ≈ {error:.1f}% (if true={true_voltage:.4f})")
    
    return True

def test_sensitivity_analysis():
    """Test sensitivity to specific measurement changes"""
    print("\n" + "="*60)
    print("SENSITIVITY ANALYSIS TEST")
    print("="*60)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.0)  # Perfect measurements as baseline
    
    print("\n1. Running baseline state estimation (perfect measurements)...")
    estimator.run_state_estimation()
    
    baseline_voltages = None
    if estimator.estimation_results and hasattr(estimator.net, 'res_bus_est'):
        baseline_voltages = estimator.net.res_bus_est.vm_pu.copy()
        print("   ✅ Baseline results obtained")
    else:
        print("   ❌ Baseline state estimation failed")
        return False
    
    # Test sensitivity to different voltage measurement errors
    voltage_errors = [0.05, 0.10, 0.15]  # 5%, 10%, 15% errors
    bus_to_test = 1  # Test bus 1
    
    print(f"\n2. Testing sensitivity to Bus {bus_to_test} voltage measurement errors:")
    
    for error_pct in voltage_errors:
        # Reset to baseline
        estimator.reset_measurements(noise_level=0.0)
        
        # Get original measurement
        baseline_voltage = baseline_voltages.iloc[bus_to_test]
        modified_voltage = baseline_voltage * (1 + error_pct)  # Add error
        
        print(f"\n   Testing {error_pct*100}% voltage error:")
        print(f"   Original: {baseline_voltage:.4f} p.u. → Modified: {modified_voltage:.4f} p.u.")
        
        # Modify the measurement
        estimator.modify_bus_voltage_measurement(bus_id=bus_to_test, new_voltage_pu=modified_voltage)
        
        # Run state estimation
        estimator.run_state_estimation()
        
        if estimator.estimation_results and hasattr(estimator.net, 'res_bus_est'):
            new_voltages = estimator.net.res_bus_est.vm_pu
            
            # Calculate impact on all bus voltages
            max_impact = 0
            for i in range(len(baseline_voltages)):
                impact = abs(new_voltages.iloc[i] - baseline_voltages.iloc[i])
                max_impact = max(max_impact, impact)
            
            print(f"   Maximum voltage impact on any bus: {max_impact:.6f} p.u.")
            print(f"   Impact on modified bus: {abs(new_voltages.iloc[bus_to_test] - baseline_voltages.iloc[bus_to_test]):.6f} p.u.")
        else:
            print(f"   ❌ State estimation failed with {error_pct*100}% error")
    
    return True

def demonstrate_interactive_modification():
    """Demonstrate interactive measurement modification"""
    print("\n" + "="*60)
    print("INTERACTIVE MODIFICATION DEMONSTRATION")
    print("="*60)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.02)
    
    print("\n1. Current system state:")
    measurements_df = estimator.list_measurements()
    
    print("\n2. Example modifications you can make:")
    print("\n   Example 1: Modify by measurement index")
    print("   estimator.modify_measurement(0, 1.15)  # Modify first measurement to 1.15")
    
    print("\n   Example 2: Modify specific bus voltage")
    print("   estimator.modify_bus_voltage_measurement(3, 1.08)  # Set Bus 3 to 1.08 p.u.")
    
    print("\n   Example 3: Modify specific line power")
    print("   estimator.modify_line_power_measurement(0, 'from', 'p', 75.5)  # Set line 0 active power")
    
    print("\n3. Demonstrating direct measurement modification:")
    
    # Modify using direct index
    if len(estimator.net.measurement) > 0:
        first_measurement = estimator.net.measurement.iloc[0]
        original_value = first_measurement['value']
        new_value = original_value * 1.1  # 10% increase
        
        print(f"   Modifying measurement index 0 from {original_value:.4f} to {new_value:.4f}")
        estimator.modify_measurement(0, new_value)
    
    print("\n4. Available helper functions:")
    print("   • list_measurements()           - Show all measurements with indices")
    print("   • modify_measurement(idx, val)  - Modify by index")
    print("   • modify_bus_voltage_measurement(bus_id, voltage)")
    print("   • modify_line_power_measurement(line_id, side, type, value)")
    print("   • reset_measurements()          - Reset to original simulated values")
    print("   • create_measurement_scenario() - Interactive modification mode")
    
    return True

if __name__ == "__main__":
    print("COMPREHENSIVE MEASUREMENT MODIFICATION TESTING")
    print("="*80)
    
    # Run all tests
    tests = [
        ("Basic Modification", test_basic_measurement_modification),
        ("Bad Data Scenario", test_bad_data_scenario),
        ("Sensitivity Analysis", test_sensitivity_analysis),
        ("Interactive Demo", demonstrate_interactive_modification)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'🧪 ' + test_name.upper()}")
        try:
            success = test_func()
            if success:
                print(f"✅ {test_name} completed successfully")
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
    
    print(f"\n🎯 MEASUREMENT MODIFICATION TESTING COMPLETE!")
    print("="*80)
    print("\nYou can now modify any measurement in your power system model:")
    print("1. Use list_measurements() to see available measurements")
    print("2. Use modify_bus_voltage_measurement() for easy bus voltage changes")
    print("3. Use modify_line_power_measurement() for line power changes")
    print("4. Use modify_measurement() for direct index-based changes")
    print("5. Use reset_measurements() to restore original values")