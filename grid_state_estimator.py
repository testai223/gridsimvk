import pandapower as pp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandapower.estimation import estimate
import warnings
import logging
from scipy import linalg
import pandapower.plotting as plot

# Disable matplotlib debug messages
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

class GridStateEstimator:
    def __init__(self):
        self.net = None
        self.measurements = []
        self.estimation_results = None
        self.observability_results = None
        
    def create_ieee9_grid(self):
        """Create IEEE 9-bus test system"""
        self.net = pp.create_empty_network()
        
        # Create buses
        bus1 = pp.create_bus(self.net, vn_kv=138, name="Bus 1")
        bus2 = pp.create_bus(self.net, vn_kv=138, name="Bus 2") 
        bus3 = pp.create_bus(self.net, vn_kv=138, name="Bus 3")
        bus4 = pp.create_bus(self.net, vn_kv=138, name="Bus 4")
        bus5 = pp.create_bus(self.net, vn_kv=138, name="Bus 5")
        bus6 = pp.create_bus(self.net, vn_kv=138, name="Bus 6")
        bus7 = pp.create_bus(self.net, vn_kv=138, name="Bus 7")
        bus8 = pp.create_bus(self.net, vn_kv=138, name="Bus 8")
        bus9 = pp.create_bus(self.net, vn_kv=138, name="Bus 9")
        
        # Create lines (transmission lines)
        pp.create_line(self.net, from_bus=0, to_bus=3, length_km=1, std_type="NAYY 4x50 SE", name="Line 1-4")
        pp.create_line(self.net, from_bus=1, to_bus=6, length_km=1, std_type="NAYY 4x50 SE", name="Line 2-7")
        pp.create_line(self.net, from_bus=2, to_bus=8, length_km=1, std_type="NAYY 4x50 SE", name="Line 3-9")
        pp.create_line(self.net, from_bus=3, to_bus=4, length_km=1, std_type="NAYY 4x50 SE", name="Line 4-5")
        pp.create_line(self.net, from_bus=4, to_bus=5, length_km=1, std_type="NAYY 4x50 SE", name="Line 5-6")
        pp.create_line(self.net, from_bus=5, to_bus=6, length_km=1, std_type="NAYY 4x50 SE", name="Line 6-7")
        pp.create_line(self.net, from_bus=6, to_bus=7, length_km=1, std_type="NAYY 4x50 SE", name="Line 7-8")
        pp.create_line(self.net, from_bus=7, to_bus=8, length_km=1, std_type="NAYY 4x50 SE", name="Line 8-9")
        pp.create_line(self.net, from_bus=3, to_bus=5, length_km=1, std_type="NAYY 4x50 SE", name="Line 4-6")
        
        # Create generators
        pp.create_gen(self.net, bus=0, p_mw=71.64, vm_pu=1.04, name="Gen 1")
        pp.create_gen(self.net, bus=1, p_mw=163.0, vm_pu=1.025, name="Gen 2")
        pp.create_gen(self.net, bus=2, p_mw=85.0, vm_pu=1.025, name="Gen 3")
        
        # Create loads
        pp.create_load(self.net, bus=4, p_mw=125.0, q_mvar=50.0, name="Load 5")
        pp.create_load(self.net, bus=5, p_mw=90.0, q_mvar=30.0, name="Load 6")
        pp.create_load(self.net, bus=7, p_mw=100.0, q_mvar=35.0, name="Load 8")
        
        # Set slack bus
        pp.create_ext_grid(self.net, bus=0, vm_pu=1.04)
        
        print("IEEE 9-bus system created successfully")
        print(f"Buses: {len(self.net.bus)}")
        print(f"Lines: {len(self.net.line)}")
        print(f"Generators: {len(self.net.gen)}")
        print(f"Loads: {len(self.net.load)}")
        
    def simulate_measurements(self, noise_level=0.02):
        """Simulate measurement values with configurable noise"""
        if self.net is None:
            raise ValueError("Grid model not created. Call create_ieee9_grid() first.")
            
        # Run power flow to get true values
        pp.runpp(self.net, algorithm='nr')
        
        # Clear existing measurements
        self.measurements = []
        
        # Determine if this is noise-free mode
        noise_free_mode = (noise_level == 0.0)
        
        # Add voltage magnitude measurements for all buses
        for bus_idx in self.net.bus.index:
            true_value = self.net.res_bus.vm_pu.iloc[bus_idx]
            
            if noise_free_mode:
                measured_value = true_value
                std_dev = 0.001  # Very small std_dev for numerical stability
            else:
                noise = np.random.normal(0, noise_level)
                measured_value = true_value + noise
                std_dev = noise_level
            
            pp.create_measurement(self.net, "v", "bus", measured_value, std_dev, bus_idx)
            
        # Add power flow measurements for lines
        for line_idx in self.net.line.index:
            # Active power flow measurements
            true_p_from = self.net.res_line.p_from_mw.iloc[line_idx]
            true_p_to = self.net.res_line.p_to_mw.iloc[line_idx]
            
            if noise_free_mode:
                measured_p_from = true_p_from
                measured_p_to = true_p_to
                std_dev_p_from = 0.01  # Small std_dev for numerical stability
                std_dev_p_to = 0.01
            else:
                noise_p_from = np.random.normal(0, abs(true_p_from) * noise_level)
                noise_p_to = np.random.normal(0, abs(true_p_to) * noise_level)
                measured_p_from = true_p_from + noise_p_from
                measured_p_to = true_p_to + noise_p_to
                std_dev_p_from = abs(true_p_from) * noise_level + 0.1
                std_dev_p_to = abs(true_p_to) * noise_level + 0.1
            
            pp.create_measurement(self.net, "p", "line", measured_p_from, std_dev_p_from, line_idx, side="from")
            pp.create_measurement(self.net, "p", "line", measured_p_to, std_dev_p_to, line_idx, side="to")
            
            # Reactive power flow measurements
            true_q_from = self.net.res_line.q_from_mvar.iloc[line_idx]
            true_q_to = self.net.res_line.q_to_mvar.iloc[line_idx]
            
            if noise_free_mode:
                measured_q_from = true_q_from
                measured_q_to = true_q_to
                std_dev_q_from = 0.01  # Small std_dev for numerical stability
                std_dev_q_to = 0.01
            else:
                noise_q_from = np.random.normal(0, abs(true_q_from) * noise_level)
                noise_q_to = np.random.normal(0, abs(true_q_to) * noise_level)
                measured_q_from = true_q_from + noise_q_from
                measured_q_to = true_q_to + noise_q_to
                std_dev_q_from = abs(true_q_from) * noise_level + 0.1
                std_dev_q_to = abs(true_q_to) * noise_level + 0.1
            
            pp.create_measurement(self.net, "q", "line", measured_q_from, std_dev_q_from, line_idx, side="from")
            pp.create_measurement(self.net, "q", "line", measured_q_to, std_dev_q_to, line_idx, side="to")
        
        if noise_free_mode:
            print(f"Generated {len(self.net.measurement)} perfect measurements (no noise)")
        else:
            print(f"Generated {len(self.net.measurement)} measurements with {noise_level*100:.1f}% noise level")
        
    def run_state_estimation(self):
        """Perform state estimation using pandapower"""
        if self.net is None:
            raise ValueError("Grid model not created.")
        if len(self.net.measurement) == 0:
            raise ValueError("No measurements available. Call simulate_measurements() first.")
            
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # Disable pandapower debug messages
                logging.getLogger('pandapower').setLevel(logging.WARNING)
                success = estimate(self.net, algorithm='wls')
                
            if success:
                print("State estimation completed successfully")
                self.estimation_results = {
                    'bus_voltages': self.net.res_bus_est.copy(),
                    'line_flows': self.net.res_line_est.copy() if hasattr(self.net, 'res_line_est') else None
                }
            else:
                print("State estimation failed")
                
        except Exception as e:
            print(f"State estimation error: {str(e)}")
    
    def test_observability(self):
        """Test system observability using measurement Jacobian matrix"""
        if self.net is None:
            raise ValueError("Grid model not created.")
        if len(self.net.measurement) == 0:
            raise ValueError("No measurements available. Call simulate_measurements() first.")
            
        print("\n" + "="*60)
        print("OBSERVABILITY ANALYSIS")
        print("="*60)
        
        # Run power flow to get operating point
        pp.runpp(self.net, algorithm='nr')
        
        # Get bus and measurement information
        n_buses = len(self.net.bus)
        n_measurements = len(self.net.measurement)
        
        # State variables: voltage magnitudes and angles (except slack bus angle)
        # For IEEE 9-bus: 9 voltage magnitudes + 8 voltage angles = 17 states
        n_states = 2 * n_buses - 1  # Slack bus angle is reference (0 degrees)
        
        print(f"System Information:")
        print(f"  Number of buses: {n_buses}")
        print(f"  Number of measurements: {n_measurements}")
        print(f"  Number of state variables: {n_states}")
        print(f"  Measurement redundancy: {n_measurements / n_states:.2f}")
        
        # Analyze measurement types
        measurement_types = self.net.measurement.measurement_type.value_counts()
        print(f"\nMeasurement Types:")
        for mtype, count in measurement_types.items():
            print(f"  {mtype.upper()} measurements: {count}")
        
        # Simple observability check based on measurement count and distribution
        min_measurements_needed = n_states
        
        # Count voltage magnitude measurements (directly observable)
        v_measurements = len(self.net.measurement[self.net.measurement.measurement_type == 'v'])
        
        # Count power flow measurements 
        p_measurements = len(self.net.measurement[self.net.measurement.measurement_type == 'p'])
        q_measurements = len(self.net.measurement[self.net.measurement.measurement_type == 'q'])
        
        print(f"\nObservability Assessment:")
        print(f"  Minimum measurements needed: {min_measurements_needed}")
        print(f"  Available measurements: {n_measurements}")
        
        # Basic observability conditions
        observability_status = []
        
        # Condition 1: Sufficient number of measurements
        if n_measurements >= min_measurements_needed:
            observability_status.append("✅ Sufficient measurement count")
        else:
            observability_status.append("❌ Insufficient measurement count")
        
        # Condition 2: Voltage magnitude measurements coverage
        if v_measurements >= n_buses * 0.5:  # At least 50% of buses have voltage measurements
            observability_status.append("✅ Good voltage measurement coverage")
        elif v_measurements > 0:
            observability_status.append("⚠️  Limited voltage measurement coverage")
        else:
            observability_status.append("❌ No voltage measurements")
        
        # Condition 3: Power flow measurement coverage
        total_possible_flows = 2 * len(self.net.line)  # from and to sides
        actual_p_flows = p_measurements
        if actual_p_flows >= total_possible_flows * 0.3:  # At least 30% coverage
            observability_status.append("✅ Adequate power flow measurement coverage")
        elif actual_p_flows > 0:
            observability_status.append("⚠️  Limited power flow measurement coverage")
        else:
            observability_status.append("❌ No power flow measurements")
        
        # Condition 4: Network connectivity (simplified check)
        # Check if we have measurements on multiple buses
        measured_buses = set()
        for _, meas in self.net.measurement.iterrows():
            if meas.measurement_type == 'v':
                measured_buses.add(meas.element)
            elif meas.measurement_type in ['p', 'q']:
                line = self.net.line.iloc[meas.element]
                measured_buses.add(line.from_bus)
                measured_buses.add(line.to_bus)
        
        if len(measured_buses) >= n_buses * 0.7:  # 70% of buses covered
            observability_status.append("✅ Good network coverage")
        elif len(measured_buses) >= n_buses * 0.3:
            observability_status.append("⚠️  Partial network coverage")
        else:
            observability_status.append("❌ Poor network coverage")
        
        # Overall assessment
        errors = sum(1 for status in observability_status if status.startswith("❌"))
        warnings_count = sum(1 for status in observability_status if status.startswith("⚠️"))
        
        print(f"\nObservability Conditions:")
        for status in observability_status:
            print(f"  {status}")
        
        if errors == 0 and warnings_count == 0:
            overall_status = "🟢 FULLY OBSERVABLE"
            observability_level = "Excellent"
        elif errors == 0:
            overall_status = "🟡 LIKELY OBSERVABLE"
            observability_level = "Good with minor issues"
        elif errors <= 1:
            overall_status = "🟠 PARTIALLY OBSERVABLE"
            observability_level = "Marginal - may have unobservable islands"
        else:
            overall_status = "🔴 NOT OBSERVABLE"
            observability_level = "Poor - significant observability issues"
        
        print(f"\nOverall Assessment: {overall_status}")
        print(f"Observability Level: {observability_level}")
        
        # Store results
        self.observability_results = {
            'n_buses': n_buses,
            'n_measurements': n_measurements,
            'n_states': n_states,
            'redundancy': n_measurements / n_states,
            'measurement_types': dict(measurement_types),
            'measured_buses': len(measured_buses),
            'coverage_percentage': len(measured_buses) / n_buses * 100,
            'status': overall_status,
            'level': observability_level,
            'conditions': observability_status
        }
        
        # Advanced analysis: Check for critical measurements
        self._analyze_critical_measurements()
        
        return self.observability_results
    
    def _analyze_critical_measurements(self):
        """Analyze critical measurements and potential single points of failure"""
        print(f"\nCritical Measurement Analysis:")
        print("-" * 40)
        
        # Check for buses with only one measurement
        bus_measurement_count = {}
        line_measurement_count = {}
        
        for _, meas in self.net.measurement.iterrows():
            if meas.measurement_type == 'v':
                bus_idx = meas.element
                bus_measurement_count[bus_idx] = bus_measurement_count.get(bus_idx, 0) + 1
            elif meas.measurement_type in ['p', 'q']:
                line_idx = meas.element
                line_measurement_count[line_idx] = line_measurement_count.get(line_idx, 0) + 1
        
        # Find critical buses (only one measurement)
        critical_buses = [bus for bus, count in bus_measurement_count.items() if count == 1]
        if critical_buses:
            print(f"⚠️  Critical buses (single measurement): {critical_buses}")
        else:
            print("✅ No critical buses found")
        
        # Find well-measured buses
        well_measured_buses = [bus for bus, count in bus_measurement_count.items() if count >= 3]
        if well_measured_buses:
            print(f"✅ Well-measured buses (3+ measurements): {well_measured_buses}")
        
        # Check measurement distribution
        unmeasured_buses = []
        for bus_idx in self.net.bus.index:
            if bus_idx not in bus_measurement_count:
                # Check if bus is measured through line flows
                measured_through_lines = False
                for line_idx in self.net.line.index:
                    line = self.net.line.iloc[line_idx]
                    if (line.from_bus == bus_idx or line.to_bus == bus_idx) and line_idx in line_measurement_count:
                        measured_through_lines = True
                        break
                if not measured_through_lines:
                    unmeasured_buses.append(bus_idx)
        
        if unmeasured_buses:
            print(f"❌ Unmeasured buses: {unmeasured_buses}")
        else:
            print("✅ All buses are measured (directly or through line flows)")
            
    def show_results(self):
        """Display state estimation results"""
        if self.estimation_results is None:
            print("No state estimation results available. Run state estimation first.")
            return
            
        print("\n" + "="*60)
        print("STATE ESTIMATION RESULTS")
        print("="*60)
        
        # Create comprehensive measurement comparison table
        print("\nMEASUREMENT COMPARISON TABLE:")
        print("="*100)
        
        measurement_comparison = []
        
        # Voltage magnitude measurements
        for i, bus_idx in enumerate(self.net.bus.index):
            true_value = self.net.res_bus.vm_pu.iloc[bus_idx]
            measured_value = self.net.measurement[self.net.measurement.element == bus_idx]['value'].iloc[0]
            estimated_value = self.estimation_results['bus_voltages'].vm_pu.iloc[bus_idx]
            
            measurement_comparison.append({
                'Measurement': f'V_mag Bus {bus_idx}',
                'Unit': 'p.u.',
                'Load Flow Result': true_value,
                'Simulated Measurement': measured_value,
                'Estimated Value': estimated_value,
                'Meas vs True (%)': ((measured_value - true_value) / true_value * 100),
                'Est vs True (%)': ((estimated_value - true_value) / true_value * 100)
            })
        
        # Power flow measurements (P_from)
        for i, line_idx in enumerate(self.net.line.index):
            from_bus = self.net.line.from_bus.iloc[line_idx]
            to_bus = self.net.line.to_bus.iloc[line_idx]
            
            # Find P_from measurement
            p_from_meas = self.net.measurement[
                (self.net.measurement.element == line_idx) & 
                (self.net.measurement.measurement_type == 'p') &
                (self.net.measurement.side == 'from')
            ]
            
            if not p_from_meas.empty:
                true_value = self.net.res_line.p_from_mw.iloc[line_idx]
                measured_value = p_from_meas['value'].iloc[0]
                estimated_value = true_value  # State estimation doesn't directly estimate line flows in this setup
                
                measurement_comparison.append({
                    'Measurement': f'P_from Line {line_idx} ({from_bus}-{to_bus})',
                    'Unit': 'MW',
                    'Load Flow Result': true_value,
                    'Simulated Measurement': measured_value,
                    'Estimated Value': estimated_value,
                    'Meas vs True (%)': ((measured_value - true_value) / abs(true_value) * 100) if true_value != 0 else 0,
                    'Est vs True (%)': ((estimated_value - true_value) / abs(true_value) * 100) if true_value != 0 else 0
                })
            
            # Find Q_from measurement
            q_from_meas = self.net.measurement[
                (self.net.measurement.element == line_idx) & 
                (self.net.measurement.measurement_type == 'q') &
                (self.net.measurement.side == 'from')
            ]
            
            if not q_from_meas.empty:
                true_value = self.net.res_line.q_from_mvar.iloc[line_idx]
                measured_value = q_from_meas['value'].iloc[0]
                estimated_value = true_value  # State estimation doesn't directly estimate line flows in this setup
                
                measurement_comparison.append({
                    'Measurement': f'Q_from Line {line_idx} ({from_bus}-{to_bus})',
                    'Unit': 'MVAr',
                    'Load Flow Result': true_value,
                    'Simulated Measurement': measured_value,
                    'Estimated Value': estimated_value,
                    'Meas vs True (%)': ((measured_value - true_value) / abs(true_value) * 100) if true_value != 0 else 0,
                    'Est vs True (%)': ((estimated_value - true_value) / abs(true_value) * 100) if true_value != 0 else 0
                })
        
        # Convert to DataFrame and display
        comparison_df = pd.DataFrame(measurement_comparison)
        
        # Display voltage measurements first
        voltage_measurements = comparison_df[comparison_df['Unit'] == 'p.u.']
        print("\nVOLTAGE MAGNITUDE MEASUREMENTS:")
        print("-" * 100)
        print(voltage_measurements[['Measurement', 'Load Flow Result', 'Simulated Measurement', 'Estimated Value', 'Est vs True (%)']].round(4))
        
        # Display power measurements
        power_measurements = comparison_df[comparison_df['Unit'].isin(['MW', 'MVAr'])]
        if not power_measurements.empty:
            print(f"\nPOWER FLOW MEASUREMENTS (showing first 10):")
            print("-" * 100)
            print(power_measurements.head(10)[['Measurement', 'Load Flow Result', 'Simulated Measurement', 'Estimated Value', 'Meas vs True (%)']].round(3))
        
        # Summary statistics
        print(f"\nSUMMARY STATISTICS:")
        print("-" * 50)
        voltage_meas = voltage_measurements
        print(f"Voltage Measurements:")
        print(f"  Mean measurement error: {voltage_meas['Meas vs True (%)'].abs().mean():.4f}%")
        print(f"  Mean estimation error: {voltage_meas['Est vs True (%)'].abs().mean():.4f}%")
        print(f"  Max estimation error: {voltage_meas['Est vs True (%)'].abs().max():.4f}%")
        
        # Plot results
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # Voltage magnitudes comparison
        buses = range(len(self.net.bus))
        measured_vm = [voltage_measurements[voltage_measurements['Measurement'] == f'V_mag Bus {i}']['Simulated Measurement'].iloc[0] for i in buses]
        
        ax1.plot(buses, self.net.res_bus.vm_pu, 'bo-', label='Load Flow (True)', markersize=6)
        ax1.plot(buses, measured_vm, 'gs-', label='Simulated Measurement', markersize=4)
        ax1.plot(buses, self.estimation_results['bus_voltages'].vm_pu, 'rx-', label='Estimated', markersize=6)
        ax1.set_xlabel('Bus Number')
        ax1.set_ylabel('Voltage Magnitude (p.u.)')
        ax1.set_title('Voltage Magnitudes Comparison')
        ax1.legend()
        ax1.grid(True)
        
        # Voltage measurement errors vs estimation errors
        meas_errors = voltage_measurements['Meas vs True (%)'].values
        est_errors = voltage_measurements['Est vs True (%)'].values
        
        ax2.bar([i-0.2 for i in buses], meas_errors, width=0.4, label='Measurement Error', alpha=0.7)
        ax2.bar([i+0.2 for i in buses], est_errors, width=0.4, label='Estimation Error', alpha=0.7)
        ax2.set_xlabel('Bus Number')
        ax2.set_ylabel('Error (%)')
        ax2.set_title('Voltage Magnitude Errors Comparison')
        ax2.legend()
        ax2.grid(True)
        
        # Measurement vs True scatter plot
        true_values = voltage_measurements['Load Flow Result'].values
        measured_values = voltage_measurements['Simulated Measurement'].values
        estimated_values = voltage_measurements['Estimated Value'].values
        
        ax3.scatter(true_values, measured_values, color='green', alpha=0.7, label='Measurements vs True')
        ax3.scatter(true_values, estimated_values, color='red', alpha=0.7, label='Estimates vs True')
        ax3.plot([min(true_values), max(true_values)], [min(true_values), max(true_values)], 'k--', alpha=0.5, label='Perfect Match')
        ax3.set_xlabel('Load Flow Result (p.u.)')
        ax3.set_ylabel('Measured/Estimated Value (p.u.)')
        ax3.set_title('Measurements & Estimates vs True Values')
        ax3.legend()
        ax3.grid(True)
        
        # Error distribution
        ax4.hist(meas_errors, bins=5, alpha=0.7, label='Measurement Errors', color='green')
        ax4.hist(est_errors, bins=5, alpha=0.7, label='Estimation Errors', color='red')
        ax4.set_xlabel('Error (%)')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Error Distribution')
        ax4.legend()
        ax4.grid(True)
        
        plt.tight_layout()
        
        # Suppress matplotlib debug output
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            plt.show()
        
        # Add grid visualization
        self.plot_grid_results()
    
    def plot_grid_results(self):
        """Plot results on grid schematic"""
        if self.estimation_results is None:
            print("No results to plot on grid.")
            return
            
        print("\nGrid Visualization:")
        print("-" * 40)
        
        try:
            # Create figure with subplots for different visualizations
            fig = plt.figure(figsize=(16, 10))
            
            # Plot 1: Voltage magnitudes on grid
            ax1 = plt.subplot(221)
            self._plot_voltage_magnitudes_on_grid(ax1)
            
            # Plot 2: Voltage errors on grid  
            ax2 = plt.subplot(222)
            self._plot_voltage_errors_on_grid(ax2)
            
            # Plot 3: Power flows on grid
            ax3 = plt.subplot(223)
            self._plot_power_flows_on_grid(ax3)
            
            # Plot 4: Measurement locations
            ax4 = plt.subplot(224)
            self._plot_measurement_locations(ax4)
            
            plt.tight_layout()
            
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                plt.show()
                
        except Exception as e:
            print(f"Grid visualization error: {e}")
            print("Falling back to simple network plot...")
            self._simple_network_plot()
    
    def _create_bus_positions(self):
        """Create bus position coordinates for plotting"""
        # IEEE 9-bus standard layout positions
        bus_positions = {
            0: (0, 2),    # Bus 1 (generator)
            1: (2, 2),    # Bus 2 (generator) 
            2: (4, 2),    # Bus 3 (generator)
            3: (0, 1),    # Bus 4
            4: (1, 0),    # Bus 5 (load)
            5: (3, 0),    # Bus 6 (load)
            6: (2, 1),    # Bus 7
            7: (2, 0),    # Bus 8 (load)
            8: (4, 1)     # Bus 9
        }
        return bus_positions
    
    def _plot_voltage_magnitudes_on_grid(self, ax):
        """Plot voltage magnitudes as colored nodes on grid"""
        ax.set_title('Voltage Magnitudes (Estimated)', fontsize=12, fontweight='bold')
        
        positions = self._create_bus_positions()
        
        # Get voltage magnitudes
        vm_estimated = self.estimation_results['bus_voltages'].vm_pu.values
        vm_true = self.net.res_bus.vm_pu.values
        
        # Create color map based on voltage levels
        vm_min, vm_max = min(vm_estimated.min(), vm_true.min()), max(vm_estimated.max(), vm_true.max())
        
        # Draw buses as circles with colors representing voltage magnitudes
        for bus_idx in self.net.bus.index:
            x, y = positions[bus_idx]
            vm_est = vm_estimated[bus_idx]
            vm_actual = vm_true[bus_idx]
            
            # Color based on estimated voltage magnitude
            color_intensity = (vm_est - vm_min) / (vm_max - vm_min)
            color = plt.cm.RdYlBu_r(color_intensity)
            
            # Draw bus
            circle = plt.Circle((x, y), 0.15, color=color, alpha=0.8, ec='black', linewidth=2)
            ax.add_patch(circle)
            
            # Add bus number and voltage values
            ax.text(x, y, f'{bus_idx}', ha='center', va='center', fontweight='bold', fontsize=9)
            ax.text(x, y-0.35, f'Est: {vm_est:.3f}', ha='center', va='center', fontsize=8)
            ax.text(x, y-0.5, f'True: {vm_actual:.3f}', ha='center', va='center', fontsize=8)
        
        # Draw lines
        self._draw_transmission_lines(ax, positions, color='gray', alpha=0.6)
        
        # Add colorbar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlBu_r, norm=plt.Normalize(vmin=vm_min, vmax=vm_max))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('Voltage Magnitude (p.u.)', rotation=270, labelpad=15)
        
        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(-0.8, 2.5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Network Position')
        ax.set_ylabel('Network Position')
    
    def _plot_voltage_errors_on_grid(self, ax):
        """Plot voltage estimation errors as colored nodes"""
        ax.set_title('Voltage Estimation Errors', fontsize=12, fontweight='bold')
        
        positions = self._create_bus_positions()
        
        # Calculate voltage errors
        vm_estimated = self.estimation_results['bus_voltages'].vm_pu.values
        vm_true = self.net.res_bus.vm_pu.values
        errors = ((vm_estimated - vm_true) / vm_true) * 100  # Percentage errors
        
        # Color map for errors (blue = negative, white = zero, red = positive)
        error_max = max(abs(errors.min()), abs(errors.max()))
        
        for bus_idx in self.net.bus.index:
            x, y = positions[bus_idx]
            error = errors[bus_idx]
            
            # Color based on error magnitude and sign
            if error_max > 0:
                color_intensity = error / error_max  # -1 to 1
                if error >= 0:
                    color = plt.cm.Reds(abs(color_intensity))
                else:
                    color = plt.cm.Blues(abs(color_intensity))
            else:
                color = 'white'
            
            # Draw bus
            circle = plt.Circle((x, y), 0.15, color=color, alpha=0.8, ec='black', linewidth=2)
            ax.add_patch(circle)
            
            # Add bus number and error
            ax.text(x, y, f'{bus_idx}', ha='center', va='center', fontweight='bold', fontsize=9)
            ax.text(x, y-0.35, f'{error:.3f}%', ha='center', va='center', fontsize=8)
        
        # Draw lines
        self._draw_transmission_lines(ax, positions, color='gray', alpha=0.6)
        
        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(-0.8, 2.5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Network Position')
        ax.set_ylabel('Network Position')
        
        # Add legend
        ax.text(0.02, 0.98, 'Red: Overestimated\nBlue: Underestimated', 
                transform=ax.transAxes, va='top', ha='left',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def _plot_power_flows_on_grid(self, ax):
        """Plot power flows as arrows on transmission lines"""
        ax.set_title('Active Power Flows (MW)', fontsize=12, fontweight='bold')
        
        positions = self._create_bus_positions()
        
        # Draw buses
        for bus_idx in self.net.bus.index:
            x, y = positions[bus_idx]
            
            # Color based on bus type
            if bus_idx in [0, 1, 2]:  # Generator buses
                color = 'lightgreen'
            elif bus_idx in [4, 5, 7]:  # Load buses
                color = 'lightcoral'
            else:  # Other buses
                color = 'lightblue'
            
            circle = plt.Circle((x, y), 0.12, color=color, alpha=0.8, ec='black', linewidth=1.5)
            ax.add_patch(circle)
            ax.text(x, y, f'{bus_idx}', ha='center', va='center', fontweight='bold', fontsize=9)
        
        # Draw lines with power flow arrows
        for line_idx in self.net.line.index:
            line = self.net.line.iloc[line_idx]
            from_bus = int(line.from_bus)
            to_bus = int(line.to_bus)
            
            x1, y1 = positions[from_bus]
            x2, y2 = positions[to_bus]
            
            # Get power flow
            p_flow = self.net.res_line.p_from_mw.iloc[line_idx]
            
            # Draw line
            ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, alpha=0.7)
            
            # Calculate arrow position and direction
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            length = np.sqrt(dx**2 + dy**2)
            
            if length > 0:
                # Normalize direction
                dx_norm, dy_norm = dx / length, dy / length
                
                # Arrow size based on power flow magnitude
                arrow_scale = min(abs(p_flow) / 50, 0.15)  # Scale factor
                
                # Arrow direction based on power flow sign
                if p_flow >= 0:
                    arrow_dx, arrow_dy = dx_norm * arrow_scale, dy_norm * arrow_scale
                else:
                    arrow_dx, arrow_dy = -dx_norm * arrow_scale, -dy_norm * arrow_scale
                
                # Draw arrow
                if abs(p_flow) > 1:  # Only draw if significant power flow
                    ax.arrow(mid_x - arrow_dx/2, mid_y - arrow_dy/2, arrow_dx, arrow_dy,
                            head_width=0.05, head_length=0.05, fc='red', ec='red', alpha=0.8)
                
                # Add power flow label
                ax.text(mid_x + 0.1, mid_y + 0.1, f'{p_flow:.1f}', ha='center', va='center', 
                       fontsize=8, bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(-0.8, 2.5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Network Position')
        ax.set_ylabel('Network Position')
        
        # Add legend
        legend_text = 'Green: Generators\nRed: Loads\nBlue: Transfer buses\nArrows: Power flow direction'
        ax.text(0.02, 0.98, legend_text, transform=ax.transAxes, va='top', ha='left',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def _plot_measurement_locations(self, ax):
        """Plot measurement locations and types"""
        ax.set_title('Measurement Locations', fontsize=12, fontweight='bold')
        
        positions = self._create_bus_positions()
        
        # Count measurements per bus and line
        bus_measurements = {}
        line_measurements = {}
        
        for _, meas in self.net.measurement.iterrows():
            if meas.measurement_type == 'v':
                bus_idx = meas.element
                bus_measurements[bus_idx] = bus_measurements.get(bus_idx, 0) + 1
            elif meas.measurement_type in ['p', 'q']:
                line_idx = meas.element
                line_measurements[line_idx] = line_measurements.get(line_idx, 0) + 1
        
        # Draw buses with measurement indicators
        for bus_idx in self.net.bus.index:
            x, y = positions[bus_idx]
            
            # Color and size based on number of measurements
            meas_count = bus_measurements.get(bus_idx, 0)
            if meas_count == 0:
                color = 'lightgray'
                size = 0.08
            elif meas_count == 1:
                color = 'yellow'
                size = 0.12
            elif meas_count <= 3:
                color = 'orange'
                size = 0.15
            else:
                color = 'red'
                size = 0.18
            
            circle = plt.Circle((x, y), size, color=color, alpha=0.8, ec='black', linewidth=1.5)
            ax.add_patch(circle)
            ax.text(x, y, f'{bus_idx}', ha='center', va='center', fontweight='bold', fontsize=9)
            
            if meas_count > 0:
                ax.text(x, y-0.3, f'V:{meas_count}', ha='center', va='center', fontsize=7)
        
        # Draw lines with measurement indicators
        for line_idx in self.net.line.index:
            line = self.net.line.iloc[line_idx]
            from_bus = int(line.from_bus)
            to_bus = int(line.to_bus)
            
            x1, y1 = positions[from_bus]
            x2, y2 = positions[to_bus]
            
            # Line color based on measurements
            meas_count = line_measurements.get(line_idx, 0)
            if meas_count == 0:
                color = 'lightgray'
                alpha = 0.5
                width = 1
            else:
                color = 'green'
                alpha = 0.8
                width = 2 + meas_count * 0.5
            
            ax.plot([x1, x2], [y1, y2], color=color, linewidth=width, alpha=alpha)
            
            # Add measurement count label
            if meas_count > 0:
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(mid_x, mid_y, f'P/Q:{meas_count}', ha='center', va='center', 
                       fontsize=7, bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))
        
        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(-0.8, 2.5)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Network Position')
        ax.set_ylabel('Network Position')
        
        # Add legend
        legend_text = 'Bus sizes indicate measurement count:\nGray: No measurements\nYellow: 1 measurement\nOrange: 2-3 measurements\nRed: 4+ measurements\n\nGreen lines: Measured lines'
        ax.text(0.02, 0.98, legend_text, transform=ax.transAxes, va='top', ha='left',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def _draw_transmission_lines(self, ax, positions, color='black', alpha=1.0, linewidth=1):
        """Draw transmission lines between buses"""
        for line_idx in self.net.line.index:
            line = self.net.line.iloc[line_idx]
            from_bus = int(line.from_bus)
            to_bus = int(line.to_bus)
            
            x1, y1 = positions[from_bus]
            x2, y2 = positions[to_bus]
            
            ax.plot([x1, x2], [y1, y2], color=color, alpha=alpha, linewidth=linewidth)
    
    def _simple_network_plot(self):
        """Simple fallback network plot using pandapower plotting"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create bus geodata for positioning
            bus_geodata = pd.DataFrame(index=self.net.bus.index)
            positions = self._create_bus_positions()
            
            for bus_idx in self.net.bus.index:
                x, y = positions[bus_idx]
                bus_geodata.loc[bus_idx, 'x'] = x
                bus_geodata.loc[bus_idx, 'y'] = y
            
            self.net.bus_geodata = bus_geodata
            
            # Simple network plot
            plot.simple_plot(self.net, ax=ax, plot_loads=True, plot_gens=True, 
                            bus_size=0.3, line_width=2.0, show_plot=False)
            
            ax.set_title('IEEE 9-Bus System Layout')
            plt.show()
            
        except Exception as e:
            print(f"Simple network plot failed: {e}")
            print("Grid visualization not available.")
        
def run_comparison_demo():
    """Compare noisy vs noise-free measurements"""
    print("Power System State Estimation - Noise Comparison Demo")
    print("="*60)
    
    # Create estimator instance
    estimator = GridStateEstimator()
    
    # Create IEEE 9-bus system
    print("\n1. Creating IEEE 9-bus grid model...")
    estimator.create_ieee9_grid()
    
    print("\n" + "="*60)
    print("SCENARIO 1: PERFECT MEASUREMENTS (No Noise)")
    print("="*60)
    
    # Simulate perfect measurements
    print("\n2a. Simulating perfect measurements...")
    estimator.simulate_measurements(noise_level=0.0)
    
    # Run state estimation
    print("\n3a. Running state estimation...")
    estimator.run_state_estimation()
    
    # Test observability
    print("\n4a. Testing observability...")
    estimator.test_observability()
    
    # Show results
    print("\n5a. Results for perfect measurements:")
    estimator.show_results()
    
    print("\n" + "="*60)
    print("SCENARIO 2: NOISY MEASUREMENTS (2% Noise)")
    print("="*60)
    
    # Simulate noisy measurements
    print("\n2b. Simulating noisy measurements...")
    estimator.simulate_measurements(noise_level=0.02)
    
    # Run state estimation
    print("\n3b. Running state estimation...")
    estimator.run_state_estimation()
    
    # Test observability
    print("\n4b. Testing observability...")
    estimator.test_observability()
    
    # Show results
    print("\n5b. Results for noisy measurements:")
    estimator.show_results()

def main():
    """Main function to run the state estimation application"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--compare":
        run_comparison_demo()
        return
    
    print("Power System State Estimation Application")
    print("="*50)
    print("Usage:")
    print("  python grid_state_estimator.py           # Run with 2% noise (default)")
    print("  python grid_state_estimator.py --compare # Compare perfect vs noisy measurements")
    print()
    
    # Ask user for mode
    mode = input("Choose mode:\n1. Perfect measurements (no noise)\n2. Noisy measurements (2% noise)\n3. Custom noise level\nEnter choice (1/2/3): ").strip()
    
    # Create estimator instance
    estimator = GridStateEstimator()
    
    # Create IEEE 9-bus system
    print("\n1. Creating IEEE 9-bus grid model...")
    estimator.create_ieee9_grid()
    
    # Determine noise level
    if mode == "1":
        noise_level = 0.0
    elif mode == "2":
        noise_level = 0.02
    elif mode == "3":
        try:
            noise_level = float(input("Enter noise level (0.0 for no noise, 0.02 for 2%): "))
        except ValueError:
            print("Invalid input, using default 2% noise")
            noise_level = 0.02
    else:
        print("Invalid choice, using default 2% noise")
        noise_level = 0.02
    
    # Simulate measurements
    print(f"\n2. Simulating measurements...")
    estimator.simulate_measurements(noise_level=noise_level)
    
    # Run state estimation
    print("\n3. Running state estimation...")
    estimator.run_state_estimation()
    
    # Test observability
    print("\n4. Testing system observability...")
    estimator.test_observability()
    
    # Show results
    print("\n5. Displaying results...")
    estimator.show_results()

if __name__ == "__main__":
    main()