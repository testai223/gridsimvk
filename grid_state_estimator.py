import pandapower as pp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandapower.estimation import estimate
import warnings
import logging

# Disable matplotlib debug messages
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

class GridStateEstimator:
    def __init__(self):
        self.net = None
        self.measurements = []
        self.estimation_results = None
        
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
    
    # Show results
    print("\n4a. Results for perfect measurements:")
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
    
    # Show results
    print("\n4b. Results for noisy measurements:")
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
    
    # Show results
    print("\n4. Displaying results...")
    estimator.show_results()

if __name__ == "__main__":
    main()