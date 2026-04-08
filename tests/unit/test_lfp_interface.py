import json

from vehron.engine import SimulationResult
from vehron.interfaces.lfp_model_v2 import (
    apply_lfp_model_v2_feedback,
    export_lfp_model_v2_hook,
)
from vehron.state import SimState


def test_apply_lfp_feedback_overrides_battery(tmp_path):
    vehicle_cfg = {
        "vehicle": {"name": "x", "powertrain": "bev"},
        "battery": {"capacity_kwh": 55.0, "internal_resistance_ohm": 0.08, "soc_init": 0.98},
    }

    feedback = {
        "model": "LFP_model_v2",
        "pack_overrides": {
            "capacity_kwh": 52.5,
            "internal_resistance_ohm": 0.09,
            "soc_init": 0.9,
            "ignored_key": 1,
        },
    }
    feedback_path = tmp_path / "feedback.json"
    feedback_path.write_text(json.dumps(feedback), encoding="utf-8")

    updated, applied = apply_lfp_model_v2_feedback(vehicle_cfg, feedback_path)

    assert updated["battery"]["capacity_kwh"] == 52.5
    assert updated["battery"]["internal_resistance_ohm"] == 0.09
    assert updated["battery"]["soc_init"] == 0.9
    assert "ignored_key" not in applied


def test_export_lfp_hook_writes_csv_and_manifest(tmp_path):
    rows = [
        {
            "t": 0.0,
            "step_count": 0,
            "v_kmh": 0.0,
            "soc": 0.98,
            "v_batt_v": 360.0,
            "i_batt_a": 0.0,
            "p_batt_w": 0.0,
            "p_drive_w": 0.0,
            "p_regen_w": 0.0,
            "p_hvac_w": 1000.0,
            "p_aux_w": 300.0,
            "t_batt_k": 298.15,
            "t_ambient_k": 298.15,
            "t_coolant_k": 298.15,
            "distance_m": 0.0,
        }
    ]
    result = SimulationResult(time_series=rows, final_state=SimState())
    out_dir = tmp_path / "lfp_export"

    export_lfp_model_v2_hook(
        result=result,
        vehicle_cfg={"vehicle": {"name": "City EV", "powertrain": "bev"}},
        testcase_cfg={"testcase": {"name": "test"}, "route": {"mode": "parametric"}, "simulation": {"dt_s": 0.1}},
        export_dir=out_dir,
        feedback_applied=["capacity_kwh"],
    )

    assert (out_dir / "lfp_model_v2_input.csv").exists()
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["model_interface"] == "LFP_model_v2"
    assert manifest["feedback_applied"] == ["capacity_kwh"]
