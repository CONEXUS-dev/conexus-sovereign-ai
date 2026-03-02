"""
Scaling harness: run baseline vs FE hybrid at n=50,100,200,400,800.
Outputs CSV + JSON summary.
"""

import csv
import json
import os
import time
from typing import List, Dict, Any

from .instance import generate_instance, auto_capacity
from .engine import FEEngine
from .baseline import baseline_solve
from .pilot import PilotAdapter


DEFAULT_SIZES = [50, 100, 200, 400, 800]


def run_scale(sizes: List[int] = None, seeds: int = 3,
              mode: str = "stub", llm_provider: str = "openai",
              max_gens: int = 200, pop_size: int = 20,
              output_dir: str = "results") -> List[Dict[str, Any]]:
    """
    Run scaling experiments.

    For each (n, seed):
      1. Generate instance
      2. Run baseline
      3. Run FE hybrid
      4. Compute gain %

    Returns list of result rows and writes CSV + JSON.
    """
    if sizes is None:
        sizes = DEFAULT_SIZES

    os.makedirs(output_dir, exist_ok=True)
    rows: List[Dict[str, Any]] = []

    for n in sizes:
        n_vehicles = max(3, n // 10)
        for s in range(seeds):
            seed = 42 + s
            cap = auto_capacity(n, n_vehicles, seed=seed)
            inst = generate_instance(n, n_vehicles, cap, seed=seed)

            print(f"\n{'='*60}")
            print(f"n={n}, vehicles={n_vehicles}, cap={cap}, seed={seed}")
            print(f"  demand={inst.total_demand}, capacity={inst.total_capacity}, "
                  f"feasible={inst.is_feasible}")
            print(f"{'='*60}")

            # Baseline
            print(f"\n  --- Baseline ---")
            bl = baseline_solve(inst, seed=seed, max_gens=max_gens, pop_size=pop_size)

            # FE Hybrid
            print(f"\n  --- FE Hybrid (mode={mode}) ---")
            pilot = PilotAdapter(mode=mode, llm_provider=llm_provider, seed=seed)
            engine = FEEngine(inst, pilot, seed=seed, max_gens=max_gens, pop_size=pop_size)
            fe = engine.run()

            # Gain
            bl_d = bl["best_distance"]
            fe_d = fe["best_distance"]
            gain_pct = ((bl_d - fe_d) / bl_d * 100) if bl_d > 0 else 0.0

            row = {
                "n": n,
                "seed": seed,
                "baseline_best": round(bl_d, 2),
                "baseline_feasible": bl["best_feasible"],
                "baseline_time": round(bl["elapsed"], 2),
                "hybrid_best": round(fe_d, 2),
                "hybrid_feasible": fe["best_feasible"],
                "hybrid_time": round(fe["elapsed"], 2),
                "gain_pct": round(gain_pct, 2),
                "paradox_size": fe["paradox_summary"]["size"],
            }
            rows.append(row)

            print(f"\n  RESULT: baseline={bl_d:.1f}  hybrid={fe_d:.1f}  "
                  f"gain={gain_pct:+.1f}%")

    # Write CSV
    csv_path = os.path.join(output_dir, "scale_results.csv")
    if rows:
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nCSV written: {csv_path}")

    # Write JSON summary
    summary = {
        "sizes": sizes,
        "seeds": seeds,
        "mode": mode,
        "results": rows,
    }
    json_path = os.path.join(output_dir, "scale_summary.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"JSON written: {json_path}")

    # Console summary
    print(f"\n{'='*70}")
    print(f"{'n':>6} {'seed':>5} {'baseline':>10} {'hybrid':>10} {'gain%':>8} {'bl_t':>6} {'fe_t':>6}")
    print(f"{'-'*70}")
    for r in rows:
        print(f"{r['n']:>6} {r['seed']:>5} {r['baseline_best']:>10.1f} "
              f"{r['hybrid_best']:>10.1f} {r['gain_pct']:>+7.1f}% "
              f"{r['baseline_time']:>5.1f}s {r['hybrid_time']:>5.1f}s")
    print(f"{'='*70}")

    return rows
