# Power System State Estimation Application

A Python application for power system state estimation using the pandapower library. This application demonstrates the complete workflow of state estimation in power systems, from grid modeling to results visualization.

## Features

- **IEEE 9-Bus Grid Model**: Creates standard IEEE 9-bus test system
- **Measurement Simulation**: Generates realistic voltage and power flow measurements with configurable noise levels
- **State Estimation**: Performs weighted least squares state estimation using pandapower
- **Comprehensive Results**: Displays results in both tabular and graphical formats
- **Error Analysis**: Provides detailed statistical analysis of estimation accuracy

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

# Run the application
python grid_state_estimator.py
```

The application will:
1. Create an IEEE 9-bus power system model
2. Generate 45 measurements with 2% noise level
3. Perform state estimation
4. Display comprehensive results including:
   - Bus voltage magnitudes and angles comparison
   - Line power flows (active and reactive)
   - Measurement summary table
   - Visualization plots
   - Statistical error analysis

## Application Structure

### GridStateEstimator Class

- `create_ieee9_grid()`: Creates the IEEE 9-bus test system with buses, lines, generators, and loads
- `simulate_measurements()`: Generates noisy measurements for voltage magnitudes and power flows
- `run_state_estimation()`: Performs weighted least squares state estimation
- `show_results()`: Displays comprehensive results in tabular and graphical formats

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
- Voltage magnitude comparison plots
- Voltage angle comparison plots
- Error distribution charts

### Typical Performance
- Mean voltage magnitude error: ~0.5%
- Mean voltage angle error: ~0.03°
- Convergence: 4-5 iterations

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