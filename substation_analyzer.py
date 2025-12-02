#!/usr/bin/env python3
"""
Substation Analysis Module for Power System State Estimation
Provides advanced substation grouping, analysis, and visualization capabilities
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple

class SubstationAnalyzer:
    """Advanced substation analysis and grouping functionality"""
    
    def __init__(self, grid_estimator):
        """Initialize with reference to GridStateEstimator"""
        self.estimator = grid_estimator
        self.net = grid_estimator.net if grid_estimator else None
    
    def get_substation_analysis(self) -> Dict[str, Any]:
        """Get comprehensive substation analysis and grouping"""
        if self.net is None:
            return {}
            
        # Detect grid type
        grid_type = self._detect_grid_type()
        
        # Get substation definitions based on grid type
        substations = self._define_substations(grid_type)
        
        # Analyze each substation
        substation_analysis = {}
        for substation in substations:
            analysis = self._analyze_substation(substation)
            substation_analysis[substation['id']] = analysis
            
        return {
            'grid_type': grid_type,
            'substations': substations,
            'analysis': substation_analysis,
            'topology': self._analyze_substation_topology(substations),
            'summary': self._generate_system_summary(substations, substation_analysis)
        }
    
    def _detect_grid_type(self) -> str:
        """Detect the type of grid system"""
        if self.net is None:
            return 'unknown'
            
        num_buses = len(self.net.bus)
        voltage_levels = set()
        
        if hasattr(self.net, 'bus'):
            voltage_levels = set(self.net.bus['vn_kv'].unique())
            
        # IEEE 9-bus detection
        if num_buses == 9 and 138.0 in voltage_levels:
            return 'ieee9'
            
        # ENTSO-E detection  
        elif 400.0 in voltage_levels and 220.0 in voltage_levels:
            return 'entsoe'
            
        return 'custom'
    
    def _define_substations(self, grid_type: str) -> List[Dict[str, Any]]:
        """Define substation groupings based on grid type"""
        if grid_type == 'ieee9':
            return [
                {
                    'id': 'sub1',
                    'name': 'Generation Station A',
                    'buses': [0, 1, 2],
                    'voltage': '138kV',
                    'type': 'generation',
                    'coordinates': {'x': 200, 'y': 150},
                    'description': 'Primary generation facility with three generator units'
                },
                {
                    'id': 'sub2', 
                    'name': 'Transmission Hub',
                    'buses': [3, 4, 5],
                    'voltage': '138kV',
                    'type': 'transmission',
                    'coordinates': {'x': 600, 'y': 250},
                    'description': 'Central transmission switching station'
                },
                {
                    'id': 'sub3',
                    'name': 'Distribution Center', 
                    'buses': [6, 7, 8],
                    'voltage': '138kV',
                    'type': 'distribution',
                    'coordinates': {'x': 1000, 'y': 350},
                    'description': 'Load distribution center serving major loads'
                }
            ]
            
        elif grid_type == 'entsoe':
            return [
                {
                    'id': 'sub1',
                    'name': 'Northern 400kV Station',
                    'buses': [0], 
                    'voltage': '400kV',
                    'type': 'transmission',
                    'coordinates': {'x': 200, 'y': 100},
                    'description': 'High voltage transmission station with thermal generation'
                },
                {
                    'id': 'sub2',
                    'name': 'Central Hub 400/220kV',
                    'buses': [1],
                    'voltage': 'Mixed', 
                    'type': 'interconnection',
                    'coordinates': {'x': 600, 'y': 200},
                    'description': 'Main interconnection hub with voltage transformation'
                },
                {
                    'id': 'sub3', 
                    'name': 'Southern 400kV Station',
                    'buses': [2],
                    'voltage': '400kV',
                    'type': 'transmission', 
                    'coordinates': {'x': 1000, 'y': 100},
                    'description': 'Southern transmission node serving load centers'
                },
                {
                    'id': 'sub4',
                    'name': '220kV East Station',
                    'buses': [3],
                    'voltage': '220kV',
                    'type': 'distribution',
                    'coordinates': {'x': 400, 'y': 400},
                    'description': 'Eastern wind farm connection point'
                },
                {
                    'id': 'sub5',
                    'name': '220kV West Station', 
                    'buses': [4],
                    'voltage': '220kV',
                    'type': 'distribution',
                    'coordinates': {'x': 800, 'y': 400},
                    'description': 'Western industrial load connection'
                }
            ]
            
        else:
            # Auto-detect substations for custom grids
            return self._auto_detect_substations()
    
    def _auto_detect_substations(self) -> List[Dict[str, Any]]:
        """Auto-detect substation groupings for custom grids"""
        substations = []
        
        if not hasattr(self.net, 'bus'):
            return substations
            
        # Group buses by voltage level and geographical proximity
        voltage_groups = {}
        for idx in self.net.bus.index:
            voltage = self.net.bus.loc[idx, 'vn_kv']
            if voltage not in voltage_groups:
                voltage_groups[voltage] = []
            voltage_groups[voltage].append(int(idx))
            
        # Create substations for each voltage group
        for i, (voltage, buses) in enumerate(voltage_groups.items()):
            # For larger voltage groups, try to split geographically
            if len(buses) > 5:
                # Split into multiple substations
                chunk_size = 3
                for j, chunk_start in enumerate(range(0, len(buses), chunk_size)):
                    chunk_buses = buses[chunk_start:chunk_start + chunk_size]
                    substations.append({
                        'id': f'auto_sub_{voltage}kV_{j+1}',
                        'name': f'{voltage}kV Substation {j+1}',
                        'buses': chunk_buses,
                        'voltage': f'{voltage}kV',
                        'type': 'auto_detected',
                        'coordinates': {'x': 200 + j * 300, 'y': 200 + i * 150},
                        'description': f'Auto-detected {voltage}kV substation cluster {j+1}'
                    })
            else:
                substations.append({
                    'id': f'auto_sub_{i+1}',
                    'name': f'{voltage}kV Substation {i+1}',
                    'buses': buses,
                    'voltage': f'{voltage}kV',
                    'type': 'auto_detected',
                    'coordinates': {'x': 200 + i * 400, 'y': 200 + i * 100},
                    'description': f'Auto-detected {voltage}kV substation'
                })
            
        return substations
    
    def _analyze_substation(self, substation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual substation characteristics"""
        analysis = {
            'bus_count': len(substation['buses']),
            'buses': [],
            'generators': [],
            'loads': [],
            'lines': [],
            'transformers': [],
            'switches': [],
            'voltage_profile': {},
            'power_balance': {},
            'reliability': {},
            'operational_status': 'normal'
        }
        
        # Analyze buses in substation
        for bus_idx in substation['buses']:
            if bus_idx < len(self.net.bus):
                bus_analysis = self._analyze_substation_bus(bus_idx)
                analysis['buses'].append(bus_analysis)
                
        # Find connected equipment
        analysis['generators'] = self._find_substation_generators(substation['buses'])
        analysis['loads'] = self._find_substation_loads(substation['buses'])
        analysis['lines'] = self._find_substation_lines(substation['buses'])
        analysis['transformers'] = self._find_substation_transformers(substation['buses'])
        analysis['switches'] = self._find_substation_switches(substation['buses'])
        
        # Calculate aggregated metrics
        analysis['voltage_profile'] = self._calculate_substation_voltage_profile(substation['buses'])
        analysis['power_balance'] = self._calculate_substation_power_balance(substation['buses'])
        analysis['reliability'] = self._assess_substation_reliability(substation['buses'])
        
        # Determine operational status
        analysis['operational_status'] = self._determine_operational_status(analysis)
        
        return analysis
    
    def _analyze_substation_bus(self, bus_idx: int) -> Dict[str, Any]:
        """Analyze individual bus within substation"""
        bus_analysis = {
            'index': int(bus_idx),
            'name': f"Bus {bus_idx}",
            'voltage_kv': 0.0,
            'voltage_pu': 1.0,
            'estimated_voltage_pu': None,
            'angle_deg': 0.0,
            'status': 'online'
        }
        
        try:
            if hasattr(self.net, 'bus') and bus_idx in self.net.bus.index:
                # Find the position in the dataframe
                bus_positions = list(self.net.bus.index)
                if bus_idx in bus_positions:
                    i = bus_positions.index(bus_idx)
                    bus_analysis['voltage_kv'] = float(self.net.bus.iloc[i]['vn_kv'])
                    
                    if hasattr(self.net, 'res_bus') and i < len(self.net.res_bus):
                        bus_analysis['voltage_pu'] = float(self.net.res_bus.iloc[i]['vm_pu'])
                        bus_analysis['angle_deg'] = float(self.net.res_bus.iloc[i]['va_degree'])
                        
                    if hasattr(self.net, 'res_bus_est') and i < len(self.net.res_bus_est):
                        bus_analysis['estimated_voltage_pu'] = float(self.net.res_bus_est.iloc[i]['vm_pu'])
                        
        except (IndexError, KeyError) as e:
            print(f"Warning: Could not analyze bus {bus_idx}: {e}")
            bus_analysis['status'] = 'analysis_error'
            
        return bus_analysis
    
    def _find_substation_generators(self, bus_list: List[int]) -> List[Dict[str, Any]]:
        """Find generators connected to substation buses"""
        generators = []
        
        if hasattr(self.net, 'gen'):
            for i, gen_idx in enumerate(self.net.gen.index):
                gen_bus = int(self.net.gen.iloc[i]['bus'])
                if gen_bus in bus_list:
                    gen_info = {
                        'index': int(gen_idx),
                        'bus': gen_bus,
                        'p_mw': float(self.net.gen.iloc[i]['p_mw']),
                        'vm_pu': float(self.net.gen.iloc[i]['vm_pu']) if 'vm_pu' in self.net.gen.columns else 1.0,
                        'in_service': bool(self.net.gen.iloc[i]['in_service']),
                        'name': str(self.net.gen.iloc[i]['name']) if 'name' in self.net.gen.columns else f"Gen {gen_idx}",
                        'generation_type': self._classify_generator_type(self.net.gen.iloc[i]['p_mw'])
                    }
                    
                    # Add actual output if available
                    if hasattr(self.net, 'res_gen') and i < len(self.net.res_gen):
                        gen_info['actual_p_mw'] = float(self.net.res_gen.iloc[i]['p_mw'])
                        gen_info['actual_q_mvar'] = float(self.net.res_gen.iloc[i]['q_mvar'])
                    
                    generators.append(gen_info)
                    
        return generators
    
    def _classify_generator_type(self, p_mw: float) -> str:
        """Classify generator type based on capacity"""
        if p_mw > 500:
            return 'large_thermal'
        elif p_mw > 200:
            return 'medium_thermal'
        elif p_mw > 50:
            return 'renewable'
        else:
            return 'small_unit'
    
    def _find_substation_loads(self, bus_list: List[int]) -> List[Dict[str, Any]]:
        """Find loads connected to substation buses"""
        loads = []
        
        if hasattr(self.net, 'load'):
            for i, load_idx in enumerate(self.net.load.index):
                load_bus = int(self.net.load.iloc[i]['bus'])
                if load_bus in bus_list:
                    load_info = {
                        'index': int(load_idx),
                        'bus': load_bus,
                        'p_mw': float(self.net.load.iloc[i]['p_mw']),
                        'q_mvar': float(self.net.load.iloc[i]['q_mvar']),
                        'in_service': bool(self.net.load.iloc[i]['in_service']),
                        'name': str(self.net.load.iloc[i]['name']) if 'name' in self.net.load.columns else f"Load {load_idx}",
                        'load_type': self._classify_load_type(self.net.load.iloc[i]['p_mw'])
                    }
                    loads.append(load_info)
                    
        return loads
    
    def _classify_load_type(self, p_mw: float) -> str:
        """Classify load type based on consumption"""
        if p_mw > 300:
            return 'industrial_major'
        elif p_mw > 100:
            return 'urban_center'
        elif p_mw > 50:
            return 'residential'
        else:
            return 'small_commercial'
    
    def _find_substation_lines(self, bus_list: List[int]) -> List[Dict[str, Any]]:
        """Find transmission lines connected to substation"""
        lines = []
        
        if hasattr(self.net, 'line'):
            for i, line_idx in enumerate(self.net.line.index):
                from_bus = int(self.net.line.iloc[i]['from_bus'])
                to_bus = int(self.net.line.iloc[i]['to_bus']) 
                
                # Line connected if either end is in substation
                if from_bus in bus_list or to_bus in bus_list:
                    line_info = {
                        'index': int(line_idx),
                        'from_bus': from_bus,
                        'to_bus': to_bus,
                        'length_km': float(self.net.line.iloc[i]['length_km']) if 'length_km' in self.net.line.columns else 0.0,
                        'in_service': bool(self.net.line.iloc[i]['in_service']),
                        'name': str(self.net.line.iloc[i]['name']) if 'name' in self.net.line.columns else f"Line {line_idx}",
                        'connection_type': 'internal' if (from_bus in bus_list and to_bus in bus_list) else 'external',
                        'line_type': self._classify_line_type(float(self.net.line.iloc[i]['length_km']) if 'length_km' in self.net.line.columns else 0.0)
                    }
                    
                    # Add loading information if available
                    if hasattr(self.net, 'res_line') and i < len(self.net.res_line):
                        line_info['loading_percent'] = float(self.net.res_line.iloc[i]['loading_percent'])
                        line_info['p_from_mw'] = float(self.net.res_line.iloc[i]['p_from_mw'])
                        line_info['p_to_mw'] = float(self.net.res_line.iloc[i]['p_to_mw'])
                        
                    lines.append(line_info)
                    
        return lines
    
    def _classify_line_type(self, length_km: float) -> str:
        """Classify transmission line type"""
        if length_km > 100:
            return 'long_distance'
        elif length_km > 50:
            return 'regional'
        elif length_km > 10:
            return 'local'
        else:
            return 'interconnection'
    
    def _find_substation_transformers(self, bus_list: List[int]) -> List[Dict[str, Any]]:
        """Find transformers connected to substation"""
        transformers = []
        
        if hasattr(self.net, 'trafo'):
            for i, trafo_idx in enumerate(self.net.trafo.index):
                hv_bus = int(self.net.trafo.iloc[i]['hv_bus'])
                lv_bus = int(self.net.trafo.iloc[i]['lv_bus'])
                
                # Transformer connected if either side is in substation
                if hv_bus in bus_list or lv_bus in bus_list:
                    trafo_info = {
                        'index': int(trafo_idx),
                        'hv_bus': hv_bus,
                        'lv_bus': lv_bus,
                        'sn_mva': float(self.net.trafo.iloc[i]['sn_mva']) if 'sn_mva' in self.net.trafo.columns else 0.0,
                        'in_service': bool(self.net.trafo.iloc[i]['in_service']),
                        'name': str(self.net.trafo.iloc[i]['name']) if 'name' in self.net.trafo.columns else f"Trafo {trafo_idx}",
                        'transformer_type': self._classify_transformer_type(float(self.net.trafo.iloc[i]['sn_mva']) if 'sn_mva' in self.net.trafo.columns else 0.0)
                    }
                    
                    # Add loading information if available
                    if hasattr(self.net, 'res_trafo') and i < len(self.net.res_trafo):
                        trafo_info['loading_percent'] = float(self.net.res_trafo.iloc[i]['loading_percent'])
                        trafo_info['p_hv_mw'] = float(self.net.res_trafo.iloc[i]['p_hv_mw'])
                        trafo_info['p_lv_mw'] = float(self.net.res_trafo.iloc[i]['p_lv_mw'])
                        
                    transformers.append(trafo_info)
                    
        return transformers
    
    def _classify_transformer_type(self, sn_mva: float) -> str:
        """Classify transformer type based on rating"""
        if sn_mva > 500:
            return 'grid_transformer'
        elif sn_mva > 100:
            return 'bulk_transformer'  
        elif sn_mva > 50:
            return 'distribution_transformer'
        else:
            return 'small_transformer'
    
    def _find_substation_switches(self, bus_list: List[int]) -> List[Dict[str, Any]]:
        """Find switches within substation"""
        switches = []
        
        if hasattr(self.net, 'switch'):
            for i, switch_idx in enumerate(self.net.switch.index):
                switch_bus = int(self.net.switch.iloc[i]['bus'])
                
                if switch_bus in bus_list:
                    switch_info = {
                        'index': int(switch_idx),
                        'bus': switch_bus,
                        'element': int(self.net.switch.iloc[i]['element']),
                        'et': str(self.net.switch.iloc[i]['et']),
                        'closed': bool(self.net.switch.iloc[i]['closed']),
                        'name': str(self.net.switch.iloc[i]['name']) if 'name' in self.net.switch.columns else f"Switch {switch_idx}",
                        'switch_type': self._classify_switch_type(str(self.net.switch.iloc[i]['et']))
                    }
                    switches.append(switch_info)
                    
        return switches
    
    def _classify_switch_type(self, et: str) -> str:
        """Classify switch type"""
        switch_types = {
            'l': 'line_switch',
            'b': 'bus_switch', 
            't': 'trafo_switch',
            'g': 'generator_switch'
        }
        return switch_types.get(et, 'circuit_breaker')
    
    def _calculate_substation_voltage_profile(self, bus_list: List[int]) -> Dict[str, Any]:
        """Calculate voltage profile statistics for substation"""
        voltages = []
        estimated_voltages = []
        
        if hasattr(self.net, 'res_bus'):
            for bus_idx in bus_list:
                try:
                    if bus_idx in self.net.bus.index:
                        bus_positions = list(self.net.bus.index)
                        if bus_idx in bus_positions:
                            i = bus_positions.index(bus_idx)
                            if i < len(self.net.res_bus):
                                voltage = self.net.res_bus.iloc[i]['vm_pu']
                                voltages.append(float(voltage))
                                
                            if hasattr(self.net, 'res_bus_est') and i < len(self.net.res_bus_est):
                                est_voltage = self.net.res_bus_est.iloc[i]['vm_pu']
                                estimated_voltages.append(float(est_voltage))
                except (IndexError, KeyError):
                    continue
                    
        voltage_profile = {
            'min_voltage': 0, 'max_voltage': 0, 'avg_voltage': 0, 
            'std_voltage': 0, 'voltage_violations': 0,
            'estimation_available': len(estimated_voltages) > 0
        }
        
        if voltages:
            voltage_profile.update({
                'min_voltage': float(np.min(voltages)),
                'max_voltage': float(np.max(voltages)), 
                'avg_voltage': float(np.mean(voltages)),
                'std_voltage': float(np.std(voltages)),
                'voltage_violations': len([v for v in voltages if v < 0.95 or v > 1.05])
            })
            
        if estimated_voltages:
            voltage_profile.update({
                'est_min_voltage': float(np.min(estimated_voltages)),
                'est_max_voltage': float(np.max(estimated_voltages)),
                'est_avg_voltage': float(np.mean(estimated_voltages)),
                'est_std_voltage': float(np.std(estimated_voltages))
            })
            
        return voltage_profile
    
    def _calculate_substation_power_balance(self, bus_list: List[int]) -> Dict[str, Any]:
        """Calculate power balance for substation"""
        power_balance = {
            'generation_p_mw': 0.0, 'generation_q_mvar': 0.0,
            'load_p_mw': 0.0, 'load_q_mvar': 0.0,
            'net_export_p_mw': 0.0, 'net_export_q_mvar': 0.0,
            'largest_generator_mw': 0.0, 'largest_load_mw': 0.0
        }
        
        # Sum generation
        if hasattr(self.net, 'gen') and hasattr(self.net, 'res_gen'):
            for i, gen_idx in enumerate(self.net.gen.index):
                gen_bus = int(self.net.gen.iloc[i]['bus'])
                if gen_bus in bus_list and i < len(self.net.res_gen):
                    gen_p = float(self.net.res_gen.iloc[i]['p_mw'])
                    gen_q = float(self.net.res_gen.iloc[i]['q_mvar'])
                    power_balance['generation_p_mw'] += gen_p
                    power_balance['generation_q_mvar'] += gen_q
                    power_balance['largest_generator_mw'] = max(power_balance['largest_generator_mw'], gen_p)
                    
        # Sum loads
        if hasattr(self.net, 'load'):
            for i, load_idx in enumerate(self.net.load.index):
                load_bus = int(self.net.load.iloc[i]['bus'])
                if load_bus in bus_list:
                    load_p = float(self.net.load.iloc[i]['p_mw'])
                    load_q = float(self.net.load.iloc[i]['q_mvar'])
                    power_balance['load_p_mw'] += load_p
                    power_balance['load_q_mvar'] += load_q
                    power_balance['largest_load_mw'] = max(power_balance['largest_load_mw'], load_p)
                    
        # Calculate net export
        power_balance['net_export_p_mw'] = power_balance['generation_p_mw'] - power_balance['load_p_mw']
        power_balance['net_export_q_mvar'] = power_balance['generation_q_mvar'] - power_balance['load_q_mvar']
        
        # Calculate power factor and utilization
        total_apparent = np.sqrt(power_balance['generation_p_mw']**2 + power_balance['generation_q_mvar']**2)
        power_balance['power_factor'] = power_balance['generation_p_mw'] / total_apparent if total_apparent > 0 else 1.0
        power_balance['load_factor'] = power_balance['load_p_mw'] / power_balance['generation_p_mw'] if power_balance['generation_p_mw'] > 0 else 0.0
        
        return power_balance
    
    def _assess_substation_reliability(self, bus_list: List[int]) -> Dict[str, Any]:
        """Assess reliability metrics for substation"""
        reliability = {
            'redundant_lines': 0, 'single_fed_buses': 0, 'backup_transformers': 0,
            'switch_count': 0, 'reliability_score': 0.0, 'critical_elements': [],
            'contingency_rating': 'unknown'
        }
        
        # Count line connections per bus
        line_connections = {bus: 0 for bus in bus_list}
        
        if hasattr(self.net, 'line'):
            for i, line_idx in enumerate(self.net.line.index):
                from_bus = int(self.net.line.iloc[i]['from_bus'])
                to_bus = int(self.net.line.iloc[i]['to_bus'])
                
                if from_bus in bus_list:
                    line_connections[from_bus] += 1
                if to_bus in bus_list:
                    line_connections[to_bus] += 1
                    
        # Analyze redundancy
        reliability['redundant_lines'] = sum(1 for count in line_connections.values() if count > 1)
        reliability['single_fed_buses'] = sum(1 for count in line_connections.values() if count == 1)
        
        # Identify critical elements
        for bus, connections in line_connections.items():
            if connections <= 1:
                reliability['critical_elements'].append(f"Bus {bus} (single connection)")
        
        # Count transformers (backup capability)
        if hasattr(self.net, 'trafo'):
            for i, trafo_idx in enumerate(self.net.trafo.index):
                hv_bus = int(self.net.trafo.iloc[i]['hv_bus'])
                lv_bus = int(self.net.trafo.iloc[i]['lv_bus'])
                if hv_bus in bus_list or lv_bus in bus_list:
                    reliability['backup_transformers'] += 1
                    
        # Count switches (operational flexibility)
        if hasattr(self.net, 'switch'):
            for i, switch_idx in enumerate(self.net.switch.index):
                switch_bus = int(self.net.switch.iloc[i]['bus'])
                if switch_bus in bus_list:
                    reliability['switch_count'] += 1
                    
        # Calculate reliability score (0-1)
        total_buses = len(bus_list)
        if total_buses > 0:
            redundancy_factor = reliability['redundant_lines'] / total_buses
            switch_factor = min(reliability['switch_count'] / (total_buses * 2), 1.0)
            transformer_factor = min(reliability['backup_transformers'] / max(1, total_buses // 2), 1.0)
            
            reliability['reliability_score'] = (redundancy_factor + switch_factor + transformer_factor) / 3.0
            
        # Determine contingency rating
        if reliability['reliability_score'] > 0.8:
            reliability['contingency_rating'] = 'high'
        elif reliability['reliability_score'] > 0.5:
            reliability['contingency_rating'] = 'medium'
        else:
            reliability['contingency_rating'] = 'low'
            
        return reliability
    
    def _determine_operational_status(self, analysis: Dict[str, Any]) -> str:
        """Determine overall operational status of substation"""
        voltage_profile = analysis['voltage_profile']
        power_balance = analysis['power_balance']
        reliability = analysis['reliability']
        
        # Check for critical issues
        if voltage_profile.get('voltage_violations', 0) > 0:
            return 'voltage_violation'
        
        if reliability.get('contingency_rating') == 'low':
            return 'reliability_concern'
            
        # Check for warnings
        if abs(power_balance.get('net_export_p_mw', 0)) > 500:
            return 'high_transfer'
            
        if voltage_profile.get('std_voltage', 0) > 0.05:
            return 'voltage_variation'
            
        return 'normal'
    
    def _analyze_substation_topology(self, substations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze overall substation topology and interconnections"""
        topology = {
            'substation_count': len(substations),
            'interconnections': [],
            'voltage_levels': set(),
            'critical_substations': [],
            'isolation_groups': [],
            'system_strength': 'unknown'
        }
        
        # Analyze voltage levels
        for substation in substations:
            topology['voltage_levels'].add(substation['voltage'])
            
        # Find interconnections between substations
        if hasattr(self.net, 'line'):
            for i, line_idx in enumerate(self.net.line.index):
                from_bus = int(self.net.line.iloc[i]['from_bus'])
                to_bus = int(self.net.line.iloc[i]['to_bus'])
                
                from_sub = self._find_bus_substation(from_bus, substations)
                to_sub = self._find_bus_substation(to_bus, substations)
                
                if from_sub and to_sub and from_sub != to_sub:
                    connection = {
                        'from_substation': from_sub['id'],
                        'to_substation': to_sub['id'],
                        'line_index': int(line_idx),
                        'voltage_from': from_sub['voltage'],
                        'voltage_to': to_sub['voltage'],
                        'in_service': bool(self.net.line.iloc[i]['in_service']),
                        'connection_type': 'same_voltage' if from_sub['voltage'] == to_sub['voltage'] else 'different_voltage'
                    }
                    topology['interconnections'].append(connection)
        
        # Identify critical substations (highly connected)
        connection_counts = {}
        for connection in topology['interconnections']:
            for sub_id in [connection['from_substation'], connection['to_substation']]:
                connection_counts[sub_id] = connection_counts.get(sub_id, 0) + 1
                
        # Substations with many connections are critical
        avg_connections = np.mean(list(connection_counts.values())) if connection_counts else 0
        for sub_id, count in connection_counts.items():
            if count > avg_connections * 1.5:
                topology['critical_substations'].append(sub_id)
        
        # Assess system strength
        total_connections = len(topology['interconnections'])
        total_substations = len(substations)
        if total_substations > 1:
            connectivity_ratio = total_connections / (total_substations - 1)
            if connectivity_ratio > 1.5:
                topology['system_strength'] = 'high'
            elif connectivity_ratio > 1.0:
                topology['system_strength'] = 'medium'
            else:
                topology['system_strength'] = 'low'
        
        topology['voltage_levels'] = list(topology['voltage_levels'])
        return topology
    
    def _find_bus_substation(self, bus_idx: int, substations: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find which substation contains a specific bus"""
        for substation in substations:
            if bus_idx in substation['buses']:
                return substation
        return None
    
    def _generate_system_summary(self, substations: List[Dict[str, Any]], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level system summary"""
        total_generation = sum(
            sub_analysis['power_balance']['generation_p_mw'] 
            for sub_analysis in analysis.values()
        )
        
        total_load = sum(
            sub_analysis['power_balance']['load_p_mw'] 
            for sub_analysis in analysis.values()
        )
        
        avg_reliability = np.mean([
            sub_analysis['reliability']['reliability_score'] 
            for sub_analysis in analysis.values()
        ]) if analysis else 0
        
        voltage_violations = sum(
            sub_analysis['voltage_profile']['voltage_violations'] 
            for sub_analysis in analysis.values()
        )
        
        return {
            'total_substations': len(substations),
            'total_generation_mw': total_generation,
            'total_load_mw': total_load,
            'system_balance_mw': total_generation - total_load,
            'average_reliability_score': avg_reliability,
            'total_voltage_violations': voltage_violations,
            'system_status': 'healthy' if voltage_violations == 0 and avg_reliability > 0.7 else 'attention_needed',
            'generation_adequacy': 'adequate' if total_generation > total_load * 1.1 else 'tight'
        }

# Add the substation analysis capability to GridStateEstimator
def add_substation_analysis_to_estimator():
    """Add substation analysis methods to GridStateEstimator"""
    from grid_state_estimator import GridStateEstimator
    
    def get_substation_analysis(self):
        """Get comprehensive substation analysis"""
        analyzer = SubstationAnalyzer(self)
        return analyzer.get_substation_analysis()
    
    # Add the method to GridStateEstimator
    GridStateEstimator.get_substation_analysis = get_substation_analysis

# Automatically add the capability when this module is imported
add_substation_analysis_to_estimator()