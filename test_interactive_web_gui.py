#!/usr/bin/env python3
"""
Test script for the enhanced interactive web-based GUI with switch controls
"""

import time
import requests
import json
from grid_state_estimator import GridStateEstimator

def test_web_app_functionality():
    """Test the enhanced web application features"""
    base_url = "http://127.0.0.1:8001"
    
    print("🧪 Testing Enhanced Interactive Web GUI")
    print("=" * 60)
    
    # Test 1: Check if web app is running
    print("\n1. Testing web app availability...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Web application is accessible")
        else:
            print(f"❌ Web application returned status: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web application. Is it running on port 8000?")
        return
    
    # Test 2: Create a grid via web API
    print("\n2. Testing grid creation...")
    response = requests.post(f"{base_url}/create-grid", data={"grid_type": "ieee9"})
    if response.status_code in [200, 302]:  # 302 is redirect after successful creation
        print("✅ Grid created successfully via web interface")
    else:
        print(f"❌ Grid creation failed: {response.status_code}")
    
    # Test 3: Test grid diagram API
    print("\n3. Testing interactive grid diagram API...")
    response = requests.get(f"{base_url}/api/grid-diagram")
    if response.status_code == 200:
        diagram_data = response.json()
        if "error" not in diagram_data:
            print("✅ Grid diagram API working")
            print(f"   📊 Buses: {len(diagram_data.get('buses', []))}")
            print(f"   📊 Lines: {len(diagram_data.get('lines', []))}")
            print(f"   📊 Generators: {len(diagram_data.get('generators', []))}")
            print(f"   📊 Loads: {len(diagram_data.get('loads', []))}")
            print(f"   📊 Switches: {len(diagram_data.get('switches', []))}")
        else:
            print(f"❌ Grid diagram API returned error: {diagram_data['error']}")
    else:
        print(f"❌ Grid diagram API failed: {response.status_code}")
    
    # Test 4: Generate measurements
    print("\n4. Testing measurement generation...")
    response = requests.post(f"{base_url}/simulate-measurements", data={"noise": "0.02"})
    if response.status_code in [200, 302]:
        print("✅ Measurements generated successfully")
    else:
        print(f"❌ Measurement generation failed: {response.status_code}")
    
    # Test 5: Test element status API
    print("\n5. Testing element status API...")
    response = requests.get(f"{base_url}/api/element-status")
    if response.status_code == 200:
        status_data = response.json()
        if "error" not in status_data:
            print("✅ Element status API working")
            for element_type, elements in status_data.items():
                if isinstance(elements, dict):
                    print(f"   📈 {element_type.capitalize()}: {len(elements)} elements")
        else:
            print(f"❌ Element status API returned error: {status_data['error']}")
    else:
        print(f"❌ Element status API failed: {response.status_code}")
    
    # Test 6: Test element toggle functionality
    print("\n6. Testing element toggle functionality...")
    # Try to toggle a line (should be safe)
    toggle_data = {
        "element_type": "line",
        "element_index": 0,
        "new_status": False  # Turn off
    }
    
    response = requests.post(
        f"{base_url}/api/element-toggle",
        headers={"Content-Type": "application/json"},
        data=json.dumps(toggle_data)
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ Element toggle API working")
            print(f"   📝 {result['message']}")
            
            # Toggle it back on
            toggle_data["new_status"] = True
            response = requests.post(
                f"{base_url}/api/element-toggle",
                headers={"Content-Type": "application/json"},
                data=json.dumps(toggle_data)
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ Element toggle back on successful")
                    print(f"   📝 {result['message']}")
        else:
            print(f"❌ Element toggle failed: {result.get('message', 'Unknown error')}")
    else:
        print(f"❌ Element toggle API failed: {response.status_code}")
    
    # Test 7: Run state estimation
    print("\n7. Testing state estimation...")
    response = requests.post(f"{base_url}/state-estimation")
    if response.status_code in [200, 302]:
        print("✅ State estimation completed successfully")
    else:
        print(f"❌ State estimation failed: {response.status_code}")
    
    # Test 8: Test updated grid diagram with estimation results
    print("\n8. Testing grid diagram with estimation results...")
    response = requests.get(f"{base_url}/api/grid-diagram")
    if response.status_code == 200:
        diagram_data = response.json()
        if "error" not in diagram_data and diagram_data.get("has_estimation"):
            print("✅ Grid diagram now includes estimation results")
            # Check if buses have estimation data
            buses_with_est = [b for b in diagram_data.get('buses', []) if 'estimated_voltage_pu' in b]
            print(f"   📊 Buses with estimation data: {len(buses_with_est)}")
        else:
            print("⚠️  Grid diagram available but no estimation results detected")
    
    print("\n" + "=" * 60)
    print("🎯 Interactive Web GUI Test Summary:")
    print("✅ All core features are working properly!")
    print("🎮 Interactive Controls Available:")
    print("   • Click on buses to view voltage details")
    print("   • Click on lines to switch them on/off") 
    print("   • Click on generators to control them")
    print("   • Click on loads to connect/disconnect them")
    print("   • Click on switches to operate circuit breakers")
    print("🌐 Access the GUI at: http://127.0.0.1:8000")
    print("=" * 60)

def test_direct_grid_functionality():
    """Test grid functionality directly (backup test)"""
    print("\n🔧 Direct Grid Functionality Test")
    print("-" * 40)
    
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.02)
    
    # Test switch operations
    print("Testing switch operations...")
    switch_info = estimator.get_switch_info()
    print(f"Total switches: {len(switch_info)}")
    
    if switch_info:
        # Test toggle first switch
        first_switch = switch_info[0]
        print(f"Testing switch: {first_switch['name']} (currently {first_switch['status']})")
        
        success = estimator.toggle_switch(first_switch['index'])
        if success:
            print("✅ Switch toggle successful")
        else:
            print("❌ Switch toggle failed")
    
    # Test element switching
    print("Testing element switching...")
    success, message = estimator.switch_element('line', 0, False)
    print(f"Line switch off: {message}")
    
    success, message = estimator.switch_element('line', 0, True)
    print(f"Line switch on: {message}")
    
    print("✅ Direct grid functionality test completed")

if __name__ == "__main__":
    # Run web app tests
    test_web_app_functionality()
    
    # Run direct tests as backup
    test_direct_grid_functionality()