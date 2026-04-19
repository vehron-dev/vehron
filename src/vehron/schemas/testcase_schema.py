"""Pydantic schema for testcase YAML."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TestcaseSection(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(default="")


class EnvironmentSection(BaseModel):
    ambient_temp_c: float = Field(default=25.0)
    wind_speed_ms: float = Field(ge=0, default=0.0)
    wind_angle_deg: float = Field(default=0.0)
    solar_irradiance_wm2: float = Field(ge=0, default=0.0)


class RouteSection(BaseModel):
    mode: str = Field(default="parametric")
    distance_km: float = Field(gt=0)
    grade_pct: float = Field(default=0.0)
    target_speed_kmh: float = Field(ge=0, default=0.0)
    drive_cycle_file: str | None = None


class PayloadSection(BaseModel):
    passengers: int = Field(ge=0, default=0)
    cargo_kg: float = Field(ge=0, default=0.0)


class SimulationSection(BaseModel):
    dt_s: float = Field(gt=0, default=0.1)
    max_duration_s: float = Field(gt=0, default=3600.0)
    stop_on_soc_min: bool = Field(default=True)
    external_charging_power_kw: float = Field(ge=0, default=0.0)
    external_charging_start_s: float = Field(ge=0, default=0.0)
    external_charging_end_s: float = Field(ge=0, default=0.0)
    auto_charge: dict[str, float | bool] = Field(default_factory=dict)


class OutputsSection(BaseModel):
    time_series: bool = Field(default=True)
    energy_audit: bool = Field(default=True)
    plots: list[str] = Field(default_factory=list)
    report: bool = Field(default=True)


class TestcaseConfig(BaseModel):
    testcase: TestcaseSection
    environment: EnvironmentSection = Field(default_factory=EnvironmentSection)
    route: RouteSection
    payload: PayloadSection = Field(default_factory=PayloadSection)
    simulation: SimulationSection = Field(default_factory=SimulationSection)
    outputs: OutputsSection = Field(default_factory=OutputsSection)
