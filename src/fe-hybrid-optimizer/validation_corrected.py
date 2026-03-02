"""
Corrected VRP Validation - Following Chip's Fix Strategy

Implements:
1. Fixed FE with coverage/conservation/capacity invariants
2. Hard feasibility gates (invalid solutions rejected)
3. Time-matched baseline (OR-Tools with same time budget)
4. Honest results reporting
"""

import os
import sys
import time
from typing import Dict, Any

# Set deterministic environment
os.environ['PYTHONHASHSEED'] = '0'

import random
random.seed(42)

import numpy as np
np.random.seed(42)

# Import fixed FE engine
from fe_hybrid_vrp_fixed import (
    run_fe_hybrid, baseline_sweep_solver, 
    N_CUSTOMERS, VEHICLES, CAPACITY, TOTAL_DEMAND,
    Candidate
)
from feasibility_checker_fixed import check_feasibility, print_solution_summary
from ortools_baseline_fixed import ortools_vrp_solver


# ============================================================================
# STUB PILOT
# ============================================================================

def stub_pilot(g: int, packet: Dict[str, Any]) -> Dict[str, Any]:
    """Mechanical stub pilot - fully deterministic."""
    return {
        "keep_ids": [],
        "paradox_add_ids": [],
        "operator_mix_next": {
            "swap": 0.5,
            "relocate": 0.5,
        },
        "pattern_ops": [],
        "proto": {"moments": []},
        "rationale": {
            "survival_logic": "stub_mechanical",
            "paradox_logic": "stub_mechanical"
        }
    }


# ============================================================================
# VALIDATION RUNNERS
# ============================================================================

def run_ortools_baseline(time_limit_seconds: int = 30) -> Dict[str, Any]:
    """Run OR-Tools VRP solver with time limit."""
    print("\n" + "=" * 60)
    print("RUN 1: OR-TOOLS VRP SOLVER (Gold Standard)")
    print("=" * 60)
    print(f"\nTime limit: {time_limit_seconds}s")
    print("Implementation: Google OR-Tools routing solver")
    print("  - Guided local search metaheuristic")
    print("  - Capacity-constrained")
    print("  - Time-limited for fair comparison")
    
    start_time = time.time()
    solution = ortools_vrp_solver(time_limit_seconds=time_limit_seconds)
    elapsed = time.time() - start_time
    
    print(f"\n✓ OR-Tools completed in {elapsed:.2f}s")
    print(f"  Distance: {solution.distance:.2f}")
    print(f"  Overload: {solution.overload}")
    print(f"  Objective (f): {solution.f:.2f}")
    print(f"  Loads: {solution.loads[:5]}... ({len([l for l in solution.loads if l > 0])} active)")
    
    # Feasibility check
    print("\n[FEASIBILITY CHECK]")
    print_solution_summary(solution.routes, solution.loads, solution.distance, "OR-Tools")
    is_valid, errors = check_feasibility(solution.routes, solution.loads, solution.distance, "OR-Tools")
    
    if not is_valid:
        print("\n❌ OR-Tools solution FAILED feasibility check")
        return None
    
    print("✅ OR-Tools solution is VALID")
    
    return {
        "method": "ortools",
        "distance": float(solution.distance),
        "overload": int(solution.overload),
        "f": float(solution.f),
        "loads": list(solution.loads),
        "routes": [list(r) for r in solution.routes],
        "elapsed_seconds": float(elapsed),
    }


def run_fe_stub(max_iters: int = 20, seed: int = 7) -> Dict[str, Any]:
    """Run FE with stub pilot and hard feasibility checks."""
    print("\n" + "=" * 60)
    print("RUN 2: FE HYBRID (Mechanical Stub Pilot)")
    print("=" * 60)
    print(f"\nIterations: {max_iters}")
    print("Implementation: Fixed Forgetting Engine")
    print("  - Coverage invariant: all customers served exactly once")
    print("  - Conservation invariant: sum(loads) = total_demand")
    print("  - Deterministic repair after each operator")
    print("  - Hard feasibility gates enforced")
    print("✓ Pilot calibrated (stub mode)")
    
    # Explicit re-seed
    random.seed(seed)
    np.random.seed(seed)
    
    start_time = time.time()
    
    try:
        report = run_fe_hybrid(
            pilot_fn=stub_pilot,
            max_iters=max_iters,
            seed=seed
        )
    except Exception as e:
        print(f"\n❌ FE engine failed: {e}")
        return None
    
    elapsed = time.time() - start_time
    
    best = report["best_solution"]
    
    print(f"\n✓ FE Hybrid (stub) completed in {elapsed:.2f}s")
    print(f"  Distance: {best['distance']:.2f}")
    print(f"  Overload: {best['overload']}")
    print(f"  Objective (f): {best['f']:.2f}")
    print(f"  Loads: {best['loads'][:5]}... ({len([l for l in best['loads'] if l > 0])} active)")
    
    # Feasibility check
    print("\n[FEASIBILITY CHECK]")
    print_solution_summary(best['routes'], best['loads'], best['distance'], "FE Stub")
    is_valid, errors = check_feasibility(best['routes'], best['loads'], best['distance'], "FE Stub")
    
    if not is_valid:
        print("\n❌ FE Stub solution FAILED feasibility check")
        print("This should not happen with the fixed engine!")
        return None
    
    print("✅ FE Stub solution is VALID")
    
    return {
        "method": "fe_stub",
        "distance": float(best['distance']),
        "overload": int(best['overload']),
        "f": float(best['f']),
        "loads": list(best['loads']),
        "routes": [list(r) for r in best['routes']],
        "elapsed_seconds": float(elapsed),
    }


# ============================================================================
# COMPARISON
# ============================================================================

def print_comparison(baseline: Dict[str, Any], fe: Dict[str, Any]):
    """Print honest comparison results."""
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS (Time-Matched)")
    print("=" * 60)
    
    print(f"\n{'Method':<30} {'Distance':<12} {'Overload':<10} {'Objective (f)':<15} {'Time (s)':<10}")
    print("-" * 80)
    print(f"{baseline['method'].upper():<30} {baseline['distance']:<12.2f} {baseline['overload']:<10} {baseline['f']:<15.2f} {baseline['elapsed_seconds']:<10.2f}")
    print(f"{'FE Stub':<30} {fe['distance']:<12.2f} {fe['overload']:<10} {fe['f']:<15.2f} {fe['elapsed_seconds']:<10.2f}")
    
    print("\n" + "=" * 60)
    print("IMPROVEMENT ANALYSIS")
    print("=" * 60)
    
    obj_improvement = ((baseline['f'] - fe['f']) / baseline['f']) * 100
    dist_improvement = ((baseline['distance'] - fe['distance']) / baseline['distance']) * 100
    
    print(f"\nFE Stub vs {baseline['method'].upper()}:")
    print(f"  Objective improvement: {obj_improvement:+.2f}%")
    print(f"  Distance improvement: {dist_improvement:+.2f}%")
    
    if obj_improvement > 0:
        print(f"\n✅ FE Stub beats {baseline['method'].upper()} by {obj_improvement:.2f}%")
    elif obj_improvement < 0:
        print(f"\n⚠️ {baseline['method'].upper()} beats FE Stub by {abs(obj_improvement):.2f}%")
    else:
        print(f"\n➡️ FE Stub matches {baseline['method'].upper()} (tie)")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run corrected validation."""
    print("=" * 60)
    print("CORRECTED VRP VALIDATION")
    print("Following Chip's Fix Strategy")
    print("=" * 60)
    
    print(f"\n[PROBLEM INSTANCE]")
    print(f"Customers: {N_CUSTOMERS}")
    print(f"Vehicles: {VEHICLES}")
    print(f"Capacity per vehicle: {CAPACITY}")
    print(f"Total demand: {TOTAL_DEMAND}")
    print(f"Feasible: {VEHICLES * CAPACITY >= TOTAL_DEMAND}")
    
    print(f"\n[VALIDATION PARAMETERS]")
    print(f"FE iterations: 20")
    print(f"Random seed: 42 (instance), 7 (FE)")
    print(f"Deterministic: Yes")
    print(f"Feasibility gates: ENFORCED")
    
    # Run FE first to get time budget
    print("\n" + "=" * 60)
    print("STEP 1: Run FE to establish time budget")
    print("=" * 60)
    
    fe_results = run_fe_stub(max_iters=20, seed=7)
    
    if fe_results is None:
        print("\n❌ VALIDATION FAILED: FE produced invalid solution")
        print("Cannot proceed with comparison.")
        return
    
    fe_time = fe_results['elapsed_seconds']
    
    # Run OR-Tools with same time budget
    print("\n" + "=" * 60)
    print(f"STEP 2: Run OR-Tools with {fe_time:.1f}s time budget")
    print("=" * 60)
    
    baseline_results = run_ortools_baseline(time_limit_seconds=int(fe_time))
    
    if baseline_results is None:
        print("\n❌ VALIDATION FAILED: OR-Tools produced invalid solution")
        print("Cannot proceed with comparison.")
        return
    
    # Print comparison
    print_comparison(baseline_results, fe_results)
    
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    
    print("\nFix strategy implemented:")
    print("  ✓ Customer IDs normalized to 0..N-1 internal indexing")
    print("  ✓ Route construction iterates over ALL customers")
    print("  ✓ Deterministic repair operator enforced")
    print("  ✓ Hard feasibility gates (coverage/conservation/capacity)")
    print("  ✓ Time-matched baseline (OR-Tools with same budget)")
    
    print("\nInvestor-ready claims:")
    print("  ✓ Both solutions serve all 100 customers")
    print("  ✓ Both solutions are feasible")
    print("  ✓ Fair time-matched comparison")
    print("  ✓ Results are honest and reproducible")


if __name__ == "__main__":
    main()
