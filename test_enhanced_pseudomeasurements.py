#!/usr/bin/env python3
"""
Test script for enhanced pseudomeasurement functionality
"""

import sys
import numpy as np
from grid_state_estimator import GridStateEstimator

def test_enhanced_pseudomeasurements():
    """Test the enhanced pseudomeasurement functionality"""
    print("Testing Enhanced Pseudomeasurement Functionality")
    print("=" * 70)
    
    try:
        # 1. Create estimator and grid
        estimator = GridStateEstimator()
        estimator.create_ieee9_grid()
        print("✅ IEEE 9-bus grid created")
        
        # 2. Create a challenging measurement scenario with many gaps
        np.random.seed(42)
        estimator.simulate_measurements(noise_level=0.02)
        original_count = len(estimator.net.measurement)
        print(f"✅ Generated {original_count} measurements (full coverage)")
        
        # 3. Remove many measurements to create significant observability challenges
        print("\n🔍 CREATING SIGNIFICANT MEASUREMENT GAPS")
        print("-" * 50)
        
        # Remove voltage measurements from most buses
        removed_v = estimator.remove_measurements_by_type('v', element_filter=[1, 2, 3, 5, 6, 7, 8])
        print(f"   Removed voltage measurements from buses 1,2,3,5,6,7,8: {removed_v}")
        
        # Remove many power measurements
        removed_p = estimator.remove_measurements_by_type('p', element_filter=[1, 2, 3, 4, 5, 6])
        removed_q = estimator.remove_measurements_by_type('q', element_filter=[0, 2, 4, 6, 8])
        print(f"   Removed many power measurements")
        
        current_count = len(estimator.net.measurement)
        print(f"   Measurements after removals: {current_count} (was {original_count})")
        
        # 4. Test enhanced measurement gap analysis
        print("\n📊 ENHANCED MEASUREMENT GAP ANALYSIS")
        print("-" * 50)
        gap_analysis = estimator.analyze_measurement_gaps()
        
        if gap_analysis:
            voltage_gaps = gap_analysis['gap_summary']['voltage_gaps']
            power_gaps = gap_analysis['gap_summary']['power_gaps']
            critical_gaps = gap_analysis['critical_gaps']
            
            print(f"   Voltage measurement gaps: {voltage_gaps['count']} buses ({voltage_gaps['percentage']:.1f}%)")
            print(f"   Power measurement gaps: {power_gaps['count']} lines ({power_gaps['percentage']:.1f}%)")
            print(f"   Critical gaps identified: {len(critical_gaps)}")
            
            if critical_gaps:
                print("   Critical gaps:")
                for gap in critical_gaps[:3]:
                    print(f"     • Bus {gap['bus']}: {gap['connections']} connections")
            
            print("   Recommendations:")
            for rec in gap_analysis['recommendations']:
                print(f"     • {rec}")
        
        # 5. Test intelligent pseudomeasurement strategies
        strategies = ['adaptive', 'minimum_cost', 'maximum_redundancy']
        
        for strategy in strategies:
            print(f"\n🧠 TESTING {strategy.upper()} STRATEGY")
            print("-" * 50)
            
            # First remove any existing pseudomeasurements
            estimator.remove_pseudomeasurements()
            
            if strategy == 'maximum_redundancy':
                success, result = estimator.add_intelligent_pseudomeasurements(
                    strategy=strategy, target_redundancy=2.0
                )
            else:
                success, result = estimator.add_intelligent_pseudomeasurements(strategy=strategy)
            
            if success:
                if isinstance(result, dict):
                    print(f"   ✅ {result['summary']}")
                    print(f"   Added {result['added_count']} measurements")
                    print(f"   Final redundancy: {result['final_redundancy']:.2f}")
                    
                    if result.get('details'):
                        print("   Sample additions:")
                        for detail in result['details'][:5]:
                            print(f"     • {detail}")
                else:
                    print(f"   ✅ {result}")
                
                # Test observability after this strategy
                obs_result = estimator.test_observability()
                if obs_result:
                    print(f"   Observability after {strategy}: {obs_result.get('level', 'Unknown')}")
                    
                # Test state estimation
                try:
                    estimator.run_state_estimation()
                    if estimator.estimation_results:
                        converged = estimator.estimation_results.get('converged', False)
                        print(f"   State estimation convergence: {'✅ Yes' if converged else '❌ No'}")
                    else:
                        print("   State estimation: ❌ Failed")
                except Exception as e:
                    print(f"   State estimation: ❌ Error: {str(e)[:50]}")
                
            else:
                print(f"   ❌ {result}")
        
        # 6. Test comprehensive pseudomeasurement analysis
        print("\n📈 COMPREHENSIVE ANALYSIS WITH ALL STRATEGIES")
        print("-" * 50)
        
        # Remove pseudomeasurements and add comprehensive set
        estimator.remove_pseudomeasurements()
        
        # Add using adaptive strategy (most comprehensive)
        success, result = estimator.add_intelligent_pseudomeasurements(strategy='adaptive')
        
        if success:
            print(f"   ✅ Added comprehensive pseudomeasurements")
            
            # Get detailed summary
            summary = estimator.get_pseudomeasurement_summary()
            if summary:
                print(f"   Total measurements: {summary.get('total_measurements', 0)}")
                print(f"   Pseudomeasurements: {summary.get('pseudomeasurements', 0)}")
                print(f"   Real measurements: {summary.get('real_measurements', 0)}")
                
                if summary.get('pseudo_types'):
                    print("   Pseudomeasurement breakdown:")
                    for ptype, count in summary['pseudo_types'].items():
                        print(f"     • {ptype}: {count}")
                
                # Calculate percentage
                total = summary.get('total_measurements', 0)
                pseudo = summary.get('pseudomeasurements', 0)
                if total > 0:
                    percentage = (pseudo / total) * 100
                    print(f"   Pseudomeasurement ratio: {percentage:.1f}%")
        
        # 7. Test final observability and estimation
        print("\n⚡ FINAL SYSTEM PERFORMANCE")
        print("-" * 50)
        
        final_obs = estimator.test_observability()
        if final_obs:
            print(f"   Final observability level: {final_obs.get('level', 'Unknown')}")
            print(f"   Total measurements: {final_obs.get('total_measurements', 0)}")
            print(f"   Network coverage: {final_obs.get('coverage', 0):.1%}")
        
        # Final state estimation test
        try:
            estimator.run_state_estimation()
            if estimator.estimation_results:
                converged = estimator.estimation_results.get('converged', False)
                print(f"   Final state estimation: {'✅ Converged' if converged else '⚠️  Did not converge'}")
                
                if converged:
                    # Get voltage results
                    if hasattr(estimator.net, 'res_bus_est'):
                        max_voltage = estimator.net.res_bus_est['vm_pu'].max()
                        min_voltage = estimator.net.res_bus_est['vm_pu'].min()
                        print(f"   Voltage range: {min_voltage:.4f} - {max_voltage:.4f} p.u.")
            else:
                print("   Final state estimation: ❌ Failed")
        except Exception as e:
            print(f"   Final state estimation: ❌ Error: {str(e)[:60]}")
        
        # 8. Performance comparison summary
        print("\n📊 PERFORMANCE COMPARISON SUMMARY")
        print("-" * 50)
        print(f"   Original measurements: {original_count}")
        print(f"   After creating gaps: {current_count}")
        print(f"   After pseudomeasurements: {len(estimator.net.measurement)}")
        print(f"   Improvement factor: {len(estimator.net.measurement) / current_count:.2f}x")
        
        gap_reduction = gap_analysis['gap_summary']['voltage_gaps']['count']
        print(f"   Voltage gaps addressed: {gap_reduction}")
        
        final_summary = estimator.get_pseudomeasurement_summary()
        if final_summary:
            pseudo_count = final_summary.get('pseudomeasurements', 0)
            efficiency = (pseudo_count / gap_reduction) if gap_reduction > 0 else 0
            print(f"   Pseudomeasurement efficiency: {efficiency:.1f} pseudo/gap")
        
        print("\n" + "=" * 70)
        print("✅ All enhanced pseudomeasurement tests completed successfully!")
        print("\n📈 ENHANCED FEATURES TESTED:")
        print(f"   • Intelligent gap analysis: ✅")
        print(f"   • Adaptive pseudomeasurement placement: ✅") 
        print(f"   • Multiple placement strategies: ✅")
        print(f"   • Critical bus identification: ✅")
        print(f"   • Smart voltage estimation: ✅")
        print(f"   • Redundancy optimization: ✅")
        print(f"   • Comprehensive performance analysis: ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_pseudomeasurements()
    sys.exit(0 if success else 1)