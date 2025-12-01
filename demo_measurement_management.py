#!/usr/bin/env python3
"""
Comprehensive demo of measurement management functionality
"""

import tkinter as tk
import sys
import numpy as np

# Set matplotlib backend
import matplotlib
matplotlib.use('TkAgg')

from simple_gui import PowerSystemGUI

def demo_measurement_management():
    """Demo measurement management features"""
    print("🔌 MEASUREMENT MANAGEMENT DEMO")
    print("=" * 60)
    print("This demo showcases the comprehensive measurement management")
    print("system with the following features:")
    print()
    print("📊 FEATURES DEMONSTRATED:")
    print("• Measurement selection and filtering")
    print("• Bulk measurement removal operations")
    print("• Measurement failure simulation")
    print("• Backup and restore functionality")
    print("• Observability and redundancy analysis")
    print("• Real-time display updates")
    print("• Integration with auto-refresh system")
    print("=" * 60)
    
    # Create GUI
    root = tk.Tk()
    app = PowerSystemGUI(root)
    
    def run_automated_demo():
        """Run comprehensive automated demo"""
        try:
            print("Starting comprehensive measurement management demo...")
            
            # Step 1: Create grid and measurements
            app.log("🏗️  STEP 1: Creating IEEE 9-bus grid...")
            app.create_ieee9_grid()
            
            app.log("📏 STEP 2: Generating measurements with 2% noise...")
            app.noise_var.set("0.02")
            app.generate_measurements()
            
            # Step 3: Switch to measurement management tab
            root.after(2000, lambda: [
                app.notebook.select(4),  # Measurement Management tab
                app.log("🔍 STEP 3: Switching to Measurement Management tab...")
            ])
            
            # Step 4: Initial analysis
            def step4_analysis():
                app.log("📊 STEP 4: Performing initial observability analysis...")
                app.analyze_observability()
                app.log("📈 STEP 4b: Checking measurement redundancy...")
                app.check_measurement_redundancy()
            
            root.after(3500, step4_analysis)
            
            # Step 5: Backup measurements
            def step5_backup():
                app.log("💾 STEP 5: Creating measurement backup...")
                app.backup_measurements()
                app.log("✅ Backup completed - measurements are now protected")
            
            root.after(5000, step5_backup)
            
            # Step 6: Test filtering and selection
            def step6_filtering():
                app.log("🔍 STEP 6: Testing measurement filtering...")
                app.filter_type_var.set("v")  # Filter to voltage measurements
                app.refresh_measurement_display()
                app.log("   Filtered to show only voltage measurements")
                
                # Select all visible measurements
                root.after(1000, lambda: [
                    app.select_all_measurements(),
                    app.log("   Selected all voltage measurements")
                ])
            
            root.after(6500, step6_filtering)
            
            # Step 7: Remove selected measurements
            def step7_removal():
                app.log("❌ STEP 7: Removing selected voltage measurements...")
                # Clear filter first to see all measurements
                app.clear_measurement_filter()
                # Remove some voltage measurements by type
                try:
                    result = app.estimator.remove_measurements_by_type('v', element_filter=[0, 1, 2])
                    app.log(f"   Removed voltage measurements from buses 0, 1, 2")
                    app.refresh_measurement_display()
                    
                    # Check impact on observability
                    app.log("🔍 STEP 7b: Analyzing impact on observability...")
                    app.analyze_observability()
                except Exception as e:
                    app.log(f"❌ Removal error: {e}")
            
            root.after(8500, step7_removal)
            
            # Step 8: Simulate failures
            def step8_failures():
                app.log("💥 STEP 8: Simulating random measurement failures...")
                app.failure_rate_var.set("0.15")  # 15% failure rate
                try:
                    result = app.estimator.simulate_measurement_failures(0.15, ['random'])
                    if result[0]:
                        app.log(f"   Simulated failures: {result[1]}")
                        app.refresh_measurement_display()
                        
                        # Check observability after failures
                        app.log("🔍 STEP 8b: Checking observability after failures...")
                        app.analyze_observability()
                except Exception as e:
                    app.log(f"❌ Failure simulation error: {e}")
            
            root.after(11000, step8_failures)
            
            # Step 9: Restore measurements
            def step9_restore():
                app.log("🔧 STEP 9: Restoring measurements from backup...")
                app.restore_measurements()
                app.log("✅ All measurements restored to original state")
                
                # Final analysis
                app.log("📊 STEP 9b: Final observability check...")
                app.analyze_observability()
            
            root.after(13500, step9_restore)
            
            # Step 10: Final demonstration
            def step10_final():
                app.log("🎉 STEP 10: Demo complete - Manual testing instructions:")
                app.log("")
                app.log("🖱️  MANUAL TESTING INSTRUCTIONS:")
                app.log("• Use filter controls to filter by type (v, p, q)")
                app.log("• Filter by element number (bus or line index)")
                app.log("• Click measurements to select/deselect")
                app.log("• Use bulk selection operations")
                app.log("• Remove selected measurements and see impact")
                app.log("• Test failure simulation with different rates")
                app.log("• Use backup/restore for safety")
                app.log("• Run observability analysis after changes")
                app.log("• Check redundancy analysis results")
                app.log("")
                app.log("🔄 AUTO-REFRESH: All changes automatically update")
                app.log("the grid visualization when auto-refresh is enabled!")
                app.log("")
                app.log("✅ MEASUREMENT MANAGEMENT DEMO COMPLETE!")
            
            root.after(16000, step10_final)
            
        except Exception as e:
            app.log(f"❌ Demo error: {e}")
    
    # Schedule demo after GUI is ready
    root.after(1000, run_automated_demo)
    
    # Add demo instructions
    instructions = """
🎯 MEASUREMENT MANAGEMENT DEMO

This demonstration will show:
1. Grid creation and measurement generation
2. Observability and redundancy analysis
3. Measurement filtering and selection
4. Bulk removal operations
5. Failure simulation
6. Backup and restore functionality
7. Real-time impact analysis

The demo runs automatically, then you can test manually!
"""
    
    app.log(instructions)
    
    # Enable auto-refresh for the demo
    app.auto_refresh_var.set(True)
    app.log("🔄 Auto-refresh enabled for real-time updates")
    
    def on_closing():
        if tk.messagebox.askokcancel("Quit", "Exit the measurement management demo?"):
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
    success = demo_measurement_management()
    print("Demo completed!")
    sys.exit(0 if success else 1)