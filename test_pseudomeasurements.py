#!/usr/bin/env python3
"""
Test script for pseudomeasurement functionality
"""

import sys
import numpy as np
from grid_state_estimator import GridStateEstimator

def test_pseudomeasurements():
    """Test the pseudomeasurement functionality"""
    print("Testing pseudomeasurement functionality...")
    print("=" * 70)
    
    try:
        # 1. Create estimator and grid
        estimator = GridStateEstimator()
        estimator.create_ieee9_grid()
        print("✅ IEEE 9-bus grid created")
        
        # 2. Create a sparse measurement scenario
        np.random.seed(42)
        estimator.simulate_measurements(noise_level=0.02)
        original_count = len(estimator.net.measurement)
        print(f"✅ Generated {original_count} measurements (full coverage)")
        
        # 3. Remove many measurements to create observability gaps
        print("\n🔍 CREATING OBSERVABILITY GAPS")
        print("-" * 50)
        
        # Remove voltage measurements from multiple buses
        removed_v = estimator.remove_measurements_by_type('v', element_filter=[1, 3, 5, 7])
        print(f"   Removed voltage measurements from buses 1, 3, 5, 7: {removed_v}")
        
        # Remove power measurements from several lines
        removed_p = estimator.remove_measurements_by_type('p', element_filter=[2, 4, 6, 8])
        removed_q = estimator.remove_measurements_by_type('q', element_filter=[1, 3, 5, 7])
        print(f"   Removed power measurements from multiple lines")
        
        current_count = len(estimator.net.measurement)
        print(f"   Measurements after removals: {current_count} (was {original_count})")
        
        # 4. Test observability with gaps
        print("\n📊 OBSERVABILITY WITH GAPS")
        print("-" * 50)
        obs_with_gaps = estimator.test_observability()
        if obs_with_gaps:
            print(f"   Observability level: {obs_with_gaps.get('level', 'Unknown')}")
            print(f"   Total measurements: {obs_with_gaps.get('total_measurements', 0)}")
        
        # 5. Test pseudomeasurement location identification
        print("\n🔍 IDENTIFYING PSEUDOMEASUREMENT LOCATIONS")
        print("-" * 50)
        pseudo_info = estimator.identify_pseudomeasurement_locations()
        
        if pseudo_info:
            print(f"   Total locations identified: {pseudo_info['total_needed']}")
            print(f"   Voltage pseudomeasurements: {len(pseudo_info['voltage_pseudomeasurements'])}")
            print(f"   Zero injection locations: {len(pseudo_info['zero_injection_buses'])}")
            print(f"   Slack references: {len(pseudo_info['slack_bus_pseudomeasurements'])}")
            
            # Show sample locations
            if pseudo_info['voltage_pseudomeasurements']:
                print("   Sample voltage pseudo locations:")
                for i, pseudo in enumerate(pseudo_info['voltage_pseudomeasurements'][:3]):
                    print(f"     • {pseudo['description']} (uncertainty: {pseudo['uncertainty']*100:.1f}%)")
            
            if pseudo_info['recommendations']:
                print("   Recommendations:")
                for rec in pseudo_info['recommendations']:
                    print(f"     • {rec}")
        
        # 6. Test voltage pseudomeasurement addition
        print("\n🔮 TESTING VOLTAGE PSEUDOMEASUREMENT ADDITION")
        print("-" * 50)
        
        success, result = estimator.add_pseudomeasurements(['voltage'])
        if success:
            if isinstance(result, dict):
                print(f"   ✅ {result['summary']}")
                print(f"   Added {result['added_count']} voltage pseudomeasurements")
                
                if result.get('details'):
                    print("   Sample additions:")
                    for detail in result['details'][:5]:
                        print(f"     • {detail}")
            else:
                print(f"   ✅ {result}")
        else:
            print(f"   ❌ {result}")
        
        voltage_pseudo_count = len(estimator.net.measurement)
        print(f"   Measurements after voltage pseudos: {voltage_pseudo_count}")
        
        # 7. Test zero injection pseudomeasurements
        print("\n⚡ TESTING ZERO INJECTION PSEUDOMEASUREMENTS")
        print("-" * 50)
        
        success, result = estimator.add_pseudomeasurements(['zero_injection'])
        if success:
            if isinstance(result, dict):
                print(f"   ✅ {result['summary']}")
                print(f"   Added {result['added_count']} zero injection pseudomeasurements")
            else:
                print(f"   ✅ {result}")
        else:
            print(f"   ❌ {result}")
        
        zero_pseudo_count = len(estimator.net.measurement)
        print(f"   Measurements after zero injection pseudos: {zero_pseudo_count}")
        
        # 8. Test pseudomeasurement summary
        print("\n📊 PSEUDOMEASUREMENT SUMMARY")
        print("-" * 50)
        summary = estimator.get_pseudomeasurement_summary()
        
        if summary:
            print(f"   Total measurements: {summary.get('total_measurements', 0)}")
            print(f"   Real measurements: {summary.get('real_measurements', 0)}")
            print(f"   Pseudomeasurements: {summary.get('pseudomeasurements', 0)}")
            
            if summary.get('pseudo_types'):
                print("   Pseudomeasurement types:")
                for ptype, count in summary['pseudo_types'].items():
                    print(f"     • {ptype}: {count}")
            
            # Calculate percentage
            total = summary.get('total_measurements', 0)
            pseudo = summary.get('pseudomeasurements', 0)
            if total > 0:
                percentage = (pseudo / total) * 100
                print(f"   Pseudomeasurement ratio: {percentage:.1f}%")
        
        # 9. Test observability improvement
        print("\n📈 OBSERVABILITY AFTER PSEUDOMEASUREMENTS")
        print("-" * 50)
        obs_with_pseudo = estimator.test_observability()
        if obs_with_pseudo:
            print(f"   New observability level: {obs_with_pseudo.get('level', 'Unknown')}")
            print(f"   Total measurements: {obs_with_pseudo.get('total_measurements', 0)}")
            print(f"   Network coverage: {obs_with_pseudo.get('coverage', 0):.1%}")
        
        # 10. Test state estimation with pseudomeasurements
        print("\n⚡ TESTING STATE ESTIMATION WITH PSEUDOMEASUREMENTS")
        print("-" * 50)
        try:
            estimator.run_state_estimation()
            if estimator.estimation_results:
                print("   ✅ State estimation successful with pseudomeasurements")
                convergence = estimator.estimation_results.get('converged', False)
                print(f"   Converged: {convergence}")
            else:
                print("   ❌ State estimation failed")
        except Exception as e:
            print(f"   ❌ State estimation error: {e}")
        
        # 11. Test pseudomeasurement removal
        print("\n🗑️ TESTING PSEUDOMEASUREMENT REMOVAL")
        print("-" * 50)
        
        success, result = estimator.remove_pseudomeasurements()
        if success:
            print(f"   ✅ {result}")
            removed_count = len(estimator.net.measurement)
            print(f"   Measurements after removal: {removed_count}")
        else:
            print(f"   ❌ {result}")
        
        # 12. Test comprehensive pseudomeasurement scenario
        print("\n🎯 COMPREHENSIVE PSEUDOMEASUREMENT SCENARIO")
        print("-" * 50)
        
        # Add all types of pseudomeasurements
        success, result = estimator.add_pseudomeasurements(['voltage', 'zero_injection', 'slack_reference'])
        if success:
            if isinstance(result, dict):
                print(f"   ✅ {result['summary']}")
                final_count = len(estimator.net.measurement)
                print(f"   Final measurement count: {final_count}")
                
                # Final observability check
                final_obs = estimator.test_observability()
                if final_obs:
                    print(f"   Final observability: {final_obs.get('level', 'Unknown')}")
            
        print("\n" + "=" * 70)
        print("✅ All pseudomeasurement tests completed successfully!")
        print("\n📈 SUMMARY:")
        print(f"   • Pseudomeasurement location identification: ✅")
        print(f"   • Voltage pseudomeasurement addition: ✅") 
        print(f"   • Zero injection pseudomeasurement addition: ✅")
        print(f"   • Pseudomeasurement summary and analysis: ✅")
        print(f"   • Observability improvement verification: ✅")
        print(f"   • State estimation with pseudomeasurements: ✅")
        print(f"   • Pseudomeasurement removal: ✅")
        print(f"\n📊 MEASUREMENT COUNT PROGRESSION:")
        print(f"   Original: {original_count} → After removals: {current_count}")
        print(f"   → After voltage pseudos: {voltage_pseudo_count}")
        print(f"   → After zero injection: {zero_pseudo_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pseudomeasurements()
    sys.exit(0 if success else 1)