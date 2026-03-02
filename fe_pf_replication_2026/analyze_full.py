"""Analyze V2 full scaling sweep results — all 9 lengths."""

import csv
import json
import os
import numpy as np
from scipy import stats as sp_stats

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")

LENGTHS = [20, 25, 30, 35, 40, 45, 50, 75, 100]


def load_phase_b(length):
    mc_e, fe_e = [], []
    mc_succ, fe_succ = 0, 0
    mc_par, fe_par = [], []
    path = os.path.join(RESULTS_DIR, f"phase_B_L{length}.csv")
    with open(path) as f:
        for row in csv.DictReader(f):
            e = float(row["final_energy"])
            s = int(row["success_flag"])
            p = int(row["paradox_activity"])
            if row["algorithm"] == "MC":
                mc_e.append(e)
                mc_succ += s
                mc_par.append(p)
            else:
                fe_e.append(e)
                fe_succ += s
                fe_par.append(p)
    return {
        "mc_e": np.array(mc_e), "fe_e": np.array(fe_e),
        "mc_succ": mc_succ, "fe_succ": fe_succ,
        "n_mc": len(mc_e), "n_fe": len(fe_e),
        "fe_par": np.array(fe_par),
    }


def main():
    with open(os.path.join(RESULTS_DIR, "pilot_thresholds.json")) as f:
        thresholds = json.load(f)

    print("=" * 95)
    print("V2 FULL SCALING SWEEP RESULTS — ALL 9 LENGTHS")
    print("=" * 95)
    print()

    print("Thresholds (Phase A):")
    for L in LENGTHS:
        print(f"  E*({L}) = {thresholds[str(L)]}")
    print()

    rows = []
    for L in LENGTHS:
        d = load_phase_b(L)
        mc_rate = d["mc_succ"] / d["n_mc"] * 100
        fe_rate = d["fe_succ"] / d["n_fe"] * 100
        delta = fe_rate - mc_rate

        pooled_std = np.sqrt((d["mc_e"].std()**2 + d["fe_e"].std()**2) / 2)
        cohens_d = (d["mc_e"].mean() - d["fe_e"].mean()) / pooled_std if pooled_std > 0 else 0

        u_stat, p_val = sp_stats.mannwhitneyu(d["fe_e"], d["mc_e"], alternative="less")

        par_mean = d["fe_par"].mean()

        rows.append({
            "L": L, "mc_rate": mc_rate, "fe_rate": fe_rate,
            "delta": delta, "cohens_d": cohens_d, "p_val": p_val,
            "mc_mean_e": d["mc_e"].mean(), "fe_mean_e": d["fe_e"].mean(),
            "par_mean": par_mean, "n_mc": d["n_mc"], "n_fe": d["n_fe"],
        })

    # Print table
    print(f"{'L':>4} | {'N':>5} | {'MC%':>7} | {'FE%':>7} | {'D(FE-MC)':>9} | {'MC<E>':>8} | {'FE<E>':>8} | {'d':>7} | {'p(MW)':>12} | {'Paradox':>7}")
    print("-" * 100)
    for r in rows:
        p_str = f"{r['p_val']:.6f}" if r["p_val"] >= 0.000001 else "<0.000001"
        print(f"{r['L']:>4} | {r['n_mc']+r['n_fe']:>5} | {r['mc_rate']:>6.1f}% | {r['fe_rate']:>6.1f}% | {r['delta']:>+8.1f}% | {r['mc_mean_e']:>8.2f} | {r['fe_mean_e']:>8.2f} | {r['cohens_d']:>7.2f} | {p_str:>12} | {r['par_mean']:>7.1f}")
    print()

    # === TREND TEST: L=20-50 only (original validated range) ===
    rows_orig = [r for r in rows if r["L"] <= 50]
    deltas_orig = np.array([r["delta"] for r in rows_orig])
    ls_orig = np.array([r["L"] for r in rows_orig])
    slope_o, intercept_o, r_val_o, p_val_o, std_err_o = sp_stats.linregress(ls_orig, deltas_orig)

    print("TREND TEST — ORIGINAL RANGE (L=20-50):")
    print(f"  D(L) = {intercept_o:.2f} + {slope_o:.4f} * L")
    print(f"  R^2 = {r_val_o**2:.3f}, p = {p_val_o:.6f}, slope = {slope_o:.4f} +/- {std_err_o:.4f}")

    rng = np.random.RandomState(42)
    count = sum(1 for _ in range(10000) if sp_stats.linregress(ls_orig, rng.permutation(deltas_orig))[0] >= slope_o)
    p_perm_o = count / 10000
    print(f"  Permutation test (10,000): p_perm = {p_perm_o:.4f}")
    print()

    # === TREND TEST: Full range L=20-100 ===
    deltas_all = np.array([r["delta"] for r in rows])
    ls_all = np.array([r["L"] for r in rows])
    slope_a, intercept_a, r_val_a, p_val_a, std_err_a = sp_stats.linregress(ls_all, deltas_all)

    print("TREND TEST — EXTENDED RANGE (L=20-100):")
    print(f"  D(L) = {intercept_a:.2f} + {slope_a:.4f} * L")
    print(f"  R^2 = {r_val_a**2:.3f}, p = {p_val_a:.6f}, slope = {slope_a:.4f} +/- {std_err_a:.4f}")

    rng2 = np.random.RandomState(42)
    count2 = sum(1 for _ in range(10000) if sp_stats.linregress(ls_all, rng2.permutation(deltas_all))[0] >= slope_a)
    p_perm_a = count2 / 10000
    print(f"  Permutation test (10,000): p_perm = {p_perm_a:.4f}")
    print()

    # === ENERGY GAP ANALYSIS ===
    print("ENERGY GAP ANALYSIS (MC_mean - FE_mean, negative = MC better):")
    print(f"{'L':>4} | {'MC<E>':>8} | {'FE<E>':>8} | {'Gap':>8} | {'Who Wins':>10}")
    print("-" * 50)
    for r in rows:
        gap = r["mc_mean_e"] - r["fe_mean_e"]
        who = "MC" if gap < 0 else "FE" if gap > 0 else "Tied"
        print(f"{r['L']:>4} | {r['mc_mean_e']:>8.2f} | {r['fe_mean_e']:>8.2f} | {gap:>+8.2f} | {who:>10}")
    print()

    # Energy gap trend
    gaps = np.array([r["mc_mean_e"] - r["fe_mean_e"] for r in rows])
    slope_g, intercept_g, r_val_g, p_val_g, std_err_g = sp_stats.linregress(ls_all, gaps)
    print(f"  Energy gap trend: gap(L) = {intercept_g:.2f} + {slope_g:.4f} * L")
    print(f"  R^2 = {r_val_g**2:.3f}, p = {p_val_g:.6f}")
    if slope_g < 0:
        print("  --> MC's energy advantage GROWS with L (gap becomes more negative)")
    else:
        print("  --> MC's energy advantage SHRINKS with L (gap trends toward 0 or positive)")
    print()

    # === MC's lead on success rate ===
    print("MC's SUCCESS RATE LEAD BY LENGTH:")
    print(f"{'L':>4} | {'MC Lead':>8}")
    print("-" * 20)
    for r in rows:
        print(f"{r['L']:>4} | {-r['delta']:>7.1f}%")
    print()

    # === SUMMARY ===
    print("=" * 95)
    print("SUMMARY")
    print("=" * 95)
    total_trials = sum(r["n_mc"] + r["n_fe"] for r in rows)
    print(f"Total trials: {total_trials}")
    print()
    print(f"L=20-50 CAE trend: slope={slope_o:.4f}, p_perm={p_perm_o:.4f} {'(SIGNIFICANT)' if p_perm_o < 0.05 else '(not significant)'}")
    print(f"L=20-100 CAE trend: slope={slope_a:.4f}, p_perm={p_perm_a:.4f} {'(SIGNIFICANT)' if p_perm_a < 0.05 else '(not significant)'}")
    print(f"Energy gap trend: slope={slope_g:.4f}, p={p_val_g:.6f}")
    print()

    if slope_o > 0 and p_perm_o < 0.05:
        print("L=20-50: CAE CONFIRMED — MC's lead shrinks with complexity.")
    else:
        print("L=20-50: No significant CAE trend.")

    if slope_a > 0 and p_perm_a < 0.05:
        print("L=20-100: CAE CONFIRMED across extended range.")
    elif slope_a > 0:
        print("L=20-100: Positive trend but NOT statistically significant.")
    else:
        print("L=20-100: No CAE — MC maintains or extends advantage.")
    print("=" * 95)


if __name__ == "__main__":
    main()
