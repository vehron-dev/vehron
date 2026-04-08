# VEHRON <-> LFP_model_v2 Interface (v0.1)

This document defines the first integration contract between VEHRON and the external battery team model named `LFP_model_v2`.

## 1. Integration Pattern

Current pattern supports:

1. **Pre-run feedback import** (optional)
- `LFP_model_v2` sends pack-level parameter overrides (JSON).
- VEHRON applies overrides before simulation starts.

2. **Post-run trace export**
- VEHRON exports battery-relevant and environment-relevant time-series for `LFP_model_v2`.
- Export files include units and metadata.

## 2. CLI Hooks

Run with interface export:

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_car_sedan.yaml \
  --testcase src/vehron/testcases/wltp_class3b_standard.yaml \
  --lfp-export-dir output/interop/LFP_model_v2/wltp_run_001
```

Run with optional feedback import + export:

```bash
vehron run \
  --vehicle src/vehron/archetypes/bev_car_sedan.yaml \
  --testcase src/vehron/testcases/wltp_class3b_standard.yaml \
  --lfp-feedback-file input/lfp_model_v2_feedback.json \
  --lfp-export-dir output/interop/LFP_model_v2/wltp_run_002
```

## 3. Export File Set

Output directory contains:

- `lfp_model_v2_input.csv`
- `manifest.json`

### 3.1 CSV columns

- `time_s`
- `step_count`
- `speed_kmh`
- `soc`
- `v_batt_v`
- `i_batt_a`
- `p_batt_w`
- `p_drive_w`
- `p_regen_w`
- `p_hvac_w`
- `p_aux_w`
- `t_batt_k`
- `t_ambient_k`
- `t_coolant_k`
- `distance_m`

Sign conventions:

- `i_batt_a > 0`: pack discharging
- `i_batt_a < 0`: pack charging
- `p_batt_w > 0`: battery delivering power
- `p_batt_w < 0`: battery receiving power
- `p_regen_w > 0`: recovered regen power channel

## 4. Feedback JSON format

Expected top-level shape:

```json
{
  "model": "LFP_model_v2",
  "pack_overrides": {
    "capacity_kwh": 53.1,
    "internal_resistance_ohm": 0.075,
    "soc_init": 0.95,
    "soc_min": 0.05,
    "soc_max": 0.98,
    "max_charge_rate_c": 2.0,
    "max_discharge_rate_c": 5.0
  }
}
```

Only known keys are applied. Unknown keys are ignored.

## 5. Recommended Team Workflow

1. VEHRON team runs standard drive cycles (for example WLTP Class 3b).
2. Export generated via `--lfp-export-dir`.
3. `LFP_model_v2` team computes electro-thermal response and degradation projections.
4. If needed, they send updated pack-level feedback JSON.
5. VEHRON reruns with feedback for iteration and comparison.

## 6. Next Interface Upgrade Ideas

- Add explicit charging event channels and charger constraints in export.
- Add pack temperature limits and power-derating feedback path.
- Add round-trip comparison reports for baseline vs feedback-adjusted runs.
