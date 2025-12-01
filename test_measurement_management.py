#!/usr/bin/env python3
"""
Test script for measurement management functionality
"""

import sys
import numpy as np
from grid_state_estimator import GridStateEstimator

def test_measurement_management():
    """Test the measurement management functionality"""
    print("Testing measurement management functionality...")
    print("=" * 60)
    
    try:
        # Create estimator and grid
        estimator = GridStateEstimator()
        estimator.create_ieee9_grid()
        print("✅ IEEE 9-bus grid created")
        
        # Set seed for reproducible results
        np.random.seed(42)
        estimator.simulate_measurements(noise_level=0.02)
        print("✅ Measurements generated")
        
        # Test measurement info extraction
        print("\n1. Testing measurement info extraction...")
        measurement_info = estimator.get_measurement_info()
        
        if measurement_info:
            print(f"✅ Successfully extracted {len(measurement_info)} measurements")
            
            # Show sample measurements
            print("\nSample measurements:")
            print("-" * 70)
            print(f"{'Type':<6} {'Element':<8} {'Description':<25} {'Value':<10} {'StdDev':<8}")
            print("-" * 70)
            
            for i, meas in enumerate(measurement_info[:8]):  # Show first 8
                print(f"{meas['type']:<6} {meas['element']:<8} {meas['element_description'][:24]:<25} "
                      f"{meas['value']:<10.4f} {meas['std_dev']:<8.4f}")
        
        # Test backup functionality
        print("\n2. Testing backup functionality...")
        backup_success = estimator.backup_measurements()
        print(f"✅ Backup successful: {backup_success}")
        
        # Test removal functionality
        print("\n3. Testing measurement removal...")
        original_count = len(estimator.net.measurement) if hasattr(estimator.net, 'measurement') and estimator.net.measurement is not None else 0
        print(f"Original measurement count: {original_count}")
        
        # Remove some measurements by indices
        if original_count > 5:
            removal_indices = [0, 2, 4]  # Remove first, third, and fifth measurements
            removed_count = estimator.remove_measurements(removal_indices)
            
            new_count = len(estimator.net.measurement) if hasattr(estimator.net, 'measurement') and estimator.net.measurement is not None else 0
            print(f"✅ Removed {removed_count} measurements, remaining: {new_count}")
        
        # Test removal by type
        print("\n4. Testing removal by type...")
        if estimator.net.measurement is not None and len(estimator.net.measurement) > 0:
            v_measurements = estimator.net.measurement[estimator.net.measurement.measurement_type == 'v']
            if len(v_measurements) > 2:
                v_removed = estimator.remove_measurements_by_type('v', element_filter=[0, 1])
                print(f"✅ Removed {v_removed} voltage measurements from buses 0 and 1")
        
        # Test failure simulation
        print("\n5. Testing failure simulation...")
        if estimator.net.measurement is not None and len(estimator.net.measurement) > 0:
            pre_failure_count = len(estimator.net.measurement)
            failed_count = estimator.simulate_measurement_failures(failure_rate=0.2, 
                                                                 failure_types=['random'])
            post_failure_count = len(estimator.net.measurement)
            print(f"✅ Simulated {failed_count} measurement failures")
            print(f"   Measurements before: {pre_failure_count}, after: {post_failure_count}")
        
        # Test restore functionality
        print("\n6. Testing restore functionality...")
        restore_success = estimator.restore_measurements()
        restored_count = len(estimator.net.measurement) if hasattr(estimator.net, 'measurement') and estimator.net.measurement is not None else 0
        print(f"✅ Restore successful: {restore_success}")
        print(f"   Restored measurement count: {restored_count}")
        
        # Final measurement info
        print("\n7. Final measurement check...")
        final_info = estimator.get_measurement_info()
        if final_info:
            print(f"✅ Final measurement count: {len(final_info)}")
            
            # Count by type
            type_counts = {}
            for meas in final_info:
                meas_type = meas['type']
                type_counts[meas_type] = type_counts.get(meas_type, 0) + 1
            
            print("Measurement breakdown by type:")
            for mtype, count in sorted(type_counts.items()):
                print(f"   {mtype}: {count}")
        
        print("\n" + "=" * 60)
        print("✅ All measurement management tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_measurement_management()
    sys.exit(0 if success else 1)