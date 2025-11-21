#!/usr/bin/env python3
"""
Observability testing script for power system state estimation
Tests different measurement scenarios and their observability
"""

from grid_state_estimator import GridStateEstimator
import pandapower as pp
import numpy as np

def create_custom_measurements(estimator, scenario):
    """Create different measurement scenarios for observability testing"""
    
    # Clear existing measurements
    estimator.net.measurement = estimator.net.measurement.iloc[0:0]  # Empty dataframe
    
    # Run power flow to get true values
    pp.runpp(estimator.net, algorithm='nr')
    
    if scenario == "full":
        print("Creating FULL measurement set (all buses + all lines)")
        # All voltage measurements
        for bus_idx in estimator.net.bus.index:
            true_value = estimator.net.res_bus.vm_pu.iloc[bus_idx]
            pp.create_measurement(estimator.net, "v", "bus", true_value, 0.01, bus_idx)
        
        # All power flow measurements
        for line_idx in estimator.net.line.index:
            true_p_from = estimator.net.res_line.p_from_mw.iloc[line_idx]
            true_p_to = estimator.net.res_line.p_to_mw.iloc[line_idx]
            true_q_from = estimator.net.res_line.q_from_mvar.iloc[line_idx]
            true_q_to = estimator.net.res_line.q_to_mvar.iloc[line_idx]
            
            pp.create_measurement(estimator.net, "p", "line", true_p_from, 1.0, line_idx, side="from")
            pp.create_measurement(estimator.net, "p", "line", true_p_to, 1.0, line_idx, side="to")
            pp.create_measurement(estimator.net, "q", "line", true_q_from, 1.0, line_idx, side="from")
            pp.create_measurement(estimator.net, "q", "line", true_q_to, 1.0, line_idx, side="to")
    
    elif scenario == "minimal_good":
        print("Creating MINIMAL but GOOD measurement set")
        # Voltage measurements at key buses (generators + some load buses)
        key_buses = [0, 1, 2, 4, 7]  # Generator buses + some load buses
        for bus_idx in key_buses:
            true_value = estimator.net.res_bus.vm_pu.iloc[bus_idx]
            pp.create_measurement(estimator.net, "v", "bus", true_value, 0.01, bus_idx)
        
        # Power flow measurements on key lines
        key_lines = [0, 1, 2, 5, 7]  # Strategic lines for network coverage
        for line_idx in key_lines:
            true_p_from = estimator.net.res_line.p_from_mw.iloc[line_idx]
            true_q_from = estimator.net.res_line.q_from_mvar.iloc[line_idx]
            pp.create_measurement(estimator.net, "p", "line", true_p_from, 1.0, line_idx, side="from")
            pp.create_measurement(estimator.net, "q", "line", true_q_from, 1.0, line_idx, side="from")
    
    elif scenario == "voltage_only":
        print("Creating VOLTAGE ONLY measurements")
        # Only voltage measurements at all buses
        for bus_idx in estimator.net.bus.index:
            true_value = estimator.net.res_bus.vm_pu.iloc[bus_idx]
            pp.create_measurement(estimator.net, "v", "bus", true_value, 0.01, bus_idx)
    
    elif scenario == "power_only":
        print("Creating POWER FLOW ONLY measurements")
        # Only power flow measurements
        for line_idx in estimator.net.line.index:
            true_p_from = estimator.net.res_line.p_from_mw.iloc[line_idx]
            true_q_from = estimator.net.res_line.q_from_mvar.iloc[line_idx]
            pp.create_measurement(estimator.net, "p", "line", true_p_from, 1.0, line_idx, side="from")
            pp.create_measurement(estimator.net, "q", "line", true_q_from, 1.0, line_idx, side="from")
    
    elif scenario == "insufficient":
        print("Creating INSUFFICIENT measurement set")
        # Only a few voltage measurements
        sparse_buses = [0, 4, 8]  # Only 3 buses
        for bus_idx in sparse_buses:
            true_value = estimator.net.res_bus.vm_pu.iloc[bus_idx]
            pp.create_measurement(estimator.net, "v", "bus", true_value, 0.01, bus_idx)
        
        # Very few power measurements
        sparse_lines = [0, 4]  # Only 2 lines
        for line_idx in sparse_lines:
            true_p_from = estimator.net.res_line.p_from_mw.iloc[line_idx]
            pp.create_measurement(estimator.net, "p", "line", true_p_from, 1.0, line_idx, side="from")
    
    elif scenario == "critical_bus":
        print("Creating scenario with CRITICAL BUSES (single measurements)")
        # Each bus has exactly one measurement, creating critical measurements
        for bus_idx in estimator.net.bus.index:
            true_value = estimator.net.res_bus.vm_pu.iloc[bus_idx]
            pp.create_measurement(estimator.net, "v", "bus", true_value, 0.01, bus_idx)
        # No redundant measurements

def test_all_scenarios():
    """Test observability under different measurement scenarios"""
    
    print("POWER SYSTEM OBSERVABILITY TESTING")
    print("="*80)
    
    scenarios = [
        ("full", "Full Redundant Measurements"),
        ("minimal_good", "Minimal but Adequate Measurements"), 
        ("voltage_only", "Voltage Measurements Only"),
        ("power_only", "Power Flow Measurements Only"),
        ("insufficient", "Insufficient Measurements"),
        ("critical_bus", "Critical Bus Scenario")
    ]
    
    results_summary = []
    
    for scenario_id, scenario_name in scenarios:
        print(f"\n{'='*80}")
        print(f"SCENARIO: {scenario_name.upper()}")
        print("="*80)
        
        # Create fresh estimator for each test
        estimator = GridStateEstimator()
        estimator.create_ieee9_grid()
        
        # Create custom measurement set
        create_custom_measurements(estimator, scenario_id)
        
        print(f"Created {len(estimator.net.measurement)} measurements")
        
        # Test observability
        obs_results = estimator.test_observability()
        
        # Try to run state estimation to see if it works
        print(f"\nState Estimation Test:")
        try:
            estimator.run_state_estimation()
            if estimator.estimation_results:
                se_status = "✅ SUCCESS"
            else:
                se_status = "❌ FAILED"
        except Exception as e:
            se_status = f"❌ ERROR: {str(e)[:50]}..."
        
        print(f"  State Estimation Status: {se_status}")
        
        results_summary.append({
            'scenario': scenario_name,
            'measurements': len(estimator.net.measurement),
            'redundancy': obs_results['redundancy'],
            'status': obs_results['status'],
            'se_status': se_status
        })
    
    # Summary table
    print(f"\n{'='*80}")
    print("OBSERVABILITY TEST SUMMARY")
    print("="*80)
    
    print(f"{'Scenario':<30} {'Meas':<6} {'Redun':<8} {'Observability':<20} {'State Est.':<15}")
    print("-" * 80)
    
    for result in results_summary:
        se_short = "✅ OK" if result['se_status'].startswith("✅") else "❌ FAIL"
        print(f"{result['scenario']:<30} {result['measurements']:<6} {result['redundancy']:<8.2f} {result['status']:<20} {se_short:<15}")
    
    print("\nKey Observations:")
    print("• Redundancy = Measurements / State Variables")
    print("• Redundancy > 1.0 generally indicates good observability")  
    print("• State estimation success confirms practical observability")
    print("• Critical measurements create single points of failure")

def test_measurement_loss():
    """Test what happens when measurements are lost"""
    
    print(f"\n{'='*80}")
    print("MEASUREMENT LOSS IMPACT ANALYSIS")
    print("="*80)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    
    # Start with full measurement set
    estimator.simulate_measurements(noise_level=0.0)
    initial_count = len(estimator.net.measurement)
    
    print(f"Starting with {initial_count} measurements")
    
    # Test removal of different percentages
    removal_percentages = [10, 25, 50, 75, 90]
    
    print(f"\n{'Removed %':<10} {'Remaining':<12} {'Redundancy':<12} {'Observability':<20}")
    print("-" * 60)
    
    for remove_pct in removal_percentages:
        # Create copy of estimator
        test_estimator = GridStateEstimator()
        test_estimator.create_ieee9_grid()
        test_estimator.simulate_measurements(noise_level=0.0)
        
        # Remove random measurements
        n_remove = int(initial_count * remove_pct / 100)
        measurement_indices = test_estimator.net.measurement.index.tolist()
        remove_indices = np.random.choice(measurement_indices, n_remove, replace=False)
        test_estimator.net.measurement = test_estimator.net.measurement.drop(remove_indices)
        
        remaining = len(test_estimator.net.measurement)
        
        # Test observability
        try:
            obs_results = test_estimator.test_observability()
            redundancy = obs_results['redundancy']
            status = obs_results['status'].split()[1] if len(obs_results['status'].split()) > 1 else "UNKNOWN"
        except:
            redundancy = 0.0
            status = "ERROR"
        
        print(f"{remove_pct}%{'':<7} {remaining:<12} {redundancy:<12.2f} {status:<20}")

if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Run all observability tests
    test_all_scenarios()
    
    # Test measurement loss
    test_measurement_loss()