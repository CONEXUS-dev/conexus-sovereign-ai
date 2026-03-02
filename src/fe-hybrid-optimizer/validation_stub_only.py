"""
Standalone Validation: Clarke-Wright vs FE Stub
NO AI PILOT - Pure mechanical comparison

Compares:
1. Clarke-Wright Savings (Industry Standard Baseline)
2. FE Hybrid with Stub Pilot (Mechanical, no LLM)

Does NOT modify or import any AI pilot files.
"""

import time
from typing import Dict, Any
from clarke_wright_baseline import clarke_wright_vrp
from fe_hybrid_vrp import run_fe_hybrid, CUSTOMERS, VEHICLES, CAPACITY


def stub_pilot(g: int, packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mechanical stub pilot - no AI, pure heuristics.
    Same logic as in validation_harness.py but standalone.
    """
    return {
        "keep_ids": [],
        "paradox_add_ids": [],
        "operator_mix_next": {
            "swap": 0.4,
            "relocate": 0.3,
            "reseed": 0.2,
            "pattern_injection": 0.1
        },
        "pattern_ops": [],
        "proto": {"moments": []},
        "rationale": {
            "survival_logic": "stub_mechanical",
            "paradox_logic": "stub_mechanical"
        }
    }


def run_clarke_wright() -> Dict[str, Any]:
    """Run Clarke-Wright baseline."""
    print("\n" + "=" * 60)
    print("RUN 1: CLARKE-WRIGHT SAVINGS (Industry Standard)")
    print("=" * 60)
    
    start_time = time.time()
    solution = clarke_wright_vrp()
    elapsed = time.time() - start_time
    
    print(f"\n✓ Clarke-Wright completed in {elapsed:.2f}s")
    print(f"  Distance: {solution.distance:.2f}")
    print(f"  Overload: {solution.overload}")
    print(f"  Objective (f): {solution.f:.2f}")
    print(f"  Loads: {solution.loads}")
    
    return {
        "method": "clarke_wright",
        "distance": solution.distance,
        "overload": solution.overload,
        "f": solution.f,
        "loads": solution.loads,
        "routes": solution.routes,
        "elapsed_seconds": elapsed,
    }


def run_fe_stub(max_iters: int = 20, seed: int = 7) -> Dict[str, Any]:
    """Run FE with stub pilot."""
    print("\n" + "=" * 60)
    print("RUN 2: FE HYBRID (Mechanical Stub Pilot)")
    print("=" * 60)
    print("✓ Pilot calibrated (stub mode)")
    
    start_time = time.time()
    report = run_fe_hybrid(
        pilot_fn=stub_pilot,
        max_iters=max_iters,
        seed=seed
    )
    elapsed = time.time() - start_time
    
    best = report["best_solution"]
    
    print(f"\n✓ FE Hybrid (stub) completed in {elapsed:.2f}s")
    print(f"  Distance: {best['distance']:.2f}")
    print(f"  Overload: {best['overload']}")
    print(f"  Objective (f): {best['f']:.2f}")
    print(f"  Loads: {best['loads']}")
    print(f"  Paradox buffer final size: {len(report.get('final_paradox_buffer', []))}")
    
    return {
        "method": "fe_stub",
        "distance": best['distance'],
        "overload": best['overload'],
        "f": best['f'],
        "loads": best['loads'],
        "routes": best['routes'],
        "elapsed_seconds": elapsed,
        "paradox_size": len(report.get('final_paradox_buffer', []))
    }


def print_comparison(baseline: Dict[str, Any], fe: Dict[str, Any]):
    """Print comparison results."""
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    
    print(f"\n{'Method':<30} {'Distance':<12} {'Overload':<10} {'Objective (f)':<15} {'Time (s)':<10}")
    print("-" * 80)
    print(f"{'Clarke-Wright':<30} {baseline['distance']:<12.2f} {baseline['overload']:<10} {baseline['f']:<15.2f} {baseline['elapsed_seconds']:<10.2f}")
    print(f"{'FE Hybrid (Stub)':<30} {fe['distance']:<12.2f} {fe['overload']:<10} {fe['f']:<15.2f} {fe['elapsed_seconds']:<10.2f}")
    
    print("\n" + "=" * 60)
    print("IMPROVEMENT ANALYSIS")
    print("=" * 60)
    
    # Calculate improvements
    if baseline['f'] > 0:
        obj_improvement = ((baseline['f'] - fe['f']) / baseline['f']) * 100
        dist_improvement = ((baseline['distance'] - fe['distance']) / baseline['distance']) * 100
        
        print(f"\nFE Stub vs Clarke-Wright:")
        print(f"  Objective improvement: {obj_improvement:+.2f}%")
        print(f"  Distance improvement: {dist_improvement:+.2f}%")
        
        if obj_improvement > 0:
            print(f"\n✅ FE Stub beats Clarke-Wright by {obj_improvement:.2f}%")
        elif obj_improvement < 0:
            print(f"\n⚠️ Clarke-Wright beats FE Stub by {abs(obj_improvement):.2f}%")
        else:
            print(f"\n➡️ FE Stub matches Clarke-Wright (tie)")


def main():
    """Run validation."""
    print("=" * 60)
    print("STUB-ONLY VALIDATION TEST")
    print("FE Hybrid (Mechanical) vs Clarke-Wright (Industry Standard)")
    print("=" * 60)
    
    print(f"\nInstance: {len(CUSTOMERS)} customers, {VEHICLES} vehicles, capacity {CAPACITY}")
    
    total_demand = sum(d for _, d in CUSTOMERS.values())
    total_capacity = VEHICLES * CAPACITY
    
    print(f"Total demand: {total_demand}")
    print(f"Total capacity: {total_capacity}")
    
    if total_demand > total_capacity:
        print(f"Minimum overload: {total_demand - total_capacity}")
    else:
        print("Problem is FEASIBLE (no overload required)")
    
    print(f"\nIterations: 20")
    print(f"Random seed: 7")
    
    # Run baseline
    baseline_results = run_clarke_wright()
    
    # Run FE stub
    fe_results = run_fe_stub(max_iters=20, seed=7)
    
    # Print comparison
    print_comparison(baseline_results, fe_results)
    
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    print("\nThis validation uses:")
    print("  ✓ Clarke-Wright Savings (1964) - Industry standard baseline")
    print("  ✓ FE Hybrid with Stub Pilot - Mechanical heuristics only")
    print("  ✓ NO AI/LLM involved - Pure algorithmic comparison")
    print("  ✓ Same problem instance for fair comparison")


if __name__ == "__main__":
    main()
