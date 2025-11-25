#!/usr/bin/env python3
"""
Simple demonstration of bad data detection functionality
Shows how to detect and handle bad measurements
"""

from grid_state_estimator import GridStateEstimator
import numpy as np

def main():
    print("🔍 BAD DATA DETECTION DEMO")
    print("="*40)
    print("This demo shows how to detect bad measurements")
    print("="*40)
    
    # Set random seed for reproducible results
    np.random.seed(123)
    
    # 1. Create grid and measurements
    print("\n1️⃣ Setup")
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.02)
    print(f"✅ Created grid with {len(estimator.net.measurement)} measurements")
    
    # 2. Test on clean data
    print("\n2️⃣ Testing on clean measurements")
    print("Running bad data detection on clean data...")
    
    # Save original input function
    import builtins
    original_input = builtins.input
    builtins.input = lambda prompt: 'y'  # Auto-answer 'yes' to restore measurements
    
    try:
        results_clean = estimator.detect_bad_data(confidence_level=0.95, max_iterations=3)
        if results_clean and results_clean.get('final_status') == 'clean':
            print("✅ Correctly identified clean data - no bad measurements found")
        else:
            print("⚠️  Unexpected result on clean data")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        builtins.input = original_input  # Restore original input function
    
    # 3. Create bad data scenario
    print("\n3️⃣ Creating bad data scenario")
    print("Injecting bad measurements...")
    
    # Manually create a few bad measurements for clear demonstration
    voltage_meas = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'v']
    if len(voltage_meas) > 0:
        # Corrupt first voltage measurement
        bad_idx = voltage_meas.index[0]
        original_value = estimator.net.measurement.loc[bad_idx, 'value']
        bad_value = original_value * 2.0  # Double the voltage (clearly bad)
        
        estimator.net.measurement.loc[bad_idx, 'value'] = bad_value
        
        print(f"Corrupted voltage measurement at index {bad_idx}:")
        print(f"  Original: {original_value:.4f} p.u.")
        print(f"  Corrupted: {bad_value:.4f} p.u.")
        print(f"  Error: {((bad_value - original_value) / original_value * 100):+.1f}%")
    
    # Corrupt a power measurement too
    power_meas = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'p']
    if len(power_meas) > 0:
        bad_idx2 = power_meas.index[0]
        original_value2 = estimator.net.measurement.loc[bad_idx2, 'value']
        bad_value2 = original_value2 * 3.0  # Triple the power
        
        estimator.net.measurement.loc[bad_idx2, 'value'] = bad_value2
        
        print(f"Corrupted power measurement at index {bad_idx2}:")
        print(f"  Original: {original_value2:.4f} MW")
        print(f"  Corrupted: {bad_value2:.4f} MW")
        print(f"  Error: {((bad_value2 - original_value2) / original_value2 * 100):+.1f}%")
    
    # 4. Run bad data detection
    print("\n4️⃣ Running bad data detection")
    print("Analyzing measurements for bad data...")
    
    builtins.input = lambda prompt: 'y'  # Auto-answer 'yes' to restore measurements
    
    try:
        results_bad = estimator.detect_bad_data(confidence_level=0.95, max_iterations=5)
        
        if results_bad and results_bad.get('bad_measurements'):
            detected_bad = results_bad['bad_measurements']
            print(f"\n🚨 DETECTED {len(detected_bad)} BAD MEASUREMENTS:")
            
            for i, bad_meas in enumerate(detected_bad, 1):
                meas_type = bad_meas['measurement_type'].upper()
                element = bad_meas['element']
                norm_residual = bad_meas['normalized_residual']
                
                print(f"   {i}. {meas_type} measurement at element {element}")
                print(f"      Normalized residual: {norm_residual:.3f}")
                
                # Classify severity
                if norm_residual > 5:
                    severity = "🚨 SEVERE"
                elif norm_residual > 3:
                    severity = "⚠️  MODERATE"
                else:
                    severity = "ℹ️  MILD"
                print(f"      Severity: {severity}")
            
            print(f"\n✅ Bad data detection successful!")
            print(f"Final status: {results_bad.get('final_status')}")
        else:
            print("❌ No bad measurements detected (unexpected)")
            
    except Exception as e:
        print(f"❌ Error in bad data detection: {e}")
    finally:
        builtins.input = original_input
    
    # 5. Summary
    print("\n5️⃣ Summary")
    print("Bad data detection features:")
    print("• ✅ Chi-square test for global bad data presence")
    print("• ✅ Largest normalized residual test")
    print("• ✅ Statistical outlier detection")
    print("• ✅ Iterative bad measurement removal")
    print("• ✅ Automatic measurement restoration")
    
    print("\n💡 Usage in your code:")
    print("```python")
    print("estimator = GridStateEstimator()")
    print("estimator.create_ieee9_grid()")
    print("estimator.simulate_measurements()")
    print("")
    print("# Create bad data for testing")
    print("estimator.create_bad_data_scenario('mixed')")
    print("")
    print("# Detect bad measurements")
    print("results = estimator.detect_bad_data(confidence_level=0.95)")
    print("```")
    
    print(f"\n🎯 Demo completed!")

if __name__ == "__main__":
    main()