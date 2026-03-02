"""
FE Protein Folding Scaling Study — Analysis Pipeline

Reads Phase B trial CSVs and produces:
  - manuscript_outputs/scaling_table.csv
  - manuscript_outputs/scaling_plot.png
  - manuscript_outputs/stats_summary.json

Usage:
  python analyze_results.py              # Analyze all available Phase B data
  python analyze_results.py --phase A    # Analyze pilot data instead

Patent Reference: US 63/898,911
"""

import argparse
import csv
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats as sp_stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class NumpyEncoder(json.JSONEncoder):
    """Handle numpy types in JSON serialization."""
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# ============================================================================
# PATHS
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "manuscript_outputs")

with open(os.path.join(SCRIPT_DIR, "config.json")) as f:
    CONFIG = json.load(f)

LENGTHS = CONFIG["lengths"]


# ============================================================================
# LOAD DATA
# ============================================================================

def load_phase_data(phase: str) -> pd.DataFrame:
    """Load all CSVs for a given phase into a single DataFrame."""
    frames = []
    for L in LENGTHS:
        path = os.path.join(RESULTS_DIR, f"phase_{phase}_L{L}.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            frames.append(df)
    if not frames:
        print(f"ERROR: No Phase {phase} data found in {RESULTS_DIR}")
        sys.exit(1)
    return pd.concat(frames, ignore_index=True)


# ============================================================================
# STATISTICS
# ============================================================================

def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple:
    """Wilson score confidence interval for a proportion."""
    if n == 0:
        return (0.0, 0.0)
    p_hat = successes / n
    denom = 1 + z**2 / n
    center = (p_hat + z**2 / (2 * n)) / denom
    margin = z * np.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * n)) / n) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Cohen's d effect size (pooled SD)."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_sd == 0:
        return 0.0
    return (np.mean(group2) - np.mean(group1)) / pooled_sd


def analyze_length(df_length: pd.DataFrame, L: int) -> dict:
    """Compute all metrics for a single length."""
    mc = df_length[df_length["algorithm"] == "MC"]
    fe = df_length[df_length["algorithm"] == "FE"]

    mc_energies = mc["final_energy"].values
    fe_energies = fe["final_energy"].values

    n_mc = len(mc)
    n_fe = len(fe)

    # Success rates (Phase A has empty success_flag, Phase B has 0/1)
    mc_success = 0
    fe_success = 0
    if "success_flag" in mc.columns:
        mc_sf = pd.to_numeric(mc["success_flag"], errors="coerce").fillna(0)
        mc_success = int(mc_sf.sum())
    if "success_flag" in fe.columns:
        fe_sf = pd.to_numeric(fe["success_flag"], errors="coerce").fillna(0)
        fe_success = int(fe_sf.sum())

    mc_rate = mc_success / n_mc if n_mc > 0 else 0.0
    fe_rate = fe_success / n_fe if n_fe > 0 else 0.0

    # Delta and ratio
    delta = fe_rate - mc_rate
    ratio = fe_rate / mc_rate if mc_rate > 0 else float('inf')

    # Wilson CIs
    mc_ci = wilson_ci(mc_success, n_mc)
    fe_ci = wilson_ci(fe_success, n_fe)

    # Cohen's d on energies
    d = cohens_d(mc_energies, fe_energies)

    # Mann-Whitney U
    if n_mc > 0 and n_fe > 0:
        u_stat, p_val = sp_stats.mannwhitneyu(mc_energies, fe_energies, alternative='greater')
    else:
        u_stat, p_val = 0, 1.0

    # Energy stats
    mc_mean_e = float(np.mean(mc_energies)) if n_mc > 0 else 0.0
    fe_mean_e = float(np.mean(fe_energies)) if n_fe > 0 else 0.0
    mc_std_e = float(np.std(mc_energies, ddof=1)) if n_mc > 1 else 0.0
    fe_std_e = float(np.std(fe_energies, ddof=1)) if n_fe > 1 else 0.0

    # Runtime stats
    mc_mean_ms = float(mc["runtime_ms"].mean()) if n_mc > 0 else 0.0
    fe_mean_ms = float(fe["runtime_ms"].mean()) if n_fe > 0 else 0.0

    return {
        "L": L,
        "n_mc": n_mc,
        "n_fe": n_fe,
        "mc_success": mc_success,
        "fe_success": fe_success,
        "mc_rate": round(mc_rate * 100, 2),
        "fe_rate": round(fe_rate * 100, 2),
        "delta": round(delta * 100, 2),
        "ratio": round(ratio, 3) if ratio != float('inf') else "inf",
        "mc_ci_95": [round(mc_ci[0] * 100, 2), round(mc_ci[1] * 100, 2)],
        "fe_ci_95": [round(fe_ci[0] * 100, 2), round(fe_ci[1] * 100, 2)],
        "cohens_d": round(d, 3),
        "mann_whitney_p": float(p_val),
        "mc_mean_energy": round(mc_mean_e, 3),
        "fe_mean_energy": round(fe_mean_e, 3),
        "mc_std_energy": round(mc_std_e, 3),
        "fe_std_energy": round(fe_std_e, 3),
        "mc_mean_runtime_ms": round(mc_mean_ms, 1),
        "fe_mean_runtime_ms": round(fe_mean_ms, 1),
    }


# ============================================================================
# TREND TEST
# ============================================================================

def trend_test(results: list, n_permutations: int = 10000) -> dict:
    """
    Fit Δ(L) = a + bL and test b > 0 via permutation test.
    Primary claim: "The success-rate gap increases with length."
    """
    lengths = np.array([r["L"] for r in results], dtype=float)
    deltas = np.array([r["delta"] for r in results], dtype=float)

    if len(lengths) < 3:
        return {
            "slope_b": 0, "intercept_a": 0, "p_permutation_one_sided": 1.0,
            "r_squared": 0, "p_ols": 1.0, "std_err": 0, "n_permutations": 0,
            "interpretation": f"Too few data points ({len(lengths)}) for trend test",
        }

    # OLS fit
    slope, intercept, r_value, p_ols, std_err = sp_stats.linregress(lengths, deltas)

    # Permutation test for b > 0
    rng = np.random.RandomState(42)
    count_ge = 0
    for _ in range(n_permutations):
        perm_deltas = rng.permutation(deltas)
        perm_slope = sp_stats.linregress(lengths, perm_deltas).slope
        if perm_slope >= slope:
            count_ge += 1
    p_perm = count_ge / n_permutations

    return {
        "slope_b": round(float(slope), 5),
        "intercept_a": round(float(intercept), 3),
        "r_squared": round(float(r_value**2), 4),
        "p_ols": float(p_ols),
        "p_permutation_one_sided": float(p_perm),
        "std_err": round(float(std_err), 5),
        "n_permutations": n_permutations,
        "interpretation": (
            f"Δ(L) = {intercept:.2f} + {slope:.4f}·L  "
            f"(R²={r_value**2:.3f}, p_perm={p_perm:.4f})"
        ),
    }


# ============================================================================
# OUTPUTS
# ============================================================================

def write_scaling_table(results: list):
    """Write manuscript-ready CSV table."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "scaling_table.csv")
    fields = ["L", "mc_rate", "fe_rate", "delta", "ratio", "cohens_d",
              "mann_whitney_p", "mc_ci_95", "fe_ci_95"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            row = {k: r[k] for k in fields}
            row["mc_ci_95"] = f"[{r['mc_ci_95'][0]}, {r['mc_ci_95'][1]}]"
            row["fe_ci_95"] = f"[{r['fe_ci_95'][0]}, {r['fe_ci_95'][1]}]"
            writer.writerow(row)
    print(f"  Saved: {path}")


def write_scaling_plot(results: list, trend: dict):
    """Generate R(L) vs L and Δ(L) vs L publication plots."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    lengths = [r["L"] for r in results]
    deltas = [r["delta"] for r in results]
    mc_rates = [r["mc_rate"] for r in results]
    fe_rates = [r["fe_rate"] for r in results]
    ratios = [r["ratio"] if r["ratio"] != "inf" else None for r in results]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle("FE vs MC Scaling Behavior — 3D HP Lattice Protein Folding",
                 fontsize=14, fontweight="bold")

    # Plot 1: Absolute success rates
    ax1 = axes[0]
    ax1.plot(lengths, mc_rates, "o-", color="#1f77b4", label="Monte Carlo", linewidth=2)
    ax1.plot(lengths, fe_rates, "s-", color="#d62728", label="Forgetting Engine", linewidth=2)
    ax1.set_xlabel("Sequence Length L")
    ax1.set_ylabel("Success Rate (%)")
    ax1.set_title("Absolute Success Rates")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Δ(L) with trend line
    ax2 = axes[1]
    ax2.plot(lengths, deltas, "D-", color="#2ca02c", linewidth=2, label="Δ(L) = FE% − MC%")
    if trend["slope_b"] != 0:
        fit_x = np.linspace(min(lengths), max(lengths), 100)
        fit_y = trend["intercept_a"] + trend["slope_b"] * fit_x
        ax2.plot(fit_x, fit_y, "--", color="gray", alpha=0.7,
                 label=f"Fit: Δ = {trend['intercept_a']:.1f} + {trend['slope_b']:.3f}·L")
    ax2.set_xlabel("Sequence Length L")
    ax2.set_ylabel("Δ(L) = FE% − MC%")
    ax2.set_title("Success Rate Gap vs Length")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # Plot 3: R(L) = FE/MC ratio
    ax3 = axes[2]
    valid_ratios = [(l, r) for l, r in zip(lengths, ratios) if r is not None]
    if valid_ratios:
        r_lengths, r_vals = zip(*valid_ratios)
        ax3.plot(r_lengths, r_vals, "^-", color="#9467bd", linewidth=2, label="R(L) = FE% / MC%")
    ax3.set_xlabel("Sequence Length L")
    ax3.set_ylabel("R(L) = FE% / MC%")
    ax3.set_title("Relative Advantage Ratio")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "scaling_plot.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


def write_stats_summary(results: list, trend: dict, phase: str):
    """Write full stats JSON."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary = {
        "experiment_id": CONFIG["experiment_id"],
        "phase": phase,
        "per_length": results,
        "trend_test": trend,
        "config": CONFIG,
    }
    path = os.path.join(OUTPUT_DIR, "stats_summary.json")
    with open(path, "w") as f:
        json.dump(summary, f, indent=2, cls=NumpyEncoder)
    print(f"  Saved: {path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Analyze scaling study results")
    parser.add_argument("--phase", choices=["A", "B"], default="B",
                        help="Which phase data to analyze (default: B)")
    args = parser.parse_args()

    print("=" * 70)
    print(f"ANALYZING PHASE {args.phase} RESULTS")
    print("=" * 70)

    df = load_phase_data(args.phase)
    available_lengths = sorted(df["length"].unique())
    print(f"  Lengths found: {available_lengths}")
    print(f"  Total rows: {len(df)}")

    # Per-length analysis
    results = []
    for L in available_lengths:
        df_L = df[df["length"] == L]
        r = analyze_length(df_L, L)
        results.append(r)
        print(f"\n  L={L}: MC={r['mc_rate']}% FE={r['fe_rate']}% "
              f"Δ={r['delta']}% R={r['ratio']} d={r['cohens_d']} p={r['mann_whitney_p']:.6f}")

    # Trend test
    print("\n" + "-" * 70)
    trend = trend_test(results)
    print(f"  TREND: {trend['interpretation']}")
    if trend["p_permutation_one_sided"] < 0.05:
        print(f"  ** b > 0 is SIGNIFICANT (p_perm = {trend['p_permutation_one_sided']:.4f}) **")
    else:
        print(f"  b > 0 is NOT significant (p_perm = {trend['p_permutation_one_sided']:.4f})")

    # Write outputs
    print("\n" + "-" * 70)
    print("  Writing outputs...")
    write_scaling_table(results)
    write_scaling_plot(results, trend)
    write_stats_summary(results, trend, args.phase)

    # Print manuscript-ready table
    print("\n" + "=" * 70)
    print("MANUSCRIPT TABLE")
    print("=" * 70)
    print(f"{'L':>4} | {'MC%':>7} | {'FE%':>7} | {'Δ(L)':>7} | {'R(L)':>7} | {'d':>7} | {'p':>10}")
    print("-" * 70)
    for r in results:
        print(f"{r['L']:>4} | {r['mc_rate']:>6.1f}% | {r['fe_rate']:>6.1f}% | "
              f"{r['delta']:>6.1f}% | {str(r['ratio']):>7} | {r['cohens_d']:>7.3f} | "
              f"{r['mann_whitney_p']:>10.6f}")
    print("=" * 70)


if __name__ == "__main__":
    main()
