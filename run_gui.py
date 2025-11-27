#!/usr/bin/env python3
"""
Startup script for Power System GUI that handles macOS threading properly
"""

import sys
import os

def main():
    """Main function with proper macOS handling"""
    # Set matplotlib backend before importing GUI
    import matplotlib
    matplotlib.use('TkAgg')
    
    # Import and run GUI
    from simple_gui import PowerSystemGUI
    import tkinter as tk
    
    print("🔌 Starting Power System State Estimation GUI...")
    print("Features available:")
    print("• IEEE 9-bus and ENTSO-E grid models")
    print("• Measurement simulation and modification")
    print("• State estimation and observability analysis")
    print("• Bad data detection and consistency checking")
    print("• Interactive visualization")
    print("="*60)
    
    root = tk.Tk()
    app = PowerSystemGUI(root)
    
    # Window closing handler
    def on_closing():
        import tkinter.messagebox as messagebox
        if messagebox.askokcancel("Quit", "Do you want to quit the Power System GUI?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 GUI application interrupted")
    except Exception as e:
        print(f"❌ GUI error: {e}")
    finally:
        print("GUI application closed")

if __name__ == "__main__":
    main()