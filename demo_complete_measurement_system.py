#!/usr/bin/env python3
"""
Complete demonstration of measurement management system with estimation capabilities
"""

import tkinter as tk
import sys
import numpy as np

# Set matplotlib backend
import matplotlib
matplotlib.use('TkAgg')

from simple_gui import PowerSystemGUI

def demo_complete_measurement_system():
    """Demo complete measurement management system including estimation"""
    print("🔌 COMPLETE MEASUREMENT MANAGEMENT SYSTEM DEMO")
    print("=" * 70)
    print("This comprehensive demo showcases the full measurement management")
    print("system with advanced estimation capabilities:")
    print()
    print("🎯 FEATURES DEMONSTRATED:")
    print("📊 Core Measurement Management:")
    print("• Measurement selection, filtering, and removal")
    print("• Backup and restore functionality")
    print("• Failure simulation and impact analysis")
    print("• Real-time observability monitoring")
    print()
    print("🔮 Advanced Estimation Capabilities:")
    print("• Missing measurement identification")
    print("• Interpolation-based estimation")
    print("• Load-flow based estimation")
    print("• Strategic measurement placement")
    print("• Observability optimization")
    print()
    print("⚡ Integration Features:")
    print("• Auto-refresh system integration")
    print("• State estimation compatibility")
    print("• Real-time network analysis")
    print("=" * 70)
    
    # Create GUI
    root = tk.Tk()
    app = PowerSystemGUI(root)
    
    def run_comprehensive_demo():
        """Run comprehensive automated demo"""
        try:
            print("Starting comprehensive measurement system demo...")
            
            # Phase 1: Setup and Initial Analysis
            app.log("🏗️  PHASE 1: SYSTEM SETUP")
            app.log("=" * 50)
            app.create_ieee9_grid()
            app.log("✅ Created IEEE 9-bus grid")
            
            app.noise_var.set("0.02")
            app.generate_measurements()
            app.log("✅ Generated full measurement set with 2% noise")
            
            # Switch to measurement management tab
            root.after(2000, lambda: [
                app.notebook.select(4),
                app.log("🔍 Switched to Measurement Management tab")
            ])
            
            # Phase 2: Initial Analysis
            def phase2_initial_analysis():
                app.log("\n📊 PHASE 2: INITIAL SYSTEM ANALYSIS")
                app.log("=" * 50)
                app.analyze_observability()
                app.check_measurement_redundancy()
                app.backup_measurements()
                app.log("✅ System analyzed and backed up")
            
            root.after(3500, phase2_initial_analysis)
            
            # Phase 3: Create Measurement Gaps
            def phase3_create_gaps():
                app.log("\n❌ PHASE 3: CREATING MEASUREMENT GAPS")
                app.log("=" * 50)
                
                # Remove some voltage measurements
                try:
                    result = app.estimator.remove_measurements_by_type('v', element_filter=[1, 3, 5])
                    app.log(f"Removed voltage measurements from buses 1, 3, 5")
                    
                    # Remove some power measurements
                    result = app.estimator.remove_measurements_by_type('p', element_filter=[2, 4])
                    app.log(f"Removed power measurements from lines 2, 4")
                    
                    app.refresh_measurement_display()
                    app.log("✅ Created realistic measurement gaps")
                    
                    # Analyze impact
                    app.log("\n🔍 Analyzing impact of measurement gaps...")
                    app.analyze_observability()
                    
                except Exception as e:
                    app.log(f"❌ Error creating gaps: {e}")
            
            root.after(6000, phase3_create_gaps)
            
            # Phase 4: Identify Missing Measurements
            def phase4_identify_missing():
                app.log("\n🔍 PHASE 4: MISSING MEASUREMENT ANALYSIS")
                app.log("=" * 50)
                app.identify_missing_measurements()
                app.log("✅ Missing measurements identified")
            
            root.after(9000, phase4_identify_missing)
            
            # Phase 5: Test Interpolation Estimation
            def phase5_interpolation():
                app.log("\n🔮 PHASE 5: INTERPOLATION-BASED ESTIMATION")
                app.log("=" * 50)
                app.estimation_method_var.set("interpolation")
                app.estimation_noise_var.set("0.02")
                app.estimate_missing_measurements()
                app.log("✅ Applied interpolation-based estimation")
                
                # Check improvement
                app.log("\n📈 Checking observability improvement...")
                app.analyze_observability()
            
            root.after(12000, phase5_interpolation)
            
            # Phase 6: Create More Gaps and Test Load-Flow
            def phase6_loadflow():
                app.log("\n⚡ PHASE 6: LOAD-FLOW BASED ESTIMATION")
                app.log("=" * 50)
                
                # Remove more measurements
                try:
                    result = app.estimator.remove_measurements_by_type('v', element_filter=[2, 6])
                    app.log(f"Removed additional voltage measurements")
                    app.refresh_measurement_display()
                    
                    # Use load-flow estimation
                    app.estimation_method_var.set("load_flow")
                    app.estimation_noise_var.set("0.01")
                    app.estimate_missing_measurements()
                    app.log("✅ Applied load-flow based estimation")
                    
                except Exception as e:
                    app.log(f"❌ Error in load-flow estimation: {e}")
            
            root.after(15500, phase6_loadflow)
            
            # Phase 7: Strategic Measurement Addition
            def phase7_strategic():
                app.log("\n🎯 PHASE 7: STRATEGIC MEASUREMENT OPTIMIZATION")
                app.log("=" * 50)
                app.add_strategic_measurements()
                app.log("✅ Added strategic measurements for optimal observability")
                
                # Final analysis
                app.log("\n📊 Final system analysis...")
                app.analyze_observability()
                app.check_measurement_redundancy()
            
            root.after(18500, phase7_strategic)
            
            # Phase 8: Test Failure Simulation with Recovery
            def phase8_failure_recovery():
                app.log("\n💥 PHASE 8: FAILURE SIMULATION & RECOVERY")
                app.log("=" * 50)
                
                # Simulate failures
                app.failure_rate_var.set("0.15")
                try:
                    result = app.estimator.simulate_measurement_failures(0.15, ['random'])
                    app.log(f"Simulated 15% random failures")
                    app.refresh_measurement_display()
                    
                    # Check impact
                    app.log("Checking failure impact...")
                    app.analyze_observability()
                    
                    # Restore and re-estimate
                    app.log("\n🔧 Performing recovery...")
                    app.restore_measurements()
                    app.estimate_missing_measurements()
                    app.log("✅ System recovered with estimation")
                    
                except Exception as e:
                    app.log(f"❌ Error in failure simulation: {e}")
            
            root.after(22000, phase8_failure_recovery)
            
            # Phase 9: Final State Estimation Test
            def phase9_final_test():
                app.log("\n⚡ PHASE 9: STATE ESTIMATION VALIDATION")
                app.log("=" * 50)
                
                try:
                    app.run_state_estimation()
                    app.log("✅ State estimation successful with estimated measurements")
                    
                    if hasattr(app.estimator, 'estimation_results') and app.estimator.estimation_results:
                        app.log("State estimation converged successfully")
                        app.refresh_results_table()
                    
                except Exception as e:
                    app.log(f"State estimation: {e}")
                
                app.log("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
                app.log("=" * 50)
                app.log("")
                app.log("🖱️  MANUAL TESTING INSTRUCTIONS:")
                app.log("• Test different estimation methods (interpolation vs load-flow)")
                app.log("• Adjust noise levels for estimated measurements")
                app.log("• Try strategic measurement placement")
                app.log("• Simulate different failure scenarios")
                app.log("• Use backup/restore for safe experimentation")
                app.log("• Monitor real-time observability changes")
                app.log("• Test state estimation with various measurement sets")
                app.log("")
                app.log("🔄 AUTO-REFRESH: All changes automatically update")
                app.log("the grid visualization and analysis results!")
                app.log("")
                app.log("✅ COMPLETE MEASUREMENT MANAGEMENT SYSTEM READY!")
            
            root.after(25500, phase9_final_test)
            
        except Exception as e:
            app.log(f"❌ Demo error: {e}")
    
    # Schedule comprehensive demo
    root.after(1000, run_comprehensive_demo)
    
    # Add instructions
    instructions = """
🎯 COMPLETE MEASUREMENT MANAGEMENT SYSTEM DEMO

This demonstration showcases the full capabilities of our
advanced measurement management system including:

CORE FEATURES:
• Measurement manipulation and analysis
• Real-time observability monitoring
• Backup and restore operations

ESTIMATION CAPABILITIES:
• Missing measurement identification
• Multiple estimation methods
• Strategic measurement placement
• Automatic observability optimization

The demo runs automatically through 9 phases, then allows
manual testing of all features!

Enable auto-refresh for real-time updates!
"""
    
    app.log(instructions)
    
    # Enable auto-refresh for the demo
    app.auto_refresh_var.set(True)
    app.log("🔄 Auto-refresh enabled for comprehensive system updates")
    
    def on_closing():
        if tk.messagebox.askokcancel("Quit", "Exit the complete measurement system demo?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
        return True
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
        return True
    except Exception as e:
        print(f"❌ Demo error: {e}")
        return False

if __name__ == "__main__":
    success = demo_complete_measurement_system()
    print("Complete measurement system demo finished!")
    sys.exit(0 if success else 1)