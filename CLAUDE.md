# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python application for power system state estimation using the pandapower library. The application demonstrates complete power system state estimation workflows including IEEE 9-bus and ENTSO-E transmission grid modeling, measurement simulation with noise, interactive measurement modification, state estimation with bad data detection, and comprehensive results visualization.

## Development Environment Setup

### Prerequisites
- Python 3.7+
- Virtual environment (venv)

### Quick Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or: venv\Scripts\activate  # Windows

# Install dependencies 
pip install -r requirements.txt

# Alternative: Use provided setup script
./activate_venv.sh
```

### Main Dependencies
- pandapower>=2.13.0 (power system modeling and state estimation)
- numpy>=1.21.0 (numerical computations)
- pandas>=1.3.0 (data manipulation)
- matplotlib>=3.5.0 (visualization)
- scipy>=1.7.0 (scientific computing)

## Running the Application

### Primary Entry Point
```bash
# Interactive main application with complete menu system
python3 main.py

# Quick launcher with auto-setup
./run.sh
```

### Core Functionality Scripts
```bash
# Core state estimation functionality
python3 grid_state_estimator.py

# Individual test scripts (no testing framework - standalone executables)
python3 test_entso_grid.py              # ENTSO-E transmission grid testing
python3 test_bad_data_detection.py      # Bad data detection validation
python3 test_observability.py           # Observability analysis
python3 test_measurement_modification.py # Measurement modification examples
python3 test_grid_visualization.py      # Visualization testing
python3 test_noise_modes.py             # Noise level comparison
python3 test_consistency_check.py       # Data consistency validation

# Demo scripts
python3 demo_main_script.py             # Complete workflow demonstration
python3 demo_measurement_modification.py # Measurement modification examples
python3 demo_bad_data_detection.py      # Bad data scenarios
python3 demo_grid_plots.py              # Grid visualization features
python3 demo_modes.py                   # Different noise modes
```

### Command Line Options
```bash
# Interactive mode with noise selection
python3 grid_state_estimator.py

# Automatic comparison of perfect vs noisy measurements  
python3 grid_state_estimator.py --compare

# CGMES interface testing
python3 cgmes_interface.py

# Quick measurement modification example
python3 example_set_bus_voltage.py
```

## Architecture Overview

### Core Components

#### GridStateEstimator Class (`grid_state_estimator.py`)
The central class containing all power system analysis functionality:

- **Grid Creation**: `create_ieee9_grid()`, `create_simple_entso_grid()`, `load_cgmes_model()`
- **Measurement Simulation**: `simulate_measurements(noise_level)` 
- **State Estimation**: `run_state_estimation()` (weighted least squares algorithm)
- **Observability Analysis**: `test_observability()`, comprehensive redundancy analysis
- **Bad Data Detection**: Chi-square test, largest normalized residual test, statistical outlier detection
- **Results & Visualization**: `show_results()`, `plot_grid_results()` with network schematic overlays
- **Interactive Modification**: Methods for modifying specific measurements

#### PowerSystemApp Class (`main.py`) 
Interactive menu-driven interface providing access to all functionality through numbered menu options.

### Grid Models

1. **IEEE 9-Bus Test System**: Standard validation system with 9 buses, 9 lines, 3 generators, 3 loads
2. **ENTSO-E Transmission Grid**: Realistic 400kV/220kV multi-voltage transmission system with transformers
3. **CGMES Interface**: Support for CGMES/CIM model loading (requires specialized libraries)

### Measurement System
- Voltage magnitudes at all buses
- Active/reactive power flows at line terminals
- Configurable noise levels (0.0 = perfect, >0.0 = Gaussian noise)
- Interactive modification capabilities ("set bus 1 = 1.2 p.u.")

### Analysis Features
- **Observability**: Measurement redundancy ratios, coverage analysis, critical measurement detection
- **State Estimation**: Weighted least squares with convergence monitoring
- **Bad Data Detection**: Statistical tests for measurement validation
- **Visualization**: Network schematic plots with color-coded results, power flow arrows, error heat maps

## Testing Strategy

This project uses **standalone test scripts** instead of a traditional testing framework like pytest. Each test file is an executable script that demonstrates specific functionality:

### Test Categories
- `test_*.py` files: Comprehensive functionality validation
- `demo_*.py` files: Step-by-step examples and tutorials  
- `simple_*.py` files: Basic functionality tests

### Running Tests
Execute test scripts directly:
```bash
python3 test_bad_data_detection.py      # Test bad data detection algorithms
python3 test_observability.py           # Validate observability analysis
python3 test_entso_grid.py              # Test ENTSO-E grid model
python3 test_grid_visualization.py      # Validate visualization features
```

## Key Design Patterns

### Interactive Workflow Pattern
The application follows an interactive workflow where users:
1. Create grid model → 2. Generate measurements → 3. Modify measurements (optional) → 4. Run state estimation → 5. Analyze results

### Measurement Modification Pattern  
Users can interactively modify specific measurements using natural language-like commands:
```python
estimator.modify_bus_voltage_measurement(bus_id=1, new_voltage_pu=1.2)
```

### Results Analysis Pattern
Comprehensive results include:
- Tabular comparisons (Load Flow vs Measured vs Estimated)
- Network schematic visualizations with overlay data
- Statistical performance metrics
- Error analysis and distribution plots

## File Organization

### Core Files
- `main.py`: Interactive application entry point
- `grid_state_estimator.py`: Core estimation functionality class
- `cgmes_interface.py`: CGMES/CIM interface support

### Test & Demo Files  
- `test_*.py`: Functional validation scripts
- `demo_*.py`: Tutorial and example scripts
- `example_*.py`: Quick usage examples

### Utility Scripts
- `run.sh`: Application launcher with auto-setup
- `activate_venv.sh`: Virtual environment setup

### Configuration Files
- `requirements.txt`: Python dependencies
- `*.md` files: Documentation and summaries

## Common Development Tasks

### Adding New Grid Models
Extend `GridStateEstimator` class with new `create_*_grid()` methods following the pattern of existing IEEE 9-bus and ENTSO-E implementations.

### Adding New Measurement Types
Modify `simulate_measurements()` method to include additional measurement types using pandapower measurement creation functions.

### Extending Visualization
Add new plot types in `plot_grid_results()` method using matplotlib and pandapower plotting utilities.

### Adding Bad Data Detection Algorithms
Implement new detection methods in the state estimation workflow, following the pattern of existing chi-square and normalized residual tests.