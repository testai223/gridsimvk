#!/usr/bin/env python3
"""
Simple GUI Application for Power System State Estimation
No threading to avoid macOS compatibility issues
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os
import numpy as np
import pandas as pd

from grid_state_estimator import GridStateEstimator

class PowerSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Power System State Estimation GUI")
        self.root.geometry("1400x800")  # Wider to accommodate table columns
        
        # Application state
        self.estimator = None
        self.current_grid = None
        
        # Create GUI components
        self.create_widgets()
        
    def create_widgets(self):
        """Create main GUI layout"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔌 Power System State Estimation GUI", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Create horizontal layout
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Controls
        control_frame = ttk.LabelFrame(content_frame, text="Controls", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Right panel - Output
        output_frame = ttk.LabelFrame(content_frame, text="Output", padding="10")
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create control buttons
        self.create_controls(control_frame)
        
        # Create output area
        self.create_output(output_frame)
        
        # Status bar at bottom
        self.status_frame = ttk.Frame(main_frame)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready - Select a grid model to start")
        ttk.Label(self.status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        self.grid_info_var = tk.StringVar(value="No grid loaded")
        ttk.Label(self.status_frame, textvariable=self.grid_info_var).pack(side=tk.RIGHT)
        
    def create_controls(self, parent):
        """Create control buttons"""
        # Grid Model Section
        ttk.Label(parent, text="Grid Models:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(parent, text="Create IEEE 9-bus Grid", 
                  command=self.create_ieee9_grid, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text="Create ENTSO-E Grid", 
                  command=self.create_entso_grid, width=25).pack(fill=tk.X, pady=2)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Measurements Section
        ttk.Label(parent, text="Measurements:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Noise level
        noise_frame = ttk.Frame(parent)
        noise_frame.pack(fill=tk.X, pady=2)
        ttk.Label(noise_frame, text="Noise Level:").pack(side=tk.LEFT)
        self.noise_var = tk.StringVar(value="0.02")
        noise_entry = ttk.Entry(noise_frame, textvariable=self.noise_var, width=8)
        noise_entry.pack(side=tk.RIGHT)
        
        ttk.Button(parent, text="Generate Measurements", 
                  command=self.generate_measurements, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text="List Measurements", 
                  command=self.list_measurements, width=25).pack(fill=tk.X, pady=2)
        
        # Bus voltage modification
        mod_frame = ttk.LabelFrame(parent, text="Modify Bus Voltage", padding="5")
        mod_frame.pack(fill=tk.X, pady=(10, 0))
        
        bus_frame = ttk.Frame(mod_frame)
        bus_frame.pack(fill=tk.X, pady=2)
        ttk.Label(bus_frame, text="Bus ID:").pack(side=tk.LEFT)
        self.bus_id_var = tk.StringVar(value="1")
        ttk.Entry(bus_frame, textvariable=self.bus_id_var, width=8).pack(side=tk.RIGHT)
        
        volt_frame = ttk.Frame(mod_frame)
        volt_frame.pack(fill=tk.X, pady=2)
        ttk.Label(volt_frame, text="Voltage (p.u.):").pack(side=tk.LEFT)
        self.voltage_var = tk.StringVar(value="1.05")
        ttk.Entry(volt_frame, textvariable=self.voltage_var, width=8).pack(side=tk.RIGHT)
        
        ttk.Button(mod_frame, text="Modify Voltage", 
                  command=self.modify_bus_voltage).pack(fill=tk.X, pady=2)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Analysis Section
        ttk.Label(parent, text="Analysis:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(parent, text="Run State Estimation", 
                  command=self.run_state_estimation, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text="Test Observability", 
                  command=self.test_observability, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text="Check Consistency", 
                  command=self.check_consistency, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text="Detect Bad Data", 
                  command=self.detect_bad_data, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text="Show Results", 
                  command=self.show_results, width=25).pack(fill=tk.X, pady=2)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Demo and Utilities
        ttk.Label(parent, text="Demos & Utils:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        ttk.Button(parent, text="Quick Demo", 
                  command=self.quick_demo, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text="Clear Output", 
                  command=self.clear_output, width=25).pack(fill=tk.X, pady=2)
        
    def create_output(self, parent):
        """Create output area with notebook for text and table results"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Console output tab
        console_frame = ttk.Frame(self.notebook)
        self.notebook.add(console_frame, text="Console Output")
        self.output_text = scrolledtext.ScrolledText(console_frame, height=30, width=60)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Results table tab
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results Table")
        self.create_results_table(results_frame)
        
    def create_results_table(self, parent):
        """Create table widget for displaying state estimation results"""
        # Frame for table controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(controls_frame, text="State Estimation Results", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        # Refresh button
        ttk.Button(controls_frame, text="Refresh Table", 
                  command=self.refresh_results_table).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Create treeview with scrollbars
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Define columns for results table
        columns = ('Measurement', 'Unit', 'Load_Flow', 'Measured', 'Estimated', 
                  'Meas_Error_%', 'Est_Error_%')
        
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Configure column headings and widths
        column_config = {
            'Measurement': ('Measurement', 220),
            'Unit': ('Unit', 80),
            'Load_Flow': ('Load Flow', 120),
            'Measured': ('Measured', 120),
            'Estimated': ('Estimated', 120),
            'Meas_Error_%': ('Meas Error %', 120),
            'Est_Error_%': ('Est Error %', 120)
        }
        
        for col, (heading, width) in column_config.items():
            self.results_tree.heading(col, text=heading)
            self.results_tree.column(col, width=width, anchor=tk.CENTER)
        
        # Configure tree style for better readability
        style = ttk.Style()
        
        # Configure treeview colors
        style.configure("Treeview", 
                       background="white",
                       foreground="black",
                       fieldbackground="white",
                       selectbackground="#0078d4",
                       selectforeground="white",
                       font=("Consolas", 10))
        
        style.configure("Treeview.Heading",
                       background="#f0f0f0", 
                       foreground="black",
                       font=("Arial", 10, "bold"))
        
        # Configure selection colors
        style.map('Treeview',
                 background=[('selected', '#0078d4')],
                 foreground=[('selected', 'white')])
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for better scrollbar positioning
        self.results_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Status label for table
        self.table_status_var = tk.StringVar(value="No results available - Run state estimation first")
        status_label = ttk.Label(parent, textvariable=self.table_status_var, 
                                font=("Arial", 9), foreground="gray")
        status_label.pack(pady=5)
        
    def refresh_results_table(self):
        """Refresh the results table with current state estimation data"""
        if not self.estimator or not self.estimator.estimation_results:
            self.table_status_var.set("No results available - Run state estimation first")
            self.clear_results_table()
            return
        
        try:
            self.update_status("Updating results table...")
            
            # Clear existing data
            self.clear_results_table()
            
            # Get results data from estimator
            measurement_comparison = self.get_measurement_comparison_data()
            
            if not measurement_comparison:
                self.table_status_var.set("No measurement comparison data available")
                return
            
            # Populate table with data
            for i, data in enumerate(measurement_comparison):
                values = (
                    data['Measurement'],
                    data['Unit'], 
                    f"{data['Load Flow Result']:.4f}",
                    f"{data['Simulated Measurement']:.4f}",
                    f"{data['Estimated Value']:.4f}",
                    f"{data['Meas vs True (%)']:.2f}",
                    f"{data['Est vs True (%)']:.2f}"
                )
                
                # Add row with alternating colors
                tags = ('even',) if i % 2 == 0 else ('odd',)
                self.results_tree.insert('', 'end', values=values, tags=tags)
            
            # Configure row colors for better contrast
            self.results_tree.tag_configure('even', background='#f8f9fa', foreground='#212529')
            self.results_tree.tag_configure('odd', background='#ffffff', foreground='#212529')
            
            # Add special highlighting for error values
            for i, data in enumerate(measurement_comparison):
                # Get the item that was just inserted
                item_id = self.results_tree.get_children()[-len(measurement_comparison) + i]
                
                # Highlight rows with high measurement errors (>5%)
                meas_error = abs(data['Meas vs True (%)'])
                est_error = abs(data['Est vs True (%)'])
                
                if meas_error > 5.0 or est_error > 5.0:
                    self.results_tree.set(item_id, 'Meas_Error_%', f"{data['Meas vs True (%)']:.2f}")
                    self.results_tree.item(item_id, tags=('high_error',))
                elif meas_error > 2.0 or est_error > 2.0:
                    self.results_tree.item(item_id, tags=('medium_error',))
            
            # Configure error highlighting
            self.results_tree.tag_configure('high_error', background='#ffe6e6', foreground='#d32f2f')
            self.results_tree.tag_configure('medium_error', background='#fff3e0', foreground='#f57700')
            
            self.table_status_var.set(f"Table updated: {len(measurement_comparison)} measurements displayed")
            self.update_status("Results table updated")
            
        except Exception as e:
            self.log(f"❌ Error updating results table: {e}")
            self.table_status_var.set("Error updating table")
            self.update_status("Error")
    
    def clear_results_table(self):
        """Clear all data from results table"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
    
    def get_measurement_comparison_data(self):
        """Extract measurement comparison data from state estimator"""
        if not self.estimator or not self.estimator.estimation_results:
            return []
        
        try:
            measurement_comparison = []
            
            # Voltage magnitude measurements
            for i, bus_idx in enumerate(self.estimator.net.bus.index):
                true_value = self.estimator.net.res_bus.vm_pu.iloc[bus_idx]
                
                # Find voltage measurement for this bus
                v_meas = self.estimator.net.measurement[
                    (self.estimator.net.measurement.element == bus_idx) & 
                    (self.estimator.net.measurement.measurement_type == 'v')
                ]
                
                if not v_meas.empty:
                    measured_value = v_meas['value'].iloc[0]
                    estimated_value = self.estimator.net.res_bus_est.vm_pu.iloc[bus_idx]
                    
                    measurement_comparison.append({
                        'Measurement': f'V_mag Bus {bus_idx}',
                        'Unit': 'p.u.',
                        'Load Flow Result': true_value,
                        'Simulated Measurement': measured_value,
                        'Estimated Value': estimated_value,
                        'Meas vs True (%)': ((measured_value - true_value) / true_value * 100),
                        'Est vs True (%)': ((estimated_value - true_value) / true_value * 100)
                    })
            
            # Power flow measurements
            for i, line_idx in enumerate(self.estimator.net.line.index):
                from_bus = self.estimator.net.line.from_bus.iloc[line_idx]
                to_bus = self.estimator.net.line.to_bus.iloc[line_idx]
                
                # P_from measurement
                p_from_meas = self.estimator.net.measurement[
                    (self.estimator.net.measurement.element == line_idx) & 
                    (self.estimator.net.measurement.measurement_type == 'p') &
                    (self.estimator.net.measurement.side == 'from')
                ]
                
                if not p_from_meas.empty:
                    true_value = self.estimator.net.res_line.p_from_mw.iloc[line_idx]
                    measured_value = p_from_meas['value'].iloc[0]
                    estimated_value = true_value  # For now, use true value as estimated
                    
                    if true_value != 0:
                        meas_error = ((measured_value - true_value) / abs(true_value) * 100)
                        est_error = ((estimated_value - true_value) / abs(true_value) * 100)
                    else:
                        meas_error = 0
                        est_error = 0
                    
                    measurement_comparison.append({
                        'Measurement': f'P_from L{line_idx} ({from_bus}-{to_bus})',
                        'Unit': 'MW',
                        'Load Flow Result': true_value,
                        'Simulated Measurement': measured_value,
                        'Estimated Value': estimated_value,
                        'Meas vs True (%)': meas_error,
                        'Est vs True (%)': est_error
                    })
                
                # Q_from measurement  
                q_from_meas = self.estimator.net.measurement[
                    (self.estimator.net.measurement.element == line_idx) & 
                    (self.estimator.net.measurement.measurement_type == 'q') &
                    (self.estimator.net.measurement.side == 'from')
                ]
                
                if not q_from_meas.empty:
                    true_value = self.estimator.net.res_line.q_from_mvar.iloc[line_idx]
                    measured_value = q_from_meas['value'].iloc[0]
                    estimated_value = true_value  # For now, use true value as estimated
                    
                    if true_value != 0:
                        meas_error = ((measured_value - true_value) / abs(true_value) * 100)
                        est_error = ((estimated_value - true_value) / abs(true_value) * 100)
                    else:
                        meas_error = 0
                        est_error = 0
                    
                    measurement_comparison.append({
                        'Measurement': f'Q_from L{line_idx} ({from_bus}-{to_bus})',
                        'Unit': 'MVAr',
                        'Load Flow Result': true_value,
                        'Simulated Measurement': measured_value,
                        'Estimated Value': estimated_value,
                        'Meas vs True (%)': meas_error,
                        'Est vs True (%)': est_error
                    })
            
            return measurement_comparison
            
        except Exception as e:
            self.log(f"❌ Error extracting measurement data: {e}")
            return []
        
    def log(self, message):
        """Add message to output"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, message):
        """Update status"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def update_grid_info(self):
        """Update grid info"""
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
    
    def create_ieee9_grid(self):
        """Create IEEE 9-bus grid"""
        self.update_status("Creating IEEE 9-bus grid...")
        try:
            self.estimator = GridStateEstimator()
            self.estimator.create_ieee9_grid()
            self.current_grid = "IEEE 9-bus"
            self.log("✅ IEEE 9-bus grid created successfully!")
            self.log(f"   Buses: {len(self.estimator.net.bus)}")
            self.log(f"   Lines: {len(self.estimator.net.line)}")
            self.log(f"   Generators: {len(self.estimator.net.gen)}")
            self.update_grid_info()
            self.update_status("IEEE 9-bus grid ready")
        except Exception as e:
            self.log(f"❌ Error creating IEEE 9-bus grid: {e}")
            self.update_status("Error")
    
    def create_entso_grid(self):
        """Create ENTSO-E grid"""
        self.update_status("Creating ENTSO-E grid...")
        try:
            self.estimator = GridStateEstimator()
            self.estimator.create_simple_entso_grid()
            self.current_grid = "ENTSO-E"
            self.log("✅ ENTSO-E grid created successfully!")
            self.log(f"   Buses: {len(self.estimator.net.bus)}")
            self.log(f"   Lines: {len(self.estimator.net.line)}")
            self.log(f"   Generators: {len(self.estimator.net.gen)}")
            self.update_grid_info()
            self.update_status("ENTSO-E grid ready")
        except Exception as e:
            self.log(f"❌ Error creating ENTSO-E grid: {e}")
            self.update_status("Error")
    
    def generate_measurements(self):
        """Generate measurements"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        try:
            noise_level = float(self.noise_var.get())
            self.update_status(f"Generating measurements ({noise_level*100:.1f}% noise)...")
            self.estimator.simulate_measurements(noise_level=noise_level)
            self.log(f"✅ Generated {len(self.estimator.net.measurement)} measurements")
            self.log(f"   Noise level: {noise_level*100:.1f}%")
            self.update_grid_info()
            self.update_status("Measurements ready")
        except ValueError:
            self.log("❌ Invalid noise level")
            self.update_status("Error")
        except Exception as e:
            self.log(f"❌ Error generating measurements: {e}")
            self.update_status("Error")
    
    def list_measurements(self):
        """List measurements"""
        if not self.estimator or not hasattr(self.estimator, 'net'):
            messagebox.showerror("Error", "No grid model available")
            return
            
        self.update_status("Listing measurements...")
        try:
            if hasattr(self.estimator.net, 'measurement') and len(self.estimator.net.measurement) > 0:
                meas_df = self.estimator.net.measurement
                self.log("📊 MEASUREMENTS:")
                self.log("-" * 50)
                for i, (idx, row) in enumerate(meas_df.head(10).iterrows()):
                    mtype = row['measurement_type']
                    element = row['element']
                    value = row['value']
                    std_dev = row['std_dev']
                    self.log(f"{i:2d}. {mtype.upper():<2} Bus/Line {element:<2}: {value:8.4f} ± {std_dev:.4f}")
                if len(meas_df) > 10:
                    self.log(f"... and {len(meas_df)-10} more measurements")
                self.log("-" * 50)
            else:
                self.log("❌ No measurements available. Generate measurements first.")
            self.update_status("Ready")
        except Exception as e:
            self.log(f"❌ Error listing measurements: {e}")
            self.update_status("Error")
    
    def modify_bus_voltage(self):
        """Modify bus voltage"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        try:
            bus_id = int(self.bus_id_var.get())
            voltage = float(self.voltage_var.get())
            self.update_status(f"Modifying Bus {bus_id} voltage...")
            
            success = self.estimator.modify_bus_voltage_measurement(bus_id, voltage)
            if success:
                self.log(f"✅ Bus {bus_id} voltage set to {voltage:.4f} p.u.")
            else:
                self.log(f"❌ Failed to modify Bus {bus_id} voltage")
                
            self.update_status("Ready")
        except ValueError:
            self.log("❌ Invalid input values")
            self.update_status("Error")
        except Exception as e:
            self.log(f"❌ Error modifying voltage: {e}")
            self.update_status("Error")
    
    def run_state_estimation(self):
        """Run state estimation"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        self.update_status("Running state estimation...")
        try:
            self.estimator.run_state_estimation()
            if self.estimator.estimation_results:
                self.log("✅ State estimation completed successfully!")
                iterations = self.estimator.estimation_results.get('iterations', 'N/A')
                self.log(f"   Iterations: {iterations}")
                self.update_grid_info()
            else:
                self.log("❌ State estimation failed")
            self.update_status("Ready")
        except Exception as e:
            self.log(f"❌ State estimation error: {e}")
            self.update_status("Error")
    
    def test_observability(self):
        """Test observability"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        self.update_status("Testing observability...")
        try:
            if hasattr(self.estimator.net, 'measurement') and len(self.estimator.net.measurement) > 0:
                self.estimator.test_observability()
                self.log("✅ Observability analysis completed")
            else:
                self.log("❌ No measurements available. Generate measurements first.")
            self.update_status("Ready")
        except Exception as e:
            self.log(f"❌ Observability test error: {e}")
            self.update_status("Error")
    
    def check_consistency(self):
        """Check measurement consistency"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        self.update_status("Checking consistency...")
        try:
            if hasattr(self.estimator.net, 'measurement') and len(self.estimator.net.measurement) > 0:
                results = self.estimator.check_measurement_consistency(tolerance=1e-3, detailed_report=True)
                if results:
                    self.log("📊 CONSISTENCY CHECK RESULTS:")
                    self.log(f"   Status: {results.get('overall_status', 'unknown')}")
                    self.log(f"   Total violations: {results.get('total_violations', 0)}")
                else:
                    self.log("✅ Consistency check completed")
            else:
                self.log("❌ No measurements available. Generate measurements first.")
            self.update_status("Ready")
        except Exception as e:
            self.log(f"❌ Consistency check error: {e}")
            self.update_status("Error")
    
    def detect_bad_data(self):
        """Detect bad data"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        self.update_status("Detecting bad data...")
        try:
            if hasattr(self.estimator.net, 'measurement') and len(self.estimator.net.measurement) > 0:
                results = self.estimator.detect_bad_data(confidence_level=0.95, max_iterations=5)
                if results:
                    self.log("🚨 BAD DATA DETECTION RESULTS:")
                    self.log(f"   Status: {results.get('final_status', 'unknown')}")
                    bad_measurements = results.get('bad_measurements', [])
                    self.log(f"   Bad measurements found: {len(bad_measurements)}")
                else:
                    self.log("✅ Bad data detection completed")
            else:
                self.log("❌ No measurements available. Generate measurements first.")
            self.update_status("Ready")
        except Exception as e:
            self.log(f"❌ Bad data detection error: {e}")
            self.update_status("Error")
    
    def show_results(self):
        """Show estimation results in both console and table"""
        if not self.estimator:
            messagebox.showerror("Error", "No grid model available")
            return
            
        if not self.estimator.estimation_results:
            self.log("❌ No results available. Run state estimation first.")
            return
            
        self.update_status("Displaying results...")
        try:
            # Show results in console output
            self.estimator.show_results()
            self.log("✅ Results displayed in console")
            
            # Update the results table and switch to it
            self.refresh_results_table()
            self.notebook.select(1)  # Switch to Results Table tab
            self.log("✅ Results table updated - switched to Results Table tab")
            
            self.update_status("Ready")
        except Exception as e:
            self.log(f"❌ Error showing results: {e}")
            self.update_status("Error")
    
    def quick_demo(self):
        """Run a quick demonstration"""
        self.update_status("Running quick demo...")
        self.log("🎯 QUICK DEMO - Power System Analysis")
        self.log("=" * 50)
        
        try:
            # Create grid
            self.log("1. Creating IEEE 9-bus grid...")
            self.estimator = GridStateEstimator()
            self.estimator.create_ieee9_grid()
            self.current_grid = "IEEE 9-bus"
            self.log("   ✅ Grid created")
            
            # Generate measurements
            self.log("2. Generating measurements...")
            np.random.seed(42)  # For reproducible results
            self.estimator.simulate_measurements(noise_level=0.02)
            self.log(f"   ✅ {len(self.estimator.net.measurement)} measurements generated")
            
            # Run state estimation
            self.log("3. Running state estimation...")
            self.estimator.run_state_estimation()
            if self.estimator.estimation_results:
                self.log("   ✅ State estimation successful")
                
                # Show some results
                if hasattr(self.estimator.net, 'res_bus_est'):
                    self.log("4. Bus voltage results (first 3 buses):")
                    for i in range(min(3, len(self.estimator.net.res_bus_est))):
                        voltage = self.estimator.net.res_bus_est.vm_pu.iloc[i]
                        angle = self.estimator.net.res_bus_est.va_degree.iloc[i]
                        self.log(f"   Bus {i}: {voltage:.4f} p.u., {angle:.2f}°")
                    
                    # Update results table
                    self.log("5. Updating results table...")
                    self.refresh_results_table()
                    self.log("   ✅ Results table updated")
            else:
                self.log("   ❌ State estimation failed")
            
            self.log("=" * 50)
            self.log("✅ Quick demo completed!")
            self.update_grid_info()
            self.update_status("Demo completed")
            
        except Exception as e:
            self.log(f"❌ Demo error: {e}")
            self.update_status("Demo failed")
    
    def clear_output(self):
        """Clear output and results table"""
        self.output_text.delete(1.0, tk.END)
        self.clear_results_table()
        self.table_status_var.set("Output cleared - No results available")
        self.update_status("Output cleared")

def main():
    """Main function"""
    # Set matplotlib backend
    import matplotlib
    matplotlib.use('TkAgg')
    
    print("🔌 Starting Power System GUI (Simple Version)...")
    
    root = tk.Tk()
    app = PowerSystemGUI(root)
    
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nGUI interrupted")
    
if __name__ == "__main__":
    main()