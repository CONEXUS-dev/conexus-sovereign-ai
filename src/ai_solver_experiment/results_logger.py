"""
Results Logger — JSON, CSV, and convergence curve output.

Logs everything:
  - Every proposal, score, violation, feedback
  - Per-run metrics
  - Cross-condition comparisons
  - Convergence curves as CSV for plotting
"""

import csv
import json
import os
from datetime import datetime
from typing import Dict, Any, List


def ensure_dir(path: str):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def save_run_json(
    run_result: Dict[str, Any],
    run_metrics: Dict[str, Any],
    output_dir: str,
    condition: str,
    instance_name: str,
    seed: int,
) -> str:
    """
    Save full run data as JSON.
    Returns path to saved file.
    """
    ensure_dir(output_dir)

    # Strip raw_response from iteration log to keep file size manageable
    log_compact = []
    for entry in run_result.get("iteration_log", []):
        compact = {k: v for k, v in entry.items() if k != "raw_response"}
        # Keep first 200 chars of raw response for debugging
        raw = entry.get("raw_response", "")
        compact["raw_response_preview"] = raw[:200] if raw else ""
        log_compact.append(compact)

    data = {
        "condition": condition,
        "instance_name": instance_name,
        "seed": seed,
        "timestamp": datetime.now().isoformat(),
        "best_result": run_result.get("best_result"),
        "best_routes": run_result.get("best_routes"),
        "best_iteration": run_result.get("best_iteration"),
        "total_time_s": run_result.get("total_time_s"),
        "engine_stats": run_result.get("engine_stats"),
        "parse_failures": run_result.get("parse_failures"),
        "max_iterations": run_result.get("max_iterations"),
        "metrics": {
            k: v for k, v in run_metrics.items()
            if k not in ("variance_reduction", "fitness_series",
                         "violation_trend", "stagnation_periods")
        },
        "fitness_series": run_metrics.get("fitness_series", []),
        "iteration_log": log_compact,
    }

    filename = f"{condition}_{instance_name}_s{seed}.json"
    path = os.path.join(output_dir, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

    return path


def save_convergence_csv(
    all_runs: List[Dict[str, Any]],
    output_dir: str,
) -> str:
    """
    Save convergence curves as CSV.
    Columns: condition, instance, seed, iteration, fitness, distance, feasible
    """
    ensure_dir(output_dir)
    path = os.path.join(output_dir, "convergence_curves.csv")

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "condition", "instance", "seed", "iteration",
            "fitness", "distance", "feasible", "overload",
        ])

        for run in all_runs:
            condition = run.get("condition", "")
            instance = run.get("instance_name", "")
            seed = run.get("seed", 0)

            for entry in run.get("iteration_log", []):
                ev = entry.get("eval", {})
                writer.writerow([
                    condition, instance, seed,
                    entry.get("iteration", 0),
                    entry.get("fitness", ""),
                    ev.get("distance", ""),
                    ev.get("feasible", ""),
                    ev.get("overload", ""),
                ])

    return path


def save_diversity_csv(
    all_runs: List[Dict[str, Any]],
    output_dir: str,
) -> str:
    """
    Save proposal diversity data as CSV.
    Columns: condition, instance, seed, iteration, similarity_to_prev
    """
    ensure_dir(output_dir)
    path = os.path.join(output_dir, "diversity_metrics.csv")

    from .metrics import route_set_similarity

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "condition", "instance", "seed", "iteration",
            "similarity_to_prev", "change_magnitude",
        ])

        for run in all_runs:
            condition = run.get("condition", "")
            instance = run.get("instance_name", "")
            seed = run.get("seed", 0)
            log = run.get("iteration_log", [])

            for i, entry in enumerate(log):
                sim = ""
                change = ""
                if i > 0:
                    prev_routes = log[i - 1].get("routes", [])
                    curr_routes = entry.get("routes", [])
                    if prev_routes and curr_routes:
                        sim = route_set_similarity(prev_routes, curr_routes)
                        change = 1.0 - sim

                writer.writerow([
                    condition, instance, seed,
                    entry.get("iteration", 0),
                    sim, change,
                ])

    return path


def save_summary_csv(
    all_metrics: List[Dict[str, Any]],
    output_dir: str,
) -> str:
    """
    Save experiment summary as CSV.
    One row per run with key metrics.
    """
    ensure_dir(output_dir)
    path = os.path.join(output_dir, "experiment_summary.csv")

    fieldnames = [
        "condition", "instance", "seed",
        "best_fitness", "best_distance", "best_feasible", "best_iteration",
        "proposal_entropy", "unique_proposal_ratio", "avg_change_magnitude",
        "iterations_to_plateau", "improvement_slope",
        "escape_count", "avg_escape_delta",
        "violation_frequency",
        "pct_vs_baseline", "total_iterations",
        "parse_failures", "total_time_s",
    ]

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in all_metrics:
            row = {k: m.get(k, "") for k in fieldnames}
            writer.writerow(row)

    return path


def save_raw_responses(
    run_result: Dict[str, Any],
    output_dir: str,
    condition: str,
    instance_name: str,
    seed: int,
) -> str:
    """
    Save full raw LLM responses for forensic analysis.
    One file per run.
    """
    ensure_dir(os.path.join(output_dir, "raw_responses"))

    filename = f"{condition}_{instance_name}_s{seed}_raw.json"
    path = os.path.join(output_dir, "raw_responses", filename)

    entries = []
    for entry in run_result.get("iteration_log", []):
        entries.append({
            "iteration": entry.get("iteration"),
            "raw_response": entry.get("raw_response", ""),
            "parse_success": entry.get("parse_success"),
            "latency_s": entry.get("latency_s"),
        })

    with open(path, "w") as f:
        json.dump(entries, f, indent=2)

    return path


def print_experiment_summary(all_metrics: List[Dict[str, Any]]):
    """Print a formatted summary table to stdout."""
    print("\n" + "=" * 80)
    print("  EXPERIMENT SUMMARY")
    print("=" * 80)

    # Group by condition
    by_condition = {}
    for m in all_metrics:
        cond = m.get("condition", "unknown")
        by_condition.setdefault(cond, []).append(m)

    for cond, runs in sorted(by_condition.items()):
        print(f"\n  Condition: {cond.upper()}")
        print(f"  {'─' * 70}")

        dists = [r["best_distance"] for r in runs if r.get("best_distance")]
        feas = [r["best_feasible"] for r in runs]
        entropies = [r["proposal_entropy"] for r in runs if r.get("proposal_entropy") is not None]
        escapes = [r["escape_count"] for r in runs if r.get("escape_count") is not None]
        pcts = [r["pct_vs_baseline"] for r in runs if r.get("pct_vs_baseline") is not None]

        if dists:
            print(f"    Best distance:  mean={sum(dists)/len(dists):.2f}  "
                  f"min={min(dists):.2f}  max={max(dists):.2f}")
        if feas:
            print(f"    Feasible:       {sum(feas)}/{len(feas)}")
        if entropies:
            print(f"    Proposal entropy: mean={sum(entropies)/len(entropies):.3f}")
        if escapes:
            print(f"    Escape count:   mean={sum(escapes)/len(escapes):.1f}")
        if pcts:
            print(f"    % vs baseline:  mean={sum(pcts)/len(pcts):.2f}%")

    print("\n" + "=" * 80)
