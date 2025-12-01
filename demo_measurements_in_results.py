#!/usr/bin/env python3
"""
Demo showing measurements in results table with management features
"""

import tkinter as tk
import sys
import numpy as np

# Set matplotlib backend
import matplotlib
matplotlib.use('TkAgg')

from simple_gui import PowerSystemGUI

def demo_measurements_in_results():
    """Demo measurements display in results table"""
    print("🔌 MEASUREMENTS IN RESULTS TABLE DEMO")
    print("=" * 60)
    print("This demo shows how measurements are displayed in the")
    print("results table and how they integrate with management features:")
    print()
    print("📊 FEATURES DEMONSTRATED:")
    print("• Immediate measurement display in results table")
    print("• Load flow comparison with measurement errors")
    print("• Real-time updates with measurement changes")
    print("• Integration with state estimation results")
    print("• Measurement management impact visualization")
    print("=" * 60)
    
    # Create GUI
    root = tk.Tk()
    app = PowerSystemGUI(root)
    
    def run_results_demo():
        """Run automated demo focused on results table"""
        try:
            print("Starting measurements in results table demo...")
            
            # Step 1: Create grid and show immediate results
            app.log("🏗️  STEP 1: CREATING GRID AND SHOWING IMMEDIATE RESULTS")
            app.log("=" * 55)
            app.create_ieee9_grid()
            app.log("✅ Created IEEE 9-bus grid")
            
            app.log("📊 Generating measurements and displaying in results table...")
            app.noise_var.set("0.02")
            app.generate_measurements()
            
            # Switch to results table tab
            root.after(2000, lambda: [
                app.notebook.select(1),  # Results Table tab
                app.log("🔍 Switched to Results Table - measurements now visible!")
            ])
            
            # Step 2: Explain table contents
            def step2_explain():
                app.log("\n📋 STEP 2: UNDERSTANDING THE RESULTS TABLE")
                app.log("=" * 55)
                app.log("The results table now shows all measurements with:")
                app.log("• Measurement descriptions (V_mag, P_from, Q_from)")
                app.log("• Units (p.u., MW, MVAr)")
                app.log("• Load Flow values (true/reference values)")
                app.log("• Measured values (with simulated noise)")
                app.log("• Measurement errors compared to load flow")
                app.log("✅ Click 'Refresh Table' button to update display")
            
            root.after(4000, step2_explain)
            
            # Step 3: Run state estimation
            def step3_state_estimation():
                app.log("\n⚡ STEP 3: RUNNING STATE ESTIMATION")
                app.log("=" * 55)
                app.run_state_estimation()
                app.log("✅ State estimation completed")
                app.log("📊 Results table now shows state estimation comparison:")
                app.log("• Estimated values from state estimator")
                app.log("• Estimation errors vs true values")
                app.log("• Enhanced error analysis and validation")
            
            root.after(7000, step3_state_estimation)
            
            # Step 4: Switch to measurement management
            def step4_measurement_mgmt():
                app.log("\n🔧 STEP 4: MEASUREMENT MANAGEMENT INTEGRATION")
                app.log("=" * 55)
                
                # Switch to measurement management tab
                app.notebook.select(4)  # Measurement Management tab
                app.log("🔍 Switched to Measurement Management tab")
                app.log("📊 You can now see measurements in both tabs:")
                app.log("• Results Table: Shows measurement values and errors")
                app.log("• Measurement Management: Shows measurement details")
                
                # Demonstrate removal
                app.log("\n❌ Demonstrating measurement removal impact...")
                try:
                    result = app.estimator.remove_measurements_by_type('v', element_filter=[1, 3])
                    app.log(f"Removed voltage measurements from buses 1, 3")
                    app.log("🔄 Auto-refresh will update Results Table...")
                except Exception as e:
                    app.log(f"❌ Removal error: {e}")
            
            root.after(10500, step4_measurement_mgmt)
            
            # Step 5: Show table update
            def step5_show_update():
                app.log("\n🔄 STEP 5: REAL-TIME TABLE UPDATES")
                app.log("=" * 55)
                
                # Switch back to results table
                app.notebook.select(1)  # Results Table tab
                app.log("🔍 Switched back to Results Table")
                app.log("✅ Notice fewer voltage measurements in the table")
                app.log("📊 The table automatically reflects measurement changes")
            
            root.after(13500, step5_show_update)
            
            # Step 6: Demonstrate estimation
            def step6_estimation():
                app.log("\n🔮 STEP 6: MISSING MEASUREMENT ESTIMATION")
                app.log("=" * 55)
                
                # Switch to measurement management
                app.notebook.select(4)  # Measurement Management tab
                
                try:
                    # Estimate missing measurements
                    app.estimation_method_var.set("interpolation")
                    app.estimation_noise_var.set("0.02")
                    app.estimate_missing_measurements()
                    app.log("✅ Added estimated measurements")
                    
                    # Switch back to results table
                    root.after(2000, lambda: [
                        app.notebook.select(1),
                        app.log("📊 Results Table updated with estimated measurements!")
                    ])
                    
                except Exception as e:
                    app.log(f"❌ Estimation error: {e}")
            
            root.after(16500, step6_estimation)
            
            # Step 7: Final instructions
            def step7_final():
                app.log("\n🎉 STEP 7: DEMO COMPLETE - MANUAL TESTING")
                app.log("=" * 55)
                app.log("✅ Measurements are now fully integrated in results table!")
                app.log("")
                app.log("🖱️  TRY THESE MANUAL TESTS:")
                app.log("• Switch between Results Table and Measurement Management tabs")
                app.log("• Remove measurements and see real-time table updates")
                app.log("• Add estimated measurements and see them appear")
                app.log("• Use 'Refresh Table' button for manual updates")
                app.log("• Run state estimation to see estimation comparison")
                app.log("• Try different measurement management operations")
                app.log("")
                app.log("🔄 AUTO-REFRESH ENABLED:")
                app.log("All measurement changes automatically update the results table!")
                app.log("")
                app.log("✅ MEASUREMENTS IN RESULTS TABLE DEMO COMPLETE!")
            
            root.after(20000, step7_final)
            
        except Exception as e:
            app.log(f"❌ Demo error: {e}")
    
    # Schedule demo
    root.after(1000, run_results_demo)
    
    # Add instructions
    instructions = """
🎯 MEASUREMENTS IN RESULTS TABLE DEMO

This demonstration shows how measurements are now
fully integrated into the results table:

IMMEDIATE DISPLAY:
• Measurements appear as soon as they're generated
• Load flow comparison shows measurement accuracy
• Real-time updates with measurement changes

MANAGEMENT INTEGRATION:
• Measurement removal immediately updates table
• Estimated measurements appear automatically
• State estimation enhances the comparison

The demo shows automatic table updates and then
allows manual testing of all features!
"""
    
    app.log(instructions)
    
    # Enable auto-refresh for the demo
    app.auto_refresh_var.set(True)
    app.log("🔄 Auto-refresh enabled for real-time table updates")
    
    def on_closing():
        if tk.messagebox.askokcancel("Quit", "Exit the measurements in results demo?"):
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
    success = demo_measurements_in_results()
    print("Measurements in results table demo completed!")
    sys.exit(0 if success else 1)