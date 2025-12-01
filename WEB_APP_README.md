# Power System State Estimation Web Application

🌐 **Advanced Grid Analysis and Visualization Platform**

This web application provides an intuitive browser-based interface for power system state estimation, bad data detection, and grid analysis using the comprehensive GridStateEstimator toolkit.

## 🚀 Quick Start

### Option 1: Python Launcher (Recommended)
```bash
python run_web_app.py
```

### Option 2: Shell Script (Unix/Linux/macOS)
```bash
./launch_web.sh
```

### Option 3: Batch File (Windows)
```bash
launch_web.bat
```

### Option 4: Manual Flask Launch
```bash
export FLASK_APP=web_ui.web_app
flask run --host=127.0.0.1 --port=8000 --debug
```

## 🎯 Features

### 🏗️ **Grid Creation & Setup**
- **IEEE 9-Bus System**: Standard test system for validation
- **ENTSO-E Grid**: Realistic transmission system model
- **Quick Demo**: Instant setup with pre-configured analysis

### 📊 **Measurement Management**
- **Generate Measurements**: Simulate realistic sensor data with configurable noise
- **List Measurements**: View all current measurements with details
- **Modify Bus Voltages**: Interactive voltage measurement adjustment
- **Measurement Preview**: Real-time display of active measurements

### ⚡ **Advanced Analysis**
- **State Estimation**: Weighted least squares state estimation
- **Observability Analysis**: Comprehensive network observability assessment
- **Consistency Checking**: Measurement validation and error detection
- **Bad Data Detection**: Statistical outlier identification and removal

### 🔧 **Switch Control**
- **Interactive Switch Operations**: Open/close/toggle individual switches
- **Switch Status Display**: Real-time switch state visualization
- **Topology Validation**: Automatic power flow verification

### 📈 **Results & Visualization**
- **Measurement Comparison**: True vs Measured vs Estimated values
- **Grid Visualization**: Interactive network diagrams with color-coded results
- **Real-time Logs**: Comprehensive operation logging and status updates
- **Status Indicators**: Observability, consistency, and bad data status

## 🖥️ **Web Interface**

### **Main Dashboard**
The web interface provides a comprehensive dashboard with:

1. **Grid Information Panel**
   - Current grid type and statistics
   - Bus, line, generator, and load counts
   - Active measurement summary

2. **Control Panels**
   - Grid creation and configuration
   - Measurement generation and modification
   - Analysis execution controls

3. **Results Display**
   - Measurement comparison table
   - Grid visualization plot
   - Switch control interface

4. **Real-time Logging**
   - Operation logs and status updates
   - Analysis results and warnings
   - Performance metrics

### **Responsive Design**
- Mobile-friendly interface
- Automatic plot scaling
- Real-time updates without page refresh

## 🔧 **Configuration Options**

### **Command Line Arguments**
```bash
python run_web_app.py --help

Options:
  --host HOST         Host to bind to (default: 127.0.0.1)
  --port PORT         Port to bind to (default: 8000)
  --no-browser        Don't automatically open web browser
  --check-only        Only check dependencies and exit
```

### **Examples**
```bash
# Default local access
python run_web_app.py

# Custom port
python run_web_app.py --port 5000

# Network access (all interfaces)
python run_web_app.py --host 0.0.0.0

# No auto-browser opening
python run_web_app.py --no-browser

# Dependency check only
python run_web_app.py --check-only
```

## 📋 **Prerequisites**

### **Required Dependencies**
- Python 3.7+
- Flask ≥ 2.3.0
- pandapower ≥ 2.13.0
- numpy ≥ 1.21.0
- pandas ≥ 1.3.0
- matplotlib ≥ 3.5.0
- scipy ≥ 1.7.0

### **Installation**
```bash
# Install all requirements
pip install -r requirements.txt

# Or install individual packages
pip install flask pandapower numpy pandas matplotlib scipy
```

## 🌐 **Accessing the Application**

### **Local Access**
- URL: `http://127.0.0.1:8000`
- Accessible only from the local machine
- Best for development and testing

### **Network Access**
```bash
python run_web_app.py --host 0.0.0.0
```
- URL: `http://[your-ip]:8000`
- Accessible from other devices on the network
- Useful for demonstrations and team collaboration

### **Browser Compatibility**
- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ⚠️ Internet Explorer (limited support)

## 🔄 **Typical Workflow**

### **1. Grid Setup**
1. Create a grid (IEEE 9-bus or ENTSO-E)
2. Generate measurements with desired noise level
3. Verify grid statistics and measurement count

### **2. Analysis Execution**
1. Run state estimation
2. Perform observability analysis
3. Check measurement consistency
4. Execute bad data detection if needed

### **3. Results Review**
1. Examine measurement comparison table
2. Review grid visualization
3. Check analysis status indicators
4. Review operation logs

### **4. Interactive Exploration**
1. Modify specific measurements
2. Operate switches to change topology
3. Re-run analyses to see impacts
4. Compare results across scenarios

## 🐛 **Troubleshooting**

### **Common Issues**

**Port Already in Use**
```bash
# Use different port
python run_web_app.py --port 8001
```

**Dependencies Missing**
```bash
# Install requirements
pip install -r requirements.txt
```

**Permission Denied (Unix/Linux)**
```bash
# Make script executable
chmod +x launch_web.sh
```

**Browser Doesn't Open Automatically**
```bash
# Open manually or disable auto-open
python run_web_app.py --no-browser
```

### **Debug Mode**
The application runs in debug mode by default, providing:
- Automatic reloading on code changes
- Detailed error messages
- Interactive debugger in browser

### **Logs and Monitoring**
- All operations are logged in the web interface
- Flask development server provides request logging
- Errors are displayed both in browser and console

## 🔒 **Security Notes**

### **Development vs Production**
- Current configuration is for **development only**
- Uses Flask development server (not for production)
- Debug mode enabled (should be disabled in production)
- No authentication or security measures

### **Network Security**
- Default configuration binds to localhost only
- Use `--host 0.0.0.0` only on trusted networks
- Consider firewall rules for network access

## 🎮 **Demo Scenarios**

### **Quick Demo**
Click "Quick Demo" to instantly:
1. Create IEEE 9-bus grid
2. Generate measurements with 2% noise
3. Run state estimation
4. Display results

### **Complete Analysis Workflow**
1. Create ENTSO-E grid
2. Generate measurements (1-5% noise)
3. Run observability analysis
4. Execute state estimation
5. Check consistency
6. Perform bad data detection
7. Review all results

### **Interactive Testing**
1. Create IEEE 9-bus grid
2. Generate clean measurements (0% noise)
3. Manually modify specific bus voltages
4. Run bad data detection
5. Observe detection results

## 📞 **Support**

### **Getting Help**
- Check console output for error details
- Review browser developer tools for JavaScript errors
- Verify all dependencies are properly installed
- Ensure Python and Flask versions are compatible

### **Feature Requests**
The web application leverages the full GridStateEstimator functionality. All core features are available through the web interface, with continuous enhancements being added.

---

🎯 **Ready to analyze power systems through your browser!**