#!/usr/bin/env python3
"""
Test script for bad data detection functionality
Demonstrates comprehensive bad data detection algorithms
"""

from grid_state_estimator import GridStateEstimator
import numpy as np

def test_basic_bad_data_detection():
    """Test basic bad data detection functionality"""
    print("🔍 BAD DATA DETECTION TEST")
    print("="*50)
    
    # Create estimator with IEEE 9-bus system
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    
    # Generate clean measurements
    print("\n1. Generating clean measurements...")
    estimator.simulate_measurements(noise_level=0.01)  # Very low noise
    print(f"Generated {len(estimator.net.measurement)} measurements")
    
    # Run state estimation on clean data
    print("\n2. Running state estimation on clean data...")
    estimator.run_state_estimation()
    
    if estimator.estimation_results:
        print("✅ State estimation successful on clean data")
    else:
        print("❌ State estimation failed on clean data")
        return False
    
    # Test detection on clean data (should find no bad data)
    print("\n3. Testing bad data detection on clean measurements...")
    results = estimator.detect_bad_data(confidence_level=0.95, max_iterations=3, prompt_restore=False)
    
    if results and results.get('final_status') == 'clean':
        print("✅ Correctly identified clean data (no false positives)")
    else:
        print("⚠️  Unexpected result on clean data")
    
    return True

def test_single_bad_measurement():
    """Test detection of single bad measurement"""
    print("\n" + "="*60)
    print("🚨 SINGLE BAD MEASUREMENT TEST")
    print("="*60)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.01)
    
    # Manually introduce a single bad measurement
    print("\n1. Introducing single bad measurement...")
    
    # Find a voltage measurement and corrupt it
    voltage_measurements = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'v']
    if len(voltage_measurements) > 0:
        bad_idx = voltage_measurements.index[0]
        original_value = estimator.net.measurement.loc[bad_idx, 'value']
        bad_value = original_value * 2.5  # 250% of original (gross error)
        
        estimator.net.measurement.loc[bad_idx, 'value'] = bad_value
        
        print(f"Corrupted measurement {bad_idx}:")
        print(f"  Original: {original_value:.6f}")
        print(f"  Corrupted: {bad_value:.6f}")
        print(f"  Error factor: {bad_value/original_value:.2f}x")
        
        # Run bad data detection
        print(f"\n2. Running bad data detection...")
        results = estimator.detect_bad_data(confidence_level=0.95, max_iterations=5, prompt_restore=False)
        
        if results and results.get('bad_measurements'):
            detected_bad = results['bad_measurements']
            print(f"\n✅ Successfully detected {len(detected_bad)} bad measurement(s)")
            for i, bad_meas in enumerate(detected_bad, 1):
                print(f"   {i}. Index {bad_meas['measurement_index']}: {bad_meas['measurement_type'].upper()} measurement")
                print(f"      Normalized residual: {bad_meas['normalized_residual']:.3f}")
                
            # Check if we found the right one
            found_indices = [bm['measurement_index'] for bm in detected_bad]
            if bad_idx in found_indices:
                print(f"🎯 Correctly identified the corrupted measurement!")
            else:
                print(f"⚠️  Did not identify the specific corrupted measurement")
        else:
            print(f"❌ Failed to detect bad measurement")
    else:
        print("❌ No voltage measurements available for corruption")

def test_multiple_bad_measurements():
    """Test detection of multiple bad measurements"""
    print("\n" + "="*60)
    print("🚨 MULTIPLE BAD MEASUREMENTS TEST")
    print("="*60)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.01)
    
    # Use the built-in scenario creator
    print("\n1. Creating multiple bad measurements scenario...")
    bad_measurements = estimator.create_bad_data_scenario("multiple")
    
    if bad_measurements:
        print(f"\n2. Running bad data detection on {len(bad_measurements)} corrupted measurements...")
        results = estimator.detect_bad_data(confidence_level=0.95, max_iterations=10, prompt_restore=False)
        
        if results and results.get('bad_measurements'):
            detected_count = len(results['bad_measurements'])
            injected_count = len(bad_measurements)
            
            print(f"\n📊 DETECTION RESULTS:")
            print(f"   Injected bad measurements: {injected_count}")
            print(f"   Detected bad measurements: {detected_count}")
            
            if detected_count >= injected_count * 0.8:  # Detected at least 80%
                print(f"✅ Good detection rate: {detected_count}/{injected_count}")
            else:
                print(f"⚠️  Low detection rate: {detected_count}/{injected_count}")
        else:
            print(f"❌ No bad measurements detected")
    else:
        print("❌ Failed to create bad measurement scenario")

def test_systematic_bias_detection():
    """Test detection of systematic bias"""
    print("\n" + "="*60)
    print("📈 SYSTEMATIC BIAS DETECTION TEST")
    print("="*60)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.01)
    
    print("\n1. Creating systematic bias scenario...")
    bad_measurements = estimator.create_bad_data_scenario("systematic")
    
    if bad_measurements:
        print(f"\n2. Running bad data detection on systematic bias...")
        results = estimator.detect_bad_data(confidence_level=0.95, max_iterations=8, prompt_restore=False)
        
        if results:
            final_status = results.get('final_status')
            print(f"\n📊 BIAS DETECTION RESULTS:")
            print(f"   Final status: {final_status}")
            
            if final_status in ['systematic_error_suspected', 'clean']:
                print(f"✅ Appropriately handled systematic bias")
            elif results.get('bad_measurements'):
                detected_count = len(results['bad_measurements'])
                print(f"🔍 Detected {detected_count} measurements as individually bad")
                print(f"   (May indicate systematic bias was partially corrected)")
            else:
                print(f"⚠️  Unexpected result for systematic bias")
        else:
            print(f"❌ Detection failed")
    else:
        print("❌ Failed to create systematic bias scenario")

def test_detection_performance():
    """Test detection algorithm performance and accuracy"""
    print("\n" + "="*60)
    print("📊 DETECTION PERFORMANCE TEST")
    print("="*60)
    
    test_scenarios = ['single', 'multiple', 'mixed']
    confidence_levels = [0.90, 0.95, 0.99]
    
    results_summary = {}
    
    for scenario in test_scenarios:
        print(f"\n🧪 Testing scenario: {scenario}")
        results_summary[scenario] = {}
        
        for confidence in confidence_levels:
            print(f"  Confidence level: {confidence*100}%")
            
            try:
                estimator = GridStateEstimator()
                estimator.create_ieee9_grid()
                estimator.simulate_measurements(noise_level=0.01)
                
                # Create bad data scenario
                bad_measurements = estimator.create_bad_data_scenario(scenario)
                injected_count = len(bad_measurements) if bad_measurements else 0
                
                # Run detection
                results = estimator.detect_bad_data(
                    confidence_level=confidence,
                    max_iterations=5,
                    prompt_restore=False,
                )
                
                if results:
                    detected_count = len(results.get('bad_measurements', []))
                    final_status = results.get('final_status')
                    
                    results_summary[scenario][confidence] = {
                        'injected': injected_count,
                        'detected': detected_count,
                        'status': final_status
                    }
                    
                    if injected_count > 0:
                        detection_rate = detected_count / injected_count
                        print(f"    Detection rate: {detection_rate:.2%}")
                    else:
                        print(f"    Status: {final_status}")
                else:
                    results_summary[scenario][confidence] = {
                        'injected': injected_count,
                        'detected': 0,
                        'status': 'failed'
                    }
                    print(f"    Detection failed")
                    
            except Exception as e:
                print(f"    Error: {e}")
                results_summary[scenario][confidence] = {
                    'error': str(e)
                }
    
    # Summary report
    print(f"\n📈 PERFORMANCE SUMMARY")
    print("=" * 50)
    for scenario, scenario_results in results_summary.items():
        print(f"\n{scenario.upper()} SCENARIO:")
        for confidence, result in scenario_results.items():
            if 'error' in result:
                print(f"  {confidence*100}%: Error - {result['error']}")
            else:
                injected = result.get('injected', 0)
                detected = result.get('detected', 0)
                status = result.get('status', 'unknown')
                
                if injected > 0:
                    rate = detected / injected
                    print(f"  {confidence*100}%: {detected}/{injected} detected ({rate:.1%}) - {status}")
                else:
                    print(f"  {confidence*100}%: {status}")

def demonstrate_detection_workflow():
    """Demonstrate complete bad data detection workflow"""
    print("\n" + "="*60)
    print("🔄 COMPLETE DETECTION WORKFLOW DEMO")
    print("="*60)
    
    # Step 1: Setup
    print("\n1️⃣ SETUP")
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.02)
    print(f"✅ Created grid with {len(estimator.net.measurement)} measurements")
    
    # Step 2: Create bad data
    print("\n2️⃣ BAD DATA INJECTION")
    bad_measurements = estimator.create_bad_data_scenario("mixed")
    print(f"✅ Injected {len(bad_measurements)} bad measurements")
    
    # Step 3: Run state estimation (will show impact of bad data)
    print("\n3️⃣ STATE ESTIMATION WITH BAD DATA")
    estimator.run_state_estimation()
    if estimator.estimation_results:
        print("✅ State estimation converged (but may have poor accuracy)")
    else:
        print("❌ State estimation failed due to bad data")
    
    # Step 4: Bad data detection
    print("\n4️⃣ BAD DATA DETECTION")
    results = estimator.detect_bad_data(confidence_level=0.95, max_iterations=5)
    
    # Step 5: Analysis
    print("\n5️⃣ RESULTS ANALYSIS")
    if results:
        bad_found = len(results.get('bad_measurements', []))
        print(f"Detected {bad_found} bad measurements")
        print(f"Final status: {results.get('final_status')}")
    
    print(f"\n✅ Complete workflow demonstration finished!")

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE BAD DATA DETECTION TESTING")
    print("="*80)
    
    # Set random seed for reproducible results
    np.random.seed(42)
    
    # Run all tests
    tests = [
        ("Basic Detection", test_basic_bad_data_detection),
        ("Single Bad Measurement", test_single_bad_measurement),
        ("Multiple Bad Measurements", test_multiple_bad_measurements),
        ("Systematic Bias", test_systematic_bias_detection),
        ("Detection Performance", test_detection_performance),
        ("Complete Workflow", demonstrate_detection_workflow)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'🧪 ' + test_name.upper()}")
        try:
            success = test_func()
            print(f"✅ {test_name} completed")
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
    
    print(f"\n🎯 BAD DATA DETECTION TESTING COMPLETE!")
    print("="*80)
    print("\nBad data detection features available:")
    print("• detect_bad_data() - Main detection algorithm")
    print("• create_bad_data_scenario() - Generate test scenarios")
    print("• Chi-square test for global detection")
    print("• Largest normalized residual test")
    print("• Statistical outlier detection")
    print("• Iterative bad data removal")
    print("• Systematic bias handling")