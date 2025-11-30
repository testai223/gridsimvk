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
        """Auto-refresh results table and grid plot if enabled"""
        if not self.auto_refresh_var.get():
            return  # Auto-refresh disabled
        
        try:
            refreshed_items = []
            
            # Refresh results table if we have estimation results
            if self.estimator and self.estimator.estimation_results:
                self.refresh_results_table()
                refreshed_items.append("results table")
            
            # Refresh grid plot if we have a grid model
            if self.estimator and hasattr(self.estimator, 'net') and self.estimator.net is not None:
                self.refresh_grid_plot()
                refreshed_items.append("grid visualization")
            
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
        """Operate a switch and update displays"""
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
            
            # Perform switch operation
            success = self.estimator.toggle_switch(switch_index, force_state)
            
            if success:
                new_state = "CLOSED" if force_state else ("OPEN" if force_state == False else ("OPEN" if switch_data['closed'] else "CLOSED"))
                self.log(f"✅ {switch_data['name']}: {old_state} → {new_state}")
                
                # Auto-refresh displays
                self.refresh_switch_display()
                if self.auto_refresh_var.get():
                    self.auto_refresh_results_and_plots()
                
            else:
                self.log(f"❌ Failed to operate {switch_data['name']} - Power flow unstable")
                
        except Exception as e:
            self.log(f"❌ Switch operation error: {e}")
    
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
            
            # Auto-refresh grid plot and switch display (new grid created)
            if self.auto_refresh_var.get():
                self.refresh_grid_plot()
                self.refresh_switch_display()
                self.log("🔄 Auto-refreshed grid visualization and switch control")
                
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
            
            # Auto-refresh grid plot and switch display (new grid created)
            if self.auto_refresh_var.get():
                self.refresh_grid_plot()
                self.refresh_switch_display()
                self.log("🔄 Auto-refreshed grid visualization and switch control")
                
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
            
            # Auto-refresh plots (measurements affect grid visualization)
            if self.auto_refresh_var.get():
                self.refresh_grid_plot()
                self.log("🔄 Auto-refreshed grid visualization")
            
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
        """Clear output, results table, grid plot, and switch display"""
        self.output_text.delete(1.0, tk.END)
        self.clear_results_table()
        self.clear_grid_plot()
        self.clear_switch_display()
        self.table_status_var.set("Output cleared - No results available")
        self.grid_plot_status_var.set("Output cleared - No grid available")
        self.switch_status_var.set("Output cleared - No switches available")
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