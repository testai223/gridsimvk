# Power System State Estimation Application

A Python application for power system state estimation using the pandapower library. This application demonstrates the complete workflow of state estimation in power systems, from grid modeling to results visualization.

## Features

- **IEEE 9-Bus Grid Model**: Creates standard IEEE 9-bus test system
- **Measurement Simulation**: Generates realistic voltage and power flow measurements with configurable noise levels
- **State Estimation**: Performs weighted least squares state estimation using pandapower
- **Observability Analysis**: Tests system observability and identifies critical measurements
- **Grid Visualization**: Interactive plots showing results directly on network schematic
- **Comprehensive Results**: Displays results in both tabular and graphical formats
- **Error Analysis**: Provides detailed statistical analysis of estimation accuracy
- **Noise-Free Mode**: Perfect measurements for algorithm validation and testing

## Requirements

- Python 3.7+
- pandapower
- numpy
- pandas
- matplotlib

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gridsimvk
```

2. Create and activate virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

**Quick setup script:**
```bash
# Use the provided activation script
./activate_venv.sh
```

## Usage

Activate the virtual environment and run the application:
```bash
# Activate virtual environment
source venv/bin/activate

# Run the application (interactive mode)
python grid_state_estimator.py

# Compare noise-free vs noisy measurements
python grid_state_estimator.py --compare

# Quick demo of different noise levels
python demo_modes.py
```

### Available Modes

1. **Perfect Measurements (No Noise)**: `noise_level = 0.0`
   - Measurements exactly match load flow results
   - Demonstrates ideal state estimation scenario
   - Shows numerical precision limits

2. **Noisy Measurements**: `noise_level > 0.0` 
   - Adds Gaussian noise to all measurements
   - Default: 2% noise level
   - Demonstrates state estimation noise filtering

3. **Interactive Mode**: Choose between perfect, noisy, or custom noise levels

### Command Line Options

```bash
# Interactive mode with noise selection
python grid_state_estimator.py

# Automatic comparison of both modes  
python grid_state_estimator.py --compare

# Quick demonstration
python demo_modes.py

# Test observability with different measurement scenarios
python test_observability.py

# Demo grid visualization features
python demo_grid_plots.py
```

The application will:
1. Create an IEEE 9-bus power system model
2. Generate 45 measurements with configurable noise level
3. Perform observability analysis
4. Run state estimation  
5. Display comprehensive results including:
   - Observability assessment and critical measurement analysis
   - Bus voltage magnitudes and angles comparison
   - Line power flows (active and reactive)  
   - Measurement comparison tables (Load Flow vs Measured vs Estimated)
   - Grid visualization with network schematic showing:
     - Color-coded voltage magnitudes across the network
     - Estimation error distribution (red/blue heat map)
     - Power flow directions and magnitudes with arrows
     - Measurement sensor locations and coverage
   - Statistical performance metrics and error analysis

## Application Structure

### GridStateEstimator Class

- `create_ieee9_grid()`: Creates the IEEE 9-bus test system with buses, lines, generators, and loads
- `simulate_measurements(noise_level)`: Generates measurements with configurable noise (0.0 = perfect, >0.0 = noisy)
- `test_observability()`: Analyzes system observability, measurement redundancy, and critical measurements
- `run_state_estimation()`: Performs weighted least squares state estimation
- `show_results()`: Displays comprehensive results in tabular and graphical formats
- `plot_grid_results()`: Creates interactive grid visualizations showing results on network schematic

### Observability Analysis

The application performs comprehensive observability testing:

- **Measurement Redundancy**: Ratio of measurements to state variables
- **Coverage Analysis**: Percentage of buses with direct or indirect measurements  
- **Critical Measurement Detection**: Identifies single points of failure
- **Measurement Distribution**: Analyzes voltage vs power flow measurement balance
- **Network Connectivity**: Ensures adequate measurement distribution across the network

### Grid Model Details

- **Buses**: 9 buses at 138 kV voltage level
- **Lines**: 9 transmission lines connecting the buses
- **Generators**: 3 generators at buses 1, 2, and 3
- **Loads**: 3 loads at buses 5, 6, and 8
- **Measurements**: Voltage magnitudes at all buses + active/reactive power flows at all line terminals

## Results

The application provides:

### Tabular Results
- Bus voltage magnitudes (true vs estimated)
- Bus voltage angles (true vs estimated) 
- Line power flows (MW and MVAr)
- Complete measurements summary
- Statistical error analysis

### Graphical Results
- **Standard Plots**: Voltage magnitude/angle comparisons and error distributions
- **Grid Visualization**: Four interactive plots on network schematic:
  1. **Voltage Magnitudes**: Color-coded buses showing estimated voltage levels
  2. **Estimation Errors**: Red/blue heat map showing over/under estimation
  3. **Power Flows**: Directional arrows showing MW flows on transmission lines
  4. **Measurement Coverage**: Sensor locations with coverage indicators

### Typical Performance
- **Perfect Measurements**: 0% error (noise_level = 0.0)
- **Noisy Measurements**: ~0.5% estimation error with 2% measurement noise
- **Observability**: Fully observable with 45 measurements vs 17 states (2.6x redundancy)
- **Convergence**: 4-5 iterations for weighted least squares

## Customization

You can modify the application by:

- Changing noise level in `simulate_measurements(noise_level=0.02)`
- Adding different grid models in `create_ieee9_grid()`
- Modifying measurement types and locations
- Adjusting estimation algorithm parameters

## Dependencies

- `pandapower>=2.13.0`: Power system modeling and state estimation
- `numpy>=1.21.0`: Numerical computations
- `pandas>=1.3.0`: Data manipulation and analysis
- `matplotlib>=3.5.0`: Plotting and visualization
- `scipy>=1.7.0`: Scientific computing (pandapower dependency)

## License

This project is provided as-is for educational and research purposes.