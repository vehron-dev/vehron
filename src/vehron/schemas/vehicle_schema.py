# Copyright (C) 2026 Subramanyam Natarajan
# SPDX-License-Identifier: AGPL-3.0-only

"""Pydantic schema for vehicle YAML."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class VehicleSection(BaseModel):
    name: str = Field(min_length=1)
    archetype: str = Field(default="car")
    powertrain: str = Field(default="bev")
    mass_kg: float = Field(gt=0)
    payload_kg: float = Field(ge=0, default=0.0)
    frontal_area_m2: float = Field(gt=0)
    drag_coefficient: float = Field(gt=0)
    wheel_radius_m: float = Field(gt=0)
    primary_reduction_ratio: float = Field(gt=0, default=1.0)
    secondary_reduction_ratio: float = Field(gt=0, default=1.0)
    transmission_efficiency: float = Field(gt=0, le=1, default=0.97)
    drivetrain_efficiency: float = Field(gt=0, le=1, default=0.95)

    @field_validator("powertrain")
    @classmethod
    def _powertrain_supported(cls, value: str) -> str:
        if value != "bev":
            raise ValueError("Only 'bev' powertrain is currently supported")
        return value


class DriverSection(BaseModel):
    model: str = Field(default="pid")
    kp: float = Field(ge=0, default=0.9)
    ki: float = Field(ge=0, default=0.08)
    kd: float = Field(ge=0, default=0.02)

    @field_validator("model")
    @classmethod
    def _driver_supported(cls, value: str) -> str:
        if value != "pid":
            raise ValueError("Only 'pid' driver is currently supported")
        return value


class BatterySection(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str = Field(default="rint")
    external_module_path: str | None = None
    external_class_name: str | None = None
    capacity_kwh: float = Field(gt=0)
    nominal_voltage_v: float = Field(gt=0)
    internal_resistance_ohm: float = Field(gt=0)
    thermal_mass_kjk: float = Field(gt=0, default=25.0)
    max_charge_rate_c: float = Field(gt=0, default=2.0)
    max_discharge_rate_c: float = Field(gt=0, default=4.0)
    soc_init: float = Field(ge=0, le=1, default=1.0)
    soc_min: float = Field(ge=0, le=1, default=0.05)
    soc_max: float = Field(ge=0, le=1, default=0.98)

    @field_validator("soc_max")
    @classmethod
    def _soc_window_valid(cls, value: float, info) -> float:
        soc_min = info.data.get("soc_min")
        if soc_min is not None and value <= soc_min:
            raise ValueError("battery.soc_max must be greater than battery.soc_min")
        return value

    @model_validator(mode="after")
    def _validate_external_battery_fields(self) -> "BatterySection":
        if self.model == "external" and (
            not self.external_module_path or not self.external_class_name
        ):
            raise ValueError(
                "battery.external_module_path and battery.external_class_name "
                "are required when battery.model is 'external'"
            )
        return self


class MotorSection(BaseModel):
    model: str = Field(default="analytical")
    map_file: str | None = None
    peak_power_kw: float = Field(gt=0)
    peak_torque_nm: float = Field(gt=0)
    max_speed_rpm: float = Field(gt=0)
    base_efficiency: float = Field(gt=0, le=1, default=0.93)
    base_speed_rpm: float | None = Field(default=None, gt=0)
    max_regen_power_kw: float | None = Field(default=None, gt=0)
    max_regen_torque_nm: float | None = Field(default=None, gt=0)
    regen_efficiency: float | None = Field(default=None, gt=0, le=1)
    min_efficiency: float = Field(gt=0, le=1, default=0.70)
    max_efficiency: float = Field(gt=0, le=1, default=0.98)


class TyreSection(BaseModel):
    model: str = Field(default="rolling_resistance")
    rolling_resistance_coeff: float = Field(gt=0, default=0.010)
    tyre_size: str = Field(default="")


class HVACSection(BaseModel):
    model: str = Field(default="cabin_load")
    external_module_path: str | None = None
    external_class_name: str | None = None
    rated_power_kw: float = Field(gt=0, default=4.0)
    cabin_volume_m3: float = Field(gt=0, default=2.8)
    cop_cooling: float = Field(gt=0, default=2.5)
    cop_heating: float = Field(gt=0, default=2.0)
    cabin_setpoint_c: float = Field(default=22.0)
    interior_thermal_mass_kjk: float = Field(gt=0, default=75.0)
    body_ua_wk: float = Field(gt=0, default=120.0)
    speed_ua_per_ms_wk: float = Field(ge=0, default=3.0)
    glazed_area_m2: float = Field(gt=0, default=2.2)
    solar_transmittance: float = Field(gt=0, le=1, default=0.55)
    fresh_air_ach: float = Field(gt=0, default=8.0)
    occupant_sensible_w: float = Field(gt=0, default=75.0)
    control_tau_s: float = Field(gt=0, default=240.0)

    @model_validator(mode="after")
    def _validate_external_hvac_fields(self) -> "HVACSection":
        if self.model == "external" and (
            not self.external_module_path or not self.external_class_name
        ):
            raise ValueError(
                "hvac.external_module_path and hvac.external_class_name "
                "are required when hvac.model is 'external'"
            )
        return self


class ChargingSection(BaseModel):
    ac_power_limit_kw: float = Field(ge=0, default=7.2)
    dc_power_limit_kw: float = Field(ge=0, default=80.0)
    charge_efficiency_ac: float = Field(gt=0, le=1, default=0.95)
    charge_efficiency_dc: float = Field(gt=0, le=1, default=0.95)
    target_voltage_v: float | None = Field(default=None)
    termination_current_a: float = Field(ge=0, default=5.0)
    max_charge_current_a: float | None = Field(default=None)
    temp_min_charge_c: float | None = Field(default=None)
    temp_max_charge_c: float | None = Field(default=None)
    cv_enabled: bool = Field(default=True)
    dc_soc_taper_start: float = Field(ge=0, le=1, default=0.8)
    dc_min_taper_fraction: float = Field(ge=0, le=1, default=0.15)


class AuxLoadsSection(BaseModel):
    headlights_w: float = Field(ge=0, default=80.0)
    adas_w: float = Field(ge=0, default=150.0)
    infotainment_w: float = Field(ge=0, default=60.0)
    power_steering_w: float = Field(ge=0, default=100.0)


class VehicleConfig(BaseModel):
    vehicle: VehicleSection
    driver: DriverSection = Field(default_factory=DriverSection)
    battery: BatterySection
    motor: MotorSection
    tyre: TyreSection = Field(default_factory=TyreSection)
    hvac: HVACSection = Field(default_factory=HVACSection)
    charging: ChargingSection = Field(default_factory=ChargingSection)
    aux_loads: AuxLoadsSection = Field(default_factory=AuxLoadsSection)
