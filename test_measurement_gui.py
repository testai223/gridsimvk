#!/usr/bin/env python3
"""
Test script for measurement management GUI functionality
"""

import tkinter as tk
import sys
import numpy as np

# Set matplotlib backend
import matplotlib
matplotlib.use('TkAgg')

from simple_gui import PowerSystemGUI

def test_measurement_gui():
    """Test measurement management GUI"""
    print("Testing measurement management GUI...")
    print("=" * 50)
    
    # Create GUI
    root = tk.Tk()
    app = PowerSystemGUI(root)
    
    def run_automated_test():
        """Run automated test sequence"""
        try:
            print("Starting automated measurement management test...")
            
            # 1. Create grid
            app.create_ieee9_grid()
            app.log("✅ Created IEEE 9-bus grid")
            
            # 2. Generate measurements
            app.noise_var.set("0.02")
            app.generate_measurements()
            app.log("✅ Generated measurements with 2% noise")
            
            # 3. Switch to measurement management tab
            root.after(1000, lambda: app.notebook.select(4))  # Measurement Management tab
            app.log("🔄 Switching to Measurement Management tab...")
            
            # 4. Test refresh measurements display
            root.after(2000, lambda: app.refresh_measurement_display())
            app.log("🔄 Refreshing measurement display...")
            
            # 5. Test backup measurements
            root.after(3000, lambda: app.backup_measurements())
            app.log("🔄 Testing backup functionality...")
            
            # 6. Test some removal
            def test_removal():
                app.log("🔄 Testing measurement removal...")
                try:
                    # Select a few measurements for removal (simulate user selection)
                    if hasattr(app, 'measurement_tree') and app.measurement_tree.get_children():
                        # Get first 3 measurement items
                        children = app.measurement_tree.get_children()[:3]
                        for child in children:
                            app.measurement_tree.selection_add(child)
                        
                        # Remove selected measurements
                        app.remove_selected_measurements()
                        app.log("✅ Removed selected measurements")
                        
                        # Refresh display
                        app.refresh_measurement_display()
                        app.log("✅ Refreshed display after removal")
                        
                except Exception as e:
                    app.log(f"❌ Removal test error: {e}")
            
            root.after(4000, test_removal)
            
            # 7. Test restore
            def test_restore():
                app.log("🔄 Testing measurement restore...")
                app.restore_measurements()
                app.refresh_measurement_display()
                app.log("✅ Measurements restored and display refreshed")
                
                # Final success message
                app.log("🎉 All measurement management GUI tests completed!")
                app.log("📋 You can now manually test the interface:")
                app.log("   • Filter measurements by type or element")
                app.log("   • Select/deselect measurements")
                app.log("   • Remove measurements manually")
                app.log("   • Simulate failures")
                app.log("   • Use backup/restore functions")
            
            root.after(6000, test_restore)
            
        except Exception as e:
            app.log(f"❌ Automated test error: {e}")
    
    # Schedule automated test
    root.after(500, run_automated_test)
    
    # Add some initial instructions
    instructions = """
🧪 MEASUREMENT MANAGEMENT GUI TEST

This test will automatically:
1. Create IEEE 9-bus grid
2. Generate measurements
3. Switch to Measurement Management tab
4. Test refresh, backup, removal, and restore functions

Manual testing after automation:
• Try the filter controls
• Select and remove measurements
• Simulate measurement failures
• Test backup and restore functions

Press Ctrl+C to exit when done.
"""
    
    app.log(instructions)
    
    def on_closing():
        if tk.messagebox.askokcancel("Quit", "Exit the GUI test?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
        return True
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
        return True
    except Exception as e:
        print(f"❌ GUI test error: {e}")
        return False

if __name__ == "__main__":
    success = test_measurement_gui()
    print("Test completed!")
    sys.exit(0 if success else 1)