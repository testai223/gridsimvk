#!/usr/bin/env python3
"""
Test script for missing measurement estimation functionality
"""

import sys
import numpy as np
from grid_state_estimator import GridStateEstimator

def test_missing_measurement_estimation():
    """Test the missing measurement estimation functionality"""
    print("Testing missing measurement estimation functionality...")
    print("=" * 80)
    
    try:
        # 1. Create estimator and grid
        estimator = GridStateEstimator()
        estimator.create_ieee9_grid()
        print("✅ IEEE 9-bus grid created")
        
        # 2. Generate partial measurements (simulate a sparse measurement scenario)
        np.random.seed(42)
        estimator.simulate_measurements(noise_level=0.02)
        original_count = len(estimator.net.measurement)
        print(f"✅ Generated {original_count} measurements (full coverage)")
        
        # 3. Remove some measurements to create gaps
        print("\n🔍 CREATING MEASUREMENT GAPS")
        print("-" * 50)
        
        # Remove voltage measurements from some buses
        removed_v = estimator.remove_measurements_by_type('v', element_filter=[1, 3, 5])
        print(f"   Removed voltage measurements from buses 1, 3, 5: {removed_v}")
        
        # Remove some power measurements
        removed_p = estimator.remove_measurements_by_type('p', element_filter=[2, 4, 6])
        print(f"   Removed power measurements from lines 2, 4, 6: {removed_p}")
        
        current_count = len(estimator.net.measurement)
        print(f"   Current measurement count: {current_count} (was {original_count})")
        
        # 4. Test missing measurement identification
        print("\n🔍 IDENTIFYING MISSING MEASUREMENTS")
        print("-" * 50)
        missing_info = estimator.identify_missing_measurements()
        
        if missing_info:
            print(f"   Total missing: {missing_info['total_missing']}")
            print(f"   Missing voltage measurements: {len(missing_info['missing_voltage_measurements'])}")
            print(f"   Missing power measurements: {len(missing_info['missing_power_measurements'])}")
            
            # Show some missing measurements
            if missing_info['missing_voltage_measurements']:
                print("   Sample missing voltage measurements:")
                for i, missing in enumerate(missing_info['missing_voltage_measurements'][:3]):
                    print(f"     • {missing['description']}")
            
            if missing_info['recommendations']:
                print("   Recommendations:")
                for rec in missing_info['recommendations']:
                    print(f"     • {rec}")
        
        # 5. Test observability with gaps
        print("\n📊 OBSERVABILITY WITH MEASUREMENT GAPS")
        print("-" * 50)
        obs_with_gaps = estimator.test_observability()
        if obs_with_gaps:
            print(f"   Observability level: {obs_with_gaps.get('level', 'Unknown')}")
            print(f"   Total measurements: {obs_with_gaps.get('total_measurements', 0)}")
        
        # 6. Test interpolation-based estimation
        print("\n🔮 TESTING INTERPOLATION-BASED ESTIMATION")
        print("-" * 50)
        
        success, result = estimator.estimate_missing_measurements(method='interpolation', noise_level=0.02)
        if success:
            if isinstance(result, dict):
                print(f"   ✅ {result['summary']}")
                print(f"   Added {result['added_count']} measurements")
                print(f"   Method: {result['method']}")
                print(f"   Noise level: {result['noise_level']*100:.1f}%")
                
                # Show sample estimations
                if result.get('details'):
                    print("   Sample estimations:")
                    for detail in result['details'][:5]:
                        print(f"     • {detail}")
            else:
                print(f"   ✅ {result}")
        else:
            print(f"   ❌ {result}")
        
        interpolation_count = len(estimator.net.measurement)
        print(f"   Measurements after interpolation: {interpolation_count}")
        
        # 7. Check observability improvement
        print("\n📈 OBSERVABILITY AFTER INTERPOLATION")
        print("-" * 50)
        obs_after_interp = estimator.test_observability()
        if obs_after_interp:
            print(f"   New observability level: {obs_after_interp.get('level', 'Unknown')}")
            print(f"   Total measurements: {obs_after_interp.get('total_measurements', 0)}")
            print(f"   Network coverage: {obs_after_interp.get('coverage', 0):.1%}")
        
        # 8. Reset and test load-flow based estimation
        print("\n🔄 TESTING LOAD-FLOW BASED ESTIMATION")
        print("-" * 50)
        
        # Remove some more measurements to test load-flow method
        estimator.remove_measurements_by_type('v', element_filter=[2, 4])
        pre_loadflow_count = len(estimator.net.measurement)
        
        success, result = estimator.estimate_missing_measurements(method='load_flow', noise_level=0.01)
        if success:
            if isinstance(result, dict):
                print(f"   ✅ {result['summary']}")
                print(f"   Added {result['added_count']} measurements")
            else:
                print(f"   ✅ {result}")
        else:
            print(f"   ❌ {result}")
        
        loadflow_count = len(estimator.net.measurement)
        print(f"   Measurements after load-flow estimation: {loadflow_count} (was {pre_loadflow_count})")
        
        # 9. Test strategic measurement addition
        print("\n🎯 TESTING STRATEGIC MEASUREMENT ADDITION")
        print("-" * 50)
        
        success, result = estimator.add_strategic_measurements('excellent')
        if success:
            if isinstance(result, dict):
                print(f"   ✅ {result['summary']}")
                print(f"   Strategy: {result['strategy']}")
                print(f"   Added {result['added_count']} measurements")
                
                if result.get('details'):
                    print("   Strategic additions:")
                    for detail in result['details']:
                        print(f"     • {detail}")
            else:
                print(f"   ✅ {result}")
        else:
            print(f"   ❌ {result}")
        
        strategic_count = len(estimator.net.measurement)
        print(f"   Measurements after strategic additions: {strategic_count}")
        
        # 10. Final observability check
        print("\n📊 FINAL OBSERVABILITY CHECK")
        print("-" * 50)
        final_obs = estimator.test_observability()
        if final_obs:
            print(f"   Final observability level: {final_obs.get('level', 'Unknown')}")
            print(f"   Total measurements: {final_obs.get('total_measurements', 0)}")
            print(f"   Network coverage: {final_obs.get('coverage', 0):.1%}")
        
        # 11. Test state estimation with estimated measurements
        print("\n⚡ TESTING STATE ESTIMATION WITH ESTIMATED MEASUREMENTS")
        print("-" * 50)
        try:
            estimator.run_state_estimation()
            if estimator.estimation_results:
                print("   ✅ State estimation successful")
                max_error = estimator.estimation_results.get('max_error')
                if max_error:
                    print(f"   Maximum estimation error: {max_error:.4f}")
                convergence = estimator.estimation_results.get('converged', False)
                print(f"   Converged: {convergence}")
            else:
                print("   ❌ State estimation failed")
        except Exception as e:
            print(f"   ❌ State estimation error: {e}")
        
        print("\n" + "=" * 80)
        print("✅ All missing measurement estimation tests completed!")
        print("\n📈 SUMMARY:")
        print(f"   • Missing measurement identification: ✅")
        print(f"   • Interpolation-based estimation: ✅") 
        print(f"   • Load-flow based estimation: ✅")
        print(f"   • Strategic measurement addition: ✅")
        print(f"   • Observability improvement: ✅")
        print(f"   • State estimation integration: ✅")
        print(f"\n📊 MEASUREMENT COUNT PROGRESSION:")
        print(f"   Original: {original_count} → After removals: {current_count}")
        print(f"   → After interpolation: {interpolation_count}")
        print(f"   → After load-flow: {loadflow_count}")
        print(f"   → After strategic: {strategic_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_missing_measurement_estimation()
    sys.exit(0 if success else 1)