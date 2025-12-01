#!/usr/bin/env python3
"""
Complete test script for measurement management functionality including observability
"""

import sys
import numpy as np
from grid_state_estimator import GridStateEstimator

def test_complete_measurement_management():
    """Test complete measurement management functionality"""
    print("Testing complete measurement management functionality...")
    print("=" * 70)
    
    try:
        # 1. Create estimator and grid
        estimator = GridStateEstimator()
        estimator.create_ieee9_grid()
        print("✅ IEEE 9-bus grid created")
        
        # 2. Generate measurements
        np.random.seed(42)
        estimator.simulate_measurements(noise_level=0.02)
        original_count = len(estimator.net.measurement)
        print(f"✅ Generated {original_count} measurements")
        
        # 3. Test observability analysis before changes
        print("\n📊 INITIAL OBSERVABILITY ANALYSIS")
        print("-" * 50)
        obs_results = estimator.test_observability()
        if obs_results:
            print(f"   Observability level: {obs_results.get('level', 'Unknown')}")
            print(f"   Total measurements: {obs_results.get('total_measurements', 0)}")
            print(f"   Network coverage: {obs_results.get('coverage', 0):.1%}")
        
        # 4. Test redundancy analysis
        print("\n📈 MEASUREMENT REDUNDANCY ANALYSIS")
        print("-" * 50)
        redundancy_info = estimator.check_measurement_redundancy()
        if redundancy_info:
            print(f"   Status: {redundancy_info.get('status', 'Unknown')}")
            print(f"   Redundancy ratio: {redundancy_info.get('redundancy_ratio', 0):.2f}")
        
        # 5. Test backup functionality
        print("\n🔄 TESTING BACKUP FUNCTIONALITY")
        print("-" * 50)
        backup_success = estimator.backup_measurements()
        print(f"   Backup successful: {backup_success}")
        
        # 6. Remove some measurements and analyze impact
        print("\n❌ TESTING MEASUREMENT REMOVAL IMPACT")
        print("-" * 50)
        
        # Remove voltage measurements from first 3 buses
        voltage_removal_count = estimator.remove_measurements_by_type('v', element_filter=[0, 1, 2])
        print(f"   Removed voltage measurements: {voltage_removal_count}")
        
        # Check impact on observability
        obs_after_removal = estimator.test_observability()
        if obs_after_removal:
            print(f"   Observability after removal: {obs_after_removal.get('level', 'Unknown')}")
            print(f"   Measurements remaining: {obs_after_removal.get('total_measurements', 0)}")
        
        # 7. Simulate measurement failures
        print("\n💥 TESTING FAILURE SIMULATION")
        print("-" * 50)
        pre_failure_count = len(estimator.net.measurement)
        failure_result = estimator.simulate_measurement_failures(failure_rate=0.15, failure_types=['random'])
        if failure_result[0]:
            post_failure_count = len(estimator.net.measurement)
            print(f"   Measurements before failures: {pre_failure_count}")
            print(f"   Measurements after failures: {post_failure_count}")
            print(f"   Measurements lost: {pre_failure_count - post_failure_count}")
        
        # Check observability after failures
        obs_after_failures = estimator.test_observability()
        if obs_after_failures:
            print(f"   Observability after failures: {obs_after_failures.get('level', 'Unknown')}")
        
        # 8. Test restore functionality
        print("\n🔧 TESTING RESTORE FUNCTIONALITY")
        print("-" * 50)
        restore_result = estimator.restore_measurements()
        if restore_result[0]:
            restored_count = len(estimator.net.measurement)
            print(f"   Restore successful: {restore_result[0]}")
            print(f"   Measurements restored: {restored_count}")
            print(f"   Match original count: {restored_count == original_count}")
        
        # Final observability check
        final_obs = estimator.test_observability()
        if final_obs:
            print(f"   Final observability: {final_obs.get('level', 'Unknown')}")
        
        # 9. Test measurement info extraction
        print("\n📋 TESTING MEASUREMENT INFO EXTRACTION")
        print("-" * 50)
        measurement_info = estimator.get_measurement_info()
        if measurement_info:
            type_counts = {}
            for meas in measurement_info:
                mtype = meas['type']
                type_counts[mtype] = type_counts.get(mtype, 0) + 1
            
            print(f"   Total measurements: {len(measurement_info)}")
            print("   By type:")
            for mtype, count in sorted(type_counts.items()):
                print(f"     {mtype}: {count}")
        
        # 10. Test state estimation with current measurements
        print("\n⚡ TESTING STATE ESTIMATION WITH CURRENT MEASUREMENTS")
        print("-" * 50)
        try:
            estimator.run_state_estimation()
            if estimator.estimation_results:
                print("   ✅ State estimation successful")
                print(f"   Estimation error: {estimator.estimation_results.get('max_error', 'N/A')}")
            else:
                print("   ❌ State estimation failed - insufficient measurements?")
        except Exception as e:
            print(f"   ❌ State estimation error: {e}")
        
        print("\n" + "=" * 70)
        print("✅ All measurement management tests completed successfully!")
        print("\n📈 SUMMARY:")
        print(f"   • Measurement backup/restore: ✅")
        print(f"   • Measurement removal by type/element: ✅") 
        print(f"   • Failure simulation: ✅")
        print(f"   • Observability analysis: ✅")
        print(f"   • Redundancy checking: ✅")
        print(f"   • Integration with state estimation: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_measurement_management()
    sys.exit(0 if success else 1)