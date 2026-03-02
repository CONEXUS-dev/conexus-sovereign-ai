"""
Benchmark harness for multi-seed paired A/B/C comparisons.

Usage:
  python -m fe_vrp.benchmark --conditions stub,llm --seeds 10 --n 100
  python -m fe_vrp.benchmark --conditions stub,llm,llm-regime --seeds 10 --n 100
"""

import argparse
import csv
import json
import os
import statistics
from datetime import datetime, timezone

from .instance import generate_instance, auto_capacity
from .engine import FEEngine
from .pilot import PilotAdapter


def run_single(n: int, seed: int, mode: str, llm_provider: str,
               max_gens: int, pop_size: int, pilot_every: int,
               calibrate: bool, prompt_variant: str = "current") -> dict:
    """Run a single benchmark trial. Returns metrics dict."""
    vehicles = max(3, n // 10)
    cap = auto_capacity(n, vehicles, seed=seed)
    inst = generate_instance(n, vehicles, cap, seed=seed)

    pilot = PilotAdapter(mode=mode, llm_provider=llm_provider, seed=seed)

    # Tag prompt variant on the pilot for regime prompt switching
    pilot._prompt_variant = prompt_variant

    if mode == "llm" and calibrate:
        pilot.calibrate_or_fail(retries=3)

    engine = FEEngine(
        inst, pilot, seed=seed,
        max_gens=max_gens, pop_size=pop_size,
        pilot_every=pilot_every,
    )

    results = engine.run()
    pstats = pilot.stats()

    return {
        "seed": seed,
        "condition": f"{mode}" if mode == "stub" else f"{mode}-{prompt_variant}",
        "n": n,
        "best_distance": round(results["best_distance"], 2),
        "feasible": results["best_feasible"],
        "overload": results["best_overload"],
        "generations": results["generations"],
        "elapsed": round(results["elapsed"], 2),
        "pilot_calls": results.get("pilot_calls", 0),
        "cache_hits": results.get("cache_hits", 0),
        "llm_decisions": pstats.get("llm_decisions", 0),
        "llm_fallbacks": pstats.get("llm_fallbacks", 0),
        "pilot_call_log": results.get("pilot_call_log", []),
    }


def run_benchmark(conditions: list, seeds: list, n: int,
                  llm_provider: str, max_gens: int, pop_size: int,
                  pilot_every: int, output_dir: str,
                  prompt_variant_override: str = None):
    """Run full benchmark across conditions and seeds.
    
    Each completed seed flushes to CSV and JSON immediately.
    """
    os.makedirs(output_dir, exist_ok=True)
    all_results = []
    total_runs = len(conditions) * len(seeds)
    run_idx = 0

    csv_path = os.path.join(output_dir, "benchmark_results.csv")
    csv_fields = [
        "seed", "condition", "n", "best_distance", "feasible", "overload",
        "generations", "elapsed", "pilot_calls", "cache_hits",
        "llm_decisions", "llm_fallbacks",
    ]
    # Write CSV header
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()

    for condition in conditions:
        for seed in seeds:
            run_idx += 1
            # Parse condition
            if condition == "stub":
                mode, calibrate, prompt_variant = "stub", False, "current"
            elif condition == "llm-current":
                mode, calibrate, prompt_variant = "llm", True, "current"
            elif condition == "llm-regime":
                mode, calibrate, prompt_variant = "llm", True, "regime"
            else:
                print(f"Unknown condition: {condition}, skipping")
                continue

            # Allow CLI override of prompt_variant
            if prompt_variant_override:
                prompt_variant = prompt_variant_override

            print(f"\n[{run_idx}/{total_runs}] condition={condition} seed={seed}")
            try:
                result = run_single(
                    n=n, seed=seed, mode=mode,
                    llm_provider=llm_provider,
                    max_gens=max_gens, pop_size=pop_size,
                    pilot_every=pilot_every,
                    calibrate=calibrate,
                    prompt_variant=prompt_variant,
                )
                all_results.append(result)
                print(f"  -> dist={result['best_distance']} "
                      f"feasible={result['feasible']} "
                      f"time={result['elapsed']}s "
                      f"fallbacks={result['llm_fallbacks']}")
            except Exception as e:
                print(f"  -> ERROR: {e}")
                all_results.append({
                    "seed": seed,
                    "condition": condition,
                    "n": n,
                    "best_distance": None,
                    "feasible": None,
                    "overload": None,
                    "generations": None,
                    "elapsed": None,
                    "pilot_calls": 0,
                    "cache_hits": 0,
                    "llm_decisions": 0,
                    "llm_fallbacks": 0,
                    "pilot_call_log": [],
                    "error": str(e),
                })

            # Flush this seed to CSV immediately
            with open(csv_path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
                writer.writerow(all_results[-1])

            # Flush full JSON after each seed
            json_path = os.path.join(output_dir, "benchmark_results.json")
            with open(json_path, "w") as f:
                json.dump({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "params": {
                        "n": n, "max_gens": max_gens, "pop_size": pop_size,
                        "pilot_every": pilot_every, "conditions": conditions,
                        "seeds": seeds, "llm_provider": llm_provider,
                    },
                    "results": all_results,
                }, f, indent=2)

    print(f"\nCSV written: {csv_path}")
    json_path = os.path.join(output_dir, "benchmark_results.json")
    print(f"JSON written: {json_path}")

    # Compute and print aggregate stats
    print(f"\n{'='*60}")
    print("AGGREGATE STATS")
    print(f"{'='*60}")
    for condition in conditions:
        cond_results = [r for r in all_results
                        if r["condition"] == condition and r["best_distance"] is not None]
        if not cond_results:
            print(f"\n  {condition}: no valid results")
            continue
        dists = [r["best_distance"] for r in cond_results]
        times = [r["elapsed"] for r in cond_results]
        fallbacks = sum(r["llm_fallbacks"] for r in cond_results)
        feasible_count = sum(1 for r in cond_results if r["feasible"])
        print(f"\n  {condition} ({len(cond_results)} runs):")
        print(f"    Distance: median={statistics.median(dists):.2f} "
              f"mean={statistics.mean(dists):.2f} "
              f"std={statistics.stdev(dists):.2f}" if len(dists) > 1 else
              f"    Distance: {dists[0]:.2f}")
        print(f"    Runtime:  median={statistics.median(times):.2f}s "
              f"mean={statistics.mean(times):.2f}s")
        print(f"    Feasible: {feasible_count}/{len(cond_results)}")
        print(f"    Fallbacks: {fallbacks}")

    # Win-rate comparisons
    cond_names = list(set(r["condition"] for r in all_results if r["best_distance"] is not None))
    if len(cond_names) >= 2:
        print(f"\n{'='*60}")
        print("WIN-RATE COMPARISONS")
        print(f"{'='*60}")
        for i, c1 in enumerate(cond_names):
            for c2 in cond_names[i+1:]:
                wins_c1, wins_c2, ties = 0, 0, 0
                for seed in seeds:
                    r1 = next((r for r in all_results if r["condition"] == c1 and r["seed"] == seed and r["best_distance"] is not None), None)
                    r2 = next((r for r in all_results if r["condition"] == c2 and r["seed"] == seed and r["best_distance"] is not None), None)
                    if r1 and r2:
                        if r1["best_distance"] < r2["best_distance"]:
                            wins_c1 += 1
                        elif r2["best_distance"] < r1["best_distance"]:
                            wins_c2 += 1
                        else:
                            ties += 1
                total = wins_c1 + wins_c2 + ties
                if total > 0:
                    print(f"  {c1} vs {c2}: {c1} wins {wins_c1}/{total} ({100*wins_c1/total:.0f}%), "
                          f"{c2} wins {wins_c2}/{total} ({100*wins_c2/total:.0f}%), ties {ties}")

    return all_results


def main():
    parser = argparse.ArgumentParser(description="FE-VRP Benchmark Harness")
    parser.add_argument("--conditions", type=str, default="stub,llm-current",
                        help="Comma-separated conditions: stub, llm-current, llm-regime")
    parser.add_argument("--seeds", type=int, default=10, help="Number of seeds (0..N-1)")
    parser.add_argument("--n", type=int, default=100, help="Number of customers")
    parser.add_argument("--llm_provider", default="anthropic", help="LLM provider (anthropic/gemini)")
    parser.add_argument("--max_gens", type=int, default=80, help="Max generations")
    parser.add_argument("--pop_size", type=int, default=15, help="Population size")
    parser.add_argument("--pilot_every", type=int, default=5, help="Pilot call frequency")
    parser.add_argument("--prompt_variant", choices=["current", "regime"], default=None,
                        help="Override prompt variant for all LLM conditions")
    parser.add_argument("--output_dir", default="results", help="Output directory")
    args = parser.parse_args()

    conditions = [c.strip() for c in args.conditions.split(",")]
    seeds = list(range(args.seeds))

    run_benchmark(
        conditions=conditions,
        seeds=seeds,
        n=args.n,
        llm_provider=args.llm_provider,
        max_gens=args.max_gens,
        pop_size=args.pop_size,
        pilot_every=args.pilot_every,
        output_dir=args.output_dir,
        prompt_variant_override=args.prompt_variant,
    )


if __name__ == "__main__":
    main()
