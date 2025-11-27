# Codebase Analysis

## Purpose and Scope
This repository implements an interactive power-system state estimation toolkit built on top of pandapower. It provides scripts for creating transmission grid models, simulating and modifying measurements, running weighted least-squares estimation, performing observability and consistency checks, and exploring bad data scenarios.

## Core Components

### `grid_state_estimator.py`
* Defines the `GridStateEstimator` class, which encapsulates grid construction, measurement handling, and estimation workflows.
* Grid creation helpers build either a simplified ENTSO-E-style network with multiple voltage levels and manual parameters or the IEEE 9-bus benchmark case. These methods assemble buses, transformers, lines, generators, loads, and a slack bus before reporting network statistics. 【F:grid_state_estimator.py†L62-L186】
* Measurement simulation runs a power-flow, clears prior values, and populates bus voltage and line power measurements with optional Gaussian noise; it reports coverage based on whether noise-free or noisy mode is requested. 【F:grid_state_estimator.py†L187-L261】
* State estimation executes pandapower's weighted least-squares routine with warning suppression, storing estimated bus voltages and line flows on success. 【F:grid_state_estimator.py†L262-L287】
* Convenience utilities list measurements, edit specific entries (bus voltages or line power on a side), and reset the measurement set for scenario testing. 【F:grid_state_estimator.py†L288-L416】
* Analysis routines cover observability checks via measurement counts and coverage heuristics, alongside a multi-step bad data detection pipeline that calculates residuals, normalizes them, applies statistical tests, and optionally restores original measurements. 【F:grid_state_estimator.py†L438-L840】

### `main.py`
* Implements `PowerSystemApp`, an interactive CLI that guides users through grid creation, measurement simulation, modification, estimation, observability testing, and demo flows via structured menus. 【F:main.py†L1-L200】
* Menu handlers delegate to `GridStateEstimator` for domain logic while providing user prompts, validation, and feedback for operations such as setting noise levels, adjusting bus voltages, or selecting analysis actions. 【F:main.py†L85-L200】

## Notable Scripts
The repository includes multiple helper scripts (e.g., `run.sh`, `demo_*`, and `test_*` files) described in the README for launching demos, visualization, and targeted tests, supporting varied exploration scenarios without modifying the core estimator or CLI.
