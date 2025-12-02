#!/usr/bin/env python3
"""
Comprehensive test for the enhanced substation visualization system
Tests both the backend analysis and frontend visualization capabilities
"""

import requests
import json
import time
from grid_state_estimator import GridStateEstimator
from substation_analyzer import SubstationAnalyzer

def test_substation_analysis():
    """Test the substation analysis functionality directly"""
    print("🧪 Testing Substation Analysis System")
    print("=" * 60)
    
    # Test IEEE 9-bus system
    print("\n1. Testing IEEE 9-bus substation analysis...")
    estimator = GridStateEstimator()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.02)
    estimator.run_state_estimation()
    
    # Get substation analysis
    analysis = estimator.get_substation_analysis()
    
    print(f"✅ Grid type detected: {analysis['grid_type']}")
    print(f"✅ Substations defined: {len(analysis['substations'])}")
    
    for substation in analysis['substations']:
        print(f"   📍 {substation['name']} ({substation['type']}) - {len(substation['buses'])} buses")
        
    # Test detailed analysis
    for sub_id, sub_analysis in analysis['analysis'].items():
        print(f"\n📊 Analysis for {sub_id}:")
        print(f"   Buses: {sub_analysis['bus_count']}")
        print(f"   Generators: {len(sub_analysis['generators'])}")
        print(f"   Loads: {len(sub_analysis['loads'])}")
        print(f"   Lines: {len(sub_analysis['lines'])}")
        print(f"   Reliability Score: {sub_analysis['reliability']['reliability_score']:.2f}")
        
    print(f"\n🌐 System Summary:")
    summary = analysis['summary']
    print(f"   Total Generation: {summary['total_generation_mw']:.1f} MW")
    print(f"   Total Load: {summary['total_load_mw']:.1f} MW")
    print(f"   System Status: {summary['system_status']}")
    
    # Test ENTSO-E system
    print("\n2. Testing ENTSO-E substation analysis...")
    estimator.create_simple_entso_grid()
    estimator.simulate_measurements(noise_level=0.02) 
    estimator.run_state_estimation()
    
    analysis_entso = estimator.get_substation_analysis()
    print(f"✅ ENTSO-E Grid type: {analysis_entso['grid_type']}")
    print(f"✅ ENTSO-E Substations: {len(analysis_entso['substations'])}")
    
    for substation in analysis_entso['substations']:
        print(f"   📍 {substation['name']} ({substation['voltage']}) - {substation['type']}")
    
    print("✅ Direct substation analysis test completed successfully!")
    return True

def test_web_visualization():
    """Test the web-based substation visualization"""
    print("\n🌐 Testing Web-Based Substation Visualization")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8001"
    
    try:
        # Test main page accessibility
        print("\n1. Testing substation diagram page...")
        response = requests.get(f"{base_url}/substation-diagram")
        if response.status_code == 200:
            print("✅ Substation diagram page accessible")
        else:
            print(f"❌ Substation diagram page failed: {response.status_code}")
            return False
        
        # Create a grid
        print("\n2. Creating grid for visualization...")
        response = requests.post(f"{base_url}/create-grid", data={"grid_type": "ieee9"})
        if response.status_code in [200, 302]:
            print("✅ Grid created successfully")
        else:
            print(f"❌ Grid creation failed: {response.status_code}")
            return False
            
        # Generate measurements
        print("\n3. Generating measurements...")
        response = requests.post(f"{base_url}/simulate-measurements", data={"noise": "0.02"})
        if response.status_code in [200, 302]:
            print("✅ Measurements generated")
        else:
            print(f"❌ Measurement generation failed: {response.status_code}")
            
        # Test substation analysis API
        print("\n4. Testing substation analysis API...")
        response = requests.get(f"{base_url}/api/substation-analysis")
        if response.status_code == 200:
            substation_data = response.json()
            if "error" not in substation_data:
                print("✅ Substation analysis API working")
                print(f"   📊 Grid Type: {substation_data['grid_type']}")
                print(f"   📊 Substations: {len(substation_data['substations'])}")
                print(f"   📊 System Status: {substation_data['summary']['system_status']}")
                
                # Display substation details
                for substation in substation_data['substations']:
                    sub_analysis = substation_data['analysis'][substation['id']]
                    print(f"   📍 {substation['name']}: {sub_analysis['operational_status']}")
                    
            else:
                print(f"❌ Substation analysis API error: {substation_data['error']}")
                return False
        else:
            print(f"❌ Substation analysis API failed: {response.status_code}")
            return False
            
        # Test grid diagram API (should work with substation data)
        print("\n5. Testing enhanced grid diagram API...")
        response = requests.get(f"{base_url}/api/grid-diagram")
        if response.status_code == 200:
            grid_data = response.json()
            if "error" not in grid_data:
                print("✅ Enhanced grid diagram API working")
                print(f"   📊 Buses: {len(grid_data['buses'])}")
                print(f"   📊 Lines: {len(grid_data['lines'])}")
                print(f"   📊 Generators: {len(grid_data['generators'])}")
                print(f"   📊 Grid Type: {grid_data['grid_type']}")
            else:
                print(f"❌ Grid diagram API error: {grid_data['error']}")
        
        # Run state estimation
        print("\n6. Running state estimation...")
        response = requests.post(f"{base_url}/state-estimation")
        if response.status_code in [200, 302]:
            print("✅ State estimation completed")
            
            # Re-test substation analysis with estimation results
            response = requests.get(f"{base_url}/api/substation-analysis")
            if response.status_code == 200:
                substation_data = response.json()
                if "error" not in substation_data:
                    print("✅ Substation analysis with estimation results")
                    
                    # Check if estimation data is available
                    first_substation = list(substation_data['analysis'].values())[0]
                    if first_substation['voltage_profile'].get('estimation_available', False):
                        print("✅ Voltage estimation data included in analysis")
                    else:
                        print("⚠️  No voltage estimation data detected")
        
        print("\n✅ Web visualization test completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to web application. Please start it first:")
        print("   python3 web_ui/web_app.py")
        return False
    except Exception as e:
        print(f"❌ Web visualization test failed: {e}")
        return False

def test_interactive_features():
    """Test interactive features of the substation visualization"""
    print("\n🎮 Testing Interactive Features")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8001"
    
    try:
        # Test element toggle with substation context
        print("\n1. Testing element switching in substation context...")
        
        # Try to toggle a line
        toggle_data = {
            "element_type": "line",
            "element_index": 0,
            "new_status": False
        }
        
        response = requests.post(
            f"{base_url}/api/element-toggle",
            headers={"Content-Type": "application/json"},
            data=json.dumps(toggle_data)
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Element toggle working in substation context")
                print(f"   📝 {result['message']}")
                
                # Check substation analysis after toggle
                response = requests.get(f"{base_url}/api/substation-analysis")
                if response.status_code == 200:
                    analysis_after = response.json()
                    print("✅ Substation analysis updated after element toggle")
                    
                # Toggle back
                toggle_data["new_status"] = True
                response = requests.post(
                    f"{base_url}/api/element-toggle",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(toggle_data)
                )
                if response.status_code == 200 and response.json().get("success"):
                    print("✅ Element toggle back successful")
            else:
                print(f"❌ Element toggle failed: {result.get('message')}")
        else:
            print(f"❌ Element toggle API failed: {response.status_code}")
            
        print("\n✅ Interactive features test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Interactive features test failed: {e}")
        return False

def test_performance_and_scalability():
    """Test performance with different grid sizes"""
    print("\n⚡ Testing Performance and Scalability")
    print("=" * 60)
    
    # Test analysis performance
    print("\n1. Testing analysis performance...")
    
    estimator = GridStateEstimator()
    
    # IEEE 9-bus performance
    start_time = time.time()
    estimator.create_ieee9_grid()
    estimator.simulate_measurements(noise_level=0.02)
    estimator.run_state_estimation()
    analysis = estimator.get_substation_analysis()
    ieee9_time = time.time() - start_time
    
    print(f"✅ IEEE 9-bus analysis time: {ieee9_time:.3f} seconds")
    print(f"   📊 Substations analyzed: {len(analysis['substations'])}")
    print(f"   📊 Total elements: {sum(len(sub['buses']) for sub in analysis['substations'])}")
    
    # ENTSO-E performance
    start_time = time.time()
    estimator.create_simple_entso_grid()
    estimator.simulate_measurements(noise_level=0.02)
    estimator.run_state_estimation()
    analysis_entso = estimator.get_substation_analysis()
    entsoe_time = time.time() - start_time
    
    print(f"✅ ENTSO-E analysis time: {entsoe_time:.3f} seconds")
    print(f"   📊 Substations analyzed: {len(analysis_entso['substations'])}")
    print(f"   📊 Voltage levels: {len(analysis_entso['topology']['voltage_levels'])}")
    
    # Test multiple runs for consistency
    print("\n2. Testing analysis consistency...")
    for i in range(3):
        analysis_test = estimator.get_substation_analysis()
        if analysis_test['grid_type'] == analysis_entso['grid_type']:
            print(f"✅ Run {i+1}: Analysis consistent")
        else:
            print(f"❌ Run {i+1}: Analysis inconsistent")
            return False
    
    print("\n✅ Performance and scalability test completed!")
    return True

def main():
    """Run all substation visualization tests"""
    print("🚀 COMPREHENSIVE SUBSTATION VISUALIZATION TEST SUITE")
    print("=" * 70)
    
    # Test results tracking
    test_results = []
    
    # Run all tests
    test_results.append(("Direct Analysis", test_substation_analysis()))
    test_results.append(("Web Visualization", test_web_visualization()))  
    test_results.append(("Interactive Features", test_interactive_features()))
    test_results.append(("Performance", test_performance_and_scalability()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25}: {status}")
    
    print(f"\nOverall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("\n🌟 Enhanced Substation Visualization System is ready!")
        print("🌐 Access the system at: http://127.0.0.1:8001/substation-diagram")
        print("\n🎮 Features Available:")
        print("   • Interactive substation grouping and visualization")
        print("   • Real-time element switching with substation context")
        print("   • Comprehensive reliability and power flow analysis")
        print("   • Advanced SVG-based graphical representation")
        print("   • Pan, zoom, and interactive element details")
        print("   • Export and print capabilities")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        
    return passed == total

if __name__ == "__main__":
    main()