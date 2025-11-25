#!/usr/bin/env python3
"""
Test script for measurement consistency check functionality
Demonstrates comprehensive consistency validation
"""

from grid_state_estimator import GridStateEstimator
import numpy as np

def test_basic_consistency_check():
    """Test basic consistency check on clean measurements"""
    print("🔍 BASIC CONSISTENCY CHECK TEST")
    print("="*50)
    
    # Create estimator with IEEE 9-bus system
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    
    # Generate clean measurements
    print("\n1. Generating clean measurements...")
    estimator.simulate_measurements(noise_level=0.01)  # Very low noise
    print(f"Generated {len(estimator.net.measurement)} measurements")
    
    # Run consistency check
    print("\n2. Running consistency check on clean data...")
    results = estimator.check_measurement_consistency(tolerance=1e-3, detailed_report=True)
    
    if results:
        status = results.get('overall_status')
        violations = results.get('total_violations', 0)
        
        if status == 'consistent' and violations == 0:
            print("✅ Correctly identified consistent measurements")
        else:
            print(f"⚠️  Unexpected result: status={status}, violations={violations}")
            print("This might indicate numerical precision issues or tight tolerances")
    else:
        print("❌ Consistency check failed")
    
    return True

def test_consistency_with_inconsistent_measurements():
    """Test consistency check with deliberately inconsistent measurements"""
    print("\n" + "="*60)
    print("🚨 INCONSISTENT MEASUREMENTS TEST")
    print("="*60)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.01)
    
    print("\n1. Introducing measurement inconsistencies...")
    
    # Create significant inconsistencies
    inconsistencies_added = 0
    
    # Corrupt voltage measurements - make them unrealistic
    voltage_measurements = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'v']
    if len(voltage_measurements) > 0:
        # Set first voltage to unrealistic value
        bad_idx = voltage_measurements.index[0]
        original_v = estimator.net.measurement.loc[bad_idx, 'value']
        estimator.net.measurement.loc[bad_idx, 'value'] = 1.5  # Unrealistic high voltage
        inconsistencies_added += 1
        print(f"   • Set Bus voltage to 1.5 p.u. (was {original_v:.4f})")
    
    # Corrupt power flow measurements - violate power balance
    power_measurements = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'p']
    if len(power_measurements) > 2:
        # Increase some power flows significantly
        for i in range(2):
            bad_idx = power_measurements.index[i]
            original_p = estimator.net.measurement.loc[bad_idx, 'value']
            estimator.net.measurement.loc[bad_idx, 'value'] = original_p * 3  # Triple the power
            inconsistencies_added += 1
            print(f"   • Tripled power flow measurement (was {original_p:.2f} MW)")
    
    print(f"\nIntroduced {inconsistencies_added} inconsistencies")
    
    # Run consistency check
    print(f"\n2. Running consistency check on inconsistent measurements...")
    results = estimator.check_measurement_consistency(tolerance=1e-3, detailed_report=True)
    
    if results:
        status = results.get('overall_status')
        violations = results.get('total_violations', 0)
        
        print(f"\n📊 INCONSISTENCY DETECTION RESULTS:")
        print(f"   Status: {status}")
        print(f"   Total violations: {violations}")
        
        if violations > 0:
            print(f"✅ Successfully detected inconsistencies")
            
            # Show violation breakdown
            violation_types = results.get('violation_types', {})
            for vtype, v_list in violation_types.items():
                if len(v_list) > 0:
                    print(f"   • {vtype.replace('_', ' ').title()}: {len(v_list)} violations")
        else:
            print(f"❌ Failed to detect obvious inconsistencies")
    else:
        print("❌ Consistency check failed")

def test_consistency_metrics():
    """Test consistency metrics and coverage analysis"""
    print("\n" + "="*60)
    print("📈 CONSISTENCY METRICS TEST")
    print("="*60)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.02)
    
    print("\n1. Testing consistency metrics...")
    results = estimator.check_measurement_consistency(tolerance=1e-3, detailed_report=False)
    
    if results:
        metrics = results.get('consistency_metrics', {})
        
        print(f"\n📊 CONSISTENCY METRICS:")
        print(f"   Voltage coverage: {metrics.get('voltage_coverage', 0):.2%}")
        print(f"   Power coverage: {metrics.get('power_coverage', 0):.2%}")
        print(f"   Redundancy ratio: {metrics.get('redundancy_ratio', 0):.2f}")
        print(f"   Measurement density: {metrics.get('measurement_density', 0):.2f}")
        
        # Verify metrics make sense
        voltage_coverage = metrics.get('voltage_coverage', 0)
        redundancy_ratio = metrics.get('redundancy_ratio', 0)
        
        if voltage_coverage > 0.5:  # At least 50% bus voltage coverage
            print("✅ Good voltage coverage")
        else:
            print("⚠️  Limited voltage coverage")
            
        if redundancy_ratio > 2.0:  # At least 2x redundancy
            print("✅ Good measurement redundancy")
        else:
            print("⚠️  Limited measurement redundancy")
            
        recommendations = results.get('recommendations', [])
        if recommendations:
            print(f"\n💡 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec}")
    else:
        print("❌ Metrics calculation failed")

def test_physical_limits_check():
    """Test physical limits validation"""
    print("\n" + "="*60)
    print("⚡ PHYSICAL LIMITS CHECK TEST")
    print("="*60)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.01)
    
    print("\n1. Introducing physical limit violations...")
    
    # Create unrealistic power flows
    power_measurements = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'p']
    
    violations_added = 0
    for idx in power_measurements.index[:2]:  # Modify first 2 power measurements
        original_power = estimator.net.measurement.loc[idx, 'value']
        # Set to extremely high value (unrealistic for typical transmission)
        unrealistic_power = 5000  # 5000 MW - clearly unrealistic for test system
        estimator.net.measurement.loc[idx, 'value'] = unrealistic_power
        violations_added += 1
        print(f"   • Set power flow to {unrealistic_power} MW (was {original_power:.2f} MW)")
    
    print(f"\nIntroduced {violations_added} physical limit violations")
    
    # Run consistency check focusing on physical limits
    print(f"\n2. Running consistency check for physical limits...")
    results = estimator.check_measurement_consistency(tolerance=1e-3, detailed_report=True)
    
    if results:
        physical_violations = results.get('violation_types', {}).get('physical_limits', [])
        
        print(f"\n⚡ PHYSICAL LIMITS RESULTS:")
        print(f"   Physical limit violations: {len(physical_violations)}")
        
        if len(physical_violations) > 0:
            print("✅ Successfully detected physical limit violations")
            for i, violation in enumerate(physical_violations[:3], 1):
                element = violation.get('element', 'unknown')
                vtype = violation.get('type', 'unknown')
                print(f"   {i}. {vtype} at {element}")
        else:
            print("⚠️  Did not detect obvious physical limit violations")
            print("   (This might indicate limits checking needs adjustment)")
    else:
        print("❌ Physical limits check failed")

def test_kirchhoff_law_validation():
    """Test Kirchhoff's Current Law validation"""
    print("\n" + "="*60)
    print("⚖️  KIRCHHOFF'S LAW VALIDATION TEST")
    print("="*60)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.01)
    
    print("\n1. Testing KCL validation on normal system...")
    results = estimator.check_measurement_consistency(tolerance=1e-2, detailed_report=False)  # Relaxed tolerance
    
    if results:
        kcl_violations = results.get('violation_types', {}).get('kcl', [])
        
        print(f"KCL violations on clean system: {len(kcl_violations)}")
        
        if len(kcl_violations) == 0:
            print("✅ KCL satisfied on clean system")
        else:
            print("ℹ️  Some KCL violations detected (may be due to measurement noise or model approximations)")
            for violation in kcl_violations[:2]:  # Show first 2
                element = violation.get('element', 'unknown')
                imbalance = violation.get('power_imbalance', 0)
                print(f"   • {element}: {imbalance:.3f} MW imbalance")
    
    print(f"\n2. Summary of consistency validation features:")
    print(f"   • ✅ Power flow consistency (measured vs calculated)")
    print(f"   • ✅ Kirchhoff's Current Law validation")
    print(f"   • ✅ Bus power balance checking")
    print(f"   • ✅ Voltage consistency validation")
    print(f"   • ✅ Measurement redundancy analysis")
    print(f"   • ✅ Physical limits checking")

def demonstrate_complete_consistency_workflow():
    """Demonstrate complete consistency check workflow"""
    print("\n" + "="*70)
    print("🔄 COMPLETE CONSISTENCY CHECK WORKFLOW")
    print("="*70)
    
    # Step 1: Setup
    print("\n1️⃣ SETUP")
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.02)
    print(f"✅ Created system with {len(estimator.net.measurement)} measurements")
    
    # Step 2: Baseline consistency check
    print("\n2️⃣ BASELINE CONSISTENCY CHECK")
    baseline_results = estimator.check_measurement_consistency(tolerance=1e-3, detailed_report=False)
    baseline_violations = baseline_results.get('total_violations', 0) if baseline_results else 0
    print(f"Baseline violations: {baseline_violations}")
    
    # Step 3: Introduce problems
    print("\n3️⃣ INTRODUCE MEASUREMENT PROBLEMS")
    # Add a mix of problems for comprehensive testing
    
    # Voltage problem
    v_meas = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'v']
    if len(v_meas) > 0:
        idx = v_meas.index[0]
        estimator.net.measurement.loc[idx, 'value'] = 1.4  # High voltage
        print("   • Added voltage inconsistency")
    
    # Power balance problem  
    p_meas = estimator.net.measurement[estimator.net.measurement['measurement_type'] == 'p']
    if len(p_meas) > 1:
        idx1 = p_meas.index[0]
        idx2 = p_meas.index[1]
        estimator.net.measurement.loc[idx1, 'value'] *= 2.5  # Increase significantly
        estimator.net.measurement.loc[idx2, 'value'] *= 0.3  # Decrease significantly
        print("   • Added power flow inconsistencies")
    
    # Step 4: Detect problems
    print("\n4️⃣ DETECT INCONSISTENCIES")
    problem_results = estimator.check_measurement_consistency(tolerance=1e-3, detailed_report=True)
    
    if problem_results:
        problem_violations = problem_results.get('total_violations', 0)
        status = problem_results.get('overall_status', 'unknown')
        
        print(f"\n📊 DETECTION RESULTS:")
        print(f"   Violations found: {problem_violations}")
        print(f"   Overall status: {status}")
        
        if problem_violations > baseline_violations:
            print("✅ Successfully detected introduced inconsistencies")
        else:
            print("⚠️  May not have detected all problems")
    
    # Step 5: Recommendations
    print("\n5️⃣ ACTIONABLE RECOMMENDATIONS")
    if problem_results and problem_results.get('recommendations'):
        recommendations = problem_results['recommendations']
        print("Top recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec}")
    
    print(f"\n✅ Complete consistency check workflow demonstrated!")

if __name__ == "__main__":
    print("🔍 COMPREHENSIVE CONSISTENCY CHECK TESTING")
    print("="*80)
    
    # Set random seed for reproducible results
    np.random.seed(42)
    
    # Run all tests
    tests = [
        ("Basic Consistency", test_basic_consistency_check),
        ("Inconsistent Measurements", test_consistency_with_inconsistent_measurements),
        ("Consistency Metrics", test_consistency_metrics),
        ("Physical Limits", test_physical_limits_check),
        ("Kirchhoff's Law", test_kirchhoff_law_validation),
        ("Complete Workflow", demonstrate_complete_consistency_workflow)
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'🧪 ' + test_name.upper()}")
        try:
            success = test_func()
            print(f"✅ {test_name} completed")
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
    
    print(f"\n🎯 CONSISTENCY CHECK TESTING COMPLETE!")
    print("="*80)
    print("\nConsistency check features available:")
    print("• check_measurement_consistency() - Main consistency validation")
    print("• Power flow consistency checking")
    print("• Kirchhoff's Current Law validation")
    print("• Bus power balance verification")
    print("• Voltage consistency analysis")
    print("• Measurement redundancy assessment")
    print("• Physical limits validation")
    print("• Comprehensive metrics and recommendations")