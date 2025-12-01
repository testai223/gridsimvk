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
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

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
        ttk.Button(parent, text="Check Topology", 
                  command=self.check_topology, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text="Detect Bad Data", 
                  command=self.detect_bad_data, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text="Show Results", 
                  command=self.show_results, width=25).pack(fill=tk.X, pady=2)
        ttk.Button(parent, text="Show Grid Plot", 
                  command=self.show_grid_plot, width=25).pack(fill=tk.X, pady=2)
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Demo and Utilities
        ttk.Label(parent, text="Demos & Utils:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        
        # Auto-refresh setting
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, text="Auto-refresh plots/results", 
                       variable=self.auto_refresh_var).pack(anchor=tk.W, pady=2)
        
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
        
        # Grid visualization tab
        viz_frame = ttk.Frame(self.notebook)
        self.notebook.add(viz_frame, text="Grid Visualization")
        self.create_grid_visualization(viz_frame)
        
        # Switch control tab
        switch_frame = ttk.Frame(self.notebook)
        self.notebook.add(switch_frame, text="Switch Control")
        self.create_switch_control(switch_frame)
        
        # Measurement management tab
        measurement_frame = ttk.Frame(self.notebook)
        self.notebook.add(measurement_frame, text="Measurement Management")
        self.create_measurement_management(measurement_frame)
        
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
        
    def create_grid_visualization(self, parent):
        """Create grid visualization with matplotlib canvas and controls"""
        # Control panel at top
        control_panel = ttk.Frame(parent)
        control_panel.pack(fill=tk.X, padx=5, pady=5)
        
        # Title and refresh button
        title_frame = ttk.Frame(control_panel)
        title_frame.pack(fill=tk.X)
        
        ttk.Label(title_frame, text="Grid Network Visualization", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(title_frame, text="Refresh Plot", 
                  command=self.refresh_grid_plot).pack(side=tk.RIGHT)
        
        # Visualization options
        options_frame = ttk.LabelFrame(control_panel, text="Display Options", padding="5")
        options_frame.pack(fill=tk.X, pady=5)
        
        # Create checkbutton variables
        self.show_voltage_magnitudes = tk.BooleanVar(value=True)
        self.show_voltage_errors = tk.BooleanVar(value=True)
        self.show_power_flows = tk.BooleanVar(value=True)
        self.show_measurement_locations = tk.BooleanVar(value=True)
        self.show_bus_labels = tk.BooleanVar(value=True)
        self.show_line_labels = tk.BooleanVar(value=False)
        
        # Arrange checkboxes in columns
        left_frame = ttk.Frame(options_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = ttk.Frame(options_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Left column checkboxes
        ttk.Checkbutton(left_frame, text="Voltage Magnitudes", 
                       variable=self.show_voltage_magnitudes,
                       command=self.on_display_option_change).pack(anchor=tk.W)
        ttk.Checkbutton(left_frame, text="Voltage Errors", 
                       variable=self.show_voltage_errors,
                       command=self.on_display_option_change).pack(anchor=tk.W)
        ttk.Checkbutton(left_frame, text="Power Flows", 
                       variable=self.show_power_flows,
                       command=self.on_display_option_change).pack(anchor=tk.W)
        
        # Right column checkboxes
        ttk.Checkbutton(right_frame, text="Measurement Locations", 
                       variable=self.show_measurement_locations,
                       command=self.on_display_option_change).pack(anchor=tk.W)
        ttk.Checkbutton(right_frame, text="Bus Labels", 
                       variable=self.show_bus_labels,
                       command=self.on_display_option_change).pack(anchor=tk.W)
        ttk.Checkbutton(right_frame, text="Line Labels", 
                       variable=self.show_line_labels,
                       command=self.on_display_option_change).pack(anchor=tk.W)
        
        # Plot type selection
        plot_type_frame = ttk.Frame(options_frame)
        plot_type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(plot_type_frame, text="Plot Type:").pack(side=tk.LEFT)
        self.plot_type_var = tk.StringVar(value="comprehensive")
        plot_type_combo = ttk.Combobox(plot_type_frame, textvariable=self.plot_type_var,
                                      values=["comprehensive", "network_only", "custom"],
                                      state="readonly", width=15)
        plot_type_combo.pack(side=tk.LEFT, padx=5)
        plot_type_combo.bind("<<ComboboxSelected>>", self.on_plot_type_change)
        
        # Matplotlib figure and canvas
        self.grid_figure = Figure(figsize=(12, 8), dpi=100)
        self.grid_canvas = FigureCanvasTkAgg(self.grid_figure, parent)
        self.grid_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Navigation toolbar
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X)
        self.grid_toolbar = NavigationToolbar2Tk(self.grid_canvas, toolbar_frame)
        self.grid_toolbar.update()
        
        # Status for grid plot
        self.grid_plot_status_var = tk.StringVar(value="No grid available - Create a grid model first")
        grid_status_label = ttk.Label(parent, textvariable=self.grid_plot_status_var, 
                                     font=("Arial", 9), foreground="gray")
        grid_status_label.pack(pady=5)
        
        # Initialize with empty plot
        self.clear_grid_plot()
        
    def refresh_grid_plot(self):
        """Refresh the grid visualization plot"""
        if not self.estimator or not hasattr(self.estimator, 'net') or self.estimator.net is None:
            self.grid_plot_status_var.set("No grid available - Create a grid model first")
            self.clear_grid_plot()
            return
        
        try:
            self.update_status("Updating grid visualization...")
            
            # Clear the figure
            self.grid_figure.clear()
            
            plot_type = self.plot_type_var.get()
            
            if plot_type == "comprehensive":
                self.create_comprehensive_plot()
            elif plot_type == "network_only":
                self.create_network_only_plot()
            else:  # custom
                self.create_custom_plot()
            
            # Update canvas
            self.grid_canvas.draw()
            
            # Update status
            total_elements = len(self.estimator.net.bus) + len(self.estimator.net.line)
            self.grid_plot_status_var.set(f"Grid visualization updated - {total_elements} network elements")
            self.update_status("Grid plot updated")
            
        except Exception as e:
            self.log(f"❌ Error updating grid plot: {e}")
            self.grid_plot_status_var.set("Error updating grid plot")
            self.clear_grid_plot()
            self.update_status("Error")
    
    def create_comprehensive_plot(self):
        """Create comprehensive 2x2 subplot grid visualization"""
        if not self.estimator.estimation_results:
            self.create_network_only_plot()
            return
            
        # Create 2x2 subplots
        axs = self.grid_figure.subplots(2, 2)
        self.grid_figure.suptitle(f'{self.current_grid} Grid - Comprehensive Analysis', fontsize=14, fontweight='bold')
        
        # Get bus positions
        try:
            positions = self.estimator._create_bus_positions()
        except:
            positions = self.create_default_positions()
        
        # Plot 1: Voltage Magnitudes
        if self.show_voltage_magnitudes.get():
            self.estimator._plot_voltage_magnitudes_on_grid(axs[0, 0])
            axs[0, 0].set_title('Voltage Magnitudes')
        else:
            self.plot_basic_network(axs[0, 0], positions, "Voltage Magnitudes (Disabled)")
        
        # Plot 2: Voltage Errors
        if self.show_voltage_errors.get() and self.estimator.estimation_results:
            self.estimator._plot_voltage_errors_on_grid(axs[0, 1])
            axs[0, 1].set_title('Voltage Estimation Errors')
        else:
            self.plot_basic_network(axs[0, 1], positions, "Voltage Errors (Disabled/No Results)")
        
        # Plot 3: Power Flows
        if self.show_power_flows.get():
            self.estimator._plot_power_flows_on_grid(axs[1, 0])
            axs[1, 0].set_title('Active Power Flows')
        else:
            self.plot_basic_network(axs[1, 0], positions, "Power Flows (Disabled)")
        
        # Plot 4: Measurement Locations
        if self.show_measurement_locations.get():
            self.estimator._plot_measurement_locations(axs[1, 1])
            axs[1, 1].set_title('Measurement Locations')
        else:
            self.plot_basic_network(axs[1, 1], positions, "Measurements (Disabled)")
        
        self.grid_figure.tight_layout()
        
    def create_network_only_plot(self):
        """Create single network topology plot"""
        ax = self.grid_figure.add_subplot(111)
        
        try:
            positions = self.estimator._create_bus_positions()
        except:
            positions = self.create_default_positions()
        
        self.plot_basic_network(ax, positions, f'{self.current_grid} Grid - Network Topology')
        
    def create_custom_plot(self):
        """Create custom plot based on selected options"""
        # Count enabled options
        enabled_options = sum([
            self.show_voltage_magnitudes.get(),
            self.show_voltage_errors.get() and bool(self.estimator.estimation_results),
            self.show_power_flows.get(),
            self.show_measurement_locations.get()
        ])
        
        if enabled_options == 0:
            self.create_network_only_plot()
            return
        elif enabled_options == 1:
            # Single plot
            ax = self.grid_figure.add_subplot(111)
            
            if self.show_voltage_magnitudes.get():
                self.estimator._plot_voltage_magnitudes_on_grid(ax)
                ax.set_title('Voltage Magnitudes')
            elif self.show_voltage_errors.get() and self.estimator.estimation_results:
                self.estimator._plot_voltage_errors_on_grid(ax)
                ax.set_title('Voltage Estimation Errors')
            elif self.show_power_flows.get():
                self.estimator._plot_power_flows_on_grid(ax)
                ax.set_title('Active Power Flows')
            elif self.show_measurement_locations.get():
                self.estimator._plot_measurement_locations(ax)
                ax.set_title('Measurement Locations')
                
        elif enabled_options == 2:
            # 1x2 subplots
            axs = self.grid_figure.subplots(1, 2)
            plot_idx = 0
            
            if self.show_voltage_magnitudes.get():
                self.estimator._plot_voltage_magnitudes_on_grid(axs[plot_idx])
                axs[plot_idx].set_title('Voltage Magnitudes')
                plot_idx += 1
            
            if self.show_voltage_errors.get() and self.estimator.estimation_results:
                self.estimator._plot_voltage_errors_on_grid(axs[plot_idx])
                axs[plot_idx].set_title('Voltage Errors')
                plot_idx += 1
            
            if self.show_power_flows.get() and plot_idx < 2:
                self.estimator._plot_power_flows_on_grid(axs[plot_idx])
                axs[plot_idx].set_title('Power Flows')
                plot_idx += 1
            
            if self.show_measurement_locations.get() and plot_idx < 2:
                self.estimator._plot_measurement_locations(axs[plot_idx])
                axs[plot_idx].set_title('Measurements')
                
        else:
            # Multiple plots - use 2x2 grid
            self.create_comprehensive_plot()
            return
        
        self.grid_figure.tight_layout()
    
    def plot_basic_network(self, ax, positions, title):
        """Plot basic network topology"""
        if not positions:
            ax.text(0.5, 0.5, 'No network topology available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title(title)
            return
        
        # Plot buses
        bus_x = [positions[bus][0] for bus in self.estimator.net.bus.index]
        bus_y = [positions[bus][1] for bus in self.estimator.net.bus.index]
        
        ax.scatter(bus_x, bus_y, c='lightblue', s=300, alpha=0.7, edgecolors='black', linewidth=2)
        
        # Plot lines
        try:
            self.estimator._draw_transmission_lines(ax, positions, color='gray', linewidth=2)
        except:
            pass  # Skip if method not available
        
        # Add bus labels if enabled
        if self.show_bus_labels.get():
            for bus_idx in self.estimator.net.bus.index:
                x, y = positions[bus_idx]
                ax.annotate(f'Bus {bus_idx}', (x, y), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8)
        
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        
    def create_default_positions(self):
        """Create default bus positions if estimator method fails"""
        if not self.estimator or not hasattr(self.estimator, 'net'):
            return {}
        
        n_buses = len(self.estimator.net.bus)
        positions = {}
        
        # Create simple circular layout
        import math
        for i, bus_idx in enumerate(self.estimator.net.bus.index):
            angle = 2 * math.pi * i / n_buses
            x = math.cos(angle)
            y = math.sin(angle)
            positions[bus_idx] = (x, y)
            
        return positions
    
    def clear_grid_plot(self):
        """Clear the grid plot"""
        self.grid_figure.clear()
        ax = self.grid_figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No grid visualization available\n\nCreate a grid model and run state estimation to see plots', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Grid Visualization')
        self.grid_canvas.draw()
    
    def on_display_option_change(self):
        """Handle display option changes"""
        if hasattr(self, 'estimator') and self.estimator:
            self.refresh_grid_plot()
    
    def on_plot_type_change(self, event=None):
        """Handle plot type changes"""
        if hasattr(self, 'estimator') and self.estimator:
            self.refresh_grid_plot()
    
    def auto_refresh_results_and_plots(self):
        """Auto-refresh results table, grid plot, and measurement display if enabled"""
        if not self.auto_refresh_var.get():
            return  # Auto-refresh disabled
        
        try:
            refreshed_items = []
            
            # Refresh results table if we have measurements or estimation results
            if self.estimator and hasattr(self.estimator, 'net') and self.estimator.net is not None:
                if hasattr(self.estimator.net, 'measurement') and len(self.estimator.net.measurement) > 0:
                    self.refresh_results_table()
                    refreshed_items.append("results table")
            
            # Refresh grid plot if we have a grid model
            if self.estimator and hasattr(self.estimator, 'net') and self.estimator.net is not None:
                self.refresh_grid_plot()
                refreshed_items.append("grid visualization")
                
                # Refresh measurement display if we have measurements
                if hasattr(self.estimator.net, 'measurement') and len(self.estimator.net.measurement) > 0:
                    self.refresh_measurement_display()
                    refreshed_items.append("measurement display")
            
            if refreshed_items:
                self.log(f"🔄 Auto-refreshed: {', '.join(refreshed_items)}")
                
        except Exception as e:
            self.log(f"❌ Auto-refresh error: {e}")
    
    def create_switch_control(self, parent):
        """Create switch control interface with interactive network visualization"""
        # Control panel at top
        control_panel = ttk.Frame(parent)
        control_panel.pack(fill=tk.X, padx=5, pady=5)
        
        # Title and refresh button
        title_frame = ttk.Frame(control_panel)
        title_frame.pack(fill=tk.X)
        
        ttk.Label(title_frame, text="Network Switch Control", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(title_frame, text="Refresh Switches", 
                  command=self.refresh_switch_display).pack(side=tk.RIGHT)
        
        # Create horizontal layout
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Switch controls
        left_panel = ttk.LabelFrame(main_frame, text="Switch Controls", padding="5")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Switch list with controls
        switch_list_frame = ttk.Frame(left_panel)
        switch_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for switches
        columns = ('Name', 'Type', 'Status')
        self.switch_tree = ttk.Treeview(switch_list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.switch_tree.heading('Name', text='Switch Name')
        self.switch_tree.heading('Type', text='Type')
        self.switch_tree.heading('Status', text='Status')
        
        self.switch_tree.column('Name', width=200)
        self.switch_tree.column('Type', width=80)
        self.switch_tree.column('Status', width=80)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Switch.Treeview", font=("Consolas", 9))
        self.switch_tree.configure(style="Switch.Treeview")
        
        # Add scrollbar for switch list
        switch_scrollbar = ttk.Scrollbar(switch_list_frame, orient=tk.VERTICAL, command=self.switch_tree.yview)
        self.switch_tree.configure(yscrollcommand=switch_scrollbar.set)
        
        # Grid layout for switch list
        self.switch_tree.grid(row=0, column=0, sticky='nsew')
        switch_scrollbar.grid(row=0, column=1, sticky='ns')
        
        switch_list_frame.grid_rowconfigure(0, weight=1)
        switch_list_frame.grid_columnconfigure(0, weight=1)
        
        # Switch operation buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Open Switch", 
                  command=self.open_selected_switch).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Close Switch", 
                  command=self.close_selected_switch).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Toggle", 
                  command=self.toggle_selected_switch).pack(side=tk.LEFT, padx=2)
        
        # Topology validation setting
        topology_frame = ttk.LabelFrame(left_panel, text="Topology Validation", padding="5")
        topology_frame.pack(fill=tk.X, pady=5)
        
        self.topology_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(topology_frame, text="Enable topology validation", 
                       variable=self.topology_check_var).pack(anchor=tk.W, pady=2)
        
        ttk.Button(topology_frame, text="Check Network Topology", 
                  command=self.check_network_topology).pack(fill=tk.X, pady=2)
        
        # Emergency operations
        emergency_frame = ttk.LabelFrame(left_panel, text="Emergency Operations", padding="5")
        emergency_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(emergency_frame, text="Open All Switches", 
                  command=self.open_all_switches).pack(fill=tk.X, pady=2)
        ttk.Button(emergency_frame, text="Close All Switches", 
                  command=self.close_all_switches).pack(fill=tk.X, pady=2)
        ttk.Button(emergency_frame, text="Reset to Normal", 
                  command=self.reset_switches_to_normal).pack(fill=tk.X, pady=2)
        
        # Right panel - Interactive network plot
        right_panel = ttk.LabelFrame(main_frame, text="Interactive Network View", padding="5")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Matplotlib figure for switch visualization
        self.switch_figure = Figure(figsize=(10, 8), dpi=100)
        self.switch_canvas = FigureCanvasTkAgg(self.switch_figure, right_panel)
        self.switch_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Navigation toolbar for switch plot
        switch_toolbar_frame = ttk.Frame(right_panel)
        switch_toolbar_frame.pack(fill=tk.X)
        self.switch_toolbar = NavigationToolbar2Tk(self.switch_canvas, switch_toolbar_frame)
        self.switch_toolbar.update()
        
        # Status for switch operations
        self.switch_status_var = tk.StringVar(value="No grid available - Create a grid model first")
        switch_status_label = ttk.Label(parent, textvariable=self.switch_status_var, 
                                       font=("Arial", 9), foreground="gray")
        switch_status_label.pack(pady=5)
        
        # Initialize with empty displays
        self.clear_switch_display()
        
    def refresh_switch_display(self):
        """Refresh the switch control display"""
        if not self.estimator or not hasattr(self.estimator, 'net') or self.estimator.net is None:
            self.switch_status_var.set("No grid available - Create a grid model first")
            self.clear_switch_display()
            return
        
        try:
            self.update_status("Updating switch display...")
            
            # Get switch information
            switch_info = self.estimator.get_switch_info()
            
            if not switch_info:
                self.switch_status_var.set("No switches available in current grid model")
                self.clear_switch_display()
                return
            
            # Clear and populate switch list
            self.clear_switch_list()
            
            for switch_data in switch_info:
                status_color = "🟢" if switch_data['closed'] else "🔴"
                status_text = f"{status_color} {switch_data['status']}"
                
                values = (
                    switch_data['name'],
                    switch_data['switch_type'],
                    status_text
                )
                
                # Add to treeview with switch index as item id
                item_id = self.switch_tree.insert('', 'end', values=values, 
                                                  tags=(str(switch_data['index']),))
                
                # Configure colors based on status
                if switch_data['closed']:
                    self.switch_tree.set(item_id, 'Status', status_text)
                else:
                    self.switch_tree.set(item_id, 'Status', status_text)
            
            # Update switch network plot
            self.update_switch_network_plot()
            
            # Update status
            self.switch_status_var.set(f"Switch display updated - {len(switch_info)} switches available")
            self.update_status("Switch display updated")
            
        except Exception as e:
            self.log(f"❌ Error updating switch display: {e}")
            self.switch_status_var.set("Error updating switch display")
            self.update_status("Error")
    
    def clear_switch_display(self):
        """Clear the switch display"""
        self.clear_switch_list()
        
        # Clear the switch plot
        self.switch_figure.clear()
        ax = self.switch_figure.add_subplot(111)
        ax.text(0.5, 0.5, 'No switch visualization available\n\nCreate a grid model to see network switches', 
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('Network Switch Control')
        self.switch_canvas.draw()
    
    def clear_switch_list(self):
        """Clear the switch list"""
        for item in self.switch_tree.get_children():
            self.switch_tree.delete(item)
    
    def get_selected_switch_index(self):
        """Get the index of the currently selected switch"""
        selection = self.switch_tree.selection()
        if not selection:
            return None
        
        # Get switch index from item tags
        item = selection[0]
        tags = self.switch_tree.item(item, 'tags')
        if tags:
            try:
                return int(tags[0])
            except (ValueError, IndexError):
                pass
        return None
    
    def open_selected_switch(self):
        """Open the selected switch"""
        switch_index = self.get_selected_switch_index()
        if switch_index is None:
            self.log("❌ No switch selected")
            return
        
        self.operate_switch(switch_index, force_state=False)
    
    def close_selected_switch(self):
        """Close the selected switch"""
        switch_index = self.get_selected_switch_index()
        if switch_index is None:
            self.log("❌ No switch selected")
            return
        
        self.operate_switch(switch_index, force_state=True)
    
    def toggle_selected_switch(self):
        """Toggle the selected switch"""
        switch_index = self.get_selected_switch_index()
        if switch_index is None:
            self.log("❌ No switch selected")
            return
        
        self.operate_switch(switch_index)
    
    def operate_switch(self, switch_index, force_state=None):
        """Operate a switch and update displays with topology validation"""
        if not self.estimator:
            return
        
        try:
            # Get switch info before operation
            switch_info = self.estimator.get_switch_info()
            switch_data = next((s for s in switch_info if s['index'] == switch_index), None)
            
            if not switch_data:
                self.log(f"❌ Switch {switch_index} not found")
                return
            
            old_state = "CLOSED" if switch_data['closed'] else "OPEN"
            
            # Perform switch operation with optional topology checking
            check_topology = self.topology_check_var.get()
            success = self.estimator.toggle_switch(switch_index, force_state, check_topology)
            
            if success:
                new_state = "CLOSED" if force_state else ("OPEN" if force_state == False else ("OPEN" if switch_data['closed'] else "CLOSED"))
                self.log(f"✅ {switch_data['name']}: {old_state} → {new_state}")
                
                # Check topology after successful operation if validation is enabled
                if check_topology:
                    try:
                        validation = self.estimator.validate_switch_operation_topology(switch_index, 
                                                                                      switch_data['closed'], 
                                                                                      not switch_data['closed'])
                        if validation['warnings']:
                            for warning in validation['warnings']:
                                self.log(f"⚠️  Topology Warning: {warning}")
                        
                        impact = validation.get('topology_impact', {})
                        if impact.get('connectivity_status') == 'islanded':
                            self.log(f"🏝️  Network now has {impact.get('total_islands', 0)} islands")
                        elif impact.get('isolated_buses', 0) > 0:
                            self.log(f"🔴 Warning: {impact.get('isolated_buses')} isolated buses")
                            
                    except Exception:
                        pass  # Don't fail the operation if topology check has issues
                
                # Auto-refresh displays
                self.refresh_switch_display()
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
                
            else:
                failure_reason = "Topology validation failed" if check_topology else "Power flow unstable"
                self.log(f"❌ Failed to operate {switch_data['name']} - {failure_reason}")
                
        except Exception as e:
            self.log(f"❌ Switch operation error: {e}")
    
    def check_network_topology(self):
        """Check network topology from switch control panel"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        try:
            self.log("🔍 Performing network topology check...")
            results = self.estimator.check_topology_consistency(detailed_report=True)
            
            # Switch to switch control tab to show results
            self.notebook.select(3)  # Switch Control is tab index 3
            
            # Summary in switch panel
            if results:
                status_icon = "✅" if results['overall_status'] == 'healthy' else "⚠️" if results['overall_status'] == 'warning' else "❌"
                self.log(f"{status_icon} Topology Status: {results['overall_status'].upper()}")
                self.log(f"   Connectivity: {results['connectivity_status'].upper()}")
                self.log(f"   Islands: {len(results['network_islands'])}, Isolated: {len(results['isolated_buses'])}")
            
        except Exception as e:
            self.log(f"❌ Topology check error: {e}")
    
    def open_all_switches(self):
        """Emergency operation: Open all switches"""
        if not self.estimator:
            return
        
        try:
            switch_info = self.estimator.get_switch_info()
            opened_count = 0
            
            for switch_data in switch_info:
                if switch_data['closed']:  # Only operate closed switches
                    success = self.estimator.toggle_switch(switch_data['index'], force_state=False)
                    if success:
                        opened_count += 1
                    else:
                        # If any switch operation fails, log it but continue
                        self.log(f"⚠️ Failed to open {switch_data['name']}")
            
            self.log(f"🚨 Emergency operation: Opened {opened_count} switches")
            self.refresh_switch_display()
            
        except Exception as e:
            self.log(f"❌ Emergency operation error: {e}")
    
    def close_all_switches(self):
        """Operation: Close all switches to normal state"""
        if not self.estimator:
            return
        
        try:
            switch_info = self.estimator.get_switch_info()
            closed_count = 0
            
            for switch_data in switch_info:
                if not switch_data['closed']:  # Only operate open switches
                    success = self.estimator.toggle_switch(switch_data['index'], force_state=True)
                    if success:
                        closed_count += 1
                    else:
                        self.log(f"⚠️ Failed to close {switch_data['name']}")
            
            self.log(f"✅ Closed {closed_count} switches - Network restored")
            self.refresh_switch_display()
            
        except Exception as e:
            self.log(f"❌ Close all operation error: {e}")
    
    def reset_switches_to_normal(self):
        """Reset all switches to their normal (closed) state"""
        self.close_all_switches()
        
    def update_switch_network_plot(self):
        """Update the network plot showing switch states"""
        if not self.estimator or not hasattr(self.estimator, 'net'):
            return
        
        try:
            # Clear the figure
            self.switch_figure.clear()
            ax = self.switch_figure.add_subplot(111)
            
            # Get bus positions
            try:
                positions = self.estimator._create_bus_positions()
            except:
                positions = self.create_default_positions()
            
            if not positions:
                ax.text(0.5, 0.5, 'Network topology not available', 
                       ha='center', va='center', transform=ax.transAxes)
                self.switch_canvas.draw()
                return
            
            # Plot buses
            bus_x = [positions[bus][0] for bus in self.estimator.net.bus.index]
            bus_y = [positions[bus][1] for bus in self.estimator.net.bus.index]
            
            ax.scatter(bus_x, bus_y, c='lightblue', s=400, alpha=0.7, 
                      edgecolors='black', linewidth=2, label='Buses')
            
            # Plot transmission lines with switch status
            self.plot_lines_with_switches(ax, positions)
            
            # Plot switches as symbols
            self.plot_switch_symbols(ax, positions)
            
            # Add bus labels
            for bus_idx in self.estimator.net.bus.index:
                x, y = positions[bus_idx]
                ax.annotate(f'Bus {bus_idx}', (x, y), xytext=(5, 5), 
                           textcoords='offset points', fontsize=8, fontweight='bold')
            
            ax.set_title(f'{self.current_grid} - Network Switch Status', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal')
            ax.legend()
            
            self.switch_canvas.draw()
            
        except Exception as e:
            self.log(f"❌ Error updating switch network plot: {e}")
    
    def plot_lines_with_switches(self, ax, positions):
        """Plot transmission lines with different styles based on switch status"""
        if not hasattr(self.estimator.net, 'switch') or len(self.estimator.net.switch) == 0:
            # No switches, plot all lines normally
            try:
                self.estimator._draw_transmission_lines(ax, positions, color='gray', linewidth=2)
            except:
                pass
            return
        
        # Get switch information grouped by element
        switch_info = self.estimator.get_switch_info()
        line_switch_status = {}
        
        for switch in switch_info:
            if switch['type'] == 'l':  # Line switches
                element_idx = switch['element']
                if element_idx not in line_switch_status:
                    line_switch_status[element_idx] = []
                line_switch_status[element_idx].append(switch['closed'])
        
        # Plot lines with appropriate styling
        for line_idx in self.estimator.net.line.index:
            from_bus = self.estimator.net.line.from_bus.iloc[line_idx]
            to_bus = self.estimator.net.line.to_bus.iloc[line_idx]
            
            if from_bus in positions and to_bus in positions:
                x1, y1 = positions[from_bus]
                x2, y2 = positions[to_bus]
                
                # Determine line style based on switch status
                if line_idx in line_switch_status:
                    # Line has switches
                    all_closed = all(line_switch_status[line_idx])
                    if all_closed:
                        # All switches closed - normal operation
                        ax.plot([x1, x2], [y1, y2], 'g-', linewidth=3, alpha=0.8, label='Energized Line')
                    else:
                        # Some switches open - line de-energized
                        ax.plot([x1, x2], [y1, y2], 'r--', linewidth=2, alpha=0.6, label='De-energized Line')
                else:
                    # No switches on this line
                    ax.plot([x1, x2], [y1, y2], 'gray', linewidth=2, alpha=0.7, label='No Switches')
    
    def plot_switch_symbols(self, ax, positions):
        """Plot switch symbols on the network"""
        if not hasattr(self.estimator.net, 'switch') or len(self.estimator.net.switch) == 0:
            return
        
        switch_info = self.estimator.get_switch_info()
        
        for switch in switch_info:
            try:
                bus_idx = switch['bus']
                if bus_idx not in positions:
                    continue
                
                x, y = positions[bus_idx]
                
                # Offset switch symbol slightly from bus
                offset = 0.05
                sx = x + offset
                sy = y + offset
                
                if switch['closed']:
                    # Closed switch - solid square
                    ax.scatter([sx], [sy], c='green', s=100, marker='s', 
                             edgecolors='darkgreen', linewidth=2, label='Closed Switch')
                else:
                    # Open switch - open square
                    ax.scatter([sx], [sy], c='white', s=100, marker='s', 
                             edgecolors='red', linewidth=2, label='Open Switch')
                
                # Add switch label
                ax.annotate(switch['switch_type'], (sx, sy), xytext=(-10, -15), 
                           textcoords='offset points', fontsize=6, ha='center')
                           
            except Exception as e:
                # Skip problematic switches
                continue
    
    def create_measurement_management(self, parent):
        """Create measurement management interface"""
        # Control panel at top
        control_panel = ttk.Frame(parent)
        control_panel.pack(fill=tk.X, padx=5, pady=5)
        
        # Title and refresh button
        title_frame = ttk.Frame(control_panel)
        title_frame.pack(fill=tk.X)
        
        ttk.Label(title_frame, text="Measurement Management", 
                 font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        
        ttk.Button(title_frame, text="Refresh Measurements", 
                  command=self.refresh_measurement_display).pack(side=tk.RIGHT)
        
        # Create horizontal layout
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Measurement controls
        left_panel = ttk.LabelFrame(main_frame, text="Measurement Controls", padding="5")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Measurement statistics
        stats_frame = ttk.LabelFrame(left_panel, text="Statistics", padding="5")
        stats_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.measurement_stats_text = tk.Text(stats_frame, height=8, width=35, font=("Consolas", 9))
        self.measurement_stats_text.pack()
        
        # Filter controls
        filter_frame = ttk.LabelFrame(left_panel, text="Filter Options", padding="5")
        filter_frame.pack(fill=tk.X, pady=5)
        
        # Filter by measurement type
        ttk.Label(filter_frame, text="Filter by Type:").pack(anchor=tk.W)
        self.filter_type_var = tk.StringVar(value="all")
        type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var,
                                 values=["all", "v", "p", "q"], state="readonly", width=15)
        type_combo.pack(fill=tk.X, pady=2)
        type_combo.bind("<<ComboboxSelected>>", self.on_measurement_filter_change)
        
        # Filter by element
        ttk.Label(filter_frame, text="Filter by Element:").pack(anchor=tk.W, pady=(5, 0))
        element_filter_frame = ttk.Frame(filter_frame)
        element_filter_frame.pack(fill=tk.X)
        
        self.filter_element_var = tk.StringVar()
        element_entry = ttk.Entry(element_filter_frame, textvariable=self.filter_element_var, width=10)
        element_entry.pack(side=tk.LEFT)
        element_entry.bind('<KeyRelease>', self.on_measurement_filter_change)
        
        ttk.Button(element_filter_frame, text="Clear", 
                  command=self.clear_measurement_filter).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Selection operations
        selection_frame = ttk.LabelFrame(left_panel, text="Selection Operations", padding="5")
        selection_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(selection_frame, text="Select All", 
                  command=self.select_all_measurements).pack(fill=tk.X, pady=1)
        ttk.Button(selection_frame, text="Select None", 
                  command=self.deselect_all_measurements).pack(fill=tk.X, pady=1)
        ttk.Button(selection_frame, text="Invert Selection", 
                  command=self.invert_measurement_selection).pack(fill=tk.X, pady=1)
        
        # Removal operations
        removal_frame = ttk.LabelFrame(left_panel, text="Removal Operations", padding="5")
        removal_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(removal_frame, text="Remove Selected", 
                  command=self.remove_selected_measurements).pack(fill=tk.X, pady=1)
        ttk.Button(removal_frame, text="Remove by Type", 
                  command=self.remove_measurements_by_type_dialog).pack(fill=tk.X, pady=1)
        ttk.Button(removal_frame, text="Remove by Element", 
                  command=self.remove_measurements_by_element_dialog).pack(fill=tk.X, pady=1)
        
        # Failure simulation
        simulation_frame = ttk.LabelFrame(left_panel, text="Failure Simulation", padding="5")
        simulation_frame.pack(fill=tk.X, pady=5)
        
        # Failure rate setting
        failure_rate_frame = ttk.Frame(simulation_frame)
        failure_rate_frame.pack(fill=tk.X, pady=2)
        ttk.Label(failure_rate_frame, text="Failure Rate:").pack(side=tk.LEFT)
        self.failure_rate_var = tk.StringVar(value="0.1")
        ttk.Entry(failure_rate_frame, textvariable=self.failure_rate_var, width=8).pack(side=tk.RIGHT)
        
        ttk.Button(simulation_frame, text="Simulate Random Failures", 
                  command=self.simulate_random_failures).pack(fill=tk.X, pady=1)
        ttk.Button(simulation_frame, text="Simulate Systematic Failures", 
                  command=self.simulate_systematic_failures).pack(fill=tk.X, pady=1)
        
        # Backup and restore
        backup_frame = ttk.LabelFrame(left_panel, text="Backup & Restore", padding="5")
        backup_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(backup_frame, text="Backup Measurements", 
                  command=self.backup_measurements).pack(fill=tk.X, pady=1)
        ttk.Button(backup_frame, text="Restore Measurements", 
                  command=self.restore_measurements).pack(fill=tk.X, pady=1)
        
        # Observability analysis
        observability_frame = ttk.LabelFrame(left_panel, text="Observability Analysis", padding="5")
        observability_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(observability_frame, text="Analyze Observability", 
                  command=self.analyze_observability).pack(fill=tk.X, pady=1)
        ttk.Button(observability_frame, text="Check Redundancy", 
                  command=self.check_measurement_redundancy).pack(fill=tk.X, pady=1)
        
        # Missing measurement estimation
        estimation_frame = ttk.LabelFrame(left_panel, text="Missing Measurement Estimation", padding="5")
        estimation_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(estimation_frame, text="Identify Missing Measurements", 
                  command=self.identify_missing_measurements).pack(fill=tk.X, pady=1)
        
        # Estimation method selection
        method_frame = ttk.Frame(estimation_frame)
        method_frame.pack(fill=tk.X, pady=2)
        ttk.Label(method_frame, text="Method:").pack(side=tk.LEFT)
        self.estimation_method_var = tk.StringVar(value="interpolation")
        method_combo = ttk.Combobox(method_frame, textvariable=self.estimation_method_var,
                                   values=["interpolation", "load_flow"], state="readonly", width=12)
        method_combo.pack(side=tk.RIGHT)
        
        # Noise level for estimated measurements
        noise_frame = ttk.Frame(estimation_frame)
        noise_frame.pack(fill=tk.X, pady=2)
        ttk.Label(noise_frame, text="Noise Level:").pack(side=tk.LEFT)
        self.estimation_noise_var = tk.StringVar(value="0.02")
        ttk.Entry(noise_frame, textvariable=self.estimation_noise_var, width=8).pack(side=tk.RIGHT)
        
        ttk.Button(estimation_frame, text="Estimate Missing Measurements", 
                  command=self.estimate_missing_measurements).pack(fill=tk.X, pady=1)
        ttk.Button(estimation_frame, text="Add Strategic Measurements", 
                  command=self.add_strategic_measurements).pack(fill=tk.X, pady=1)
        
        # Pseudomeasurement management
        pseudo_frame = ttk.LabelFrame(left_panel, text="Pseudomeasurement Management", padding="5")
        pseudo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(pseudo_frame, text="Identify Pseudo Locations", 
                  command=self.identify_pseudo_locations).pack(fill=tk.X, pady=1)
        
        # Pseudomeasurement type selection
        type_frame = ttk.Frame(pseudo_frame)
        type_frame.pack(fill=tk.X, pady=2)
        ttk.Label(type_frame, text="Types:").pack(side=tk.LEFT)
        
        # Checkboxes for pseudomeasurement types
        self.pseudo_voltage_var = tk.BooleanVar(value=True)
        self.pseudo_zero_inj_var = tk.BooleanVar(value=True)
        self.pseudo_slack_var = tk.BooleanVar(value=False)  # Less commonly needed
        
        ttk.Checkbutton(type_frame, text="Voltage", variable=self.pseudo_voltage_var).pack(side=tk.LEFT, padx=2)
        
        type_frame2 = ttk.Frame(pseudo_frame)
        type_frame2.pack(fill=tk.X, pady=1)
        ttk.Checkbutton(type_frame2, text="Zero Injection", variable=self.pseudo_zero_inj_var).pack(side=tk.LEFT)
        ttk.Checkbutton(type_frame2, text="Slack Reference", variable=self.pseudo_slack_var).pack(side=tk.LEFT)
        
        ttk.Button(pseudo_frame, text="Add Pseudomeasurements", 
                  command=self.add_pseudomeasurements).pack(fill=tk.X, pady=1)
        ttk.Button(pseudo_frame, text="Remove Pseudomeasurements", 
                  command=self.remove_pseudomeasurements).pack(fill=tk.X, pady=1)
        ttk.Button(pseudo_frame, text="Show Pseudo Summary", 
                  command=self.show_pseudo_summary).pack(fill=tk.X, pady=1)
        
        # Right panel - Measurement list
        right_panel = ttk.LabelFrame(main_frame, text="Measurements", padding="5")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create measurement treeview
        list_frame = ttk.Frame(right_panel)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Select', 'Index', 'Type', 'Element', 'Description', 'Value', 'StdDev')
        self.measurement_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        column_config = {
            'Select': ('☐', 40),
            'Index': ('Index', 50),
            'Type': ('Type', 50),
            'Element': ('Element', 80),
            'Description': ('Description', 250),
            'Value': ('Value', 80),
            'StdDev': ('Std Dev', 70)
        }
        
        for col, (heading, width) in column_config.items():
            self.measurement_tree.heading(col, text=heading)
            self.measurement_tree.column(col, width=width, anchor=tk.CENTER if col in ['Select', 'Index', 'Type'] else tk.W)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Measurement.Treeview", font=("Consolas", 9))
        self.measurement_tree.configure(style="Measurement.Treeview")
        
        # Add scrollbars
        meas_v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.measurement_tree.yview)
        meas_h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.measurement_tree.xview)
        self.measurement_tree.configure(yscrollcommand=meas_v_scrollbar.set, xscrollcommand=meas_h_scrollbar.set)
        
        # Grid layout for measurement list
        self.measurement_tree.grid(row=0, column=0, sticky='nsew')
        meas_v_scrollbar.grid(row=0, column=1, sticky='ns')
        meas_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind click events for selection
        self.measurement_tree.bind('<Button-1>', self.on_measurement_click)
        self.measurement_tree.bind('<Double-1>', self.on_measurement_double_click)
        
        # Status for measurement management
        self.measurement_status_var = tk.StringVar(value="No measurements available - Generate measurements first")
        measurement_status_label = ttk.Label(parent, textvariable=self.measurement_status_var, 
                                           font=("Arial", 9), foreground="gray")
        measurement_status_label.pack(pady=5)
        
        # Initialize displays
        self.measurement_selection = set()  # Track selected measurements
        self.clear_measurement_display()
        
    def refresh_measurement_display(self):
        """Refresh the measurement management display"""
        if not self.estimator or not hasattr(self.estimator, 'net') or self.estimator.net is None:
            self.measurement_status_var.set("No grid available - Create a grid model first")
            self.clear_measurement_display()
            return
        
        if len(self.estimator.net.measurement) == 0:
            self.measurement_status_var.set("No measurements available - Generate measurements first")
            self.clear_measurement_display()
            return
        
        try:
            self.update_status("Updating measurement display...")
            
            # Get measurement information
            measurement_info = self.estimator.get_measurement_info()
            
            # Update statistics
            self.update_measurement_statistics()
            
            # Clear and populate measurement list
            self.clear_measurement_list()
            
            # Apply filters
            filter_type = self.filter_type_var.get()
            filter_element = self.filter_element_var.get().strip()
            
            for meas_data in measurement_info:
                # Apply type filter
                if filter_type != "all" and meas_data['type'] != filter_type:
                    continue
                
                # Apply element filter
                if filter_element and str(filter_element) not in str(meas_data['element']):
                    continue
                
                # Determine selection status
                select_symbol = "☑" if meas_data['index'] in self.measurement_selection else "☐"
                
                values = (
                    select_symbol,
                    meas_data['index'],
                    meas_data['type'].upper(),
                    meas_data['element_name'],
                    meas_data['element_description'],
                    f"{meas_data['value']:.4f}",
                    f"{meas_data['std_dev']:.4f}"
                )
                
                # Add to treeview with measurement index as tag
                item_id = self.measurement_tree.insert('', 'end', values=values, 
                                                      tags=(str(meas_data['index']),))
                
                # Configure colors based on selection
                if meas_data['index'] in self.measurement_selection:
                    self.measurement_tree.item(item_id, tags=('selected',))
            
            # Configure selection highlighting
            self.measurement_tree.tag_configure('selected', background='#e6f3ff')
            
            # Update status
            total_measurements = len(measurement_info)
            visible_measurements = len(self.measurement_tree.get_children())
            selected_count = len(self.measurement_selection)
            
            status_msg = f"Showing {visible_measurements}/{total_measurements} measurements"
            if selected_count > 0:
                status_msg += f", {selected_count} selected"
            
            self.measurement_status_var.set(status_msg)
            self.update_status("Measurement display updated")
            
        except Exception as e:
            self.log(f"❌ Error updating measurement display: {e}")
            self.measurement_status_var.set("Error updating measurement display")
            self.update_status("Error")
    
    def clear_measurement_display(self):
        """Clear the measurement display"""
        self.clear_measurement_list()
        self.measurement_selection.clear()
        
        # Clear statistics
        self.measurement_stats_text.delete(1.0, tk.END)
        self.measurement_stats_text.insert(tk.END, "No measurements available")
    
    def clear_measurement_list(self):
        """Clear the measurement list"""
        for item in self.measurement_tree.get_children():
            self.measurement_tree.delete(item)
    
    def update_measurement_statistics(self):
        """Update measurement statistics display"""
        if not self.estimator or not hasattr(self.estimator, 'net'):
            return
        
        try:
            stats = self.estimator.get_measurement_statistics()
            redundancy = self.estimator.check_measurement_redundancy()
            
            # Clear and update statistics text
            self.measurement_stats_text.delete(1.0, tk.END)
            
            stats_text = f"📊 MEASUREMENT STATISTICS\n"
            stats_text += f"═══════════════════════════\n"
            stats_text += f"Total: {stats.get('total_measurements', 0)}\n\n"
            
            # By type
            stats_text += f"By Type:\n"
            for mtype, count in stats.get('by_type', {}).items():
                stats_text += f"  {mtype.upper()}: {count}\n"
            
            # Coverage
            coverage = stats.get('coverage', {})
            stats_text += f"\nCoverage:\n"
            stats_text += f"  Voltage: {coverage.get('voltage_buses', 0)}/{len(self.estimator.net.bus)} buses ({coverage.get('voltage_percentage', 0):.1f}%)\n"
            stats_text += f"  Power: {coverage.get('power_lines', 0)}/{len(self.estimator.net.line)} lines ({coverage.get('power_percentage', 0):.1f}%)\n"
            
            # Redundancy
            stats_text += f"\nRedundancy:\n"
            stats_text += f"  Sufficient: {'✅' if redundancy.get('sufficient_measurements') else '❌'}\n"
            stats_text += f"  Ratio: {redundancy.get('redundancy_ratio', 0):.2f}\n"
            stats_text += f"  Critical: {len(redundancy.get('critical_measurements', []))}\n"
            
            self.measurement_stats_text.insert(tk.END, stats_text)
            
        except Exception as e:
            self.measurement_stats_text.delete(1.0, tk.END)
            self.measurement_stats_text.insert(tk.END, f"Error updating statistics: {e}")
    
    def on_measurement_click(self, event):
        """Handle measurement list click for selection"""
        item = self.measurement_tree.selection()[0] if self.measurement_tree.selection() else None
        if not item:
            return
        
        # Get measurement index from tags
        tags = self.measurement_tree.item(item, 'tags')
        if tags:
            try:
                meas_index = int(tags[0])
                self.toggle_measurement_selection(meas_index)
            except (ValueError, IndexError):
                pass
    
    def on_measurement_double_click(self, event):
        """Handle measurement list double-click for details"""
        item = self.measurement_tree.selection()[0] if self.measurement_tree.selection() else None
        if not item:
            return
        
        values = self.measurement_tree.item(item, 'values')
        if len(values) >= 5:
            self.log(f"📋 Measurement Details: {values[3]} - {values[4]}")
    
    def toggle_measurement_selection(self, measurement_index):
        """Toggle selection of a measurement"""
        if measurement_index in self.measurement_selection:
            self.measurement_selection.remove(measurement_index)
        else:
            self.measurement_selection.add(measurement_index)
        
        # Refresh display to update selection indicators
        self.refresh_measurement_display()
    
    def on_measurement_filter_change(self, event=None):
        """Handle filter changes"""
        self.refresh_measurement_display()
    
    def clear_measurement_filter(self):
        """Clear measurement filters"""
        self.filter_type_var.set("all")
        self.filter_element_var.set("")
        self.refresh_measurement_display()
    
    def select_all_measurements(self):
        """Select all visible measurements"""
        if not self.estimator:
            return
        
        measurement_info = self.estimator.get_measurement_info()
        filter_type = self.filter_type_var.get()
        filter_element = self.filter_element_var.get().strip()
        
        for meas_data in measurement_info:
            # Apply same filters as display
            if filter_type != "all" and meas_data['type'] != filter_type:
                continue
            if filter_element and str(filter_element) not in str(meas_data['element']):
                continue
            
            self.measurement_selection.add(meas_data['index'])
        
        self.refresh_measurement_display()
        self.log(f"✅ Selected {len(self.measurement_selection)} measurements")
    
    def deselect_all_measurements(self):
        """Deselect all measurements"""
        self.measurement_selection.clear()
        self.refresh_measurement_display()
        self.log("✅ Deselected all measurements")
    
    def invert_measurement_selection(self):
        """Invert measurement selection"""
        if not self.estimator:
            return
        
        measurement_info = self.estimator.get_measurement_info()
        all_indices = {meas['index'] for meas in measurement_info}
        self.measurement_selection = all_indices - self.measurement_selection
        
        self.refresh_measurement_display()
        self.log(f"✅ Inverted selection - {len(self.measurement_selection)} measurements selected")
    
    def remove_selected_measurements(self):
        """Remove selected measurements"""
        if not self.measurement_selection:
            self.log("❌ No measurements selected")
            return
        
        if not messagebox.askyesno("Confirm Removal", 
                                 f"Remove {len(self.measurement_selection)} selected measurements?"):
            return
        
        try:
            success, message = self.estimator.remove_measurements(list(self.measurement_selection))
            if success:
                self.log(f"✅ {message}")
                self.measurement_selection.clear()
                self.refresh_measurement_display()
                
                # Auto-refresh other displays if enabled
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
            else:
                self.log(f"❌ {message}")
                
        except Exception as e:
            self.log(f"❌ Error removing measurements: {e}")
    
    def remove_measurements_by_type_dialog(self):
        """Show dialog to remove measurements by type"""
        # Simple dialog using tkinter simpledialog
        from tkinter import simpledialog
        
        mtype = simpledialog.askstring("Remove by Type", 
                                     "Enter measurement type (v, p, q):",
                                     initialvalue="v")
        if not mtype:
            return
        
        if not messagebox.askyesno("Confirm Removal", 
                                 f"Remove all '{mtype}' measurements?"):
            return
        
        try:
            success, message = self.estimator.remove_measurements_by_type(mtype)
            if success:
                self.log(f"✅ {message}")
                self.refresh_measurement_display()
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
            else:
                self.log(f"❌ {message}")
        except Exception as e:
            self.log(f"❌ Error removing measurements: {e}")
    
    def remove_measurements_by_element_dialog(self):
        """Show dialog to remove measurements by element"""
        from tkinter import simpledialog
        
        element = simpledialog.askstring("Remove by Element", 
                                       "Enter element index (bus/line number):")
        if not element:
            return
        
        try:
            element_idx = int(element)
        except ValueError:
            self.log("❌ Invalid element index")
            return
        
        if not messagebox.askyesno("Confirm Removal", 
                                 f"Remove all measurements on element {element_idx}?"):
            return
        
        try:
            success, message = self.estimator.remove_measurements_by_element([element_idx])
            if success:
                self.log(f"✅ {message}")
                self.refresh_measurement_display()
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
            else:
                self.log(f"❌ {message}")
        except Exception as e:
            self.log(f"❌ Error removing measurements: {e}")
    
    def simulate_random_failures(self):
        """Simulate random measurement failures"""
        try:
            failure_rate = float(self.failure_rate_var.get())
        except ValueError:
            self.log("❌ Invalid failure rate")
            return
        
        if not messagebox.askyesno("Simulate Failures", 
                                 f"Simulate random failures at {failure_rate*100:.1f}% rate?"):
            return
        
        try:
            success, message = self.estimator.simulate_measurement_failures(failure_rate, ['random'])
            if success:
                self.log(f"✅ {message}")
                self.refresh_measurement_display()
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
            else:
                self.log(f"❌ {message}")
        except Exception as e:
            self.log(f"❌ Error simulating failures: {e}")
    
    def simulate_systematic_failures(self):
        """Simulate systematic measurement failures"""
        try:
            failure_rate = float(self.failure_rate_var.get())
        except ValueError:
            self.log("❌ Invalid failure rate")
            return
        
        if not messagebox.askyesno("Simulate Failures", 
                                 f"Simulate systematic failures at {failure_rate*100:.1f}% rate?"):
            return
        
        try:
            success, message = self.estimator.simulate_measurement_failures(failure_rate, ['systematic'])
            if success:
                self.log(f"✅ {message}")
                self.refresh_measurement_display()
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
            else:
                self.log(f"❌ {message}")
        except Exception as e:
            self.log(f"❌ Error simulating failures: {e}")
    
    def backup_measurements(self):
        """Create backup of current measurements"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        try:
            success = self.estimator.backup_measurements()
            if success:
                self.log("✅ Measurements backed up")
            else:
                self.log("❌ No measurements to backup")
        except Exception as e:
            self.log(f"❌ Error backing up measurements: {e}")
    
    def restore_measurements(self):
        """Restore measurements from backup"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        try:
            success, message = self.estimator.restore_measurements()
            if success:
                self.log(f"✅ {message}")
                self.measurement_selection.clear()
                self.refresh_measurement_display()
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
            else:
                self.log(f"❌ {message}")
        except Exception as e:
            self.log(f"❌ Error restoring measurements: {e}")
    
    def analyze_observability(self):
        """Analyze system observability with current measurements"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        if not hasattr(self.estimator.net, 'measurement') or len(self.estimator.net.measurement) == 0:
            self.log("❌ No measurements available for observability analysis")
            return
        
        try:
            self.log("🔍 Analyzing system observability...")
            
            # Run observability analysis
            obs_results = self.estimator.test_observability()
            
            if obs_results:
                self.log("📊 OBSERVABILITY ANALYSIS RESULTS:")
                self.log(f"   Level: {obs_results.get('level', 'Unknown')}")
                self.log(f"   Total measurements: {obs_results.get('total_measurements', 0)}")
                self.log(f"   Voltage measurements: {obs_results.get('voltage_measurements', 0)}")
                self.log(f"   Power flow measurements: {obs_results.get('power_measurements', 0)}")
                
                # Show conditions
                conditions = obs_results.get('conditions', [])
                if conditions:
                    self.log("   Conditions:")
                    for condition in conditions:
                        self.log(f"     {condition}")
                
                # Show coverage
                coverage = obs_results.get('coverage', 0)
                self.log(f"   Network coverage: {coverage:.1%}")
                
                # Provide recommendations if observability is poor
                if 'Poor' in obs_results.get('level', '') or 'Marginal' in obs_results.get('level', ''):
                    self.log("💡 RECOMMENDATIONS:")
                    self.log("   • Add voltage measurements at critical buses")
                    self.log("   • Add power flow measurements on key lines")
                    self.log("   • Ensure measurement redundancy for reliability")
            
        except Exception as e:
            self.log(f"❌ Error analyzing observability: {e}")
    
    def check_measurement_redundancy(self):
        """Check measurement redundancy for reliability"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        if not hasattr(self.estimator.net, 'measurement') or len(self.estimator.net.measurement) == 0:
            self.log("❌ No measurements available for redundancy analysis")
            return
        
        try:
            self.log("🔍 Checking measurement redundancy...")
            
            # Run redundancy analysis (use the existing method)
            redundancy_info = self.estimator.check_measurement_redundancy()
            
            if redundancy_info:
                self.log("📊 MEASUREMENT REDUNDANCY ANALYSIS:")
                self.log(f"   Status: {redundancy_info.get('status', 'Unknown')}")
                self.log(f"   Total measurements: {redundancy_info.get('total_measurements', 0)}")
                self.log(f"   Minimum required: {redundancy_info.get('minimum_measurements', 0)}")
                self.log(f"   Redundancy ratio: {redundancy_info.get('redundancy_ratio', 0):.2f}")
                
                # Show recommendations
                recommendations = redundancy_info.get('recommendations', [])
                if recommendations:
                    self.log("💡 RECOMMENDATIONS:")
                    for rec in recommendations:
                        self.log(f"   • {rec}")
                
                # Check critical measurements
                measurement_info = self.estimator.get_measurement_info()
                voltage_count = sum(1 for m in measurement_info if m['type'] == 'v')
                power_count = sum(1 for m in measurement_info if m['type'] in ['p', 'q'])
                
                self.log("📈 MEASUREMENT BREAKDOWN:")
                self.log(f"   Voltage measurements: {voltage_count}")
                self.log(f"   Power measurements: {power_count}")
                
                # Critical bus analysis
                bus_count = len(self.estimator.net.bus)
                if voltage_count < bus_count:
                    missing_v = bus_count - voltage_count
                    self.log(f"   ⚠️  Missing voltage measurements: {missing_v} buses")
                
                if redundancy_info.get('redundancy_ratio', 0) < 1.5:
                    self.log("   ⚠️  Low redundancy - consider adding measurements")
                elif redundancy_info.get('redundancy_ratio', 0) > 3.0:
                    self.log("   ✅ High redundancy - good measurement coverage")
                else:
                    self.log("   ✅ Adequate redundancy level")
            
        except Exception as e:
            self.log(f"❌ Error checking redundancy: {e}")
    
    def identify_missing_measurements(self):
        """Identify and display missing measurements"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        try:
            self.log("🔍 Identifying missing measurements...")
            
            # Get missing measurement analysis
            missing_info = self.estimator.identify_missing_measurements()
            
            if missing_info['total_missing'] == 0:
                self.log("✅ No missing measurements - full coverage achieved!")
                return
            
            self.log("📋 MISSING MEASUREMENT ANALYSIS:")
            self.log(f"   Total missing: {missing_info['total_missing']}")
            
            # Show missing voltage measurements
            if missing_info['missing_voltage_measurements']:
                self.log(f"   Missing voltage measurements: {len(missing_info['missing_voltage_measurements'])}")
                for i, missing in enumerate(missing_info['missing_voltage_measurements'][:5]):  # Show first 5
                    self.log(f"     • {missing['description']}")
                if len(missing_info['missing_voltage_measurements']) > 5:
                    remaining = len(missing_info['missing_voltage_measurements']) - 5
                    self.log(f"     ... and {remaining} more voltage measurements")
            
            # Show missing power measurements
            if missing_info['missing_power_measurements']:
                power_count = len(missing_info['missing_power_measurements'])
                self.log(f"   Missing power measurements: {power_count}")
                for i, missing in enumerate(missing_info['missing_power_measurements'][:5]):  # Show first 5
                    self.log(f"     • {missing['description']}")
                if power_count > 5:
                    remaining = power_count - 5
                    self.log(f"     ... and {remaining} more power measurements")
            
            # Show recommendations
            if missing_info['recommendations']:
                self.log("💡 RECOMMENDATIONS:")
                for rec in missing_info['recommendations']:
                    self.log(f"   • {rec}")
            
        except Exception as e:
            self.log(f"❌ Error identifying missing measurements: {e}")
    
    def estimate_missing_measurements(self):
        """Estimate and add missing measurements"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        try:
            method = self.estimation_method_var.get()
            noise_level = float(self.estimation_noise_var.get())
            
            self.log(f"🔮 Estimating missing measurements using {method} method...")
            self.log(f"   Noise level: {noise_level*100:.1f}%")
            
            # Estimate missing measurements
            success, result = self.estimator.estimate_missing_measurements(method, noise_level)
            
            if success:
                if isinstance(result, dict):
                    self.log(f"✅ {result['summary']}")
                    self.log(f"   Added {result['added_count']} measurements")
                    
                    # Show some estimation details
                    if result.get('details'):
                        self.log("   Sample estimations:")
                        for detail in result['details'][:5]:
                            self.log(f"     • {detail}")
                    
                    self.log(f"   Total missing identified: {result.get('total_available', 0)}")
                else:
                    self.log(f"✅ {result}")
                
                # Refresh displays
                self.refresh_measurement_display()
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
            else:
                self.log(f"❌ {result}")
                
        except ValueError:
            self.log("❌ Invalid noise level")
        except Exception as e:
            self.log(f"❌ Error estimating measurements: {e}")
    
    def add_strategic_measurements(self):
        """Add strategic measurements for optimal observability"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        try:
            self.log("🎯 Adding strategic measurements for optimal observability...")
            
            # Add strategic measurements
            success, result = self.estimator.add_strategic_measurements('excellent')
            
            if success:
                if isinstance(result, dict):
                    self.log(f"✅ {result['summary']}")
                    self.log(f"   Strategy: {result['strategy']}")
                    self.log(f"   Added {result['added_count']} measurements")
                    
                    # Show strategy details
                    if result.get('details'):
                        self.log("   Strategic additions:")
                        for detail in result['details']:
                            self.log(f"     • {detail}")
                else:
                    self.log(f"✅ {result}")
                
                # Check observability improvement
                self.log("🔍 Analyzing observability improvement...")
                obs_results = self.estimator.test_observability()
                if obs_results:
                    self.log(f"   New observability level: {obs_results.get('level', 'Unknown')}")
                
                # Refresh displays
                self.refresh_measurement_display()
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
            else:
                self.log(f"❌ {result}")
                
        except Exception as e:
            self.log(f"❌ Error adding strategic measurements: {e}")
    
    def identify_pseudo_locations(self):
        """Identify locations where pseudomeasurements are needed"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        try:
            self.log("🔍 Identifying pseudomeasurement locations...")
            
            # Get pseudomeasurement analysis
            pseudo_info = self.estimator.identify_pseudomeasurement_locations()
            
            if pseudo_info['total_needed'] == 0:
                self.log("✅ No pseudomeasurements needed - system is fully observable")
                return
            
            self.log("📍 PSEUDOMEASUREMENT LOCATION ANALYSIS:")
            self.log(f"   Total locations identified: {pseudo_info['total_needed']}")
            
            # Show voltage pseudomeasurement locations
            if pseudo_info['voltage_pseudomeasurements']:
                count = len(pseudo_info['voltage_pseudomeasurements'])
                self.log(f"   Voltage pseudomeasurements needed: {count}")
                for i, pseudo in enumerate(pseudo_info['voltage_pseudomeasurements'][:5]):
                    self.log(f"     • {pseudo['description']} (uncertainty: {pseudo['uncertainty']*100:.1f}%)")
                if count > 5:
                    self.log(f"     ... and {count - 5} more voltage locations")
            
            # Show zero injection locations
            if pseudo_info['zero_injection_buses']:
                count = len(pseudo_info['zero_injection_buses'])
                self.log(f"   Zero injection pseudomeasurements: {count}")
                # Group by bus
                buses = set(p['bus_index'] for p in pseudo_info['zero_injection_buses'])
                for bus_idx in sorted(buses)[:3]:
                    bus_name = f"Bus {bus_idx}"
                    self.log(f"     • Zero injection at {bus_name} (P & Q)")
                if len(buses) > 3:
                    self.log(f"     ... and {len(buses) - 3} more buses")
            
            # Show slack bus reference
            if pseudo_info['slack_bus_pseudomeasurements']:
                for pseudo in pseudo_info['slack_bus_pseudomeasurements']:
                    self.log(f"   Slack reference: {pseudo['description']}")
            
            # Show recommendations
            if pseudo_info['recommendations']:
                self.log("💡 RECOMMENDATIONS:")
                for rec in pseudo_info['recommendations']:
                    self.log(f"   • {rec}")
            
        except Exception as e:
            self.log(f"❌ Error identifying pseudomeasurement locations: {e}")
    
    def add_pseudomeasurements(self):
        """Add pseudomeasurements based on selected types"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        try:
            # Determine which types to add based on checkboxes
            types = []
            if self.pseudo_voltage_var.get():
                types.append('voltage')
            if self.pseudo_zero_inj_var.get():
                types.append('zero_injection')
            if self.pseudo_slack_var.get():
                types.append('slack_reference')
            
            if not types:
                self.log("❌ No pseudomeasurement types selected")
                return
            
            type_names = {
                'voltage': 'Voltage',
                'zero_injection': 'Zero Injection',
                'slack_reference': 'Slack Reference'
            }
            selected_types = ', '.join(type_names[t] for t in types)
            self.log(f"🔮 Adding pseudomeasurements: {selected_types}")
            
            # Add pseudomeasurements
            success, result = self.estimator.add_pseudomeasurements(types)
            
            if success:
                if isinstance(result, dict):
                    self.log(f"✅ {result['summary']}")
                    self.log(f"   Added {result['added_count']} pseudomeasurements")
                    self.log(f"   Types: {', '.join(result['types'])}")
                    
                    # Show addition details
                    if result.get('details'):
                        self.log("   Added pseudomeasurements:")
                        for detail in result['details'][:8]:  # Show first 8
                            self.log(f"     • {detail}")
                        if len(result['details']) > 8:
                            remaining = len(result['details']) - 8
                            self.log(f"     ... and {remaining} more")
                    
                    self.log(f"   Total identified locations: {result.get('total_identified', 0)}")
                else:
                    self.log(f"✅ {result}")
                
                # Refresh displays
                self.refresh_measurement_display()
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
            else:
                self.log(f"❌ {result}")
                
        except Exception as e:
            self.log(f"❌ Error adding pseudomeasurements: {e}")
    
    def remove_pseudomeasurements(self):
        """Remove all pseudomeasurements"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        try:
            self.log("🗑️ Removing all pseudomeasurements...")
            
            success, result = self.estimator.remove_pseudomeasurements()
            
            if success:
                self.log(f"✅ {result}")
                
                # Refresh displays
                self.refresh_measurement_display()
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
            else:
                self.log(f"❌ {result}")
                
        except Exception as e:
            self.log(f"❌ Error removing pseudomeasurements: {e}")
    
    def show_pseudo_summary(self):
        """Show summary of current pseudomeasurements"""
        if not self.estimator:
            self.log("❌ No grid model available")
            return
        
        try:
            self.log("📊 Analyzing current pseudomeasurements...")
            
            summary = self.estimator.get_pseudomeasurement_summary()
            
            if not summary:
                self.log("❌ Could not get pseudomeasurement summary")
                return
            
            self.log("📈 PSEUDOMEASUREMENT SUMMARY:")
            self.log(f"   Total measurements: {summary.get('total_measurements', 0)}")
            self.log(f"   Real measurements: {summary.get('real_measurements', 0)}")
            self.log(f"   Pseudomeasurements: {summary.get('pseudomeasurements', 0)}")
            
            # Show breakdown by type
            if summary.get('pseudo_types'):
                self.log("   Pseudomeasurement types:")
                for ptype, count in summary['pseudo_types'].items():
                    self.log(f"     • {ptype}: {count}")
            
            # Show sample pseudomeasurements
            if summary.get('pseudo_details'):
                details = summary['pseudo_details']
                self.log("   Sample pseudomeasurements:")
                for detail in details[:5]:  # Show first 5
                    name = detail.get('name', f"{detail['type']}_elem_{detail['element']}")
                    value = detail.get('value', 0)
                    self.log(f"     • {name}: {value:.4f}")
                
                if len(details) > 5:
                    remaining = len(details) - 5
                    self.log(f"     ... and {remaining} more pseudomeasurements")
            
            # Calculate percentage
            total = summary.get('total_measurements', 0)
            pseudo = summary.get('pseudomeasurements', 0)
            if total > 0:
                percentage = (pseudo / total) * 100
                self.log(f"   Pseudomeasurement ratio: {percentage:.1f}%")
                
                if percentage > 30:
                    self.log("   ⚠️  High pseudomeasurement ratio - consider adding real measurements")
                elif percentage > 0:
                    self.log("   ✅ Reasonable pseudomeasurement usage")
                else:
                    self.log("   ℹ️  No pseudomeasurements currently in use")
            
        except Exception as e:
            self.log(f"❌ Error showing pseudomeasurement summary: {e}")
        
    def refresh_results_table(self):
        """Refresh the results table with current state estimation data or measurements"""
        if not self.estimator:
            self.table_status_var.set("No grid model available")
            self.clear_results_table()
            return
        
        # Check if we have measurements to display
        if not hasattr(self.estimator.net, 'measurement') or len(self.estimator.net.measurement) == 0:
            self.table_status_var.set("No measurements available")
            self.clear_results_table()
            return
        
        # If no state estimation results, show just measurements
        if not self.estimator.estimation_results:
            self.show_measurements_only()
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
    
    def show_measurements_only(self):
        """Show measurements in results table without state estimation comparison"""
        try:
            self.update_status("Displaying measurements...")
            self.clear_results_table()
            
            # Get all measurements
            measurement_info = self.estimator.get_measurement_info()
            
            if not measurement_info:
                self.table_status_var.set("No measurement data available")
                return
            
            # Show measurements with load flow values (if available)
            has_load_flow = hasattr(self.estimator.net, 'res_bus') and self.estimator.net.res_bus is not None
            
            for i, meas in enumerate(measurement_info):
                mtype = meas['type']
                element = meas['element']
                value = meas['value']
                std_dev = meas['std_dev']
                
                # Get load flow value for comparison
                if has_load_flow:
                    if mtype == 'v':
                        load_flow_value = self.estimator.net.res_bus.vm_pu.iloc[element]
                        error = ((value - load_flow_value) / load_flow_value * 100) if load_flow_value != 0 else 0
                        unit = 'p.u.'
                        description = f'V_mag Bus {element}'
                    elif mtype == 'p':
                        load_flow_value = self.estimator.net.res_line.p_from_mw.iloc[element]
                        error = ((value - load_flow_value) / abs(load_flow_value) * 100) if load_flow_value != 0 else 0
                        unit = 'MW'
                        from_bus = self.estimator.net.line.from_bus.iloc[element]
                        to_bus = self.estimator.net.line.to_bus.iloc[element]
                        description = f'P_from L{element} ({from_bus}-{to_bus})'
                    elif mtype == 'q':
                        load_flow_value = self.estimator.net.res_line.q_from_mvar.iloc[element]
                        error = ((value - load_flow_value) / abs(load_flow_value) * 100) if load_flow_value != 0 else 0
                        unit = 'MVAr'
                        from_bus = self.estimator.net.line.from_bus.iloc[element]
                        to_bus = self.estimator.net.line.to_bus.iloc[element]
                        description = f'Q_from L{element} ({from_bus}-{to_bus})'
                    else:
                        load_flow_value = 0
                        error = 0
                        unit = ''
                        description = f'{mtype}_elem_{element}'
                else:
                    load_flow_value = 0
                    error = 0
                    unit = 'p.u.' if mtype == 'v' else ('MW' if mtype == 'p' else 'MVAr')
                    description = meas.get('element_description', f'{mtype}_elem_{element}')
                
                # Create table row
                values = (
                    description,
                    unit,
                    f"{load_flow_value:.4f}" if has_load_flow else "N/A",
                    f"{value:.4f}",
                    "N/A",  # No estimation value yet
                    f"{error:.2f}%" if has_load_flow else "N/A",
                    "N/A"   # No estimation error yet
                )
                
                # Add row with alternating colors
                tags = ('even',) if i % 2 == 0 else ('odd',)
                self.results_tree.insert('', 'end', values=values, tags=tags)
            
            # Configure row colors
            self.results_tree.tag_configure('even', background='#f8f9fa', foreground='#212529')
            self.results_tree.tag_configure('odd', background='#ffffff', foreground='#212529')
            
            # Update status
            status_msg = f"Showing {len(measurement_info)} measurements"
            if has_load_flow:
                status_msg += " with load flow comparison"
            else:
                status_msg += " (run load flow for comparison)"
            
            self.table_status_var.set(status_msg)
            
        except Exception as e:
            self.log(f"❌ Error showing measurements: {e}")
            self.table_status_var.set("Error displaying measurements")
        
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
            
            # Auto-refresh displays (new grid created)
            if self.auto_refresh_var.get():
                self.refresh_grid_plot()
                self.refresh_switch_display()
                self.refresh_measurement_display()
                self.log("🔄 Auto-refreshed all displays")
                
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
            
            # Auto-refresh displays (new grid created)
            if self.auto_refresh_var.get():
                self.refresh_grid_plot()
                self.refresh_switch_display()
                self.refresh_measurement_display()
                self.log("🔄 Auto-refreshed all displays")
                
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
            
            # Auto-refresh plots and measurement display (new measurements generated)
            if self.auto_refresh_var.get():
                self.refresh_grid_plot()
                self.refresh_measurement_display()
                self.log("🔄 Auto-refreshed grid visualization and measurement display")
            
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
                
                # Auto-refresh plots (voltage modification affects visualization)
                if self.auto_refresh_var.get():
                    self.refresh_grid_plot()
                    self.log("🔄 Auto-refreshed grid visualization")
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
                
                # Auto-refresh results and plots
                self.auto_refresh_results_and_plots()
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
                
                # Auto-refresh plots (observability affects measurement locations display)
                if self.auto_refresh_var.get():
                    self.refresh_grid_plot()
                    self.log("🔄 Auto-refreshed grid visualization")
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
            
            # Update the results table and grid plot
            self.refresh_results_table()
            self.refresh_grid_plot()
            self.notebook.select(1)  # Switch to Results Table tab
            self.log("✅ Results table updated - switched to Results Table tab")
            
            self.update_status("Ready")
        except Exception as e:
            self.log(f"❌ Error showing results: {e}")
            self.update_status("Error")
    
    def check_topology(self):
        """Check network topology consistency"""
        if not self.estimator:
            messagebox.showerror("Error", "Please create a grid model first")
            return
            
        self.update_status("Checking topology...")
        try:
            results = self.estimator.check_topology_consistency(detailed_report=True)
            if results:
                self.log("📊 TOPOLOGY CONSISTENCY CHECK RESULTS:")
                self.log(f"   Overall Status: {results.get('overall_status', 'unknown').upper()}")
                self.log(f"   Connectivity: {results.get('connectivity_status', 'unknown').upper()}")
                self.log(f"   Network Islands: {len(results.get('network_islands', []))}")
                self.log(f"   Isolated Buses: {len(results.get('isolated_buses', []))}")
                self.log(f"   Switch Issues: {len(results.get('switch_issues', []))}")
                
                # Switch to results table if auto-refresh is enabled
                if self.auto_refresh_var.get():
                    self.refresh_switch_display()
                    self.log("🔄 Auto-refreshed switch display")
            else:
                self.log("✅ Topology check completed")
            self.update_status("Ready")
        except Exception as e:
            self.log(f"❌ Topology check error: {e}")
            self.update_status("Error")
    
    def show_grid_plot(self):
        """Show grid visualization and switch to that tab"""
        if not self.estimator:
            messagebox.showerror("Error", "No grid model available")
            return
            
        self.update_status("Updating grid visualization...")
        try:
            # Refresh the grid plot
            self.refresh_grid_plot()
            
            # Switch to Grid Visualization tab
            self.notebook.select(2)  # Grid Visualization is tab index 2
            self.log("✅ Grid visualization updated - switched to Grid Visualization tab")
            
            self.update_status("Ready")
        except Exception as e:
            self.log(f"❌ Error showing grid plot: {e}")
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
                    
                    # Update results table and grid plot
                    self.log("5. Updating results table and grid visualization...")
                    self.refresh_results_table()
                    self.refresh_grid_plot()
                    self.log("   ✅ Results table and grid plot updated")
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
        """Clear output, results table, grid plot, switch display, and measurement display"""
        self.output_text.delete(1.0, tk.END)
        self.clear_results_table()
        self.clear_grid_plot()
        self.clear_switch_display()
        self.clear_measurement_display()
        self.table_status_var.set("Output cleared - No results available")
        self.grid_plot_status_var.set("Output cleared - No grid available")
        self.switch_status_var.set("Output cleared - No switches available")
        self.measurement_status_var.set("Output cleared - No measurements available")
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