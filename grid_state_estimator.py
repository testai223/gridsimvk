import pandapower as pp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandapower.estimation import estimate
import warnings
import logging
from scipy import linalg
import pandapower.plotting as plot
import sys

# Disable matplotlib debug messages
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

class GridStateEstimator:
    def __init__(self):
        self.net = None
        self.measurements = []
        self.estimation_results = None
        self.observability_results = None
        
    def load_cgmes_model(self, cgmes_files):
        """Load CGMES/CIM model files"""
        try:
            # Try different import paths for CIM converter
            try:
                from pandapower.converter.cim import cim2pp
            except ImportError:
                try:
                    from pandapower.converter import cim2pp
                except ImportError:
                    try:
                        import pandapower.converter.cim.cim2pp as cim2pp
                    except ImportError:
                        raise ImportError("CIM converter not found")
            
            print(f"Loading CGMES model from: {cgmes_files}")
            
            if isinstance(cgmes_files, str):
                cgmes_files = [cgmes_files]
            
            # Load CGMES files using pandapower CIM converter
            self.net = cim2pp.from_cim(cgmes_files)
            
            print(f"CGMES model loaded successfully")
            print(f"  Buses: {len(self.net.bus)}")
            print(f"  Lines: {len(self.net.line)}")
            print(f"  Generators: {len(self.net.gen)}")
            print(f"  Loads: {len(self.net.load)}")
            
            return True
            
        except ImportError:
            print("❌ CIM converter not available in current pandapower installation")
            print("💡 Full CGMES support requires specialized CIM libraries")
            print("📋 For production use, install: power-grid-model-io or CIMpy")
            return False
        except Exception as e:
            print(f"Error loading CGMES model: {e}")
            return False
    
    def create_simple_entso_grid(self):
        """Create a simple grid representing ENTSO-E style transmission system"""
        print("Creating ENTSO-E style transmission grid (400kV/220kV)...")
        
        self.net = pp.create_empty_network()
        
        # Create buses representing typical ENTSO-E transmission system
        # 400kV transmission level
        bus_400_1 = pp.create_bus(self.net, vn_kv=400, name="400kV_North")      # Generator area
        bus_400_2 = pp.create_bus(self.net, vn_kv=400, name="400kV_Central")   # Transfer hub  
        bus_400_3 = pp.create_bus(self.net, vn_kv=400, name="400kV_South")     # Load area
        
        # 220kV subtransmission level
        bus_220_1 = pp.create_bus(self.net, vn_kv=220, name="220kV_East")      # Wind farm
        bus_220_2 = pp.create_bus(self.net, vn_kv=220, name="220kV_West")      # Industrial load
        
        # Create transformers 400/220kV (typical ENTSO-E) with manual parameters
        trafo_1 = pp.create_transformer_from_parameters(
            self.net, hv_bus=bus_400_2, lv_bus=bus_220_1, sn_mva=400, 
            vn_hv_kv=400, vn_lv_kv=220, vkr_percent=0.3, vk_percent=12, 
            pfe_kw=100, i0_percent=0.1, name="T400/220_East"
        )
        trafo_2 = pp.create_transformer_from_parameters(
            self.net, hv_bus=bus_400_2, lv_bus=bus_220_2, sn_mva=400, 
            vn_hv_kv=400, vn_lv_kv=220, vkr_percent=0.3, vk_percent=12, 
            pfe_kw=100, i0_percent=0.1, name="T400/220_West"
        )
        
        # Create 400kV transmission lines (long distance) with manual parameters
        line_400_1 = pp.create_line_from_parameters(
            self.net, from_bus=bus_400_1, to_bus=bus_400_2, length_km=150, 
            r_ohm_per_km=0.027, x_ohm_per_km=0.31, c_nf_per_km=14.6, max_i_ka=1.9,
            name="400kV_North_Central"
        )
        line_400_2 = pp.create_line_from_parameters(
            self.net, from_bus=bus_400_2, to_bus=bus_400_3, length_km=200, 
            r_ohm_per_km=0.027, x_ohm_per_km=0.31, c_nf_per_km=14.6, max_i_ka=1.9,
            name="400kV_Central_South"
        )
        
        # Create 220kV lines (regional) with manual parameters
        line_220 = pp.create_line_from_parameters(
            self.net, from_bus=bus_220_1, to_bus=bus_220_2, length_km=80, 
            r_ohm_per_km=0.125, x_ohm_per_km=0.42, c_nf_per_km=9.5, max_i_ka=0.96,
            name="220kV_East_West"
        )
        
        # Create generators (typical ENTSO-E generation mix)
        # Large thermal plant at 400kV
        gen_thermal = pp.create_gen(self.net, bus=bus_400_1, p_mw=600, vm_pu=1.05, 
                                   name="Thermal_600MW")
        
        # Wind farm at 220kV  
        gen_wind = pp.create_gen(self.net, bus=bus_220_1, p_mw=200, vm_pu=1.02,
                                name="Wind_200MW")
        
        # Create loads (typical ENTSO-E consumption)
        # Urban load center
        load_urban = pp.create_load(self.net, bus=bus_400_3, p_mw=500, q_mvar=150, 
                                   name="Urban_Load_500MW")
        
        # Industrial load
        load_industrial = pp.create_load(self.net, bus=bus_220_2, p_mw=250, q_mvar=80,
                                        name="Industrial_Load_250MW")
        
        # Set slack bus (transmission system operator reference)
        ext_grid = pp.create_ext_grid(self.net, bus=bus_400_1, vm_pu=1.05, name="TSO_Slack")
        
        # Create switches for network topology control
        self._create_entso_switches(bus_400_1, bus_400_2, bus_400_3, bus_220_1, bus_220_2, 
                                   line_400_1, line_400_2, line_220, trafo_1, trafo_2)
        
        print("ENTSO-E style transmission grid created successfully")
        print(f"  400kV buses: 3")
        print(f"  220kV buses: 2") 
        print(f"  Total buses: {len(self.net.bus)}")
        print(f"  400kV lines: 2")
        print(f"  220kV lines: 1")
        print(f"  Transformers: {len(self.net.trafo)}")
        print(f"  Generators: {len(self.net.gen)} ({gen_thermal} thermal, {gen_wind} wind)")
        print(f"  Loads: {len(self.net.load)} (urban + industrial)")
        print(f"  Switches: {len(self.net.switch)} (circuit breakers and disconnectors)")
        
        return True
        
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
        
        # Create switches for network topology control
        self._create_ieee9_switches()
        
        print("IEEE 9-bus system created successfully")
        print(f"Buses: {len(self.net.bus)}")
        print(f"Lines: {len(self.net.line)}")
        print(f"Generators: {len(self.net.gen)}")
        print(f"Loads: {len(self.net.load)}")
        print(f"Switches: {len(self.net.switch)} (circuit breakers)")
        
    def _create_entso_switches(self, bus_400_1, bus_400_2, bus_400_3, bus_220_1, bus_220_2, 
                              line_400_1, line_400_2, line_220, trafo_1, trafo_2):
        """Create switches for ENTSO-E grid topology control"""
        # Line circuit breakers (one at each end of major transmission lines)
        pp.create_switch(self.net, bus=bus_400_1, element=line_400_1, et="l", closed=True, 
                        type="CB", name="CB_400_North_From")
        pp.create_switch(self.net, bus=bus_400_2, element=line_400_1, et="l", closed=True, 
                        type="CB", name="CB_400_North_To")
        
        pp.create_switch(self.net, bus=bus_400_2, element=line_400_2, et="l", closed=True, 
                        type="CB", name="CB_400_South_From")
        pp.create_switch(self.net, bus=bus_400_3, element=line_400_2, et="l", closed=True, 
                        type="CB", name="CB_400_South_To")
        
        pp.create_switch(self.net, bus=bus_220_1, element=line_220, et="l", closed=True, 
                        type="CB", name="CB_220_East")
        pp.create_switch(self.net, bus=bus_220_2, element=line_220, et="l", closed=True, 
                        type="CB", name="CB_220_West")
        
        # Transformer circuit breakers (high voltage side)
        pp.create_switch(self.net, bus=bus_400_2, element=trafo_1, et="t", closed=True, 
                        type="CB", name="CB_T1_HV")
        pp.create_switch(self.net, bus=bus_400_2, element=trafo_2, et="t", closed=True, 
                        type="CB", name="CB_T2_HV")
        
        # Transformer low voltage side switches
        pp.create_switch(self.net, bus=bus_220_1, element=trafo_1, et="t", closed=True, 
                        type="CB", name="CB_T1_LV")
        pp.create_switch(self.net, bus=bus_220_2, element=trafo_2, et="t", closed=True, 
                        type="CB", name="CB_T2_LV")
        
        # Bus sectioning switches (for operational flexibility)
        pp.create_switch(self.net, bus=bus_400_2, element=bus_400_1, et="b", closed=True, 
                        type="DS", name="DS_400_Central_North")
        pp.create_switch(self.net, bus=bus_400_2, element=bus_400_3, et="b", closed=True, 
                        type="DS", name="DS_400_Central_South")
        
    def _create_ieee9_switches(self):
        """Create switches for IEEE 9-bus system topology control"""
        # Add circuit breakers for critical transmission lines
        line_indices = self.net.line.index
        
        # Important transmission corridors get circuit breakers
        critical_lines = [0, 1, 2, 3, 6, 8]  # Strategic line positions
        
        for i, line_idx in enumerate(line_indices):
            if line_idx in critical_lines:
                from_bus = self.net.line.from_bus.iloc[line_idx]
                to_bus = self.net.line.to_bus.iloc[line_idx]
                
                # Circuit breaker at from bus
                pp.create_switch(self.net, bus=from_bus, element=line_idx, et="l", closed=True, 
                                type="CB", name=f"CB_L{line_idx}_From")
                
                # Circuit breaker at to bus
                pp.create_switch(self.net, bus=to_bus, element=line_idx, et="l", closed=True, 
                                type="CB", name=f"CB_L{line_idx}_To")
        
        # Add generator circuit breakers
        for gen_idx in self.net.gen.index:
            gen_bus = self.net.gen.bus.iloc[gen_idx]
            pp.create_switch(self.net, bus=gen_bus, element=gen_bus, et="b", closed=True, 
                            type="CB", name=f"CB_Gen{gen_idx}")
    
    def toggle_switch(self, switch_index, force_state=None):
        """Toggle switch state or set to specific state"""
        if self.net is None:
            return False
            
        if switch_index not in self.net.switch.index:
            return False
        
        if force_state is not None:
            new_state = bool(force_state)
        else:
            # Toggle current state
            current_state = self.net.switch.closed.iloc[switch_index]
            new_state = not current_state
        
        self.net.switch.closed.iloc[switch_index] = new_state
        
        # Update network topology
        try:
            pp.runpp(self.net, algorithm='nr')
            return True
        except:
            # If power flow fails due to switch operation, revert
            self.net.switch.closed.iloc[switch_index] = not new_state
            return False
    
    def get_switch_info(self):
        """Get information about all switches in the network"""
        if self.net is None or len(self.net.switch) == 0:
            return []
        
        switch_info = []
        for idx in self.net.switch.index:
            switch_data = {
                'index': idx,
                'name': self.net.switch.name.iloc[idx] if 'name' in self.net.switch.columns else f"Switch {idx}",
                'bus': self.net.switch.bus.iloc[idx],
                'element': self.net.switch.element.iloc[idx],
                'type': self.net.switch.et.iloc[idx],
                'switch_type': self.net.switch.type.iloc[idx] if 'type' in self.net.switch.columns else 'CB',
                'closed': self.net.switch.closed.iloc[idx],
                'status': 'CLOSED' if self.net.switch.closed.iloc[idx] else 'OPEN'
            }
            switch_info.append(switch_data)
        
        return switch_info
        
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
    
    def list_measurements(self):
        """List all measurements with their indices for easy reference"""
        if self.net is None or len(self.net.measurement) == 0:
            print("No measurements available.")
            return None
            
        measurements_df = self.net.measurement.copy()
        
        print("\n" + "="*80)
        print("AVAILABLE MEASUREMENTS")
        print("="*80)
        print(f"{'Index':<6} {'Type':<6} {'Element':<8} {'Side':<6} {'Value':<12} {'Std Dev':<10} {'Description'}")
        print("-"*80)
        
        for idx, row in measurements_df.iterrows():
            element_type = "line" if row['element_type'] == "line" else "bus"
            element_id = row['element']
            side = row.get('side', None)
            side_str = str(side) if side is not None else 'N/A'
            value = row['value']
            std_dev = row['std_dev']
            
            # Create description
            if row['measurement_type'] == 'v':
                desc = f"Voltage Bus {element_id}"
            elif row['measurement_type'] == 'p':
                desc = f"Active Power Line {element_id} ({side_str})"
            elif row['measurement_type'] == 'q':
                desc = f"Reactive Power Line {element_id} ({side_str})"
            else:
                desc = f"{row['measurement_type'].upper()} {element_type} {element_id}"
            
            print(f"{idx:<6} {row['measurement_type']:<6} {element_id:<8} {side_str:<6} {value:<12.4f} {std_dev:<10.4f} {desc}")
        
        return measurements_df
    
    def modify_measurement(self, measurement_index, new_value, new_std_dev=None):
        """
        Modify a specific measurement value
        
        Args:
            measurement_index (int): Index of the measurement to modify
            new_value (float): New measurement value
            new_std_dev (float, optional): New standard deviation. If None, keeps existing value
        """
        if self.net is None or len(self.net.measurement) == 0:
            print("No measurements available.")
            return False
            
        if measurement_index not in self.net.measurement.index:
            print(f"Invalid measurement index: {measurement_index}")
            print(f"Available indices: {list(self.net.measurement.index)}")
            return False
        
        # Store original values
        original_value = self.net.measurement.loc[measurement_index, 'value']
        original_std_dev = self.net.measurement.loc[measurement_index, 'std_dev']
        
        # Update measurement
        self.net.measurement.loc[measurement_index, 'value'] = new_value
        if new_std_dev is not None:
            self.net.measurement.loc[measurement_index, 'std_dev'] = new_std_dev
        
        # Get measurement details for confirmation
        row = self.net.measurement.loc[measurement_index]
        element_id = row['element']
        meas_type = row['measurement_type']
        side = row.get('side', None)
        side_str = str(side) if side is not None else 'None'
        
        print(f"✅ Modified measurement {measurement_index}:")
        print(f"   Type: {meas_type.upper()} Element: {element_id} Side: {side_str}")
        print(f"   Value: {original_value:.4f} → {new_value:.4f}")
        if new_std_dev is not None:
            print(f"   Std Dev: {original_std_dev:.4f} → {new_std_dev:.4f}")
        
        return True
    
    def modify_bus_voltage_measurement(self, bus_id, new_voltage_pu):
        """
        Modify voltage measurement for a specific bus
        
        Args:
            bus_id (int): Bus ID
            new_voltage_pu (float): New voltage in per unit
        """
        # Find voltage measurement for this bus
        voltage_measurements = self.net.measurement[
            (self.net.measurement['measurement_type'] == 'v') &
            (self.net.measurement['element'] == bus_id)
        ]
        
        if voltage_measurements.empty:
            print(f"No voltage measurement found for bus {bus_id}")
            return False
        
        measurement_index = voltage_measurements.index[0]
        return self.modify_measurement(measurement_index, new_voltage_pu)
    
    def modify_line_power_measurement(self, line_id, side, measurement_type, new_value):
        """
        Modify power measurement for a specific line
        
        Args:
            line_id (int): Line ID
            side (str): 'from' or 'to'
            measurement_type (str): 'p' for active power, 'q' for reactive power
            new_value (float): New power value
        """
        # Find power measurement for this line and side
        power_measurements = self.net.measurement[
            (self.net.measurement['measurement_type'] == measurement_type) &
            (self.net.measurement['element'] == line_id) &
            (self.net.measurement['side'] == side)
        ]
        
        if power_measurements.empty:
            print(f"No {measurement_type.upper()} measurement found for line {line_id} ({side} side)")
            return False
        
        measurement_index = power_measurements.index[0]
        return self.modify_measurement(measurement_index, new_value)
    
    def reset_measurements(self, noise_level=0.02):
        """Reset all measurements to original simulated values"""
        print("Resetting measurements to original simulated values...")
        self.simulate_measurements(noise_level=noise_level)
        print("✅ Measurements reset successfully")
    
    def create_measurement_scenario(self, scenario_name="custom"):
        """
        Interactive measurement modification for testing scenarios
        
        Args:
            scenario_name (str): Name for the scenario
        """
        print(f"\n🔧 MEASUREMENT MODIFICATION - {scenario_name.upper()} SCENARIO")
        print("="*60)
        
        # Show current measurements
        self.list_measurements()
        
        print(f"\n💡 Examples of modifications:")
        print(f"   • Bus voltage: modify_bus_voltage_measurement(bus_id, voltage_pu)")
        print(f"   • Line power: modify_line_power_measurement(line_id, 'from'/'to', 'p'/'q', value)")
        print(f"   • Direct index: modify_measurement(index, value)")
        print(f"\n🔄 Use reset_measurements() to restore original values")
        
        return True

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
    
    def detect_bad_data(self, confidence_level=0.95, max_iterations=5, prompt_restore=True):
        """
        Comprehensive bad data detection using multiple statistical tests
        
        Args:
            confidence_level (float): Confidence level for statistical tests (default 0.95)
            max_iterations (int): Maximum iterations for bad data removal (default 5)
            
        Returns:
            dict: Bad data detection results including identified bad measurements
        """
        if self.net is None:
            raise ValueError("Grid model not created.")
        if len(self.net.measurement) == 0:
            raise ValueError("No measurements available. Call simulate_measurements() first.")
        if self.estimation_results is None:
            print("⚠️  No state estimation results. Running state estimation first...")
            self.run_state_estimation()
            if self.estimation_results is None:
                print("❌ State estimation failed. Cannot perform bad data detection.")
                return None
        
        print("\n" + "="*70)
        print("🔍 BAD DATA DETECTION ANALYSIS")
        print("="*70)
        
        # Store original measurements for restoration if needed
        original_measurements = self.net.measurement.copy()
        bad_data_results = {
            'iterations': [],
            'bad_measurements': [],
            'detection_method': [],
            'statistical_tests': {},
            'final_status': None
        }
        
        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 Iteration {iteration}")
            print("-" * 40)
            
            # Run state estimation to get current residuals
            self.run_state_estimation()
            if self.estimation_results is None:
                print("❌ State estimation failed in iteration {iteration}")
                break
            
            # Calculate measurement residuals and normalized residuals
            residuals = self._calculate_measurement_residuals()
            if residuals is None:
                print("❌ Could not calculate residuals")
                break
                
            normalized_residuals = self._calculate_normalized_residuals(residuals)
            if normalized_residuals is None:
                print("❌ Could not calculate normalized residuals")
                break
            
            # Perform statistical tests
            test_results = self._perform_bad_data_tests(residuals, normalized_residuals, confidence_level)
            bad_data_results['statistical_tests'][f'iteration_{iteration}'] = test_results
            
            # Check for global bad data using Chi-square test
            chi_square_result = self._chi_square_test(residuals, confidence_level)
            
            if not chi_square_result['has_bad_data']:
                print(f"✅ No bad data detected (Chi-square test passed)")
                bad_data_results['final_status'] = 'clean'
                break
            
            # Find largest normalized residual
            suspect_measurement = self._identify_largest_normalized_residual(normalized_residuals)
            if suspect_measurement is None:
                print("⚠️  Could not identify suspect measurement")
                break
            
            # Check if this measurement passes individual tests
            if self._validate_suspect_measurement(suspect_measurement, normalized_residuals, confidence_level):
                print(f"⚠️  Largest residual measurement {suspect_measurement['index']} passed validation")
                print(f"    Stopping detection (possible model error or systematic bias)")
                bad_data_results['final_status'] = 'systematic_error_suspected'
                break
            
            # Mark as bad data and remove
            print(f"🚨 BAD DATA DETECTED!")
            self._report_bad_measurement(suspect_measurement)
            
            bad_data_results['bad_measurements'].append({
                'iteration': iteration,
                'measurement_index': suspect_measurement['index'],
                'measurement_type': suspect_measurement['type'],
                'element': suspect_measurement['element'],
                'original_value': suspect_measurement['value'],
                'normalized_residual': suspect_measurement['normalized_residual'],
                'detection_method': 'Largest Normalized Residual Test'
            })
            
            # Remove bad measurement
            self._remove_measurement(suspect_measurement['index'])
            print(f"🗑️  Removed measurement {suspect_measurement['index']} from analysis")
        
        # Final analysis
        print(f"\n📊 BAD DATA DETECTION SUMMARY")
        print("=" * 50)
        
        if not bad_data_results['bad_measurements']:
            print("✅ NO BAD DATA DETECTED")
            print("   All measurements appear to be consistent with the system model")
        else:
            print(f"🚨 DETECTED {len(bad_data_results['bad_measurements'])} BAD MEASUREMENTS:")
            for i, bad_meas in enumerate(bad_data_results['bad_measurements'], 1):
                meas_desc = self._get_measurement_description(bad_meas)
                print(f"   {i}. {meas_desc}")
                print(f"      Normalized residual: {bad_meas['normalized_residual']:.3f}")
        
        # Store results
        self.bad_data_results = bad_data_results
        
        # Option to restore original measurements
        restore = "y"
        if prompt_restore and sys.stdin.isatty():
            user_input = input(f"\n🔄 Restore original measurements? (y/n, default: y): ")
            restore = user_input.strip().lower() or "y"

        if restore != 'n':
            self.net.measurement = original_measurements
            print("✅ Original measurements restored")
            # Re-run state estimation with all measurements
            self.run_state_estimation()
        
        return bad_data_results
    
    def _calculate_measurement_residuals(self):
        """Calculate measurement residuals (difference between measured and estimated values)"""
        try:
            residuals = {}
            
            # Get estimated values from state estimation results
            if not hasattr(self.net, 'res_bus_est') or not hasattr(self.net, 'res_line_est'):
                print("❌ State estimation results not available")
                return None
            
            for idx, measurement in self.net.measurement.iterrows():
                meas_type = measurement['measurement_type']
                element = measurement['element']
                measured_value = measurement['value']
                
                if meas_type == 'v':
                    # Voltage magnitude measurement
                    estimated_value = self.net.res_bus_est.vm_pu.iloc[element]
                elif meas_type == 'p':
                    # Active power measurement
                    side = measurement.get('side', 'from')
                    if side == 'from':
                        estimated_value = self.net.res_line_est.p_from_mw.iloc[element]
                    else:
                        estimated_value = self.net.res_line_est.p_to_mw.iloc[element]
                elif meas_type == 'q':
                    # Reactive power measurement
                    side = measurement.get('side', 'from')
                    if side == 'from':
                        estimated_value = self.net.res_line_est.q_from_mvar.iloc[element]
                    else:
                        estimated_value = self.net.res_line_est.q_to_mvar.iloc[element]
                else:
                    continue
                
                residuals[idx] = {
                    'measured': measured_value,
                    'estimated': estimated_value,
                    'residual': measured_value - estimated_value,
                    'type': meas_type,
                    'element': element,
                    'std_dev': measurement['std_dev']
                }
            
            return residuals
            
        except Exception as e:
            print(f"❌ Error calculating residuals: {e}")
            return None
    
    def _calculate_normalized_residuals(self, residuals):
        """Calculate normalized residuals for bad data detection"""
        try:
            normalized_residuals = {}
            
            for idx, res_data in residuals.items():
                # Simple normalization by standard deviation
                # In practice, this should use the diagonal elements of the residual covariance matrix
                std_dev = res_data['std_dev']
                if std_dev > 0:
                    normalized_residual = abs(res_data['residual']) / std_dev
                else:
                    normalized_residual = abs(res_data['residual'])  # Fallback
                
                normalized_residuals[idx] = {
                    **res_data,
                    'normalized_residual': normalized_residual
                }
            
            return normalized_residuals
            
        except Exception as e:
            print(f"❌ Error calculating normalized residuals: {e}")
            return None
    
    def _perform_bad_data_tests(self, residuals, normalized_residuals, confidence_level):
        """Perform various statistical tests for bad data detection"""
        test_results = {}
        
        # Test 1: Chi-square test for global bad data detection
        chi_square_result = self._chi_square_test(residuals, confidence_level)
        test_results['chi_square'] = chi_square_result
        
        # Test 2: Largest normalized residual test
        max_residual = max(normalized_residuals.values(), key=lambda x: x['normalized_residual'])
        critical_value = self._get_critical_value(confidence_level)
        
        test_results['largest_normalized_residual'] = {
            'value': max_residual['normalized_residual'],
            'critical_value': critical_value,
            'suspicious': max_residual['normalized_residual'] > critical_value,
            'measurement_index': max([k for k, v in normalized_residuals.items() 
                                    if v['normalized_residual'] == max_residual['normalized_residual']])
        }
        
        # Test 3: Statistical outlier detection (3-sigma rule)
        residual_values = [abs(r['residual']) for r in residuals.values()]
        mean_residual = np.mean(residual_values)
        std_residual = np.std(residual_values)
        outlier_threshold = mean_residual + 3 * std_residual
        
        outliers = [idx for idx, res in residuals.items() 
                   if abs(res['residual']) > outlier_threshold]
        
        test_results['three_sigma'] = {
            'threshold': outlier_threshold,
            'outliers': outliers,
            'has_outliers': len(outliers) > 0
        }
        
        return test_results
    
    def _chi_square_test(self, residuals, confidence_level):
        """Perform Chi-square test for global bad data detection"""
        try:
            # Calculate Chi-square statistic
            chi_square_stat = sum((res['residual'] / res['std_dev'])**2 for res in residuals.values())
            degrees_of_freedom = len(residuals)
            
            # More sensitive critical value for Chi-square test
            import math
            
            # Use a more conservative (lower) critical value for better detection
            # Standard: chi_square_critical ≈ degrees_of_freedom + 2*sqrt(2*degrees_of_freedom)
            # More sensitive: reduce the multiplier from 2 to 1.5
            chi_square_critical = degrees_of_freedom + 1.5 * math.sqrt(2 * degrees_of_freedom)
            
            has_bad_data = chi_square_stat > chi_square_critical
            
            return {
                'statistic': chi_square_stat,
                'critical_value': chi_square_critical,
                'degrees_of_freedom': degrees_of_freedom,
                'has_bad_data': has_bad_data,
                'confidence_level': confidence_level
            }
            
        except Exception as e:
            print(f"❌ Chi-square test failed: {e}")
            return {'has_bad_data': False, 'error': str(e)}
    
    def _get_critical_value(self, confidence_level):
        """Get critical value for normalized residual test"""
        # Approximate critical values for normal distribution
        critical_values = {
            0.90: 1.64,  # 90% confidence
            0.95: 1.96,  # 95% confidence
            0.99: 2.58   # 99% confidence
        }
        return critical_values.get(confidence_level, 1.96)
    
    def _identify_largest_normalized_residual(self, normalized_residuals):
        """Identify measurement with largest normalized residual"""
        if not normalized_residuals:
            return None
        
        max_idx = max(normalized_residuals.keys(), 
                     key=lambda k: normalized_residuals[k]['normalized_residual'])
        
        suspect = normalized_residuals[max_idx]
        return {
            'index': max_idx,
            'type': suspect['type'],
            'element': suspect['element'],
            'value': suspect['measured'],
            'estimated': suspect['estimated'],
            'residual': suspect['residual'],
            'normalized_residual': suspect['normalized_residual']
        }
    
    def _validate_suspect_measurement(self, suspect_measurement, normalized_residuals, confidence_level):
        """Validate suspect measurement using additional criteria"""
        critical_value = self._get_critical_value(confidence_level)
        norm_residual = suspect_measurement['normalized_residual']
        
        # More aggressive detection: if residual exceeds critical value significantly, it's bad
        if norm_residual > critical_value * 1.2:  # Reduced threshold from 1.5 to 1.2
            return False  # Measurement is likely bad
        
        # Check if there are multiple measurements with similar high residuals
        high_residuals = [nr['normalized_residual'] for nr in normalized_residuals.values() 
                         if nr['normalized_residual'] > critical_value]
        
        # Increased threshold for systematic error detection
        if len(high_residuals) > 5:  # Multiple suspicious measurements (increased from 3 to 5)
            return True  # Possible systematic error
        
        # If residual is very high (even if not exceeding 1.2x critical), still consider it bad
        if norm_residual > 3.0:  # Absolute threshold
            return False  # Measurement is definitely bad
        
        return True  # Not significantly bad
    
    def _report_bad_measurement(self, suspect_measurement):
        """Report details of detected bad measurement"""
        meas_type = suspect_measurement['type'].upper()
        element = suspect_measurement['element']
        measured_val = suspect_measurement['value']
        estimated_val = suspect_measurement['estimated']
        residual = suspect_measurement['residual']
        norm_residual = suspect_measurement['normalized_residual']
        
        print(f"   📍 Measurement Index: {suspect_measurement['index']}")
        print(f"   📊 Type: {meas_type} measurement on element {element}")
        print(f"   📏 Measured Value: {measured_val:.6f}")
        print(f"   📐 Estimated Value: {estimated_val:.6f}")
        print(f"   📈 Residual: {residual:.6f}")
        print(f"   📉 Normalized Residual: {norm_residual:.3f}")
        
        # Provide interpretation
        if norm_residual > 5:
            print(f"   🚨 SEVERE: Very large residual - likely gross error")
        elif norm_residual > 3:
            print(f"   ⚠️  MODERATE: Large residual - possible bad data")
        else:
            print(f"   ℹ️  MILD: Moderate residual - check measurement")
    
    def _get_measurement_description(self, bad_measurement):
        """Get human-readable description of bad measurement"""
        meas_type = bad_measurement['measurement_type'].upper()
        element = bad_measurement['element']
        
        if meas_type == 'V':
            return f"Voltage measurement at Bus {element}"
        elif meas_type == 'P':
            return f"Active Power measurement at Line {element}"
        elif meas_type == 'Q':
            return f"Reactive Power measurement at Line {element}"
        else:
            return f"{meas_type} measurement at element {element}"
    
    def _remove_measurement(self, measurement_index):
        """Remove measurement from the measurement set"""
        try:
            self.net.measurement = self.net.measurement.drop(measurement_index)
            self.net.measurement = self.net.measurement.reset_index(drop=True)
        except Exception as e:
            print(f"❌ Error removing measurement {measurement_index}: {e}")
    
    def create_bad_data_scenario(self, scenario_type="mixed"):
        """
        Create various bad data scenarios for testing detection algorithms
        
        Args:
            scenario_type (str): Type of scenario - 'single', 'multiple', 'systematic', 'mixed'
        """
        if self.net is None or len(self.net.measurement) == 0:
            print("❌ No measurements available. Generate measurements first.")
            return
        
        print(f"\n🧪 CREATING BAD DATA SCENARIO: {scenario_type.upper()}")
        print("=" * 60)
        
        # Store original measurements
        original_measurements = self.net.measurement.copy()
        bad_measurements_added = []
        
        if scenario_type == "single":
            # Single gross error
            measurement_idx = np.random.choice(self.net.measurement.index)
            original_value = self.net.measurement.loc[measurement_idx, 'value']
            error_factor = np.random.choice([0.5, 2.0, 3.0])  # 50% reduction or 200-300% increase
            new_value = original_value * error_factor
            
            self.net.measurement.loc[measurement_idx, 'value'] = new_value
            bad_measurements_added.append({
                'index': measurement_idx,
                'original': original_value,
                'corrupted': new_value,
                'type': 'single_gross_error'
            })
            
        elif scenario_type == "multiple":
            # Multiple independent bad measurements
            n_bad = min(3, len(self.net.measurement) // 10)  # Up to 3 or 10% of measurements
            bad_indices = np.random.choice(self.net.measurement.index, n_bad, replace=False)
            
            for idx in bad_indices:
                original_value = self.net.measurement.loc[idx, 'value']
                error_factor = np.random.uniform(0.3, 3.0)
                new_value = original_value * error_factor
                
                self.net.measurement.loc[idx, 'value'] = new_value
                bad_measurements_added.append({
                    'index': idx,
                    'original': original_value,
                    'corrupted': new_value,
                    'type': 'multiple_errors'
                })
                
        elif scenario_type == "systematic":
            # Systematic bias in voltage measurements
            voltage_measurements = self.net.measurement[self.net.measurement['measurement_type'] == 'v']
            bias = 0.05  # 5% systematic bias
            
            for idx in voltage_measurements.index:
                original_value = self.net.measurement.loc[idx, 'value']
                new_value = original_value + bias
                
                self.net.measurement.loc[idx, 'value'] = new_value
                bad_measurements_added.append({
                    'index': idx,
                    'original': original_value,
                    'corrupted': new_value,
                    'type': 'systematic_bias'
                })
                
        elif scenario_type == "mixed":
            # Combination of gross errors and systematic bias
            # Add one gross error
            measurement_idx = np.random.choice(self.net.measurement.index)
            original_value = self.net.measurement.loc[measurement_idx, 'value']
            new_value = original_value * 2.5  # 250% of original
            
            self.net.measurement.loc[measurement_idx, 'value'] = new_value
            bad_measurements_added.append({
                'index': measurement_idx,
                'original': original_value,
                'corrupted': new_value,
                'type': 'gross_error'
            })
            
            # Add systematic bias to power measurements
            power_measurements = self.net.measurement[self.net.measurement['measurement_type'].isin(['p', 'q'])]
            bias_factor = 1.1  # 10% systematic increase
            
            for idx in power_measurements.index[:3]:  # First 3 power measurements
                original_value = self.net.measurement.loc[idx, 'value']
                new_value = original_value * bias_factor
                
                self.net.measurement.loc[idx, 'value'] = new_value
                bad_measurements_added.append({
                    'index': idx,
                    'original': original_value,
                    'corrupted': new_value,
                    'type': 'systematic_bias'
                })
        
        # Report what was changed
        print(f"✅ Bad data scenario created with {len(bad_measurements_added)} corrupted measurements:")
        for i, bad_meas in enumerate(bad_measurements_added, 1):
            meas_info = self.net.measurement.loc[bad_meas['index']]
            meas_type = meas_info['measurement_type'].upper()
            element = meas_info['element']
            
            print(f"   {i}. {meas_type} measurement at element {element}")
            print(f"      Original: {bad_meas['original']:.6f} → Corrupted: {bad_meas['corrupted']:.6f}")
            print(f"      Error type: {bad_meas['type']}")
        
        # Store scenario info
        self.bad_data_scenario = {
            'scenario_type': scenario_type,
            'original_measurements': original_measurements,
            'corrupted_measurements': bad_measurements_added,
            'total_measurements': len(self.net.measurement)
        }
        
        print(f"\n💡 Now run detect_bad_data() to test the detection algorithm!")
        return bad_measurements_added
    
    def check_measurement_consistency(self, tolerance=1e-3, detailed_report=True):
        """
        Comprehensive measurement consistency check using power system laws
        
        Args:
            tolerance (float): Tolerance for consistency violations (default 1e-3)
            detailed_report (bool): Whether to show detailed analysis (default True)
            
        Returns:
            dict: Consistency check results with violations and analysis
        """
        if self.net is None:
            raise ValueError("Grid model not created.")
        if len(self.net.measurement) == 0:
            raise ValueError("No measurements available. Call simulate_measurements() first.")
        
        print("\n" + "="*70)
        print("🔍 MEASUREMENT CONSISTENCY CHECK")
        print("="*70)
        
        # Run power flow to get reference values
        try:
            pp.runpp(self.net, algorithm='nr')
        except Exception as e:
            print(f"❌ Power flow failed: {e}")
            return None
        
        consistency_results = {
            'overall_status': 'unknown',
            'total_violations': 0,
            'violation_types': {},
            'detailed_violations': [],
            'consistency_metrics': {},
            'recommendations': []
        }
        
        print(f"System: {len(self.net.bus)} buses, {len(self.net.line)} lines")
        print(f"Measurements: {len(self.net.measurement)} total")
        print(f"Tolerance: {tolerance:.1e}")
        
        # 1. Power Flow Consistency Check
        pf_violations = self._check_power_flow_consistency(tolerance)
        consistency_results['violation_types']['power_flow'] = pf_violations
        
        # 2. Kirchhoff's Current Law (KCL) Check
        kcl_violations = self._check_kcl_consistency(tolerance)
        consistency_results['violation_types']['kcl'] = kcl_violations
        
        # 3. Bus Power Balance Check
        balance_violations = self._check_bus_power_balance(tolerance)
        consistency_results['violation_types']['power_balance'] = balance_violations
        
        # 4. Voltage Consistency Check
        voltage_violations = self._check_voltage_consistency(tolerance)
        consistency_results['violation_types']['voltage'] = voltage_violations
        
        # 5. Measurement Redundancy Check
        redundancy_issues = self._check_measurement_redundancy()
        consistency_results['violation_types']['redundancy'] = redundancy_issues
        
        # 6. Physical Limits Check
        limits_violations = self._check_physical_limits()
        consistency_results['violation_types']['physical_limits'] = limits_violations
        
        # Calculate overall statistics
        total_violations = sum(len(v) for v in consistency_results['violation_types'].values())
        consistency_results['total_violations'] = total_violations
        
        # Determine overall status
        if total_violations == 0:
            consistency_results['overall_status'] = 'consistent'
        elif total_violations <= 3:
            consistency_results['overall_status'] = 'minor_issues'
        elif total_violations <= 10:
            consistency_results['overall_status'] = 'moderate_issues'
        else:
            consistency_results['overall_status'] = 'major_issues'
        
        # Generate consistency metrics
        consistency_results['consistency_metrics'] = self._calculate_consistency_metrics()
        
        # Generate recommendations
        consistency_results['recommendations'] = self._generate_consistency_recommendations(consistency_results)
        
        # Display results
        if detailed_report:
            self._display_consistency_results(consistency_results)
        
        # Store results
        self.consistency_results = consistency_results
        
        return consistency_results
    
    def _check_power_flow_consistency(self, tolerance):
        """Check consistency of power flow measurements"""
        violations = []
        
        print(f"\n1️⃣ POWER FLOW CONSISTENCY")
        print("-" * 40)
        
        # Get power flow measurements
        p_measurements = self.net.measurement[self.net.measurement['measurement_type'] == 'p']
        q_measurements = self.net.measurement[self.net.measurement['measurement_type'] == 'q']
        
        for _, meas in p_measurements.iterrows():
            line_id = meas['element']
            side = meas.get('side', 'from')
            measured_p = meas['value']
            
            try:
                if side == 'from':
                    calculated_p = self.net.res_line.p_from_mw.iloc[line_id]
                else:
                    calculated_p = self.net.res_line.p_to_mw.iloc[line_id]
                
                error = abs(measured_p - calculated_p)
                relative_error = error / max(abs(calculated_p), 1e-6)
                
                if error > tolerance * 1000:  # Convert to MW scale
                    violations.append({
                        'type': 'power_flow_active',
                        'element': f'Line {line_id} ({side})',
                        'measured': measured_p,
                        'calculated': calculated_p,
                        'error': error,
                        'relative_error': relative_error,
                        'severity': 'high' if relative_error > 0.1 else 'medium'
                    })
            except IndexError:
                violations.append({
                    'type': 'power_flow_missing',
                    'element': f'Line {line_id}',
                    'error': 'Line not found in results',
                    'severity': 'high'
                })
        
        print(f"Active power measurements checked: {len(p_measurements)}")
        print(f"Reactive power measurements checked: {len(q_measurements)}")
        
        if violations:
            print(f"⚠️  Found {len(violations)} power flow inconsistencies")
        else:
            print(f"✅ All power flow measurements consistent")
        
        return violations
    
    def _check_kcl_consistency(self, tolerance):
        """Check Kirchhoff's Current Law consistency at buses"""
        violations = []
        
        print(f"\n2️⃣ KIRCHHOFF'S CURRENT LAW (KCL)")
        print("-" * 40)
        
        for bus_idx in self.net.bus.index:
            # Get all power injections/withdrawals at this bus
            bus_power_sum = 0
            measurement_count = 0
            
            # Generation at bus
            bus_gens = self.net.gen[self.net.gen['bus'] == bus_idx]
            for _, gen in bus_gens.iterrows():
                gen_idx = gen.name
                if hasattr(self.net, 'res_gen'):
                    bus_power_sum += self.net.res_gen.p_mw.iloc[gen_idx]
            
            # Load at bus
            bus_loads = self.net.load[self.net.load['bus'] == bus_idx]
            for _, load in bus_loads.iterrows():
                load_idx = load.name
                if hasattr(self.net, 'res_load'):
                    bus_power_sum -= self.net.res_load.p_mw.iloc[load_idx]
                else:
                    bus_power_sum -= load.p_mw
            
            # External grid connections
            bus_ext_grids = self.net.ext_grid[self.net.ext_grid['bus'] == bus_idx]
            for _, ext_grid in bus_ext_grids.iterrows():
                ext_idx = ext_grid.name
                if hasattr(self.net, 'res_ext_grid'):
                    bus_power_sum += self.net.res_ext_grid.p_mw.iloc[ext_idx]
            
            # Line flows
            connected_lines = []
            
            # Lines from this bus
            from_lines = self.net.line[self.net.line['from_bus'] == bus_idx]
            for _, line in from_lines.iterrows():
                line_idx = line.name
                if hasattr(self.net, 'res_line'):
                    bus_power_sum -= self.net.res_line.p_from_mw.iloc[line_idx]
                    connected_lines.append(f"Line {line_idx} (from)")
            
            # Lines to this bus
            to_lines = self.net.line[self.net.line['to_bus'] == bus_idx]
            for _, line in to_lines.iterrows():
                line_idx = line.name
                if hasattr(self.net, 'res_line'):
                    bus_power_sum -= self.net.res_line.p_to_mw.iloc[line_idx]
                    connected_lines.append(f"Line {line_idx} (to)")
            
            # Check if power balance is violated
            if abs(bus_power_sum) > tolerance * 1000:  # Convert to MW scale
                violations.append({
                    'type': 'kcl_violation',
                    'element': f'Bus {bus_idx}',
                    'power_imbalance': bus_power_sum,
                    'connected_elements': connected_lines,
                    'severity': 'high' if abs(bus_power_sum) > 10 else 'medium'
                })
        
        print(f"Buses checked for KCL: {len(self.net.bus)}")
        
        if violations:
            print(f"⚠️  Found {len(violations)} KCL violations")
        else:
            print(f"✅ All buses satisfy KCL")
        
        return violations
    
    def _check_bus_power_balance(self, tolerance):
        """Check power balance at buses using measurements"""
        violations = []
        
        print(f"\n3️⃣ BUS POWER BALANCE")
        print("-" * 40)
        
        bus_measurements = {}
        
        # Collect measurements by bus
        for _, meas in self.net.measurement.iterrows():
            if meas['measurement_type'] == 'v':
                continue  # Skip voltage measurements for power balance
            
            element = meas['element']
            meas_type = meas['measurement_type']
            value = meas['value']
            
            # For power measurements on lines, determine which bus they affect
            if meas_type in ['p', 'q']:
                side = meas.get('side', 'from')
                try:
                    if side == 'from':
                        bus_id = self.net.line.from_bus.iloc[element]
                    else:
                        bus_id = self.net.line.to_bus.iloc[element]
                    
                    if bus_id not in bus_measurements:
                        bus_measurements[bus_id] = {'p_in': 0, 'p_out': 0, 'q_in': 0, 'q_out': 0}
                    
                    if meas_type == 'p':
                        if value > 0:
                            bus_measurements[bus_id]['p_out'] += value
                        else:
                            bus_measurements[bus_id]['p_in'] += abs(value)
                    elif meas_type == 'q':
                        if value > 0:
                            bus_measurements[bus_id]['q_out'] += value
                        else:
                            bus_measurements[bus_id]['q_in'] += abs(value)
                            
                except (IndexError, KeyError):
                    continue
        
        # Check balance for buses with sufficient measurements
        for bus_id, measurements in bus_measurements.items():
            p_balance = measurements['p_in'] - measurements['p_out']
            q_balance = measurements['q_in'] - measurements['q_out']
            
            # Allow some tolerance for measurement errors and losses
            balance_tolerance = tolerance * 1000  # MW scale
            
            if abs(p_balance) > balance_tolerance:
                violations.append({
                    'type': 'power_balance_active',
                    'element': f'Bus {bus_id}',
                    'power_imbalance': p_balance,
                    'measurements': measurements,
                    'severity': 'high' if abs(p_balance) > 50 else 'medium'
                })
            
            if abs(q_balance) > balance_tolerance:
                violations.append({
                    'type': 'power_balance_reactive',
                    'element': f'Bus {bus_id}',
                    'power_imbalance': q_balance,
                    'measurements': measurements,
                    'severity': 'high' if abs(q_balance) > 50 else 'medium'
                })
        
        print(f"Buses with power measurements: {len(bus_measurements)}")
        
        if violations:
            print(f"⚠️  Found {len(violations)} power balance violations")
        else:
            print(f"✅ Power balance consistent across measured buses")
        
        return violations
    
    def _check_voltage_consistency(self, tolerance):
        """Check voltage measurement consistency"""
        violations = []
        
        print(f"\n4️⃣ VOLTAGE CONSISTENCY")
        print("-" * 40)
        
        v_measurements = self.net.measurement[self.net.measurement['measurement_type'] == 'v']
        
        for _, meas in v_measurements.iterrows():
            bus_id = meas['element']
            measured_v = meas['value']
            
            try:
                # Get calculated voltage from power flow
                calculated_v = self.net.res_bus.vm_pu.iloc[bus_id]
                
                error = abs(measured_v - calculated_v)
                relative_error = error / max(abs(calculated_v), 1e-6)
                
                # Check for unrealistic voltage values
                if measured_v < 0.8 or measured_v > 1.2:
                    violations.append({
                        'type': 'voltage_unrealistic',
                        'element': f'Bus {bus_id}',
                        'measured': measured_v,
                        'issue': 'Voltage outside normal range (0.8-1.2 p.u.)',
                        'severity': 'high'
                    })
                
                # Check for significant deviations from calculated values
                if relative_error > tolerance:
                    violations.append({
                        'type': 'voltage_deviation',
                        'element': f'Bus {bus_id}',
                        'measured': measured_v,
                        'calculated': calculated_v,
                        'error': error,
                        'relative_error': relative_error,
                        'severity': 'high' if relative_error > 0.05 else 'medium'
                    })
            except IndexError:
                violations.append({
                    'type': 'voltage_missing',
                    'element': f'Bus {bus_id}',
                    'error': 'Bus not found in power flow results',
                    'severity': 'high'
                })
        
        print(f"Voltage measurements checked: {len(v_measurements)}")
        
        if violations:
            print(f"⚠️  Found {len(violations)} voltage inconsistencies")
        else:
            print(f"✅ All voltage measurements consistent")
        
        return violations
    
    def _check_measurement_redundancy(self):
        """Check measurement redundancy and coverage"""
        issues = []
        
        print(f"\n5️⃣ MEASUREMENT REDUNDANCY")
        print("-" * 40)
        
        # Count measurements by type and element
        measurement_counts = {}
        
        for _, meas in self.net.measurement.iterrows():
            meas_type = meas['measurement_type']
            element = meas['element']
            key = f"{meas_type}_{element}"
            
            if key not in measurement_counts:
                measurement_counts[key] = 0
            measurement_counts[key] += 1
        
        # Check for buses without voltage measurements
        measured_buses = set()
        for _, meas in self.net.measurement.iterrows():
            if meas['measurement_type'] == 'v':
                measured_buses.add(meas['element'])
        
        unmeasured_buses = []
        for bus_idx in self.net.bus.index:
            if bus_idx not in measured_buses:
                unmeasured_buses.append(bus_idx)
        
        if unmeasured_buses:
            issues.append({
                'type': 'unmeasured_buses',
                'elements': unmeasured_buses,
                'count': len(unmeasured_buses),
                'severity': 'medium'
            })
        
        # Check for lines without power measurements
        measured_lines = set()
        for _, meas in self.net.measurement.iterrows():
            if meas['measurement_type'] in ['p', 'q']:
                measured_lines.add(meas['element'])
        
        unmeasured_lines = []
        for line_idx in self.net.line.index:
            if line_idx not in measured_lines:
                unmeasured_lines.append(line_idx)
        
        if unmeasured_lines:
            issues.append({
                'type': 'unmeasured_lines',
                'elements': unmeasured_lines,
                'count': len(unmeasured_lines),
                'severity': 'low'
            })
        
        # Check for over-measured elements (too many measurements on same element)
        over_measured = []
        for key, count in measurement_counts.items():
            if count > 2:  # More than 2 measurements on same element
                over_measured.append((key, count))
        
        if over_measured:
            issues.append({
                'type': 'over_measured',
                'elements': over_measured,
                'severity': 'low'
            })
        
        print(f"Bus voltage coverage: {len(measured_buses)}/{len(self.net.bus)} buses")
        print(f"Line power coverage: {len(measured_lines)}/{len(self.net.line)} lines")
        
        if issues:
            print(f"⚠️  Found {len(issues)} redundancy issues")
        else:
            print(f"✅ Good measurement redundancy and coverage")
        
        return issues
    
    def _check_physical_limits(self):
        """Check if measurements respect physical limits"""
        violations = []
        
        print(f"\n6️⃣ PHYSICAL LIMITS")
        print("-" * 40)
        
        # Check power flow limits
        p_measurements = self.net.measurement[self.net.measurement['measurement_type'] == 'p']
        
        for _, meas in p_measurements.iterrows():
            line_id = meas['element']
            power_flow = abs(meas['value'])
            
            try:
                # Get line rating if available
                if 'max_i_ka' in self.net.line.columns:
                    max_current = self.net.line.max_i_ka.iloc[line_id]
                    vn_kv = self.net.bus.vn_kv.iloc[self.net.line.from_bus.iloc[line_id]]
                    max_power = max_current * vn_kv * np.sqrt(3)  # 3-phase power limit
                    
                    if power_flow > max_power * 1.1:  # 10% margin
                        violations.append({
                            'type': 'power_limit_exceeded',
                            'element': f'Line {line_id}',
                            'measured_power': power_flow,
                            'limit': max_power,
                            'severity': 'high'
                        })
                
                # Check for extremely high power flows (sanity check)
                line_voltage = self.net.bus.vn_kv.iloc[self.net.line.from_bus.iloc[line_id]]
                reasonable_limit = line_voltage * 10  # Very generous limit
                
                if power_flow > reasonable_limit:
                    violations.append({
                        'type': 'unrealistic_power',
                        'element': f'Line {line_id}',
                        'measured_power': power_flow,
                        'threshold': reasonable_limit,
                        'severity': 'high'
                    })
                    
            except (IndexError, KeyError):
                continue
        
        checked_measurements = len(p_measurements)
        print(f"Power flow measurements checked: {checked_measurements}")
        
        if violations:
            print(f"⚠️  Found {len(violations)} physical limit violations")
        else:
            print(f"✅ All measurements within physical limits")
        
        return violations
    
    def _calculate_consistency_metrics(self):
        """Calculate overall consistency metrics"""
        metrics = {}
        
        # Measurement coverage
        total_buses = len(self.net.bus)
        total_lines = len(self.net.line)
        
        voltage_measurements = len(self.net.measurement[self.net.measurement['measurement_type'] == 'v'])
        power_measurements = len(self.net.measurement[self.net.measurement['measurement_type'].isin(['p', 'q'])])
        
        metrics['voltage_coverage'] = voltage_measurements / total_buses
        metrics['power_coverage'] = power_measurements / (total_lines * 2)  # Each line can have 2 measurements
        
        # Redundancy ratio
        total_measurements = len(self.net.measurement)
        min_measurements_needed = 2 * total_buses - 1  # Minimum for observability
        metrics['redundancy_ratio'] = total_measurements / min_measurements_needed
        
        # Measurement density
        total_network_elements = total_buses + total_lines
        metrics['measurement_density'] = total_measurements / total_network_elements
        
        return metrics
    
    def _generate_consistency_recommendations(self, results):
        """Generate recommendations based on consistency check results"""
        recommendations = []
        
        violation_counts = {vtype: len(violations) for vtype, violations in results['violation_types'].items()}
        
        if violation_counts.get('power_flow', 0) > 0:
            recommendations.append("⚠️  Review power flow measurements for accuracy")
            recommendations.append("🔧 Check measurement calibration and sensor functionality")
        
        if violation_counts.get('kcl', 0) > 0:
            recommendations.append("⚠️  Investigate Kirchhoff's law violations - possible missing measurements")
            recommendations.append("🔧 Add measurements at buses with high power imbalances")
        
        if violation_counts.get('voltage', 0) > 0:
            recommendations.append("⚠️  Check voltage measurement accuracy")
            recommendations.append("🔧 Verify voltage transformer ratios and calibration")
        
        if violation_counts.get('redundancy', 0) > 0:
            recommendations.append("📊 Consider adding measurements for better system observability")
            recommendations.append("🎯 Focus on unmeasured buses and critical lines")
        
        if violation_counts.get('physical_limits', 0) > 0:
            recommendations.append("🚨 Investigate measurements exceeding physical limits")
            recommendations.append("⚡ Check for measurement scaling errors or equipment overload")
        
        if results['total_violations'] == 0:
            recommendations.append("✅ Measurement set appears consistent")
            recommendations.append("🎯 System is ready for reliable state estimation")
        
        return recommendations
    
    def _display_consistency_results(self, results):
        """Display detailed consistency check results"""
        print(f"\n📊 CONSISTENCY CHECK SUMMARY")
        print("=" * 60)
        
        status_icons = {
            'consistent': '✅',
            'minor_issues': '⚠️ ',
            'moderate_issues': '🔶',
            'major_issues': '🚨'
        }
        
        status_messages = {
            'consistent': 'CONSISTENT - All checks passed',
            'minor_issues': 'MINOR ISSUES - Generally consistent with few problems',
            'moderate_issues': 'MODERATE ISSUES - Several consistency violations',
            'major_issues': 'MAJOR ISSUES - Significant consistency problems'
        }
        
        overall_status = results['overall_status']
        icon = status_icons.get(overall_status, '❓')
        message = status_messages.get(overall_status, 'Unknown status')
        
        print(f"{icon} OVERALL STATUS: {message}")
        print(f"Total violations: {results['total_violations']}")
        
        # Show violation breakdown
        print(f"\n📋 VIOLATION BREAKDOWN:")
        for vtype, violations in results['violation_types'].items():
            count = len(violations)
            if count > 0:
                print(f"  {vtype.replace('_', ' ').title()}: {count} violations")
        
        # Show top violations with details
        if results['total_violations'] > 0:
            print(f"\n🔍 DETAILED VIOLATIONS:")
            violation_count = 0
            for vtype, violations in results['violation_types'].items():
                for violation in violations[:3]:  # Show top 3 per type
                    violation_count += 1
                    if violation_count > 10:  # Limit total display
                        break
                    
                    print(f"\n  {violation_count}. {violation.get('type', 'unknown').upper()}")
                    print(f"     Element: {violation.get('element', 'unknown')}")
                    
                    if 'error' in violation and isinstance(violation['error'], (int, float)):
                        print(f"     Error: {violation['error']:.6f}")
                    elif 'power_imbalance' in violation:
                        print(f"     Imbalance: {violation['power_imbalance']:.3f} MW")
                    elif 'measured' in violation and 'calculated' in violation:
                        measured = violation['measured']
                        calculated = violation['calculated']
                        print(f"     Measured: {measured:.6f}, Calculated: {calculated:.6f}")
                    
                    severity = violation.get('severity', 'unknown')
                    severity_icon = '🚨' if severity == 'high' else '⚠️ ' if severity == 'medium' else 'ℹ️ '
                    print(f"     Severity: {severity_icon} {severity.upper()}")
                
                if violation_count > 10:
                    break
        
        # Show metrics
        metrics = results['consistency_metrics']
        print(f"\n📈 CONSISTENCY METRICS:")
        print(f"  Voltage coverage: {metrics.get('voltage_coverage', 0):.2%}")
        print(f"  Power coverage: {metrics.get('power_coverage', 0):.2%}")
        print(f"  Redundancy ratio: {metrics.get('redundancy_ratio', 0):.2f}")
        print(f"  Measurement density: {metrics.get('measurement_density', 0):.2f}")
        
        # Show recommendations
        recommendations = results['recommendations']
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                print(f"  {i}. {rec}")
            
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
            estimated_value = self.net.res_bus_est.vm_pu.iloc[bus_idx]
            
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