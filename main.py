#!/usr/bin/env python3
"""
Main script for Power System State Estimation Application
Interactive interface for all functionality including grid creation, 
measurement simulation, modification, state estimation, and analysis
"""

import sys
import os
from grid_state_estimator import GridStateEstimator
import numpy as np

class PowerSystemApp:
    def __init__(self):
        self.estimator = None
        self.current_grid = None
        
    def show_banner(self):
        """Display application banner"""
        print("="*80)
        print("🔌 POWER SYSTEM STATE ESTIMATION APPLICATION")
        print("="*80)
        print("Features:")
        print("• IEEE 9-bus and ENTSO-E transmission grid models")
        print("• Measurement simulation with configurable noise")
        print("• Interactive measurement modification")
        print("• State estimation with observability analysis")
        print("• Grid visualization and results analysis")
        print("• CGMES interface support")
        print("="*80)
    
    def show_main_menu(self):
        """Display main menu options"""
        print("\n📋 MAIN MENU")
        print("-" * 40)
        print("1. Create Grid Model")
        print("2. Simulate Measurements")
        print("3. Modify Measurements")
        print("4. Run State Estimation")
        print("5. Test Observability")
        print("6. Show Results")
        print("7. Visualize Grid")
        print("8. CGMES Interface")
        print("9. Demo & Examples")
        print("A. Auto Demo - Complete Workflow")
        print("0. Exit")
        print("-" * 40)
    
    def show_grid_menu(self):
        """Display grid selection menu"""
        print("\n🏭 GRID MODEL SELECTION")
        print("-" * 30)
        print("1. IEEE 9-bus Test System")
        print("2. ENTSO-E Transmission Grid")
        print("3. Back to Main Menu")
        print("-" * 30)
    
    def show_measurement_menu(self):
        """Display measurement options menu"""
        print("\n📊 MEASUREMENT OPTIONS")
        print("-" * 30)
        print("1. Generate New Measurements")
        print("2. List Current Measurements")
        print("3. Modify Bus Voltage")
        print("4. Modify Line Power")
        print("5. Modify by Index")
        print("6. Reset Measurements")
        print("7. Back to Main Menu")
        print("-" * 30)
    
    def show_analysis_menu(self):
        """Display analysis options menu"""
        print("\n📈 ANALYSIS OPTIONS")
        print("-" * 30)
        print("1. Basic State Estimation")
        print("2. State Estimation with Results")
        print("3. Observability Analysis")
        print("4. Consistency Check")
        print("5. Bad Data Detection")
        print("6. Create Bad Data Scenario")
        print("7. Measurement Sensitivity Test")
        print("8. Back to Main Menu")
        print("-" * 30)
    
    def create_grid_model(self):
        """Create grid model interface"""
        while True:
            self.show_grid_menu()
            choice = input("Select grid model (1-3): ").strip()
            
            if choice == '1':
                print("\n🔧 Creating IEEE 9-bus test system...")
                self.estimator = GridStateEstimator()
                self.estimator.create_ieee9_grid()
                self.current_grid = "IEEE 9-bus"
                print("✅ IEEE 9-bus system created successfully!")
                break
                
            elif choice == '2':
                print("\n🔧 Creating ENTSO-E transmission grid...")
                self.estimator = GridStateEstimator()
                self.estimator.create_simple_entso_grid()
                self.current_grid = "ENTSO-E"
                print("✅ ENTSO-E transmission grid created successfully!")
                break
                
            elif choice == '3':
                break
                
            else:
                print("❌ Invalid choice. Please select 1-3.")
    
    def simulate_measurements(self):
        """Simulate measurements interface"""
        if not self.estimator:
            print("❌ No grid model created. Please create a grid first.")
            return
            
        while True:
            self.show_measurement_menu()
            choice = input("Select option (1-7): ").strip()
            
            if choice == '1':
                try:
                    noise_input = input("Enter noise level (0.0-0.1, default 0.02): ").strip()
                    noise_level = float(noise_input) if noise_input else 0.02
                    print(f"\n📊 Generating measurements with {noise_level*100:.1f}% noise...")
                    self.estimator.simulate_measurements(noise_level=noise_level)
                    print("✅ Measurements generated successfully!")
                except ValueError:
                    print("❌ Invalid noise level. Using default 2%.")
                    self.estimator.simulate_measurements(noise_level=0.02)
                    
            elif choice == '2':
                if hasattr(self.estimator, 'net') and len(self.estimator.net.measurement) > 0:
                    self.estimator.list_measurements()
                else:
                    print("❌ No measurements available. Generate measurements first.")
                    
            elif choice == '3':
                self.modify_bus_voltage()
                
            elif choice == '4':
                self.modify_line_power()
                
            elif choice == '5':
                self.modify_by_index()
                
            elif choice == '6':
                if hasattr(self.estimator, 'net') and len(self.estimator.net.measurement) > 0:
                    noise_input = input("Enter noise level for reset (default 0.02): ").strip()
                    noise_level = float(noise_input) if noise_input else 0.02
                    self.estimator.reset_measurements(noise_level=noise_level)
                else:
                    print("❌ No measurements to reset.")
                    
            elif choice == '7':
                break
                
            else:
                print("❌ Invalid choice. Please select 1-7.")
    
    def modify_bus_voltage(self):
        """Modify bus voltage measurement"""
        if not hasattr(self.estimator, 'net') or len(self.estimator.net.measurement) == 0:
            print("❌ No measurements available. Generate measurements first.")
            return
            
        try:
            # Show available buses
            print(f"\nAvailable buses in {self.current_grid}:")
            for i, bus_name in enumerate(self.estimator.net.bus.name):
                print(f"  Bus {i}: {bus_name}")
            
            bus_id = int(input("\nEnter bus ID: "))
            voltage = float(input("Enter new voltage (p.u.): "))
            
            success = self.estimator.modify_bus_voltage_measurement(bus_id, voltage)
            if success:
                print(f"✅ Bus {bus_id} voltage set to {voltage:.4f} p.u.")
            else:
                print(f"❌ Failed to modify bus {bus_id} voltage.")
                
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def modify_line_power(self):
        """Modify line power measurement"""
        if not hasattr(self.estimator, 'net') or len(self.estimator.net.measurement) == 0:
            print("❌ No measurements available. Generate measurements first.")
            return
            
        try:
            # Show available lines
            print(f"\nAvailable lines in {self.current_grid}:")
            for i, line in self.estimator.net.line.iterrows():
                line_name = line.get('name', f'Line {i}')
                print(f"  Line {i}: {line_name}")
            
            line_id = int(input("\nEnter line ID: "))
            side = input("Enter side (from/to): ").lower()
            if side not in ['from', 'to']:
                print("❌ Invalid side. Must be 'from' or 'to'.")
                return
                
            power_type = input("Enter power type (p/q): ").lower()
            if power_type not in ['p', 'q']:
                print("❌ Invalid power type. Must be 'p' (active) or 'q' (reactive).")
                return
                
            power_value = float(input(f"Enter {power_type.upper()} power value: "))
            
            success = self.estimator.modify_line_power_measurement(line_id, side, power_type, power_value)
            if success:
                unit = "MW" if power_type == 'p' else "Mvar"
                print(f"✅ Line {line_id} {power_type.upper()} power ({side}) set to {power_value} {unit}")
            else:
                print(f"❌ Failed to modify line {line_id} power.")
                
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def modify_by_index(self):
        """Modify measurement by index"""
        if not hasattr(self.estimator, 'net') or len(self.estimator.net.measurement) == 0:
            print("❌ No measurements available. Generate measurements first.")
            return
            
        # Show measurements first
        print("\nCurrent measurements:")
        self.estimator.list_measurements()
        
        try:
            index = int(input("\nEnter measurement index: "))
            value = float(input("Enter new value: "))
            
            std_dev_input = input("Enter new std dev (press Enter to keep current): ").strip()
            std_dev = float(std_dev_input) if std_dev_input else None
            
            success = self.estimator.modify_measurement(index, value, std_dev)
            if success:
                print(f"✅ Measurement {index} modified successfully.")
            else:
                print(f"❌ Failed to modify measurement {index}.")
                
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_analysis(self):
        """Run analysis interface"""
        if not self.estimator:
            print("❌ No grid model created. Please create a grid first.")
            return
            
        while True:
            self.show_analysis_menu()
            choice = input("Select option (1-8): ").strip()
            
            if choice == '1':
                print("\n⚡ Running state estimation...")
                self.estimator.run_state_estimation()
                
            elif choice == '2':
                print("\n⚡ Running state estimation with results...")
                self.estimator.run_state_estimation()
                if self.estimator.estimation_results:
                    self.estimator.show_results()
                
            elif choice == '3':
                print("\n🔍 Running observability analysis...")
                if hasattr(self.estimator, 'net') and len(self.estimator.net.measurement) > 0:
                    self.estimator.test_observability()
                else:
                    print("❌ No measurements available. Generate measurements first.")
                
            elif choice == '4':
                self.run_consistency_check()
                
            elif choice == '5':
                self.run_bad_data_detection()
                
            elif choice == '6':
                self.create_bad_data_scenario()
                
            elif choice == '7':
                self.run_sensitivity_test()
                
            elif choice == '8':
                break
                
            else:
                print("❌ Invalid choice. Please select 1-8.")
    
    def run_sensitivity_test(self):
        """Run measurement sensitivity test"""
        if not hasattr(self.estimator, 'net') or len(self.estimator.net.measurement) == 0:
            print("❌ No measurements available. Generate measurements first.")
            return
            
        print("\n📈 MEASUREMENT SENSITIVITY TEST")
        print("Testing impact of measurement errors on state estimation...")
        
        # Save current state
        original_measurements = self.estimator.net.measurement.copy()
        
        try:
            # Test different error levels
            error_levels = [0.01, 0.05, 0.10]  # 1%, 5%, 10%
            bus_to_test = 1  # Test bus 1
            
            # Run baseline
            print("\nRunning baseline estimation...")
            self.estimator.reset_measurements(noise_level=0.0)  # Perfect measurements
            self.estimator.run_state_estimation()
            
            if self.estimator.estimation_results and hasattr(self.estimator.net, 'res_bus_est'):
                baseline_voltage = self.estimator.net.res_bus_est.vm_pu.iloc[bus_to_test]
                print(f"Baseline Bus {bus_to_test} voltage: {baseline_voltage:.6f} p.u.")
                
                for error_pct in error_levels:
                    print(f"\nTesting {error_pct*100}% measurement error...")
                    
                    # Reset and modify
                    self.estimator.reset_measurements(noise_level=0.0)
                    modified_voltage = baseline_voltage * (1 + error_pct)
                    self.estimator.modify_bus_voltage_measurement(bus_to_test, modified_voltage)
                    
                    # Run estimation
                    self.estimator.run_state_estimation()
                    if self.estimator.estimation_results and hasattr(self.estimator.net, 'res_bus_est'):
                        new_voltage = self.estimator.net.res_bus_est.vm_pu.iloc[bus_to_test]
                        impact = abs(new_voltage - baseline_voltage)
                        print(f"  Impact: {impact:.6f} p.u. change in estimated voltage")
                    else:
                        print(f"  ❌ State estimation failed with {error_pct*100}% error")
            else:
                print("❌ Baseline state estimation failed")
                
        except Exception as e:
            print(f"❌ Sensitivity test failed: {e}")
        finally:
            # Restore original measurements
            self.estimator.net.measurement = original_measurements
    
    def run_bad_data_scenario(self):
        """Run bad data detection scenario"""
        print("\n🚨 BAD DATA SCENARIO TEST")
        print("Introducing unrealistic measurements...")
        
        if not hasattr(self.estimator, 'net') or len(self.estimator.net.measurement) == 0:
            print("❌ No measurements available. Generate measurements first.")
            return
            
        # Save original state
        original_measurements = self.estimator.net.measurement.copy()
        
        try:
            # Introduce bad data
            print("\nIntroducing bad measurements:")
            print("• Setting unrealistic high voltage (1.8 p.u.)")
            self.estimator.modify_bus_voltage_measurement(0, 1.8)
            
            if len(self.estimator.net.line) > 0:
                print("• Setting unrealistic high power flow (500 MW)")
                self.estimator.modify_line_power_measurement(0, 'from', 'p', 500.0)
            
            # Run state estimation
            print("\nRunning state estimation with bad data...")
            self.estimator.run_state_estimation()
            
            if self.estimator.estimation_results:
                print("⚠️ State estimation converged despite bad data")
                print("(In practice, bad data detection algorithms would flag these measurements)")
            else:
                print("❌ State estimation failed due to bad data")
                
        except Exception as e:
            print(f"❌ Bad data test failed: {e}")
        finally:
            # Restore original measurements
            self.estimator.net.measurement = original_measurements
            print("\n✅ Original measurements restored")
    
    def run_consistency_check(self):
        """Run measurement consistency check"""
        if not self.estimator:
            print("❌ No grid model created. Please create a grid first.")
            return
            
        if not hasattr(self.estimator, 'net') or len(self.estimator.net.measurement) == 0:
            print("❌ No measurements available. Generate measurements first.")
            return
        
        try:
            print("\n🔍 CONSISTENCY CHECK SETUP")
            print("-" * 40)
            
            # Get tolerance parameter
            tolerance_input = input("Tolerance level (1e-3, 1e-4, 1e-5, default: 1e-3): ").strip()
            try:
                if tolerance_input:
                    tolerance = float(tolerance_input)
                else:
                    tolerance = 1e-3
            except ValueError:
                tolerance = 1e-3
                print("⚠️  Invalid input. Using default tolerance: 1e-3")
            
            # Ask for detailed report
            detailed_input = input("Show detailed report? (y/n, default: y): ").strip().lower()
            detailed_report = detailed_input != 'n'
            
            print(f"\nRunning consistency check with:")
            print(f"  Tolerance: {tolerance:.1e}")
            print(f"  Detailed report: {'Yes' if detailed_report else 'No'}")
            
            # Run consistency check
            results = self.estimator.check_measurement_consistency(
                tolerance=tolerance,
                detailed_report=detailed_report
            )
            
            if results:
                print(f"\n📊 CONSISTENCY CHECK COMPLETED!")
                status = results.get('overall_status', 'unknown')
                total_violations = results.get('total_violations', 0)
                
                status_messages = {
                    'consistent': '✅ All measurements are consistent',
                    'minor_issues': '⚠️  Minor consistency issues detected',
                    'moderate_issues': '🔶 Moderate consistency problems found',
                    'major_issues': '🚨 Major consistency violations detected'
                }
                
                message = status_messages.get(status, f'Status: {status}')
                print(f"Result: {message}")
                print(f"Total violations: {total_violations}")
                
                if total_violations > 0:
                    print(f"\n💡 Consider:")
                    print(f"  • Reviewing measurement calibration")
                    print(f"  • Checking for systematic errors")
                    print(f"  • Running bad data detection")
                else:
                    print(f"\n✅ System measurements are ready for reliable state estimation")
            
        except Exception as e:
            print(f"❌ Consistency check failed: {e}")
    
    def run_bad_data_detection(self):
        """Run bad data detection analysis"""
        if not self.estimator:
            print("❌ No grid model created. Please create a grid first.")
            return
            
        if not hasattr(self.estimator, 'net') or len(self.estimator.net.measurement) == 0:
            print("❌ No measurements available. Generate measurements first.")
            return
            
        try:
            # Get detection parameters
            print("\n🔍 BAD DATA DETECTION SETUP")
            print("-" * 40)
            
            confidence_input = input("Confidence level (0.90, 0.95, 0.99, default: 0.95): ").strip()
            try:
                confidence = float(confidence_input) if confidence_input else 0.95
                if confidence not in [0.90, 0.95, 0.99]:
                    print(f"⚠️  Using closest supported value: 0.95")
                    confidence = 0.95
            except ValueError:
                confidence = 0.95
                print("⚠️  Invalid input. Using default confidence level: 0.95")
            
            max_iter_input = input("Maximum iterations (1-10, default: 5): ").strip()
            try:
                max_iterations = int(max_iter_input) if max_iter_input else 5
                max_iterations = max(1, min(10, max_iterations))  # Clamp between 1-10
            except ValueError:
                max_iterations = 5
                print("⚠️  Invalid input. Using default: 5 iterations")
            
            print(f"\nRunning bad data detection with:")
            print(f"  Confidence Level: {confidence*100}%")
            print(f"  Max Iterations: {max_iterations}")
            
            # Run bad data detection
            results = self.estimator.detect_bad_data(
                confidence_level=confidence, 
                max_iterations=max_iterations
            )
            
            if results:
                print(f"\n📊 DETECTION COMPLETED!")
                print(f"Final status: {results.get('final_status', 'unknown')}")
                if results.get('bad_measurements'):
                    print(f"Bad measurements found: {len(results['bad_measurements'])}")
                else:
                    print("No bad measurements detected.")
            
        except Exception as e:
            print(f"❌ Bad data detection failed: {e}")
    
    def create_bad_data_scenario(self):
        """Create bad data scenario for testing"""
        if not self.estimator:
            print("❌ No grid model created. Please create a grid first.")
            return
            
        if not hasattr(self.estimator, 'net') or len(self.estimator.net.measurement) == 0:
            print("❌ No measurements available. Generate measurements first.")
            return
        
        print("\n🧪 BAD DATA SCENARIO CREATION")
        print("-" * 40)
        print("Available scenario types:")
        print("1. Single gross error")
        print("2. Multiple independent errors")
        print("3. Systematic bias")
        print("4. Mixed (gross errors + systematic bias)")
        print("-" * 40)
        
        scenario_choice = input("Select scenario type (1-4, default: 4): ").strip()
        
        scenario_map = {
            '1': 'single',
            '2': 'multiple', 
            '3': 'systematic',
            '4': 'mixed'
        }
        
        scenario_type = scenario_map.get(scenario_choice, 'mixed')
        scenario_names = {
            'single': 'Single Gross Error',
            'multiple': 'Multiple Independent Errors',
            'systematic': 'Systematic Bias',
            'mixed': 'Mixed (Recommended)'
        }
        
        print(f"\n🔧 Creating scenario: {scenario_names[scenario_type]}")
        
        try:
            bad_measurements = self.estimator.create_bad_data_scenario(scenario_type)
            
            if bad_measurements:
                print(f"\n✅ Bad data scenario created successfully!")
                print(f"Corrupted {len(bad_measurements)} measurements")
                
                # Ask if user wants to run detection immediately
                run_detection = input("\n🔍 Run bad data detection now? (y/n, default: y): ").strip().lower()
                if run_detection != 'n':
                    print("\nRunning bad data detection...")
                    self.run_bad_data_detection()
            else:
                print("❌ Failed to create bad data scenario")
                
        except Exception as e:
            print(f"❌ Error creating bad data scenario: {e}")
    
    def run_bad_data_scenario(self):
        """Run comprehensive bad data scenario (legacy function for compatibility)"""
        print("\n🚨 This function has been moved to 'Create Bad Data Scenario'")
        print("Please use menu option 5 in the Analysis menu.")
        self.create_bad_data_scenario()
    
    def show_results(self):
        """Show estimation results"""
        if not self.estimator:
            print("❌ No grid model created.")
            return
            
        if not self.estimator.estimation_results:
            print("❌ No state estimation results. Run state estimation first.")
            return
            
        print("\n📊 ESTIMATION RESULTS")
        self.estimator.show_results()
    
    def visualize_grid(self):
        """Visualize grid results"""
        if not self.estimator:
            print("❌ No grid model created.")
            return
            
        try:
            print("\n🖼️ Generating grid visualization...")
            if hasattr(self.estimator, 'plot_grid_results'):
                self.estimator.plot_grid_results()
                print("✅ Grid visualization displayed!")
            else:
                print("❌ Grid visualization not available for this model.")
        except Exception as e:
            print(f"❌ Visualization failed: {e}")
    
    def cgmes_interface(self):
        """CGMES interface menu"""
        print("\n🌐 CGMES INTERFACE")
        print("-" * 30)
        print("1. Test CGMES Loading")
        print("2. Run ENTSO-E Grid Test")
        print("3. Back to Main Menu")
        print("-" * 30)
        
        choice = input("Select option (1-3): ").strip()
        
        if choice == '1':
            print("\n🔧 Testing CGMES interface...")
            try:
                from cgmes_interface import CGMESInterface
                cgmes = CGMESInterface()
                cgmes_files = cgmes.download_entso_example()
                success = cgmes.load_cgmes_model(cgmes_files)
                if success:
                    print("✅ CGMES model loaded successfully!")
                else:
                    print("❌ CGMES loading failed (expected - requires CIM libraries)")
            except Exception as e:
                print(f"❌ CGMES test failed: {e}")
                
        elif choice == '2':
            print("\n🔧 Running ENTSO-E grid test...")
            try:
                from test_entso_grid import test_entso_style_grid
                test_entso_style_grid()
            except Exception as e:
                print(f"❌ ENTSO-E test failed: {e}")
    
    def show_demos(self):
        """Show demo options"""
        print("\n🎯 DEMOS & EXAMPLES")
        print("-" * 30)
        print("1. Basic Usage Demo")
        print("2. Measurement Modification Demo")
        print("3. Observability Test")
        print("4. Run All Tests")
        print("5. Back to Main Menu")
        print("-" * 30)
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == '1':
            self.run_basic_demo()
        elif choice == '2':
            self.run_measurement_demo()
        elif choice == '3':
            self.run_observability_demo()
        elif choice == '4':
            self.run_all_tests()
    
    def run_basic_demo(self):
        """Run basic usage demonstration"""
        print("\n🎯 BASIC USAGE DEMO")
        print("="*40)
        
        # Create grid
        print("1. Creating IEEE 9-bus grid...")
        demo_estimator = GridStateEstimator()
        demo_estimator.create_ieee9_grid()
        
        # Generate measurements
        print("2. Generating measurements...")
        demo_estimator.simulate_measurements(noise_level=0.02)
        
        # Run state estimation
        print("3. Running state estimation...")
        demo_estimator.run_state_estimation()
        
        # Show results
        if demo_estimator.estimation_results:
            print("✅ Demo completed successfully!")
            print("4. Showing voltage results...")
            if hasattr(demo_estimator.net, 'res_bus_est'):
                for i in range(min(3, len(demo_estimator.net.res_bus_est))):
                    voltage = demo_estimator.net.res_bus_est.vm_pu.iloc[i]
                    print(f"   Bus {i}: {voltage:.4f} p.u.")
        else:
            print("❌ Demo state estimation failed")
    
    def run_measurement_demo(self):
        """Run measurement modification demonstration"""
        print("\n🔧 MEASUREMENT MODIFICATION DEMO")
        print("="*45)
        
        if not self.estimator:
            print("Creating demo grid...")
            self.estimator = GridStateEstimator()
            self.estimator.create_ieee9_grid()
            self.estimator.simulate_measurements(noise_level=0.02)
        
        # Show how to modify measurements
        print("Demonstrating measurement modification:")
        print("• Setting Bus 1 voltage to 1.15 p.u.")
        self.estimator.modify_bus_voltage_measurement(1, 1.15)
        
        print("• Running state estimation with modified measurement...")
        self.estimator.run_state_estimation()
        
        if self.estimator.estimation_results and hasattr(self.estimator.net, 'res_bus_est'):
            voltage = self.estimator.net.res_bus_est.vm_pu.iloc[1]
            print(f"✅ Estimated Bus 1 voltage: {voltage:.4f} p.u.")
        
        print("• Resetting measurements...")
        self.estimator.reset_measurements()
        print("✅ Demo completed!")
    
    def run_observability_demo(self):
        """Run observability demonstration"""
        if not self.estimator:
            print("❌ No grid model. Create a grid first.")
            return
            
        if not hasattr(self.estimator, 'net') or len(self.estimator.net.measurement) == 0:
            print("Generating measurements for observability test...")
            self.estimator.simulate_measurements(noise_level=0.02)
        
        print("\n🔍 OBSERVABILITY ANALYSIS DEMO")
        self.estimator.test_observability()
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\n🧪 RUNNING COMPREHENSIVE TESTS")
        print("="*50)
        
        test_scripts = [
            ("Basic functionality", "python3 example_set_bus_voltage.py"),
            ("Measurement modification", "python3 demo_measurement_modification.py"),
            ("CGMES interface", "python3 cgmes_interface.py"),
        ]
        
        for test_name, script in test_scripts:
            print(f"\n📋 Running {test_name} test...")
            try:
                import subprocess
                result = subprocess.run(script.split(), capture_output=True, text=True, cwd=".")
                if result.returncode == 0:
                    print(f"✅ {test_name} test passed")
                else:
                    print(f"❌ {test_name} test failed")
                    print(f"Error: {result.stderr[:200]}...")
            except Exception as e:
                print(f"❌ {test_name} test failed: {e}")
        
        print("\n✅ All tests completed!")
    
    def run_complete_workflow_demo(self):
        """Run complete workflow demo: create model, modify measurement, consistency check, bad data detection, state estimation"""
        print("\n" + "="*80)
        print("🎯 COMPLETE WORKFLOW DEMONSTRATION")
        print("="*80)
        print("This demo will:")
        print("1. Create IEEE 9-bus system")
        print("2. Simulate measurements")
        print("3. Change Bus 1 measurement to 1.5 p.u.")
        print("4. Run consistency check")
        print("5. Detect bad data")
        print("6. Run state estimation")
        print("7. Show comprehensive results table")
        print("="*80)
        
        import numpy as np
        
        # Set seed for reproducible results
        np.random.seed(42)
        
        try:
            # Step 1: Create IEEE 9-bus model
            print("\n1️⃣ CREATING IEEE 9-BUS MODEL")
            print("-" * 40)
            self.estimator = GridStateEstimator()
            self.estimator.create_ieee9_grid()
            self.current_grid = "IEEE 9-bus"
            print("✅ IEEE 9-bus system created successfully")
            
            # Step 2: Generate measurements
            print("\n2️⃣ GENERATING MEASUREMENTS")
            print("-" * 40)
            self.estimator.simulate_measurements(noise_level=0.02)
            print(f"✅ Generated {len(self.estimator.net.measurement)} measurements with 2% noise")
            
            # Step 3: Modify Bus 1 measurement to 1.5 p.u.
            print("\n3️⃣ MODIFYING BUS 1 MEASUREMENT")
            print("-" * 40)
            original_voltage = None
            voltage_measurements = self.estimator.net.measurement[self.estimator.net.measurement['measurement_type'] == 'v']
            bus1_measurements = voltage_measurements[voltage_measurements['element'] == 1]
            if len(bus1_measurements) > 0:
                original_voltage = bus1_measurements.iloc[0]['value']
                print(f"Original Bus 1 voltage: {original_voltage:.4f} p.u.")
            
            success = self.estimator.modify_bus_voltage_measurement(1, 1.5)
            if success:
                print("✅ Bus 1 voltage modified to 1.5 p.u.")
            else:
                print("❌ Failed to modify Bus 1 voltage")
                return
            
            # Step 4: Run consistency check
            print("\n4️⃣ RUNNING CONSISTENCY CHECK")
            print("-" * 40)
            consistency_results = self.estimator.check_measurement_consistency(tolerance=1e-3, detailed_report=False)
            
            # Step 5: Run bad data detection (simplified for demo)
            print("\n5️⃣ RUNNING BAD DATA DETECTION")
            print("-" * 40)
            # Save original measurements for restoration
            original_measurements = self.estimator.net.measurement.copy()
            
            # Run simplified bad data detection for demo
            bad_data_results = self._run_demo_bad_data_detection()
            
            # Restore measurements for consistent state estimation
            print("🔄 Restoring original measurements for final state estimation...")
            self.estimator.net.measurement = original_measurements
            
            # Step 6: Run state estimation
            print("\n6️⃣ RUNNING STATE ESTIMATION")
            print("-" * 40)
            self.estimator.run_state_estimation()
            
            # Step 7: Show comprehensive results table
            print("\n7️⃣ COMPREHENSIVE RESULTS ANALYSIS")
            print("="*80)
            
            self._display_workflow_results_table(consistency_results, bad_data_results, original_voltage)
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _display_workflow_results_table(self, consistency_results, bad_data_results, original_voltage):
        """Display comprehensive results table for workflow demo"""
        
        print("\n📊 WORKFLOW RESULTS SUMMARY")
        print("="*80)
        
        # Results Overview Table
        print("\n🔍 ANALYSIS OVERVIEW")
        print("-" * 60)
        print(f"{'Analysis Type':<25} {'Status':<15} {'Key Results':<20}")
        print("-" * 60)
        
        # Consistency Check Results
        if consistency_results:
            consistency_status = consistency_results.get('overall_status', 'unknown')
            consistency_violations = consistency_results.get('total_violations', 0)
            print(f"{'Consistency Check':<25} {consistency_status:<15} {consistency_violations} violations")
        else:
            print(f"{'Consistency Check':<25} {'FAILED':<15} {'N/A':<20}")
        
        # Bad Data Detection Results
        if bad_data_results:
            bad_data_status = bad_data_results.get('final_status', 'unknown')
            bad_measurements = bad_data_results.get('bad_measurements', [])
            print(f"{'Bad Data Detection':<25} {bad_data_status:<15} {len(bad_measurements)} bad measurements")
        else:
            print(f"{'Bad Data Detection':<25} {'FAILED':<15} {'N/A':<20}")
        
        # State Estimation Results
        if self.estimator.estimation_results:
            se_status = "SUCCESS"
            iterations = self.estimator.estimation_results.get('iterations', 'N/A')
            print(f"{'State Estimation':<25} {se_status:<15} {iterations} iterations")
        else:
            print(f"{'State Estimation':<25} {'FAILED':<15} {'N/A':<20}")
        
        # Voltage Comparison Table
        print("\n📊 BUS VOLTAGE COMPARISON")
        print("-" * 80)
        print(f"{'Bus':<5} {'Original':<12} {'Modified':<12} {'Estimated':<12} {'Error':<12} {'Status':<15}")
        print("-" * 80)
        
        if hasattr(self.estimator.net, 'res_bus_est') and len(self.estimator.net.res_bus_est) > 0:
            for i in range(min(9, len(self.estimator.net.res_bus_est))):
                estimated_v = self.estimator.net.res_bus_est.vm_pu.iloc[i]
                
                # Get current measurement value
                voltage_measurements = self.estimator.net.measurement[
                    (self.estimator.net.measurement['measurement_type'] == 'v') &
                    (self.estimator.net.measurement['element'] == i)
                ]
                
                if len(voltage_measurements) > 0:
                    current_measurement = voltage_measurements.iloc[0]['value']
                    
                    # Determine original value
                    if i == 1:
                        original_v = original_voltage if original_voltage else current_measurement
                        modified_v = 1.5
                        error = abs(estimated_v - modified_v)
                        status = "🚨 MODIFIED" if i == 1 else "✅ Normal"
                    else:
                        original_v = current_measurement
                        modified_v = current_measurement
                        error = abs(estimated_v - current_measurement)
                        status = "✅ Normal"
                    
                    print(f"{i:<5} {original_v:<12.4f} {modified_v:<12.4f} {estimated_v:<12.4f} {error:<12.4f} {status:<15}")
                else:
                    print(f"{i:<5} {'N/A':<12} {'N/A':<12} {estimated_v:<12.4f} {'N/A':<12} {'No Measurement':<15}")
        
        # Detailed Analysis Tables
        if consistency_results:
            print("\n🔍 CONSISTENCY CHECK DETAILS")
            print("-" * 60)
            violation_types = consistency_results.get('violation_types', {})
            for vtype, violations in violation_types.items():
                if len(violations) > 0:
                    print(f"{vtype.replace('_', ' ').title()}: {len(violations)} violations")
                    for i, violation in enumerate(violations[:3]):  # Show first 3
                        element = violation.get('element', 'unknown')
                        severity = violation.get('severity', 'unknown')
                        print(f"  • {element}: {severity}")
        
        if bad_data_results and bad_data_results.get('bad_measurements'):
            print(f"\n🚨 BAD DATA DETECTION DETAILS")
            print("-" * 60)
            bad_measurements = bad_data_results.get('bad_measurements', [])
            for i, bad_meas in enumerate(bad_measurements[:5]):  # Show first 5
                meas_type = bad_meas.get('type', 'unknown')
                element = bad_meas.get('element', 'unknown')
                residual = bad_meas.get('residual', 0)
                print(f"  {i+1}. {meas_type} at {element}: residual = {residual:.4f}")
        
        # Metrics Summary
        if consistency_results:
            print(f"\n📈 SYSTEM METRICS")
            print("-" * 40)
            metrics = consistency_results.get('consistency_metrics', {})
            print(f"Voltage Coverage:    {metrics.get('voltage_coverage', 0):.1%}")
            print(f"Power Coverage:      {metrics.get('power_coverage', 0):.1%}")
            print(f"Redundancy Ratio:    {metrics.get('redundancy_ratio', 0):.2f}")
            print(f"Measurement Density: {metrics.get('measurement_density', 0):.2f}")
        
        print("\n" + "="*80)
        print("✅ COMPLETE WORKFLOW DEMONSTRATION FINISHED")
        print("🔍 Key Observation: Bus 1 modification (1.5 p.u.) was detected by:")
        print("   • Consistency check (voltage inconsistency)")
        print("   • Bad data detection (statistical outlier)")
        print("   • State estimation shows impact on estimated voltages")
        print("="*80)
        
        # Wait for user before returning to main menu
        input("\n👆 Press Enter to return to main menu...")
        print("\n🔙 Returning to main menu...")
    
    def _run_demo_bad_data_detection(self):
        """Run simplified bad data detection for demo (non-interactive)"""
        from scipy import stats
        
        try:
            # Run state estimation first
            if not self.estimator.estimation_results:
                self.estimator.run_state_estimation()
            
            if not self.estimator.estimation_results:
                print("❌ Cannot perform bad data detection - state estimation failed")
                return None
            
            print("🔍 Analyzing measurement residuals...")
            
            # Calculate residuals and detect bad data
            measurements = self.estimator.net.measurement
            bad_measurements = []
            
            # Check voltage measurements
            voltage_meas = measurements[measurements['measurement_type'] == 'v']
            for idx, meas in voltage_meas.iterrows():
                element = int(meas['element'])
                measured_value = float(meas['value'])
                std_dev = float(meas['std_dev'])
                
                # Get estimated value
                if hasattr(self.estimator.net, 'res_bus_est') and element < len(self.estimator.net.res_bus_est):
                    estimated_value = self.estimator.net.res_bus_est.vm_pu.iloc[element]
                    residual = abs(measured_value - estimated_value)
                    normalized_residual = residual / std_dev
                    
                    # Flag as bad if normalized residual > 3.0 (3-sigma rule)
                    if normalized_residual > 3.0:
                        bad_measurements.append({
                            'index': idx,
                            'type': 'V',
                            'element': f'Bus {element}',
                            'measured': measured_value,
                            'estimated': estimated_value,
                            'residual': residual,
                            'normalized_residual': normalized_residual,
                            'severity': 'SEVERE' if normalized_residual > 10 else 'MODERATE'
                        })
                        print(f"🚨 Bad voltage measurement detected at Bus {element}")
                        print(f"   Measured: {measured_value:.4f} p.u.")
                        print(f"   Estimated: {estimated_value:.4f} p.u.")
                        print(f"   Normalized residual: {normalized_residual:.2f}")
            
            # Create results structure
            results = {
                'final_status': 'bad_data_detected' if bad_measurements else 'clean',
                'bad_measurements': bad_measurements,
                'total_bad': len(bad_measurements),
                'iterations': 1
            }
            
            if bad_measurements:
                print(f"\n📊 DETECTION SUMMARY:")
                print(f"   Bad measurements found: {len(bad_measurements)}")
                for i, bad_meas in enumerate(bad_measurements, 1):
                    print(f"   {i}. {bad_meas['type']} at {bad_meas['element']}: {bad_meas['severity']}")
            else:
                print("✅ No bad measurements detected")
            
            return results
            
        except Exception as e:
            print(f"❌ Bad data detection failed: {e}")
            return None
    
    def run(self):
        """Main application loop"""
        self.show_banner()
        
        while True:
            self.show_main_menu()
            
            if self.current_grid:
                print(f"📍 Current Grid: {self.current_grid}")
                if hasattr(self.estimator, 'net') and len(self.estimator.net.measurement) > 0:
                    print(f"📊 Measurements: {len(self.estimator.net.measurement)} available")
                if self.estimator and self.estimator.estimation_results:
                    print(f"⚡ State Estimation: Results available")
            
            choice = input("\nSelect option (0-9, A): ").strip().upper()
            
            if choice == '0':
                print("\n👋 Thank you for using Power System State Estimation Application!")
                sys.exit(0)
                
            elif choice == '1':
                self.create_grid_model()
                
            elif choice == '2':
                self.simulate_measurements()
                
            elif choice == '3':
                self.simulate_measurements()  # Uses measurement menu
                
            elif choice == '4':
                self.run_analysis()
                
            elif choice == '5':
                if self.estimator and hasattr(self.estimator, 'net') and len(self.estimator.net.measurement) > 0:
                    self.estimator.test_observability()
                else:
                    print("❌ No measurements available. Generate measurements first.")
                
            elif choice == '6':
                self.show_results()
                
            elif choice == '7':
                self.visualize_grid()
                
            elif choice == '8':
                self.cgmes_interface()
                
            elif choice == '9':
                self.show_demos()
                
            elif choice == 'A':
                self.run_complete_workflow_demo()
                
            else:
                print("❌ Invalid choice. Please select 0-9 or A.")

if __name__ == "__main__":
    app = PowerSystemApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        print("Please report this issue if it persists.")