"""
vehron/constants.py
-------------------
Physical constants for VEHRON simulations.

Rules:
- Import constants only from this module. Never redefine them elsewhere.
- All values are in SI units unless the name explicitly states otherwise.
- Do not add constants here without a clear use case in a physics module.
"""

# ── Mechanics ──────────────────────────────────────────────────────────────────

GRAVITY_MS2 = 9.81
"""Standard acceleration due to gravity, m/s²."""

# ── Atmosphere (ISA standard, sea level, 15 deg C) ────────────────────────────

AIR_DENSITY_KGM3 = 1.225
"""Density of dry air at 15 deg C and 101325 Pa, kg/m³."""

AIR_CP_JKGK = 1005.0
"""Specific heat capacity of dry air at constant pressure, J/(kg·K)."""

STANDARD_PRESSURE_PA = 101_325.0
"""Standard atmospheric pressure, Pa."""

R_SPECIFIC_AIR_JKGK = 287.05
"""Specific gas constant for dry air, J/(kg·K)."""

# ── Thermal ────────────────────────────────────────────────────────────────────

CELSIUS_TO_KELVIN = 273.15
"""Add to Celsius to get Kelvin. Subtract to go the other way."""

WATER_CP_JKGK = 4182.0
"""Specific heat capacity of liquid water at 25 deg C, J/(kg·K)."""

COOLANT_CP_JKGK = 3400.0
"""
Approximate specific heat capacity of a 50/50 water-glycol coolant mix,
J/(kg·K). Used as default for battery and motor cooling loops.
Override in module params if a different mix is used.
"""

STEFAN_BOLTZMANN = 5.6704e-8
"""Stefan-Boltzmann constant, W/(m²·K⁴). For radiative heat transfer."""

# ── Energy and power ───────────────────────────────────────────────────────────

KWH_TO_JOULES = 3_600_000
"""Joules per kilowatt-hour."""

WH_TO_JOULES = 3_600
"""Joules per watt-hour."""

# ── Mass and force ─────────────────────────────────────────────────────────────

KG_TO_G = 1000.0
"""Grams per kilogram."""

# ── Rotational ─────────────────────────────────────────────────────────────────

RPM_TO_RADS = 0.10471975511965977
"""Multiply RPM by this to get rad/s. Exact value: 2*pi/60."""

RADS_TO_RPM = 9.549296585513720
"""Multiply rad/s by this to get RPM. Exact value: 60/(2*pi)."""

# ── Speed ──────────────────────────────────────────────────────────────────────

KMH_TO_MS = 1.0 / 3.6
"""Multiply km/h by this to get m/s."""

MS_TO_KMH = 3.6
"""Multiply m/s by this to get km/h."""

# ── Electrochemistry ───────────────────────────────────────────────────────────

FARADAY_CONSTANT = 96_485.0
"""Faraday constant, C/mol. Used in electrochemical battery models."""

GAS_CONSTANT_JMOLK = 8.314
"""Universal gas constant, J/(mol·K)."""

# ── Hydrogen ───────────────────────────────────────────────────────────────────

H2_LOWER_HEATING_VALUE_MJKG = 120.1
"""Lower heating value of hydrogen, MJ/kg. Used in FCEV energy calculations."""

H2_HIGHER_HEATING_VALUE_MJKG = 141.8
"""Higher heating value of hydrogen, MJ/kg."""

# ── Fuel (petrol / gasoline) ───────────────────────────────────────────────────

PETROL_LOWER_HEATING_VALUE_MJKG = 43.4
"""Lower heating value of petrol (gasoline), MJ/kg."""

PETROL_DENSITY_KGM3 = 740.0
"""Approximate density of petrol at 15 deg C, kg/m³."""

DIESEL_LOWER_HEATING_VALUE_MJKG = 42.8
"""Lower heating value of diesel, MJ/kg."""

DIESEL_DENSITY_KGM3 = 840.0
"""Approximate density of diesel at 15 deg C, kg/m³."""

# ── Simulation defaults ────────────────────────────────────────────────────────

DEFAULT_DT_S = 0.1
"""Default master timestep, seconds. Can be overridden in testcase YAML."""

DEFAULT_AMBIENT_TEMP_K = 298.15
"""Default ambient temperature, K (25 deg C)."""

DEFAULT_INITIAL_SOC = 1.0
"""Default battery state of charge at simulation start, 0.0–1.0."""
