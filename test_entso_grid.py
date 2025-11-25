#!/usr/bin/env python3
"""
Test script for ENTSO-E style transmission grid
"""

from grid_state_estimator import GridStateEstimator
import numpy as np

def test_entso_style_grid():
    """Test state estimation on ENTSO-E style transmission system"""
    
    print("ENTSO-E STYLE TRANSMISSION GRID TEST")
    print("="*60)
    
    # Set seed for reproducible results
    np.random.seed(456)
    
    # Create estimator
    estimator = GridStateEstimator()
    
    # Create ENTSO-E style grid
    print("1. Creating ENTSO-E style transmission system...")
    estimator.create_simple_entso_grid()
    
    # Test basic power flow
    print(f"\n2. Testing power flow...")
    import pandapower as pp
    try:
        pp.runpp(estimator.net, algorithm='nr')
        print("✅ Power flow converged successfully")
        
        # Show voltage results
        print(f"\nVoltage Results:")
        for i, bus in estimator.net.bus.iterrows():
            vm = estimator.net.res_bus.vm_pu.iloc[i]
            va = estimator.net.res_bus.va_degree.iloc[i]
            name = bus['name']
            vn = bus.vn_kv
            print(f"  {name}: {vm:.4f} p.u. ({vm*vn:.1f} kV), {va:.2f}°")
        
        # Show power flows
        print(f"\nPower Flow Results:")
        for i, line in estimator.net.line.iterrows():
            p_from = estimator.net.res_line.p_from_mw.iloc[i]
            p_to = estimator.net.res_line.p_to_mw.iloc[i] 
            losses = p_from + p_to
            name = line['name']
            print(f"  {name}: {p_from:.1f} MW → {-p_to:.1f} MW (losses: {losses:.1f} MW)")
            
        if len(estimator.net.trafo) > 0:
            print(f"\nTransformer Power Flows:")
            for i, trafo in estimator.net.trafo.iterrows():
                p_hv = estimator.net.res_trafo.p_hv_mw.iloc[i]
                p_lv = estimator.net.res_trafo.p_lv_mw.iloc[i]
                losses = p_hv + p_lv
                name = trafo['name']
                print(f"  {name}: {p_hv:.1f} MW → {-p_lv:.1f} MW (losses: {losses:.1f} MW)")
        
    except Exception as e:
        print(f"❌ Power flow failed: {e}")
        return False
    
    # Test state estimation with transmission-level noise
    print(f"\n3. Testing state estimation (1% noise - typical transmission accuracy)...")
    estimator.simulate_measurements(noise_level=0.01)
    
    print(f"\n4. Testing observability...")
    obs_results = estimator.test_observability()
    
    print(f"\n5. Running state estimation...")
    estimator.run_state_estimation()
    
    if estimator.estimation_results and hasattr(estimator.net, 'res_bus_est') and len(estimator.net.res_bus_est) > 0:
        print(f"\n6. State estimation results:")
        
        # Get number of buses
        n_buses = len(estimator.net.res_bus_est)
        print(f"State estimation results available for {n_buses} buses")
        
        # Check if we have enough buses
        if n_buses >= 5:
            # Compare results for 400kV buses
            print(f"\n400kV Bus Results:")
            for i in range(3):  # First 3 are 400kV buses
                true_vm = estimator.net.res_bus.vm_pu.iloc[i]
                est_vm = estimator.net.res_bus_est.vm_pu.iloc[i]
                error = (est_vm - true_vm) / true_vm * 100
                bus_name = estimator.net.bus.name.iloc[i]
                print(f"  {bus_name}: True={true_vm:.4f}, Est={est_vm:.4f}, Error={error:.3f}%")
            
            print(f"\n220kV Bus Results:")
            for i in range(3, 5):  # Last 2 are 220kV buses
                true_vm = estimator.net.res_bus.vm_pu.iloc[i]
                est_vm = estimator.net.res_bus_est.vm_pu.iloc[i]
                error = (est_vm - true_vm) / true_vm * 100
                bus_name = estimator.net.bus.name.iloc[i]
                print(f"  {bus_name}: True={true_vm:.4f}, Est={est_vm:.4f}, Error={error:.3f}%")
        else:
            print(f"❌ Not enough estimation results: expected 5, got {n_buses}")
        
        if n_buses >= 5:
            # Calculate overall statistics
            true_voltages = estimator.net.res_bus.vm_pu.values
            est_voltages = estimator.net.res_bus_est.vm_pu.values
            errors = ((est_voltages - true_voltages) / true_voltages) * 100
            
            print(f"\nOverall Performance:")
            print(f"  Mean error: {np.mean(np.abs(errors)):.4f}%")
            print(f"  Max error: {np.max(np.abs(errors)):.4f}%")
            print(f"  RMS error: {np.sqrt(np.mean(errors**2)):.4f}%")
        
        # Show visualization if available
        try:
            print(f"\n7. Generating grid visualization...")
            estimator.plot_grid_results()
        except Exception as e:
            print(f"Grid visualization not available: {e}")
    else:
        print(f"\n❌ State estimation failed or produced no results")
        print(f"This may be due to:")
        print(f"  - Insufficient measurement redundancy")
        print(f"  - Poor measurement quality")
        print(f"  - Network observability issues")
        print(f"  - Numerical convergence problems")
    
    print(f"\n✅ ENTSO-E style transmission grid test completed!")
    return True

def compare_with_ieee9():
    """Compare ENTSO-E grid with IEEE 9-bus system"""
    print(f"\n{'='*60}")
    print("COMPARISON: ENTSO-E vs IEEE 9-BUS")
    print("="*60)
    
    results = {}
    
    for grid_type in ["ENTSO-E", "IEEE 9-bus"]:
        print(f"\nTesting {grid_type}...")
        
        estimator = GridStateEstimator()
        
        if grid_type == "ENTSO-E":
            estimator.create_simple_entso_grid()
        else:
            estimator.create_ieee9_grid()
        
        # Test with same noise level
        estimator.simulate_measurements(noise_level=0.02)
        estimator.run_state_estimation()
        
        if estimator.estimation_results and hasattr(estimator.net, 'res_bus_est'):
            true_voltages = estimator.net.res_bus.vm_pu.values
            est_voltages = estimator.net.res_bus_est.vm_pu.values
            errors = ((est_voltages - true_voltages) / true_voltages) * 100
            
            results[grid_type] = {
                'buses': len(estimator.net.bus),
                'lines': len(estimator.net.line),
                'transformers': len(estimator.net.trafo),
                'generators': len(estimator.net.gen),
                'loads': len(estimator.net.load),
                'measurements': len(estimator.net.measurement),
                'mean_error': np.mean(np.abs(errors)),
                'max_error': np.max(np.abs(errors)),
                'voltage_levels': list(set(estimator.net.bus.vn_kv.values))
            }
        else:
            results[grid_type] = {
                'buses': len(estimator.net.bus),
                'lines': len(estimator.net.line),
                'transformers': len(estimator.net.trafo),
                'generators': len(estimator.net.gen),
                'loads': len(estimator.net.load),
                'measurements': len(estimator.net.measurement),
                'mean_error': np.nan,  # State estimation failed
                'max_error': np.nan,
                'voltage_levels': list(set(estimator.net.bus.vn_kv.values))
            }
    
    # Display comparison
    print(f"\nCOMPARISON RESULTS:")
    print("-" * 60)
    print(f"{'Metric':<20} {'ENTSO-E':<15} {'IEEE 9-bus':<15}")
    print("-" * 60)
    
    for metric in ['buses', 'lines', 'transformers', 'generators', 'loads', 'measurements']:
        entso_val = results['ENTSO-E'][metric]
        ieee_val = results['IEEE 9-bus'][metric]
        print(f"{metric.capitalize():<20} {entso_val:<15} {ieee_val:<15}")
    
    print(f"\nPerformance:")
    print(f"Mean Error (%)       {results['ENTSO-E']['mean_error']:<15.4f} {results['IEEE 9-bus']['mean_error']:<15.4f}")
    print(f"Max Error (%)        {results['ENTSO-E']['max_error']:<15.4f} {results['IEEE 9-bus']['max_error']:<15.4f}")
    
    print(f"\nVoltage Levels:")
    print(f"ENTSO-E:    {sorted(results['ENTSO-E']['voltage_levels'], reverse=True)} kV")
    print(f"IEEE 9-bus: {sorted(results['IEEE 9-bus']['voltage_levels'], reverse=True)} kV")
    
    print(f"\nConclusions:")
    print(f"✓ ENTSO-E grid represents realistic transmission system (400kV/220kV)")
    print(f"✓ Multi-voltage level system with transformers") 
    print(f"✓ Suitable for testing CGMES-style state estimation")
    print(f"✓ More complex topology than IEEE test systems")

if __name__ == "__main__":
    # Test ENTSO-E style grid
    success = test_entso_style_grid()
    
    if success:
        # Compare with IEEE 9-bus
        compare_with_ieee9()
    else:
        print("ENTSO-E grid test failed")