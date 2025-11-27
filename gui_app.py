#!/usr/bin/env python3
"""
GUI Application for Power System State Estimation
Provides a user-friendly interface for all grid simulation functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
import numpy as np
from threading import Thread

from grid_state_estimator import GridStateEstimator

class PowerSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Power System State Estimation GUI")
        self.root.geometry("1200x800")
        
        # Application state
        self.estimator = None
        self.current_grid = None
        
        # Create GUI components
        self.create_widgets()
        
    def create_widgets(self):
        """Create main GUI layout"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔌 Power System State Estimation", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Left panel - Controls
        self.create_control_panel(main_frame)
        
        # Right panel - Output and results
        self.create_output_panel(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_control_panel(self, parent):
        """Create control panel with buttons and options"""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        
        # Grid Model Section
        grid_frame = ttk.LabelFrame(control_frame, text="Grid Model", padding="5")
        grid_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        grid_frame.columnconfigure(0, weight=1)
        
        ttk.Button(grid_frame, text="Create IEEE 9-bus", 
                  command=self.create_ieee9_grid).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(grid_frame, text="Create ENTSO-E Grid", 
                  command=self.create_entso_grid).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Measurements Section
        meas_frame = ttk.LabelFrame(control_frame, text="Measurements", padding="5")
        meas_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        meas_frame.columnconfigure(0, weight=1)
        
        # Noise level control
        noise_frame = ttk.Frame(meas_frame)
        noise_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        noise_frame.columnconfigure(1, weight=1)
        
        ttk.Label(noise_frame, text="Noise Level:").grid(row=0, column=0, padx=(0, 5))
        self.noise_var = tk.StringVar(value="0.02")
        noise_spinbox = ttk.Spinbox(noise_frame, from_=0.0, to=0.1, increment=0.01, 
                                   textvariable=self.noise_var, width=8)
        noise_spinbox.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Button(meas_frame, text="Generate Measurements", 
                  command=self.generate_measurements).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(meas_frame, text="List Measurements", 
                  command=self.list_measurements).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Measurement Modification Section
        mod_frame = ttk.LabelFrame(meas_frame, text="Modify Measurements", padding="5")
        mod_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        mod_frame.columnconfigure(1, weight=1)
        
        # Bus voltage modification
        ttk.Label(mod_frame, text="Bus ID:").grid(row=0, column=0, padx=(0, 5))
        self.bus_id_var = tk.StringVar()
        ttk.Entry(mod_frame, textvariable=self.bus_id_var, width=8).grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(mod_frame, text="Voltage (p.u.):").grid(row=1, column=0, padx=(0, 5))
        self.voltage_var = tk.StringVar()
        ttk.Entry(mod_frame, textvariable=self.voltage_var, width=8).grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        ttk.Button(mod_frame, text="Modify Bus Voltage", 
                  command=self.modify_bus_voltage).grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        # Analysis Section
        analysis_frame = ttk.LabelFrame(control_frame, text="Analysis", padding="5")
        analysis_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        analysis_frame.columnconfigure(0, weight=1)
        
        ttk.Button(analysis_frame, text="Run State Estimation", 
                  command=self.run_state_estimation).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(analysis_frame, text="Test Observability", 
                  command=self.test_observability).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(analysis_frame, text="Check Consistency", 
                  command=self.check_consistency).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(analysis_frame, text="Detect Bad Data", 
                  command=self.detect_bad_data).grid(row=3, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(analysis_frame, text="Show Results", 
                  command=self.show_results).grid(row=4, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(analysis_frame, text="Visualize Grid", 
                  command=self.visualize_grid).grid(row=5, column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Demo Section
        demo_frame = ttk.LabelFrame(control_frame, text="Demos", padding="5")
        demo_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        demo_frame.columnconfigure(0, weight=1)
        
        ttk.Button(demo_frame, text="Complete Workflow Demo", 
                  command=self.run_complete_demo).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(demo_frame, text="Clear Output", 
                  command=self.clear_output).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        
    def create_output_panel(self, parent):
        """Create output panel for results and logs"""
        output_frame = ttk.LabelFrame(parent, text="Output & Results", padding="10")
        output_frame.grid(row=1, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(output_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Console output tab
        console_frame = ttk.Frame(self.notebook)
        self.notebook.add(console_frame, text="Console Output")
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(console_frame, height=30, width=80)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Results tab
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results")
        results_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=0)
        results_frame.rowconfigure(2, weight=1)

        ttk.Label(results_frame, text="State Estimation Summary", font=("Arial", 11, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )

        columns = ("Bus", "True Vm (p.u.)", "Estimated Vm (p.u.)", "Error (%)", "Angle (deg)")
        self.results_table = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.results_table.heading(col, text=col)
            self.results_table.column(col, width=130, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_table.yview)
        self.results_table.configure(yscrollcommand=scrollbar.set)

        self.results_table.grid(row=1, column=0, sticky=(tk.W, tk.E))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, width=80)
        self.results_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
    def create_status_bar(self, parent):
        """Create status bar at bottom"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="Status:").grid(row=0, column=0, padx=(0, 5))
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=1, sticky=(tk.W))
        
        # Grid info
        self.grid_info_var = tk.StringVar(value="No grid loaded")
        ttk.Label(status_frame, textvariable=self.grid_info_var).grid(row=0, column=2, padx=(20, 0))
        
    def log_output(self, message):
        """Add message to console output"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
    def log_results(self, message):
        """Add message to results tab"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def update_grid_info(self):
        """Update grid information display"""
        if self.current_grid:
            info = f"Grid: {self.current_grid}"
            if hasattr(self.estimator, 'net') and self.estimator.net is not None:
                meas_count = len(self.estimator.net.measurement) if hasattr(self.estimator.net, 'measurement') else 0
                info += f" | Measurements: {meas_count}"
                if self.estimator.estimation_results:
                    info += " | Results available"
            self.grid_info_var.set(info)
        else:
            self.grid_info_var.set("No grid loaded")
    
    def run_with_output_capture(self, func, *args, **kwargs):
        """Run function and capture output"""
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            self.log_output(f"ERROR: {str(e)}")
            return None
    
    def create_ieee9_grid(self):
        """Create IEEE 9-bus grid model"""
        self.update_status("Creating IEEE 9-bus grid...")
        self.estimator = GridStateEstimator()
        self.run_with_output_capture(self.estimator.create_ieee9_grid)
        self.current_grid = "IEEE 9-bus"
        self.log_output("✅ IEEE 9-bus grid created successfully!")
        self.update_grid_info()
        self.update_status("IEEE 9-bus grid ready")
    
    def create_entso_grid(self):
        """Create ENTSO-E grid model"""
        self.update_status("Creating ENTSO-E grid...")
        self.estimator = GridStateEstimator()
        self.run_with_output_capture(self.estimator.create_simple_entso_grid)
        self.current_grid = "ENTSO-E"
        self.log_output("✅ ENTSO-E grid created successfully!")
        self.update_grid_info()
        self.update_status("ENTSO-E grid ready")
    
    def generate_measurements(self):
        """Generate measurements with specified noise level"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        try:
            noise_level = float(self.noise_var.get())
            self.update_status(f"Generating measurements with {noise_level*100:.1f}% noise...")
            self.run_with_output_capture(self.estimator.simulate_measurements, noise_level=noise_level)
            self.log_output(f"✅ Measurements generated with {noise_level*100:.1f}% noise")
            self.update_grid_info()
            self.update_status("Measurements ready")
        except ValueError:
            self.log_output("❌ Invalid noise level. Please enter a valid number.")
            self.update_status("Error in measurement generation")
    
    def list_measurements(self):
        """List current measurements"""
        if not self.estimator or not hasattr(self.estimator, 'net'):
            messagebox.showerror("Error", "No grid model available")
            return
            
        def task():
            self.update_status("Listing measurements...")
            if hasattr(self.estimator.net, 'measurement') and len(self.estimator.net.measurement) > 0:
                self.run_with_output_capture(self.estimator.list_measurements)
            else:
                self.log_output("❌ No measurements available. Generate measurements first.")
            self.update_status("Ready")
            
        Thread(target=task, daemon=True).start()
    
    def modify_bus_voltage(self):
        """Modify bus voltage measurement"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        def task():
            try:
                bus_id = int(self.bus_id_var.get())
                voltage = float(self.voltage_var.get())
                self.update_status(f"Modifying Bus {bus_id} voltage...")
                
                success = self.run_with_output_capture(
                    self.estimator.modify_bus_voltage_measurement, 
                    bus_id, voltage
                )
                
                if success:
                    self.log_output(f"✅ Bus {bus_id} voltage set to {voltage:.4f} p.u.")
                else:
                    self.log_output(f"❌ Failed to modify Bus {bus_id} voltage.")
                    
                self.update_status("Ready")
                
            except ValueError:
                self.log_output("❌ Invalid input. Please enter valid numbers.")
                self.update_status("Error")
        
        Thread(target=task, daemon=True).start()
    
    def run_state_estimation(self):
        """Run state estimation"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        def task():
            self.update_status("Running state estimation...")
            self.run_with_output_capture(self.estimator.run_state_estimation)
            
            if self.estimator.estimation_results:
                self.log_output("✅ State estimation completed successfully!")
                self._update_results_table()
                self.update_grid_info()
            else:
                self.log_output("❌ State estimation failed")
                
            self.update_status("Ready")
            
        Thread(target=task, daemon=True).start()
    
    def test_observability(self):
        """Test grid observability"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        def task():
            self.update_status("Testing observability...")
            if hasattr(self.estimator, 'net') and hasattr(self.estimator.net, 'measurement') and len(self.estimator.net.measurement) > 0:
                self.run_with_output_capture(self.estimator.test_observability)
            else:
                self.log_output("❌ No measurements available. Generate measurements first.")
            self.update_status("Ready")
            
        Thread(target=task, daemon=True).start()
    
    def check_consistency(self):
        """Check measurement consistency"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        def task():
            self.update_status("Checking measurement consistency...")
            if hasattr(self.estimator, 'net') and hasattr(self.estimator.net, 'measurement') and len(self.estimator.net.measurement) > 0:
                results = self.run_with_output_capture(
                    self.estimator.check_measurement_consistency, 
                    tolerance=1e-3, detailed_report=True
                )
                if results:
                    self.log_results("=== CONSISTENCY CHECK RESULTS ===")
                    self.log_results(f"Overall Status: {results.get('overall_status', 'unknown')}")
                    self.log_results(f"Total Violations: {results.get('total_violations', 0)}")
            else:
                self.log_output("❌ No measurements available. Generate measurements first.")
            self.update_status("Ready")
            
        Thread(target=task, daemon=True).start()
    
    def detect_bad_data(self):
        """Run bad data detection"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        def task():
            self.update_status("Detecting bad data...")
            if hasattr(self.estimator, 'net') and hasattr(self.estimator.net, 'measurement') and len(self.estimator.net.measurement) > 0:
                results = self.run_with_output_capture(
                    self.estimator.detect_bad_data,
                    confidence_level=0.95, max_iterations=5
                )
                if results:
                    self.log_results("=== BAD DATA DETECTION RESULTS ===")
                    self.log_results(f"Final Status: {results.get('final_status', 'unknown')}")
                    bad_measurements = results.get('bad_measurements', [])
                    self.log_results(f"Bad Measurements Found: {len(bad_measurements)}")
            else:
                self.log_output("❌ No measurements available. Generate measurements first.")
            self.update_status("Ready")
            
        Thread(target=task, daemon=True).start()
    
    def show_results(self):
        """Show estimation results"""
        if not self.estimator:
            messagebox.showerror("Error", "No grid model available")
            return
            
        if not self.estimator.estimation_results:
            self.log_output("❌ No state estimation results. Run state estimation first.")
            return
            
        def task():
            self.update_status("Displaying results...")
            self.log_results("=== STATE ESTIMATION RESULTS ===")
            self.run_with_output_capture(self.estimator.show_results)
            self._update_results_table()
            self.update_status("Ready")

        Thread(target=task, daemon=True).start()

    def _prepare_results_table_data(self):
        """Prepare table rows from state estimation results."""
        if not self.estimator or not self.estimator.estimation_results:
            return []

        net = self.estimator.net
        bus_results = self.estimator.estimation_results.get('bus_voltages')
        if net is None or bus_results is None:
            return []

        true_voltages = getattr(net, 'res_bus', None)
        if true_voltages is not None:
            true_voltages = true_voltages.vm_pu

        table_rows = []
        for bus_idx, row in bus_results.iterrows():
            est_vm = row.get('vm_pu', np.nan)
            angle = row.get('va_degree', np.nan)
            true_vm = true_voltages.iloc[bus_idx] if true_voltages is not None and len(true_voltages) > bus_idx else np.nan

            if not np.isnan(true_vm) and true_vm != 0:
                error_pct = (est_vm - true_vm) / true_vm * 100
            else:
                error_pct = np.nan

            table_rows.append({
                'bus': bus_idx,
                'true_vm': true_vm,
                'est_vm': est_vm,
                'error_pct': error_pct,
                'angle': angle
            })

        return table_rows

    def _populate_results_table(self, rows):
        """Populate the Treeview with state estimation values."""
        for item in self.results_table.get_children():
            self.results_table.delete(item)

        def fmt(value, precision=4):
            return f"{value:.{precision}f}" if value is not None and not np.isnan(value) else "N/A"

        for row in rows:
            self.results_table.insert(
                "",
                tk.END,
                values=(
                    row.get('bus', "N/A"),
                    fmt(row.get('true_vm')),
                    fmt(row.get('est_vm')),
                    fmt(row.get('error_pct'), precision=2),
                    fmt(row.get('angle'), precision=2)
                )
            )

    def _update_results_table(self):
        """Safely refresh the results table from a worker thread."""
        rows = self._prepare_results_table_data()
        self.root.after(0, lambda: self._populate_results_table(rows))
    
    def visualize_grid(self):
        """Visualize grid results"""
        if not self.estimator:
            messagebox.showerror("Error", "No grid model available")
            return
            
        def task():
            self.update_status("Generating visualization...")
            try:
                if hasattr(self.estimator, 'plot_grid_results'):
                    self.run_with_output_capture(self.estimator.plot_grid_results)
                    self.log_output("✅ Grid visualization displayed!")
                else:
                    self.log_output("❌ Grid visualization not available for this model.")
            except Exception as e:
                self.log_output(f"❌ Visualization failed: {e}")
            self.update_status("Ready")
            
        Thread(target=task, daemon=True).start()
    
    def run_complete_demo(self):
        """Run complete workflow demonstration"""
        def task():
            self.update_status("Running complete demo...")
            self.log_output("🎯 Starting Complete Workflow Demo")
            self.log_output("="*50)
            
            # Set random seed for reproducibility
            np.random.seed(42)
            
            # Step 1: Create grid
            self.log_output("1️⃣ Creating IEEE 9-bus grid...")
            self.estimator = GridStateEstimator()
            self.run_with_output_capture(self.estimator.create_ieee9_grid)
            self.current_grid = "IEEE 9-bus"
            
            # Step 2: Generate measurements
            self.log_output("\n2️⃣ Generating measurements...")
            self.run_with_output_capture(self.estimator.simulate_measurements, noise_level=0.02)
            
            # Step 3: Modify a measurement
            self.log_output("\n3️⃣ Modifying Bus 1 voltage to 1.5 p.u...")
            self.run_with_output_capture(self.estimator.modify_bus_voltage_measurement, 1, 1.5)
            
            # Step 4: Run consistency check
            self.log_output("\n4️⃣ Running consistency check...")
            self.run_with_output_capture(
                self.estimator.check_measurement_consistency,
                tolerance=1e-3, detailed_report=False
            )
            
            # Step 5: Run bad data detection
            self.log_output("\n5️⃣ Running bad data detection...")
            self.run_with_output_capture(
                self.estimator.detect_bad_data,
                confidence_level=0.95, max_iterations=3
            )
            
            # Step 6: Run state estimation
            self.log_output("\n6️⃣ Running state estimation...")
            self.run_with_output_capture(self.estimator.run_state_estimation)
            
            # Step 7: Show results
            if self.estimator.estimation_results:
                self.log_output("\n7️⃣ State estimation completed successfully!")
                self.log_results("=== DEMO RESULTS ===")
                self.run_with_output_capture(self.estimator.show_results)
            
            self.log_output("\n✅ Complete workflow demo finished!")
            self.update_grid_info()
            self.update_status("Demo completed")
            
        Thread(target=task, daemon=True).start()
    
    def clear_output(self):
        """Clear output windows"""
        self.output_text.delete(1.0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.update_status("Output cleared")

def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = PowerSystemGUI(root)
    
    # Add window closing handler
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Application interrupted")
    
if __name__ == "__main__":
    main()
