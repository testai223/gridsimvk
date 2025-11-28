#!/usr/bin/env python3
"""
Demo script showing the improved GUI table functionality
"""

import tkinter as tk
import numpy as np
import sys

# Set matplotlib backend
import matplotlib
matplotlib.use('TkAgg')

from simple_gui import PowerSystemGUI

def main():
    """Run the GUI demo with automatic workflow"""
    print("🔌 Starting GUI Demo with Table Display")
    print("="*50)
    print("This demo will:")
    print("1. Launch the GUI")
    print("2. Automatically run a complete workflow")
    print("3. Display results in the improved table format")
    print("="*50)
    
    # Create and configure the GUI
    root = tk.Tk()
    app = PowerSystemGUI(root)
    
    # Auto-run demo after GUI is ready
    def run_auto_demo():
        """Automatically run demo workflow"""
        try:
            print("Starting automatic demo...")
            
            # Use the built-in quick demo
            app.quick_demo()
            
            # After demo completes, show the results table
            root.after(2000, lambda: app.notebook.select(1))  # Switch to table tab after 2 seconds
            
        except Exception as e:
            app.log(f"❌ Auto demo error: {e}")
    
    # Schedule the auto demo to run after GUI is displayed
    root.after(1000, run_auto_demo)
    
    # Add instructions to the GUI
    instructions = """
🎯 GUI TABLE DEMO INSTRUCTIONS:

The demo will automatically:
1. Create IEEE 9-bus grid
2. Generate measurements with 2% noise
3. Run state estimation
4. Display results in the table

TABLE FEATURES:
• Two tabs: Console Output & Results Table
• Color-coded rows for better readability
• Error highlighting (red=high, orange=medium)
• Sortable columns and scrollbars
• Professional formatting with monospace font

MANUAL TESTING:
• Try modifying bus voltages
• Run state estimation again
• Use "Refresh Table" button
• Compare different scenarios
"""
    
    app.log(instructions)
    
    # Window closing handler
    def on_closing():
        if tk.messagebox.askokcancel("Quit", "Exit the GUI demo?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    print("GUI launched! Check the application window.")
    print("The demo will run automatically in 1 second.")
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted")
    finally:
        print("Demo completed!")

if __name__ == "__main__":
    main()