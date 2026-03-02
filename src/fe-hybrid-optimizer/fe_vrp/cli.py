"""
CLI entry points for FE-VRP Optimizer.

Usage:
  python -m fe_vrp.cli run --n 100 --vehicles 10 --seed 42 --mode stub
  python -m fe_vrp.cli scale --seeds 3 --mode stub
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

from .instance import generate_instance, auto_capacity
from .engine import FEEngine
from .baseline import baseline_solve
from .scale import run_scale
from .pilot import PilotAdapter


def _write_manifest(results: dict, args, output_dir: str = "results"):
    """Write demo_manifest.json with evidence-grade metadata."""
    os.makedirs(output_dir, exist_ok=True)
    manifest = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "params": {
            "n": args.n,
            "vehicles": getattr(args, "vehicles", None),
            "seed": args.seed,
            "mode": getattr(args, "mode", "stub"),
            "max_gens": args.max_gens,
            "pop_size": args.pop_size,
            "time_limit_s": getattr(args, "time_limit_s", None),
        },
        "best_distance": results.get("best_distance"),
        "best_feasible": results.get("best_feasible"),
        "best_overload": results.get("best_overload", 0),
        "generations": results.get("generations"),
        "elapsed": round(results.get("elapsed", 0), 3),
        "paradox_summary": results.get("paradox_summary"),
        "pilot_stats": results.get("pilot_stats"),
    }
    path = os.path.join(output_dir, "demo_manifest.json")
    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  Manifest written: {path}")


def cmd_run(args):
    """Run a single FE hybrid optimization."""
    n = args.n
    vehicles = args.vehicles or max(3, n // 10)
    seed = args.seed
    cap = args.capacity or auto_capacity(n, vehicles, seed=seed)

    inst = generate_instance(n, vehicles, cap, seed=seed)

    print("FE-VRP Optimizer \u2014 Single Run")
    print(f"{'='*50}")
    print(f"  Customers: {n}")
    print(f"  Vehicles:  {vehicles}")
    print(f"  Capacity:  {cap}")
    print(f"  Seed:      {seed}")
    print(f"  Mode:      {args.mode}")
    print(f"  Demand:    {inst.total_demand}")
    print(f"  Capacity:  {inst.total_capacity}")
    print(f"  Feasible:  {inst.is_feasible}")
    print(f"{'='*50}")

    pilot = PilotAdapter(mode=args.mode, llm_provider=args.llm_provider, seed=seed)
    pilot._prompt_variant = getattr(args, 'prompt_variant', 'current')

    # Calibration gate
    if args.mode == "llm" and args.calibrate:
        print("  [Calibration gate: --calibrate active]")
        pilot.calibrate_or_fail(retries=3)

    engine = FEEngine(
        inst, pilot, seed=seed,
        max_gens=args.max_gens, pop_size=args.pop_size,
        time_limit_s=args.time_limit_s,
        pilot_every=args.pilot_every,
    )

    results = engine.run()
    results["pilot_stats"] = pilot.stats()

    print(f"\n{'='*50}")
    print("RESULTS")
    print(f"{'='*50}")
    print(f"  Best distance: {results['best_distance']:.2f}")
    print(f"  Feasible:      {results['best_feasible']}")
    print(f"  Overload:      {results['best_overload']}")
    print(f"  Generations:   {results['generations']}")
    print(f"  Time:          {results['elapsed']:.2f}s")
    print(f"  Paradox buf:   {results['paradox_summary']}")
    print(f"  Pilot stats:   {results['pilot_stats']}")
    print(f"  Pilot calls:   {results.get('pilot_calls', '?')}")
    print(f"  Cache hits:    {results.get('cache_hits', '?')}")
    print(f"{'='*50}")

    _write_manifest(results, args)
    return results


def cmd_baseline(args):
    """Run baseline solver only."""
    n = args.n
    vehicles = args.vehicles or max(3, n // 10)
    seed = args.seed
    cap = args.capacity or auto_capacity(n, vehicles, seed=seed)

    inst = generate_instance(n, vehicles, cap, seed=seed)

    print("Baseline Solver \u2014 Single Run")
    print(f"  n={n}, vehicles={vehicles}, cap={cap}, seed={seed}")

    results = baseline_solve(inst, seed=seed, max_gens=args.max_gens, pop_size=args.pop_size)

    print(f"\n  Best distance: {results['best_distance']:.2f}")
    print(f"  Feasible:      {results['best_feasible']}")
    print(f"  Time:          {results['elapsed']:.2f}s")

    return results


def cmd_scale(args):
    """Run scaling experiments."""
    sizes = [int(x) for x in args.sizes.split(",")] if args.sizes else None
    run_scale(
        sizes=sizes,
        seeds=args.seeds,
        mode=args.mode,
        llm_provider=args.llm_provider,
        max_gens=args.max_gens,
        pop_size=args.pop_size,
        output_dir=args.output_dir,
    )


def main():
    parser = argparse.ArgumentParser(
        prog="fe_vrp",
        description="FE-VRP Optimizer: Hybrid Forgetting Engine + Calibrated Fleet Pilot",
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # --- run ---
    p_run = sub.add_parser("run", help="Run single FE hybrid optimization")
    p_run.add_argument("--n", type=int, default=100, help="Number of customers")
    p_run.add_argument("--vehicles", type=int, default=None, help="Number of vehicles (default: n/10)")
    p_run.add_argument("--capacity", type=int, default=None, help="Vehicle capacity (auto if omitted)")
    p_run.add_argument("--seed", type=int, default=42, help="Random seed")
    p_run.add_argument("--mode", choices=["stub", "llm"], default="stub", help="Pilot mode")
    p_run.add_argument("--llm_provider", default="openai", help="LLM provider (openai/anthropic/gemini)")
    p_run.add_argument("--max_gens", type=int, default=200, help="Max generations")
    p_run.add_argument("--pop_size", type=int, default=20, help="Population size")
    p_run.add_argument("--calibrate", action="store_true", help="Force calibration handshake before LLM steering")
    p_run.add_argument("--time_limit_s", type=float, default=None, help="Wall-clock time limit in seconds")
    p_run.add_argument("--pilot_every", type=int, default=1, help="Call pilot every k generations (reuse last decision otherwise)")
    p_run.add_argument("--prompt_variant", choices=["current", "regime"], default="current", help="Pilot prompt variant (current or regime)")

    # --- baseline ---
    p_bl = sub.add_parser("baseline", help="Run baseline solver only")
    p_bl.add_argument("--n", type=int, default=100, help="Number of customers")
    p_bl.add_argument("--vehicles", type=int, default=None)
    p_bl.add_argument("--capacity", type=int, default=None)
    p_bl.add_argument("--seed", type=int, default=42)
    p_bl.add_argument("--max_gens", type=int, default=200)
    p_bl.add_argument("--pop_size", type=int, default=20)

    # --- scale ---
    p_sc = sub.add_parser("scale", help="Run scaling experiments")
    p_sc.add_argument("--sizes", type=str, default=None, help="Comma-separated sizes (default: 50,100,200,400,800)")
    p_sc.add_argument("--seeds", type=int, default=3, help="Number of seeds per size")
    p_sc.add_argument("--mode", choices=["stub", "llm"], default="stub")
    p_sc.add_argument("--llm_provider", default="openai")
    p_sc.add_argument("--max_gens", type=int, default=200)
    p_sc.add_argument("--pop_size", type=int, default=20)
    p_sc.add_argument("--output_dir", default="results")
    p_sc.add_argument("--time_limit_s", type=float, default=None, help="Wall-clock time limit per run")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args)
    elif args.command == "baseline":
        cmd_baseline(args)
    elif args.command == "scale":
        cmd_scale(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
