import base64
import io
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from flask import Flask, flash, redirect, render_template, request, url_for
import matplotlib

# Ensure the repository root (where grid_state_estimator.py lives) is importable when
# the app is run from inside the web_ui directory or via FLASK_APP=web_ui.web_app.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Use non-GUI backend for server-side rendering
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from grid_state_estimator import GridStateEstimator


@dataclass
class AppState:
    estimator: Optional[GridStateEstimator] = None
    current_grid: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    observability_status: Optional[str] = None
    consistency_status: Optional[str] = None
    bad_data_status: Optional[str] = None

    def log(self, message: str) -> None:
        self.logs.append(message)
        # Keep the log list manageable
        self.logs = self.logs[-200:]


state = AppState()
app = Flask(__name__)
app.secret_key = "power-systems-web"


@app.route("/")
def index():
    grid_info = build_grid_info()
    measurement_preview = get_measurement_preview()
    comparison_table = get_measurement_comparison_data()
    measurement_definitions = get_measurement_definitions()
    measurement_summary = get_measurement_summary(measurement_definitions)
    switch_info = state.estimator.get_switch_info() if state.estimator else []
    grid_plot = generate_grid_plot()

    return render_template(
        "index.html",
        grid_info=grid_info,
        measurement_preview=measurement_preview,
        comparison_table=comparison_table,
        measurement_definitions=measurement_definitions,
        measurement_summary=measurement_summary,
        switch_info=switch_info,
        grid_plot=grid_plot,
        logs=reversed(state.logs),
        observability_status=state.observability_status,
        consistency_status=state.consistency_status,
        bad_data_status=state.bad_data_status,
    )


@app.post("/create-grid")
def create_grid():
    grid_type = request.form.get("grid_type")

    state.estimator = GridStateEstimator()
    try:
        if grid_type == "ieee9":
            state.estimator.create_ieee9_grid()
            state.current_grid = "IEEE 9-bus"
        else:
            state.estimator.create_simple_entso_grid()
            state.current_grid = "ENTSO-E"
        state.log(f"✅ Created {state.current_grid} grid")
        flash(f"{state.current_grid} grid created", "success")
    except Exception as exc:  # pragma: no cover - defensive
        state.estimator = None
        flash(f"Failed to create grid: {exc}", "error")
        state.log(f"❌ Grid creation error: {exc}")
    return redirect(url_for("index"))


@app.post("/simulate-measurements")
def simulate_measurements():
    if not ensure_grid():
        return redirect(url_for("index"))

    try:
        noise_level = float(request.form.get("noise", "0.02"))
        state.estimator.simulate_measurements(noise_level=noise_level)
        state.log(
            f"✅ Generated {len(state.estimator.net.measurement)} measurements with {noise_level*100:.1f}% noise"
        )
        flash("Measurements generated", "success")
    except Exception as exc:  # pragma: no cover - defensive
        flash(f"Failed to generate measurements: {exc}", "error")
        state.log(f"❌ Measurement generation error: {exc}")
    return redirect(url_for("index"))


@app.post("/list-measurements")
def list_measurements():
    if not ensure_grid():
        return redirect(url_for("index"))

    try:
        measurements = state.estimator.net.measurement
        if measurements is None or len(measurements) == 0:
            flash("No measurements available. Generate measurements first.", "warning")
            return redirect(url_for("index"))

        for idx, (_, row) in enumerate(measurements.iterrows()):
            if idx >= 12:
                state.log("... additional measurements omitted ...")
                break
            m_type = row.get("measurement_type", "?")
            element = row.get("element", "?")
            value = row.get("value", 0)
            std_dev = row.get("std_dev", 0)
            side = row.get("side", "")
            state.log(f"{idx:02d}: {m_type.upper()} {element} {side} = {value:.4f} ± {std_dev:.4f}")
        flash("Measurements listed below", "info")
    except Exception as exc:  # pragma: no cover - defensive
        flash(f"Failed to list measurements: {exc}", "error")
        state.log(f"❌ Measurement listing error: {exc}")
    return redirect(url_for("index"))


@app.post("/modify-bus")
def modify_bus():
    if not ensure_grid():
        return redirect(url_for("index"))

    try:
        bus_id = int(request.form.get("bus_id", "0"))
        voltage = float(request.form.get("voltage", "1.0"))
        success = state.estimator.modify_bus_voltage_measurement(bus_id, voltage)
        if success:
            state.log(f"✅ Bus {bus_id} voltage set to {voltage:.4f} p.u.")
            flash("Bus voltage updated", "success")
        else:
            flash("Unable to modify bus voltage (measurement missing)", "warning")
            state.log(f"❌ Unable to modify bus {bus_id} voltage")
    except Exception as exc:  # pragma: no cover - defensive
        flash(f"Failed to modify bus voltage: {exc}", "error")
        state.log(f"❌ Bus voltage modification error: {exc}")
    return redirect(url_for("index"))


@app.post("/state-estimation")
def state_estimation():
    if not ensure_grid():
        return redirect(url_for("index"))

    try:
        state.estimator.run_state_estimation()
        state.log("✅ State estimation completed")
        flash("State estimation finished", "success")
    except Exception as exc:  # pragma: no cover - defensive
        flash(f"State estimation failed: {exc}", "error")
        state.log(f"❌ State estimation error: {exc}")
    return redirect(url_for("index"))


@app.post("/observability")
def observability():
    if not ensure_grid():
        return redirect(url_for("index"))

    try:
        state.estimator.test_observability()
        state.observability_status = "completed"
        flash("Observability analysis complete", "success")
        state.log("✅ Observability analysis complete")
    except Exception as exc:  # pragma: no cover - defensive
        flash(f"Observability test failed: {exc}", "error")
        state.log(f"❌ Observability error: {exc}")
    return redirect(url_for("index"))


@app.post("/consistency")
def consistency():
    if not ensure_grid():
        return redirect(url_for("index"))

    try:
        results = state.estimator.check_measurement_consistency(tolerance=1e-3, detailed_report=True)
        status = results.get("overall_status", "unknown") if results else "completed"
        state.consistency_status = status
        state.log(f"✅ Consistency check: {status}")
        flash(f"Consistency check status: {status}", "success")
    except Exception as exc:  # pragma: no cover - defensive
        flash(f"Consistency check failed: {exc}", "error")
        state.log(f"❌ Consistency check error: {exc}")
    return redirect(url_for("index"))


@app.post("/bad-data")
def bad_data():
    if not ensure_grid():
        return redirect(url_for("index"))

    try:
        results = state.estimator.detect_bad_data(confidence_level=0.95, max_iterations=5)
        status = results.get("final_status", "completed") if results else "completed"
        bad_count = len(results.get("bad_measurements", [])) if results else 0
        state.bad_data_status = f"{status} ({bad_count} flagged)"
        state.log(f"✅ Bad data detection: {state.bad_data_status}")
        flash(f"Bad data detection finished: {state.bad_data_status}", "success")
    except Exception as exc:  # pragma: no cover - defensive
        flash(f"Bad data detection failed: {exc}", "error")
        state.log(f"❌ Bad data detection error: {exc}")
    return redirect(url_for("index"))


@app.post("/quick-demo")
def quick_demo():
    try:
        state.estimator = GridStateEstimator()
        state.estimator.create_ieee9_grid()
        state.current_grid = "IEEE 9-bus"
        np.random.seed(42)
        state.estimator.simulate_measurements(noise_level=0.02)
        state.estimator.run_state_estimation()
        state.log("🎯 Quick demo completed: IEEE 9-bus with 2% noise")
        flash("Quick demo executed", "success")
    except Exception as exc:  # pragma: no cover - defensive
        flash(f"Quick demo failed: {exc}", "error")
        state.log(f"❌ Quick demo error: {exc}")
    return redirect(url_for("index"))


@app.post("/switch")
def operate_switch():
    if not ensure_grid():
        return redirect(url_for("index"))

    try:
        switch_index = int(request.form.get("switch_index", "0"))
        action = request.form.get("action", "toggle")

        if action == "open":
            success = state.estimator.toggle_switch(switch_index, force_state=False)
        elif action == "close":
            success = state.estimator.toggle_switch(switch_index, force_state=True)
        else:
            success = state.estimator.toggle_switch(switch_index)

        if success:
            state.log(f"✅ Switch {switch_index} set to {action}")
            flash(f"Switch {switch_index} updated", "success")
        else:
            flash("Switch operation failed", "warning")
            state.log(f"❌ Switch {switch_index} operation failed")
    except Exception as exc:  # pragma: no cover - defensive
        flash(f"Switch operation error: {exc}", "error")
        state.log(f"❌ Switch operation error: {exc}")
    return redirect(url_for("index"))


@app.post("/clear")
def clear_output():
    state.logs.clear()
    state.observability_status = None
    state.consistency_status = None
    state.bad_data_status = None
    flash("Logs cleared", "info")
    return redirect(url_for("index"))


def ensure_grid() -> bool:
    if state.estimator is None:
        flash("Please create a grid first", "warning")
        return False
    return True


def build_grid_info():
    if not state.estimator or not hasattr(state.estimator, "net") or state.estimator.net is None:
        return None

    net = state.estimator.net
    return {
        "type": state.current_grid or "Custom",
        "buses": len(net.bus),
        "lines": len(net.line),
        "generators": len(net.gen) if hasattr(net, "gen") else 0,
        "loads": len(net.load) if hasattr(net, "load") else 0,
        "measurements": len(net.measurement) if hasattr(net, "measurement") else 0,
    }


def get_measurement_preview():
    if not state.estimator or not hasattr(state.estimator, "net"):
        return []

    net = state.estimator.net
    if not hasattr(net, "measurement") or len(net.measurement) == 0:
        return []

    preview = []
    for _, row in net.measurement.head(5).iterrows():
        preview.append(
            {
                "type": row.get("measurement_type", ""),
                "element": row.get("element", ""),
                "side": row.get("side", ""),
                "value": row.get("value", 0.0),
                "std_dev": row.get("std_dev", 0.0),
            }
        )
    return preview


def get_measurement_definitions(max_rows: int = 50):
    if not state.estimator:
        return {"rows": [], "total": 0, "limited": False, "all_rows": []}

    measurement_rows = state.estimator.get_measurement_info()
    measurement_rows = sorted(
        measurement_rows,
        key=lambda m: (m.get("type", ""), m.get("element", 0), m.get("side", "")),
    )

    limited = len(measurement_rows) > max_rows
    return {
        "rows": measurement_rows[:max_rows],
        "total": len(measurement_rows),
        "limited": limited,
        "all_rows": measurement_rows,
    }


def get_measurement_summary(definitions):
    rows = definitions.get("all_rows") or definitions.get("rows", [])
    if not rows:
        return {}

    type_counts = {}
    element_counts = set()
    for row in rows:
        mtype = row.get("type", "?")
        type_counts[mtype] = type_counts.get(mtype, 0) + 1
        element_counts.add(row.get("element"))

    return {
        "total": definitions.get("total", len(rows)),
        "by_type": sorted(type_counts.items()),
        "unique_elements": len(element_counts),
    }


def get_measurement_comparison_data():
    if not state.estimator or not state.estimator.estimation_results:
        return []

    net = state.estimator.net
    if not hasattr(net, "measurement") or len(net.measurement) == 0:
        return []

    comparison = []

    # Voltage magnitudes
    for bus_idx in net.bus.index:
        true_value = net.res_bus.vm_pu.iloc[bus_idx]
        estimated_value = net.res_bus_est.vm_pu.iloc[bus_idx]
        v_meas = net.measurement[
            (net.measurement.element == bus_idx)
            & (net.measurement.measurement_type == "v")
        ]
        measured_value = v_meas["value"].iloc[0] if not v_meas.empty else None
        comparison.append(
            {
                "name": f"V Bus {bus_idx}",
                "unit": "p.u.",
                "true": true_value,
                "measured": measured_value,
                "estimated": estimated_value,
                "meas_error": ((measured_value - true_value) / true_value * 100)
                if measured_value is not None and true_value != 0
                else None,
                "est_error": ((estimated_value - true_value) / true_value * 100)
                if true_value != 0
                else None,
            }
        )

    # Power flows
    line_has_estimates = hasattr(net, "res_line_est") and net.res_line_est is not None
    for line_idx in net.line.index:
        from_bus = net.line.from_bus.iloc[line_idx]
        to_bus = net.line.to_bus.iloc[line_idx]

        for meas_type, label, res_column in [
            ("p", "P_from", "p_from_mw"),
            ("q", "Q_from", "q_from_mvar"),
        ]:
            measurement_row = net.measurement[
                (net.measurement.element == line_idx)
                & (net.measurement.measurement_type == meas_type)
                & (net.measurement.side == "from")
            ]
            if measurement_row.empty:
                continue

            true_value = net.res_line[res_column].iloc[line_idx]
            measured_value = measurement_row["value"].iloc[0]
            est_value = (
                net.res_line_est[res_column].iloc[line_idx]
                if line_has_estimates
                else true_value
            )

            denominator = abs(true_value) if true_value != 0 else 1
            comparison.append(
                {
                    "name": f"{label} L{line_idx} ({from_bus}-{to_bus})",
                    "unit": "MW" if meas_type == "p" else "MVAr",
                    "true": true_value,
                    "measured": measured_value,
                    "estimated": est_value,
                    "meas_error": (measured_value - true_value) / denominator * 100,
                    "est_error": (est_value - true_value) / denominator * 100,
                }
            )

    return comparison


def generate_grid_plot():
    if not state.estimator or state.estimator.net is None:
        return None

    net = state.estimator.net
    positions = {}
    if hasattr(state.estimator, "_create_bus_positions"):
        positions = state.estimator._create_bus_positions()

    if len(positions) < len(net.bus):
        # Fallback to circular layout
        count = len(net.bus)
        radius = 2.5
        for idx in net.bus.index:
            angle = 2 * math.pi * idx / count
            positions[idx] = (radius * math.cos(angle), radius * math.sin(angle))

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_title("Grid Visualization", fontsize=14, fontweight="bold")

    # Draw lines
    for line_idx in net.line.index:
        from_bus = net.line.from_bus.iloc[line_idx]
        to_bus = net.line.to_bus.iloc[line_idx]
        x1, y1 = positions[from_bus]
        x2, y2 = positions[to_bus]
        ax.plot([x1, x2], [y1, y2], "-", color="#4a4a4a", linewidth=2, alpha=0.8)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, f"L{line_idx}", fontsize=8, ha="center")

    # Determine bus colors based on estimation results
    has_estimation = state.estimator.estimation_results is not None
    for bus_idx in net.bus.index:
        x, y = positions[bus_idx]
        if has_estimation:
            vm_est = net.res_bus_est.vm_pu.iloc[bus_idx]
            color = plt.cm.Blues(min(max((vm_est - 0.9) / 0.3, 0), 1))
        else:
            color = "#5b8def"
        ax.scatter([x], [y], s=350, color=color, edgecolors="black", zorder=5)
        label = net.bus.name.iloc[bus_idx] if "name" in net.bus else f"Bus {bus_idx}"
        ax.text(x, y, label, ha="center", va="center", fontsize=9, color="white", fontweight="bold")

    ax.axis("off")
    plt.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
