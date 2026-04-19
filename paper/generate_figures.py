"""Generate paper-styled benchmark figures for the VEHRON manuscript."""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIGURES_DIR = PROJECT_ROOT / "paper" / "figures"


def _load_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            rows.append({key: float(value) for key, value in row.items()})
    return rows


def _resolve_case_timeseries(case_name: str) -> Path:
    candidates = sorted(
        (PROJECT_ROOT / "output" / "cases").glob(f"case_{case_name}_*/timeseries.csv"),
        key=lambda path: path.parent.name,
    )
    if not candidates:
        raise FileNotFoundError(
            f"No local case output found for '{case_name}'. "
            "Run the benchmark case first so the paper figures can be regenerated."
        )
    return candidates[-1]


def _setup_matplotlib():
    import os

    os.environ.setdefault("MPLCONFIGDIR", "/tmp/vehron-mpl")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "legend.fontsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "grid.linewidth": 0.5,
            "savefig.dpi": 220,
            "figure.dpi": 220,
        }
    )
    return plt


def _marker_step(n_points: int) -> int:
    return max(1, n_points // 18)


def generate_highway_motion(plt, rows: list[dict[str, float]]) -> None:
    t_s = [row["t"] for row in rows]
    v_kmh = [row["v_kmh"] for row in rows]
    a_ms2 = [row["a_ms2"] for row in rows]
    distance_km = [row["distance_km"] for row in rows]
    markevery = _marker_step(len(rows))

    fig, axes = plt.subplots(3, 1, figsize=(6.2, 5.6), sharex=True)

    axes[0].plot(
        t_s,
        v_kmh,
        color="black",
        linewidth=1.2,
        marker="o",
        markersize=2.2,
        markevery=markevery,
    )
    axes[0].set_ylabel("Speed [km/h]")
    axes[0].set_title("Flat-highway benchmark")

    axes[1].plot(
        t_s,
        a_ms2,
        color="tab:blue",
        linewidth=1.0,
        marker="s",
        markersize=2.0,
        markevery=markevery,
    )
    axes[1].set_ylabel("Accel. [m/s$^2$]")

    axes[2].plot(
        t_s,
        distance_km,
        color="tab:green",
        linewidth=1.1,
        marker="^",
        markersize=2.2,
        markevery=markevery,
    )
    axes[2].set_ylabel("Distance [km]")
    axes[2].set_xlabel("Time [s]")

    for ax in axes:
        ax.margins(x=0.01)

    fig.tight_layout(h_pad=0.45)
    fig.savefig(FIGURES_DIR / "highway_motion.png", bbox_inches="tight")
    plt.close(fig)


def generate_highway_temperatures(plt, rows: list[dict[str, float]]) -> None:
    t_s = [row["t"] for row in rows]
    t_amb_c = [row["t_ambient_c"] for row in rows]
    t_batt_c = [row["t_batt_c"] for row in rows]
    t_motor_c = [row["t_motor_c"] for row in rows]
    t_coolant_c = [row["t_coolant_c"] for row in rows]
    t_cabin_c = [row["t_cabin_c"] for row in rows]
    markevery = _marker_step(len(rows))

    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(t_s, t_amb_c, color="black", linewidth=1.1, label="Ambient")
    ax.plot(
        t_s,
        t_batt_c,
        color="tab:red",
        linewidth=1.0,
        marker="o",
        markersize=2.0,
        markevery=markevery,
        label="Battery",
    )
    ax.plot(
        t_s,
        t_motor_c,
        color="tab:blue",
        linewidth=1.0,
        marker="s",
        markersize=2.0,
        markevery=markevery,
        label="Motor",
    )
    ax.plot(
        t_s,
        t_coolant_c,
        color="tab:green",
        linewidth=1.0,
        marker="^",
        markersize=2.0,
        markevery=markevery,
        label="Coolant",
    )
    ax.plot(
        t_s,
        t_cabin_c,
        color="tab:orange",
        linewidth=1.0,
        marker="D",
        markersize=1.8,
        markevery=markevery,
        label="Cabin",
    )
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Temperature [C]")
    ax.set_title("Highway-case thermal channels", pad=30)
    ax.legend(
        ncol=3,
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.33),
        columnspacing=1.2,
        handlelength=1.8,
    )
    ax.margins(x=0.01)

    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.9))
    fig.savefig(FIGURES_DIR / "highway_temperatures.png", bbox_inches="tight")
    plt.close(fig)


def generate_city_soc_idle(plt, rows: list[dict[str, float]]) -> None:
    t_s = [row["t"] for row in rows]
    soc_pct = [row["soc"] * 100.0 for row in rows]
    idle_flag = [1.0 if abs(row["v_ms"]) < 0.1 else 0.0 for row in rows]
    markevery = _marker_step(len(rows))

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(6.2, 4.2),
        sharex=True,
        gridspec_kw={"height_ratios": [3.0, 1.1]},
    )

    axes[0].plot(
        t_s,
        soc_pct,
        color="tab:purple",
        linewidth=1.1,
        marker="o",
        markersize=2.0,
        markevery=markevery,
    )
    axes[0].set_ylabel("SoC [%]")
    axes[0].set_title("City stop-start benchmark")

    axes[1].step(t_s, idle_flag, where="post", color="tab:red", linewidth=1.0)
    axes[1].set_ylabel("Idle")
    axes[1].set_xlabel("Time [s]")
    axes[1].set_yticks([0, 1], labels=["moving", "idle"])

    for ax in axes:
        ax.margins(x=0.01)

    fig.tight_layout(h_pad=0.35)
    fig.savefig(FIGURES_DIR / "city_soc_idle.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plt = _setup_matplotlib()

    highway_rows = _load_rows(_resolve_case_timeseries("bev_car_flat_highway_100_km_h"))
    city_rows = _load_rows(_resolve_case_timeseries("bev_car_city_wltp_like_stop_start"))

    generate_highway_motion(plt, highway_rows)
    generate_highway_temperatures(plt, highway_rows)
    generate_city_soc_idle(plt, city_rows)

    print("Wrote paper figures to", FIGURES_DIR)


if __name__ == "__main__":
    main()
