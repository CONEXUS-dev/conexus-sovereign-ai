"""
Experiment Runner — CLI interface for the controlled ECP calibration study.

Runs 3 conditions:
  A) Deterministic baseline (Clarke-Wright)
  B) AI Uncalibrated Loop
  C) AI Calibrated Loop (ECP)

Fixed seeds, fixed iteration budget, identical evaluation logic.
Logs everything.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

from .vrp_instance import generate_instance, VRPInstance
from .baseline import clarke_wright_solve
from .ai_proposal_engine import AIProposalEngine
from .iterative_loop import run_ai_loop
from .metrics import compute_run_metrics
from .results_logger import (
    save_run_json,
    save_convergence_csv,
    save_diversity_csv,
    save_summary_csv,
    save_raw_responses,
    print_experiment_summary,
    ensure_dir,
)


def run_baseline(instance: VRPInstance, verbose: bool = True) -> Dict[str, Any]:
    """Run Clarke-Wright baseline (Condition A)."""
    if verbose:
        print(f"\n{'='*60}")
        print(f"  Baseline: Clarke-Wright | {instance.name}")
        print(f"{'='*60}")

    t0 = time.time()
    result = clarke_wright_solve(instance)
    elapsed = time.time() - t0

    if verbose:
        print(f"  Distance: {result['distance']:.2f}")
        print(f"  Feasible: {result['feasible']}")
        print(f"  Time: {elapsed:.3f}s")

    result["total_time_s"] = elapsed
    result["condition"] = "baseline"
    result["instance_name"] = instance.name
    return result


def run_experiment(
    instance_sizes: List[int],
    seeds: List[int],
    max_iterations: int,
    provider: str,
    model: str,
    output_dir: str,
    pacing_delay: float,
    conditions: List[str],
    temperature: float = 0.7,
    max_tokens: int = 8192,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Run the full experiment across all conditions, sizes, and seeds.

    Args:
        instance_sizes: list of n_customers values (e.g. [100, 200, 500])
        seeds: list of random seeds
        max_iterations: iteration budget per AI run
        provider: LLM provider name
        model: LLM model name (or None for default)
        output_dir: directory for results
        pacing_delay: seconds between LLM calls
        conditions: list of conditions to run (baseline, uncalibrated, calibrated)
        verbose: print progress

    Returns:
        dict with all results and metrics
    """
    ensure_dir(output_dir)

    # Save experiment config
    config = {
        "instance_sizes": instance_sizes,
        "seeds": seeds,
        "max_iterations": max_iterations,
        "provider": provider,
        "model": model,
        "conditions": conditions,
        "pacing_delay": pacing_delay,
        "temperature": temperature,
        "timestamp": datetime.now().isoformat(),
    }
    with open(os.path.join(output_dir, "experiment_config.json"), "w") as f:
        json.dump(config, f, indent=2)

    all_runs = []       # raw run results
    all_metrics = []    # computed metrics per run
    baseline_cache = {} # (n, seed) -> baseline distance

    total_runs = 0
    for n in instance_sizes:
        for seed in seeds:
            for cond in conditions:
                total_runs += 1

    run_num = 0

    for n in instance_sizes:
        for seed in seeds:
            # Generate instance (deterministic)
            instance = generate_instance(n_customers=n, seed=seed)

            if verbose:
                print(f"\n{'#'*60}")
                print(f"  Instance: {instance.name}")
                print(f"  Customers: {n}, Vehicles: {instance.n_vehicles}, "
                      f"Capacity: {instance.capacity}")
                print(f"  Total demand: {instance.total_demand}, "
                      f"Total capacity: {instance.total_capacity}")
                print(f"{'#'*60}")

            # Save instance
            instance.save(os.path.join(output_dir, f"{instance.name}.json"))

            # ── Condition A: Baseline ──
            if "baseline" in conditions:
                run_num += 1
                if verbose:
                    print(f"\n  [{run_num}/{total_runs}] Baseline")

                bl_result = run_baseline(instance, verbose)
                baseline_dist = bl_result["distance"]
                baseline_cache[(n, seed)] = baseline_dist

                # Metrics for baseline (trivial — single iteration)
                bl_metrics = {
                    "condition": "baseline",
                    "instance": instance.name,
                    "seed": seed,
                    "best_fitness": bl_result["fitness"],
                    "best_distance": bl_result["distance"],
                    "best_feasible": bl_result["feasible"],
                    "best_iteration": 0,
                    "proposal_entropy": 0.0,
                    "unique_proposal_ratio": 1.0,
                    "avg_change_magnitude": 0.0,
                    "iterations_to_plateau": 0,
                    "improvement_slope": 0.0,
                    "escape_count": 0,
                    "avg_escape_delta": 0.0,
                    "violation_frequency": 0.0 if bl_result["feasible"] else 1.0,
                    "pct_vs_baseline": 0.0,
                    "total_iterations": 1,
                    "parse_failures": 0,
                    "total_time_s": bl_result["total_time_s"],
                }
                all_metrics.append(bl_metrics)

                # Save baseline result
                save_run_json(
                    {"iteration_log": [{"iteration": 0, "routes": bl_result["routes"],
                     "eval": bl_result, "fitness": bl_result["fitness"]}],
                     "best_result": bl_result, "best_routes": bl_result["routes"],
                     "best_iteration": 0, "total_time_s": bl_result["total_time_s"],
                     "engine_stats": {}, "parse_failures": 0,
                     "max_iterations": 1},
                    bl_metrics, output_dir, "baseline", instance.name, seed,
                )

            # Get baseline distance for comparison
            baseline_dist = baseline_cache.get((n, seed))
            if baseline_dist is None:
                # Run baseline just for comparison even if not in conditions
                bl = clarke_wright_solve(instance)
                baseline_dist = bl["distance"]
                baseline_cache[(n, seed)] = baseline_dist

            # ── Condition B: AI Uncalibrated ──
            if "uncalibrated" in conditions:
                run_num += 1
                if verbose:
                    print(f"\n  [{run_num}/{total_runs}] AI Uncalibrated")

                engine = AIProposalEngine(
                    provider=provider, model=model,
                    max_tokens=max_tokens,
                    pacing_delay=pacing_delay,
                    temperature=temperature,
                )

                loop_result = run_ai_loop(
                    instance=instance,
                    engine=engine,
                    max_iterations=max_iterations,
                    calibrated=False,
                    verbose=verbose,
                )
                loop_result["seed"] = seed

                metrics = compute_run_metrics(
                    loop_result["iteration_log"], baseline_dist,
                )
                metrics["condition"] = "uncalibrated"
                metrics["instance"] = instance.name
                metrics["seed"] = seed
                metrics["parse_failures"] = loop_result["parse_failures"]
                metrics["total_time_s"] = loop_result["total_time_s"]

                all_runs.append(loop_result)
                all_metrics.append(metrics)

                save_run_json(loop_result, metrics, output_dir,
                              "uncalibrated", instance.name, seed)
                save_raw_responses(loop_result, output_dir,
                                   "uncalibrated", instance.name, seed)

            # ── Condition C: AI Calibrated ──
            if "calibrated" in conditions:
                run_num += 1
                if verbose:
                    print(f"\n  [{run_num}/{total_runs}] AI Calibrated (ECP)")

                engine = AIProposalEngine(
                    provider=provider, model=model,
                    max_tokens=max_tokens,
                    pacing_delay=pacing_delay,
                    temperature=temperature,
                )

                loop_result = run_ai_loop(
                    instance=instance,
                    engine=engine,
                    max_iterations=max_iterations,
                    calibrated=True,
                    verbose=verbose,
                )
                loop_result["seed"] = seed

                metrics = compute_run_metrics(
                    loop_result["iteration_log"], baseline_dist,
                )
                metrics["condition"] = "calibrated"
                metrics["instance"] = instance.name
                metrics["seed"] = seed
                metrics["parse_failures"] = loop_result["parse_failures"]
                metrics["total_time_s"] = loop_result["total_time_s"]

                all_runs.append(loop_result)
                all_metrics.append(metrics)

                save_run_json(loop_result, metrics, output_dir,
                              "calibrated", instance.name, seed)
                save_raw_responses(loop_result, output_dir,
                                   "calibrated", instance.name, seed)

    # ── Save aggregate outputs ──
    if all_runs:
        save_convergence_csv(all_runs, output_dir)
        save_diversity_csv(all_runs, output_dir)

    save_summary_csv(all_metrics, output_dir)

    if verbose:
        print_experiment_summary(all_metrics)

    # Save full experiment results
    summary_path = os.path.join(output_dir, "experiment_results.json")
    with open(summary_path, "w") as f:
        json.dump({
            "config": config,
            "metrics": all_metrics,
            "baseline_distances": {f"n{k[0]}_s{k[1]}": v
                                   for k, v in baseline_cache.items()},
        }, f, indent=2, default=str)

    return {
        "config": config,
        "all_metrics": all_metrics,
        "all_runs": all_runs,
        "baseline_cache": baseline_cache,
    }


# ── CLI ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Solver Experiment — Controlled ECP Calibration Study",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick smoke test (1 seed, n=20, 5 iterations)
  python -m ai_solver_experiment --sizes 20 --seeds 1 --iterations 5

  # Full experiment
  python -m ai_solver_experiment --sizes 100,200,500 --seeds 5 --iterations 50

  # Specific conditions only
  python -m ai_solver_experiment --sizes 100 --seeds 3 --conditions baseline,calibrated

  # Use Gemini instead of Anthropic
  python -m ai_solver_experiment --provider gemini --sizes 100 --seeds 3
        """,
    )

    parser.add_argument(
        "--sizes", type=str, default="100,200,500",
        help="Comma-separated instance sizes (default: 100,200,500)",
    )
    parser.add_argument(
        "--seeds", type=str, default="5",
        help="Number of seeds (e.g. 5) or comma-separated seed list (e.g. 2,3)",
    )
    parser.add_argument(
        "--iterations", type=int, default=50,
        help="Iteration budget per AI run (default: 50)",
    )
    parser.add_argument(
        "--provider", type=str, default="gemini",
        choices=["anthropic", "openai", "gemini"],
        help="LLM provider (default: gemini)",
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help="LLM model override (default: provider default)",
    )
    parser.add_argument(
        "--output", type=str, default="results/ecp_experiment",
        help="Output directory (default: results/ecp_experiment)",
    )
    parser.add_argument(
        "--pacing", type=float, default=1.0,
        help="Seconds between LLM calls (default: 1.0)",
    )
    parser.add_argument(
        "--conditions", type=str, default="baseline,uncalibrated,calibrated",
        help="Comma-separated conditions to run (default: all three)",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.7,
        help="LLM temperature, fixed across conditions (default: 0.7)",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=8192,
        help="Max output tokens per LLM call (default: 8192, increase for thinking models)",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress verbose output",
    )

    args = parser.parse_args()

    sizes = [int(s.strip()) for s in args.sizes.split(",")]
    conditions = [c.strip() for c in args.conditions.split(",")]
    seed_list = [int(s.strip()) for s in str(args.seeds).split(",")]
    # If a single integer was given, treat it as a count (backward compat)
    if len(seed_list) == 1 and "," not in str(args.seeds):
        seed_list = list(range(1, seed_list[0] + 1))

    print("=" * 60)
    print("  AI SOLVER EXPERIMENT")
    print("  Controlled ECP Calibration Behavioral Study")
    print("=" * 60)
    print(f"  Sizes:      {sizes}")
    print(f"  Seeds:      {seed_list}")
    print(f"  Iterations: {args.iterations}")
    print(f"  Provider:   {args.provider}")
    print(f"  Model:      {args.model or 'default'}")
    print(f"  Conditions: {conditions}")
    print(f"  Temp:       {args.temperature}")
    print(f"  Output:     {args.output}")
    print("=" * 60)

    run_experiment(
        instance_sizes=sizes,
        seeds=seed_list,
        max_iterations=args.iterations,
        provider=args.provider,
        model=args.model,
        output_dir=args.output,
        pacing_delay=args.pacing,
        conditions=conditions,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        verbose=not args.quiet,
    )


if __name__ == "__main__":
    main()
