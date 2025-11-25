#!/usr/bin/env python3
"""
CGMES interface for the grid state estimator
Provides ENTSO-E compliant model loading and conversion
"""

import os
import urllib.request
import tempfile
import zipfile
from grid_state_estimator import GridStateEstimator

class CGMESInterface:
    """Interface for loading CGMES/CIM models into state estimator"""
    
    def __init__(self):
        self.estimator = GridStateEstimator()
        self.cgmes_files = []
        
    def download_entso_example(self, save_dir=None):
        """Download ENTSO-E example CGMES files"""
        if save_dir is None:
            save_dir = tempfile.mkdtemp()
            
        print("Downloading ENTSO-E CGMES example...")
        
        # ENTSO-E provides example CGMES files for testing
        # For demonstration, we'll create a minimal synthetic example
        # In practice, you would download from ENTSO-E CGMES library
        
        example_files = self._create_minimal_cgmes_example(save_dir)
        
        print(f"CGMES example files created in: {save_dir}")
        return example_files
    
    def _create_minimal_cgmes_example(self, save_dir):
        """Create a minimal CGMES example for testing"""
        
        # Create Equipment Quipment (EQ) file
        eq_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:cim="http://iec.ch/TC57/CIM100#">

    <!-- Base Voltage -->
    <cim:BaseVoltage rdf:ID="BV_400">
        <cim:IdentifiedObject.name>400kV</cim:IdentifiedObject.name>
        <cim:BaseVoltage.nominalVoltage>400000</cim:BaseVoltage.nominalVoltage>
    </cim:BaseVoltage>

    <!-- Substation -->
    <cim:Substation rdf:ID="SUB_1">
        <cim:IdentifiedObject.name>Substation 1</cim:IdentifiedObject.name>
    </cim:Substation>

    <cim:Substation rdf:ID="SUB_2">
        <cim:IdentifiedObject.name>Substation 2</cim:IdentifiedObject.name>
    </cim:Substation>

    <!-- Voltage Levels -->
    <cim:VoltageLevel rdf:ID="VL_1">
        <cim:IdentifiedObject.name>VL 400kV Sub1</cim:IdentifiedObject.name>
        <cim:VoltageLevel.Substation rdf:resource="#SUB_1"/>
        <cim:VoltageLevel.BaseVoltage rdf:resource="#BV_400"/>
    </cim:VoltageLevel>

    <cim:VoltageLevel rdf:ID="VL_2">
        <cim:IdentifiedObject.name>VL 400kV Sub2</cim:IdentifiedObject.name>
        <cim:VoltageLevel.Substation rdf:resource="#SUB_2"/>
        <cim:VoltageLevel.BaseVoltage rdf:resource="#BV_400"/>
    </cim:VoltageLevel>

    <!-- Connectivity Nodes -->
    <cim:ConnectivityNode rdf:ID="CN_1">
        <cim:IdentifiedObject.name>Bus 1</cim:IdentifiedObject.name>
        <cim:ConnectivityNode.ConnectivityNodeContainer rdf:resource="#VL_1"/>
    </cim:ConnectivityNode>

    <cim:ConnectivityNode rdf:ID="CN_2">
        <cim:IdentifiedObject.name>Bus 2</cim:IdentifiedObject.name>
        <cim:ConnectivityNode.ConnectivityNodeContainer rdf:resource="#VL_2"/>
    </cim:ConnectivityNode>

    <!-- Transmission Line -->
    <cim:ACLineSegment rdf:ID="LINE_1_2">
        <cim:IdentifiedObject.name>Line 1-2</cim:IdentifiedObject.name>
        <cim:ConductingEquipment.BaseVoltage rdf:resource="#BV_400"/>
        <cim:ACLineSegment.r>10.0</cim:ACLineSegment.r>
        <cim:ACLineSegment.x>50.0</cim:ACLineSegment.x>
        <cim:ACLineSegment.bch>1e-6</cim:ACLineSegment.bch>
        <cim:ACLineSegment.length>100</cim:ACLineSegment.length>
    </cim:ACLineSegment>

    <!-- Generator -->
    <cim:SynchronousMachine rdf:ID="GEN_1">
        <cim:IdentifiedObject.name>Generator 1</cim:IdentifiedObject.name>
        <cim:ConductingEquipment.BaseVoltage rdf:resource="#BV_400"/>
        <cim:RotatingMachine.ratedS>100</cim:RotatingMachine.ratedS>
        <cim:SynchronousMachine.maxQ>50</cim:SynchronousMachine.maxQ>
        <cim:SynchronousMachine.minQ>-50</cim:SynchronousMachine.minQ>
    </cim:SynchronousMachine>

    <!-- Load -->
    <cim:EnergyConsumer rdf:ID="LOAD_2">
        <cim:IdentifiedObject.name>Load 2</cim:IdentifiedObject.name>
        <cim:ConductingEquipment.BaseVoltage rdf:resource="#BV_400"/>
        <cim:EnergyConsumer.pfixed>75</cim:EnergyConsumer.pfixed>
        <cim:EnergyConsumer.qfixed>25</cim:EnergyConsumer.qfixed>
    </cim:EnergyConsumer>

    <!-- Terminals -->
    <cim:Terminal rdf:ID="T_GEN_1">
        <cim:IdentifiedObject.name>Terminal Gen 1</cim:IdentifiedObject.name>
        <cim:Terminal.ConductingEquipment rdf:resource="#GEN_1"/>
        <cim:Terminal.ConnectivityNode rdf:resource="#CN_1"/>
        <cim:Terminal.sequenceNumber>1</cim:Terminal.sequenceNumber>
    </cim:Terminal>

    <cim:Terminal rdf:ID="T_LINE_1">
        <cim:IdentifiedObject.name>Terminal Line 1</cim:IdentifiedObject.name>
        <cim:Terminal.ConductingEquipment rdf:resource="#LINE_1_2"/>
        <cim:Terminal.ConnectivityNode rdf:resource="#CN_1"/>
        <cim:Terminal.sequenceNumber>1</cim:Terminal.sequenceNumber>
    </cim:Terminal>

    <cim:Terminal rdf:ID="T_LINE_2">
        <cim:IdentifiedObject.name>Terminal Line 2</cim:IdentifiedObject.name>
        <cim:Terminal.ConductingEquipment rdf:resource="#LINE_1_2"/>
        <cim:Terminal.ConnectivityNode rdf:resource="#CN_2"/>
        <cim:Terminal.sequenceNumber>2</cim:Terminal.sequenceNumber>
    </cim:Terminal>

    <cim:Terminal rdf:ID="T_LOAD_2">
        <cim:IdentifiedObject.name>Terminal Load 2</cim:IdentifiedObject.name>
        <cim:Terminal.ConductingEquipment rdf:resource="#LOAD_2"/>
        <cim:Terminal.ConnectivityNode rdf:resource="#CN_2"/>
        <cim:Terminal.sequenceNumber>1</cim:Terminal.sequenceNumber>
    </cim:Terminal>

</rdf:RDF>'''
        
        # Create State Variables (SV) file
        sv_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:cim="http://iec.ch/TC57/CIM100#">

    <!-- Topological Nodes -->
    <cim:TopologicalNode rdf:ID="TN_1">
        <cim:IdentifiedObject.name>Topological Node 1</cim:IdentifiedObject.name>
        <cim:TopologicalNode.BaseVoltage rdf:resource="EQ#BV_400"/>
        <cim:TopologicalNode.ConnectivityNodeContainer rdf:resource="EQ#VL_1"/>
    </cim:TopologicalNode>

    <cim:TopologicalNode rdf:ID="TN_2">
        <cim:IdentifiedObject.name>Topological Node 2</cim:IdentifiedObject.name>
        <cim:TopologicalNode.BaseVoltage rdf:resource="EQ#BV_400"/>
        <cim:TopologicalNode.ConnectivityNodeContainer rdf:resource="EQ#VL_2"/>
    </cim:TopologicalNode>

    <!-- State Variables -->
    <cim:SvVoltage rdf:ID="SV_V1">
        <cim:SvVoltage.TopologicalNode rdf:resource="#TN_1"/>
        <cim:SvVoltage.v>400000</cim:SvVoltage.v>
        <cim:SvVoltage.angle>0.0</cim:SvVoltage.angle>
    </cim:SvVoltage>

    <cim:SvVoltage rdf:ID="SV_V2">
        <cim:SvVoltage.TopologicalNode rdf:resource="#TN_2"/>
        <cim:SvVoltage.v>380000</cim:SvVoltage.v>
        <cim:SvVoltage.angle>-5.0</cim:SvVoltage.angle>
    </cim:SvVoltage>

    <cim:SvPowerFlow rdf:ID="SV_PF_GEN1">
        <cim:SvPowerFlow.Terminal rdf:resource="EQ#T_GEN_1"/>
        <cim:SvPowerFlow.p>80</cim:SvPowerFlow.p>
        <cim:SvPowerFlow.q>20</cim:SvPowerFlow.q>
    </cim:SvPowerFlow>

    <cim:SvPowerFlow rdf:ID="SV_PF_LOAD2">
        <cim:SvPowerFlow.Terminal rdf:resource="EQ#T_LOAD_2"/>
        <cim:SvPowerFlow.p>-75</cim:SvPowerFlow.p>
        <cim:SvPowerFlow.q>-25</cim:SvPowerFlow.q>
    </cim:SvPowerFlow>

</rdf:RDF>'''

        # Create Steady State Hypothesis (SSH) file
        ssh_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:cim="http://iec.ch/TC57/CIM100#">

    <!-- Generator Control -->
    <cim:SynchronousMachine rdf:about="EQ#GEN_1">
        <cim:RotatingMachine.p>80</cim:RotatingMachine.p>
        <cim:SynchronousMachine.referencePriority>1</cim:SynchronousMachine.referencePriority>
    </cim:SynchronousMachine>

    <!-- Load Control -->
    <cim:EnergyConsumer rdf:about="EQ#LOAD_2">
        <cim:EnergyConsumer.p>75</cim:EnergyConsumer.p>
        <cim:EnergyConsumer.q>25</cim:EnergyConsumer.q>
    </cim:EnergyConsumer>

    <!-- Topology -->
    <cim:Terminal rdf:about="EQ#T_GEN_1">
        <cim:Terminal.connected>true</cim:Terminal.connected>
    </cim:Terminal>

    <cim:Terminal rdf:about="EQ#T_LINE_1">
        <cim:Terminal.connected>true</cim:Terminal.connected>
    </cim:Terminal>

    <cim:Terminal rdf:about="EQ#T_LINE_2">
        <cim:Terminal.connected>true</cim:Terminal.connected>
    </cim:Terminal>

    <cim:Terminal rdf:about="EQ#T_LOAD_2">
        <cim:Terminal.connected>true</cim:Terminal.connected>
    </cim:Terminal>

</rdf:RDF>'''
        
        # Write files
        files = {}
        
        eq_file = os.path.join(save_dir, "example_EQ.xml")
        with open(eq_file, 'w') as f:
            f.write(eq_content)
        files['EQ'] = eq_file
        
        sv_file = os.path.join(save_dir, "example_SV.xml")
        with open(sv_file, 'w') as f:
            f.write(sv_content)
        files['SV'] = sv_file
        
        ssh_file = os.path.join(save_dir, "example_SSH.xml") 
        with open(ssh_file, 'w') as f:
            f.write(ssh_content)
        files['SSH'] = ssh_file
        
        print(f"Created minimal CGMES example files:")
        for profile, filepath in files.items():
            print(f"  {profile}: {filepath}")
        
        return list(files.values())
    
    def load_cgmes_model(self, cgmes_files):
        """Load CGMES model into state estimator"""
        success = self.estimator.load_cgmes_model(cgmes_files)
        if success:
            self.cgmes_files = cgmes_files if isinstance(cgmes_files, list) else [cgmes_files]
        return success
    
    def run_state_estimation_analysis(self, noise_level=0.02):
        """Run complete state estimation analysis on CGMES model"""
        if self.estimator.net is None:
            print("No model loaded. Load CGMES model first.")
            return False
        
        try:
            print(f"\n🔄 Running state estimation analysis on CGMES model...")
            
            # Simulate measurements
            print(f"📊 Simulating measurements (noise level: {noise_level*100:.1f}%)...")
            self.estimator.simulate_measurements(noise_level=noise_level)
            
            # Test observability
            print(f"🔍 Testing observability...")
            self.estimator.test_observability()
            
            # Run state estimation
            print(f"⚡ Running state estimation...")
            self.estimator.run_state_estimation()
            
            # Show results
            print(f"📈 Displaying results...")
            self.estimator.show_results()
            
            return True
            
        except Exception as e:
            print(f"Error in analysis: {e}")
            return False
    
    def export_to_cgmes(self, output_dir):
        """Export results back to CGMES format"""
        # This would require implementing CGMES export functionality
        # For now, we'll create a placeholder
        print(f"CGMES export functionality would save results to: {output_dir}")
        print("Note: Full CGMES export requires additional implementation")
        return False

def main():
    """Main function to test CGMES interface"""
    print("CGMES INTERFACE TEST")
    print("="*50)
    
    # Create CGMES interface
    cgmes_interface = CGMESInterface()
    
    # Download/create example CGMES files
    print("1. Creating CGMES example files...")
    cgmes_files = cgmes_interface.download_entso_example()
    
    # Test basic CGMES loading (this will likely fail without proper CIM support)
    print(f"\n2. Testing CGMES model loading...")
    success = cgmes_interface.load_cgmes_model(cgmes_files)
    
    if success:
        print("✅ CGMES model loaded successfully!")
        
        # Run state estimation analysis
        print(f"\n3. Running state estimation analysis...")
        cgmes_interface.run_state_estimation_analysis(noise_level=0.02)
        
    else:
        print("❌ CGMES loading failed - testing ENTSO-E style system")
        print("\nNote: Full CGMES support requires:")
        print("  - pandapower with CIM converter")
        print("  - Proper CGMES/CIM library installation")
        print("  - Valid ENTSO-E CGMES files")
        
        # Test ENTSO-E style transmission system
        print(f"\n3. Testing ENTSO-E style transmission system...")
        cgmes_interface.estimator.create_simple_entso_grid()
        cgmes_interface.run_state_estimation_analysis(noise_level=0.01)  # Lower noise for transmission system

if __name__ == "__main__":
    main()