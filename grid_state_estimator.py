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
        """Simulate measurement values with noise"""
        if self.net is None:
            raise ValueError("Grid model not created. Call create_ieee9_grid() first.")
            
        # Run power flow to get true values
        pp.runpp(self.net, algorithm='nr')
        
        # Clear existing measurements
        self.measurements = []
        
        # Add voltage magnitude measurements for all buses
        for bus_idx in self.net.bus.index:
            true_value = self.net.res_bus.vm_pu.iloc[bus_idx]
            noise = np.random.normal(0, noise_level)
            measured_value = true_value + noise
            std_dev = noise_level
            
            pp.create_measurement(self.net, "v", "bus", measured_value, std_dev, bus_idx)
            
        # Add power flow measurements for lines
        for line_idx in self.net.line.index:
            # Active power flow measurements
            true_p_from = self.net.res_line.p_from_mw.iloc[line_idx]
            true_p_to = self.net.res_line.p_to_mw.iloc[line_idx]
            
            noise_p_from = np.random.normal(0, abs(true_p_from) * noise_level)
            noise_p_to = np.random.normal(0, abs(true_p_to) * noise_level)
            
            pp.create_measurement(self.net, "p", "line", true_p_from + noise_p_from, 
                                abs(true_p_from) * noise_level + 0.1, line_idx, side="from")
            pp.create_measurement(self.net, "p", "line", true_p_to + noise_p_to,
                                abs(true_p_to) * noise_level + 0.1, line_idx, side="to")
            
            # Reactive power flow measurements
            true_q_from = self.net.res_line.q_from_mvar.iloc[line_idx]
            true_q_to = self.net.res_line.q_to_mvar.iloc[line_idx]
            
            noise_q_from = np.random.normal(0, abs(true_q_from) * noise_level)
            noise_q_to = np.random.normal(0, abs(true_q_to) * noise_level)
            
            pp.create_measurement(self.net, "q", "line", true_q_from + noise_q_from,
                                abs(true_q_from) * noise_level + 0.1, line_idx, side="from")
            pp.create_measurement(self.net, "q", "line", true_q_to + noise_q_to,
                                abs(true_q_to) * noise_level + 0.1, line_idx, side="to")
        
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
        
        # Compare true values vs estimated values
        print("\nBUS VOLTAGE MAGNITUDES (p.u.):")
        print("-" * 50)
        comparison_df = pd.DataFrame({
            'Bus': range(len(self.net.bus)),
            'True Value': self.net.res_bus.vm_pu.values,
            'Estimated': self.estimation_results['bus_voltages'].vm_pu.values,
            'Error (%)': ((self.estimation_results['bus_voltages'].vm_pu.values - 
                          self.net.res_bus.vm_pu.values) / self.net.res_bus.vm_pu.values * 100)
        })
        print(comparison_df.round(4))
        
        print("\nBUS VOLTAGE ANGLES (deg):")
        print("-" * 50)
        angle_comparison = pd.DataFrame({
            'Bus': range(len(self.net.bus)),
            'True Value': self.net.res_bus.va_degree.values,
            'Estimated': self.estimation_results['bus_voltages'].va_degree.values,
            'Error': (self.estimation_results['bus_voltages'].va_degree.values - 
                     self.net.res_bus.va_degree.values)
        })
        print(angle_comparison.round(4))
        
        # Add power flow results table if available
        if self.estimation_results['line_flows'] is not None:
            print("\nLINE POWER FLOWS (MW):")
            print("-" * 80)
            line_power_df = pd.DataFrame({
                'Line': [f"Line {i}" for i in range(len(self.net.line))],
                'From Bus': self.net.line.from_bus.values,
                'To Bus': self.net.line.to_bus.values,
                'True P_from': self.net.res_line.p_from_mw.values,
                'Est P_from': self.estimation_results['line_flows'].p_from_mw.values if hasattr(self.estimation_results['line_flows'], 'p_from_mw') else [0]*len(self.net.line),
                'True P_to': self.net.res_line.p_to_mw.values,
                'Est P_to': self.estimation_results['line_flows'].p_to_mw.values if hasattr(self.estimation_results['line_flows'], 'p_to_mw') else [0]*len(self.net.line)
            })
            print(line_power_df.round(3))
            
            print("\nLINE REACTIVE POWER FLOWS (MVAr):")
            print("-" * 80)
            line_reactive_df = pd.DataFrame({
                'Line': [f"Line {i}" for i in range(len(self.net.line))],
                'From Bus': self.net.line.from_bus.values,
                'To Bus': self.net.line.to_bus.values,
                'True Q_from': self.net.res_line.q_from_mvar.values,
                'Est Q_from': self.estimation_results['line_flows'].q_from_mvar.values if hasattr(self.estimation_results['line_flows'], 'q_from_mvar') else [0]*len(self.net.line),
                'True Q_to': self.net.res_line.q_to_mvar.values,
                'Est Q_to': self.estimation_results['line_flows'].q_to_mvar.values if hasattr(self.estimation_results['line_flows'], 'q_to_mvar') else [0]*len(self.net.line)
            })
            print(line_reactive_df.round(3))
        
        # Add measurements table
        print("\nMEASUREMENTS SUMMARY:")
        print("-" * 60)
        measurements_df = pd.DataFrame({
            'Type': self.net.measurement.measurement_type.values,
            'Element': self.net.measurement.element_type.values,
            'Element_ID': self.net.measurement.element.values,
            'Side': self.net.measurement.side.fillna('').values,
            'Value': self.net.measurement.value.values,
            'Std_Dev': self.net.measurement.std_dev.values
        })
        print(measurements_df.round(4))
        
        # Plot results
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # Voltage magnitudes
        buses = range(len(self.net.bus))
        ax1.plot(buses, self.net.res_bus.vm_pu, 'bo-', label='True', markersize=6)
        ax1.plot(buses, self.estimation_results['bus_voltages'].vm_pu, 'rx-', label='Estimated', markersize=6)
        ax1.set_xlabel('Bus Number')
        ax1.set_ylabel('Voltage Magnitude (p.u.)')
        ax1.set_title('Voltage Magnitudes')
        ax1.legend()
        ax1.grid(True)
        
        # Voltage angles
        ax2.plot(buses, self.net.res_bus.va_degree, 'bo-', label='True', markersize=6)
        ax2.plot(buses, self.estimation_results['bus_voltages'].va_degree, 'rx-', label='Estimated', markersize=6)
        ax2.set_xlabel('Bus Number')
        ax2.set_ylabel('Voltage Angle (deg)')
        ax2.set_title('Voltage Angles')
        ax2.legend()
        ax2.grid(True)
        
        # Voltage magnitude errors
        vm_errors = ((self.estimation_results['bus_voltages'].vm_pu.values - 
                      self.net.res_bus.vm_pu.values) / self.net.res_bus.vm_pu.values * 100)
        ax3.bar(buses, vm_errors)
        ax3.set_xlabel('Bus Number')
        ax3.set_ylabel('Voltage Magnitude Error (%)')
        ax3.set_title('Voltage Magnitude Estimation Errors')
        ax3.grid(True)
        
        # Voltage angle errors
        va_errors = (self.estimation_results['bus_voltages'].va_degree.values - 
                     self.net.res_bus.va_degree.values)
        ax4.bar(buses, va_errors)
        ax4.set_xlabel('Bus Number')
        ax4.set_ylabel('Voltage Angle Error (deg)')
        ax4.set_title('Voltage Angle Estimation Errors')
        ax4.grid(True)
        
        plt.tight_layout()
        
        # Suppress matplotlib debug output
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            plt.show()
        
        # Statistics
        print(f"\nESTIMATION STATISTICS:")
        print("-" * 30)
        print(f"Mean voltage magnitude error: {np.mean(np.abs(vm_errors)):.4f}%")
        print(f"Max voltage magnitude error: {np.max(np.abs(vm_errors)):.4f}%")
        print(f"Mean voltage angle error: {np.mean(np.abs(va_errors)):.4f} deg")
        print(f"Max voltage angle error: {np.max(np.abs(va_errors)):.4f} deg")
        
def main():
    """Main function to run the state estimation application"""
    print("Power System State Estimation Application")
    print("="*50)
    
    # Create estimator instance
    estimator = GridStateEstimator()
    
    # Create IEEE 9-bus system
    print("\n1. Creating IEEE 9-bus grid model...")
    estimator.create_ieee9_grid()
    
    # Simulate measurements
    print("\n2. Simulating measurements...")
    estimator.simulate_measurements(noise_level=0.02)
    
    # Run state estimation
    print("\n3. Running state estimation...")
    estimator.run_state_estimation()
    
    # Show results
    print("\n4. Displaying results...")
    estimator.show_results()

if __name__ == "__main__":
    main()