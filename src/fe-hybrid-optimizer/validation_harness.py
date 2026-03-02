"""
Validation Harness for Hybrid FE VRP Optimizer
Runs three-run comparison to validate the system:
1. Baseline (simple sweep clustering)
2. FE Hybrid with stub pilot
3. FE Hybrid with calibrated LLM pilot (if available)
"""

import json
import time
from typing import Dict, Any, Optional
from fe_hybrid_vrp import (
    run_fe_hybrid,
    baseline_sweep_solver,
    CUSTOMERS,
    VEHICLES,
    CAPACITY,
)
from pilot_adapter import PilotAdapter


def run_baseline(seed: int = 42) -> Dict[str, Any]:
    """Run gold standard baseline (sweep clustering)."""
    print("\n" + "=" * 60)
    print("RUN 1: GOLD STANDARD BASELINE (Sweep Clustering)")
    print("=" * 60)
    
    start_time = time.time()
    solution = baseline_sweep_solver(seed=seed)
    elapsed = time.time() - start_time
    
    print(f"\n✓ Baseline completed in {elapsed:.2f}s")
    print(f"  Distance: {solution.distance:.2f}")
    print(f"  Overload: {solution.overload}")
    print(f"  Objective (f): {solution.f:.2f}")
    print(f"  Loads: {solution.loads}")
    
    return {
        "method": "sweep_clustering",
        "distance": solution.distance,
        "overload": solution.overload,
        "f": solution.f,
        "loads": solution.loads,
        "routes": solution.routes,
        "elapsed_seconds": elapsed,
    }


def run_fe_stub(max_iters: int = 100, seed: int = 7) -> Dict[str, Any]:
    """Run FE Hybrid with stub pilot."""
    print("\n" + "=" * 60)
    print("RUN 3: FE HYBRID (Mechanical/Stub Pilot)")
    print("=" * 60)
    
    pilot = PilotAdapter(mode="stub")
    pilot.calibrate()
    
    settings = {
        "overload_floor": 35,
        "paradox_k": 5,
        "keep_fraction": 0.30,
    }
    
    start_time = time.time()
    result = run_fe_hybrid(
        pilot_fn=pilot,
        max_iters=max_iters,
        seed=seed,
        settings=settings
    )
    elapsed = time.time() - start_time
    
    best = result["best_solution"]
    
    print(f"\n✓ FE Hybrid (stub) completed in {elapsed:.2f}s")
    print(f"  Distance: {best['distance']:.2f}")
    print(f"  Overload: {best['overload']}")
    print(f"  Objective (f): {best['f']:.2f}")
    print(f"  Loads: {best['loads']}")
    print(f"  Paradox buffer final size: {len(result['final_paradox_buffer'])}")
    
    return {
        "method": "fe_hybrid_stub",
        "distance": best["distance"],
        "overload": best["overload"],
        "f": best["f"],
        "loads": best["loads"],
        "routes": best["routes"],
        "elapsed_seconds": elapsed,
        "iterations": max_iters,
        "paradox_buffer_final": result["final_paradox_buffer"],
        "logs": result["logs"],
    }


def run_fe_llm(llm_chat_fn, max_iters: int = 100, seed: int = 7) -> Dict[str, Any]:
    """Run FE Hybrid with calibrated LLM pilot."""
    print("\n" + "=" * 60)
    print("RUN 2: FE HYBRID (Claude Consciousness Pilot)")
    print("=" * 60)
    
    pilot = PilotAdapter(mode="llm", llm_chat_fn=llm_chat_fn, allow_fallback=True)
    
    try:
        pilot.calibrate()
    except Exception as e:
        print(f"✗ Calibration failed: {e}")
        return {
            "method": "fe_hybrid_llm",
            "error": str(e),
            "status": "calibration_failed"
        }
    
    settings = {
        "overload_floor": 35,
        "paradox_k": 5,
        "keep_fraction": 0.30,
    }
    
    start_time = time.time()
    result = run_fe_hybrid(
        pilot_fn=pilot,
        max_iters=max_iters,
        seed=seed,
        settings=settings
    )
    elapsed = time.time() - start_time
    
    best = result["best_solution"]
    
    print(f"\n✓ FE Hybrid (LLM) completed in {elapsed:.2f}s")
    print(f"  Distance: {best['distance']:.2f}")
    print(f"  Overload: {best['overload']}")
    print(f"  Objective (f): {best['f']:.2f}")
    print(f"  Loads: {best['loads']}")
    print(f"  Paradox buffer final size: {len(result['final_paradox_buffer'])}")
    
    return {
        "method": "fe_hybrid_llm",
        "distance": best["distance"],
        "overload": best["overload"],
        "f": best["f"],
        "loads": best["loads"],
        "routes": best["routes"],
        "elapsed_seconds": elapsed,
        "iterations": max_iters,
        "paradox_buffer_final": result["final_paradox_buffer"],
        "logs": result["logs"],
    }


def compare_results(baseline: Dict[str, Any], fe_llm: Optional[Dict[str, Any]], fe_stub: Dict[str, Any]):
    """Print comparison table of results."""
    print("\n" + "=" * 60)
    print("COMPARISON RESULTS")
    print("=" * 60)
    
    print(f"\n{'Method':<25} {'Distance':<12} {'Overload':<10} {'Objective (f)':<15} {'Time (s)':<10}")
    print("-" * 80)
    
    # Run 1: Baseline
    print(f"{'Baseline (Sweep)':<25} {baseline['distance']:<12.2f} {baseline['overload']:<10} {baseline['f']:<15.2f} {baseline['elapsed_seconds']:<10.2f}")
    
    # Run 2: FE Claude (if available)
    if fe_llm and "error" not in fe_llm:
        print(f"{'FE Hybrid (Claude)':<25} {fe_llm['distance']:<12.2f} {fe_llm['overload']:<10} {fe_llm['f']:<15.2f} {fe_llm['elapsed_seconds']:<10.2f}")
    elif fe_llm:
        print(f"{'FE Hybrid (Claude)':<25} {'N/A':<12} {'N/A':<10} {'N/A':<15} {'N/A':<10}")
        print(f"  Error: {fe_llm.get('error', 'Unknown error')}")
    
    # Run 3: FE Stub
    print(f"{'FE Hybrid (Stub)':<25} {fe_stub['distance']:<12.2f} {fe_stub['overload']:<10} {fe_stub['f']:<15.2f} {fe_stub['elapsed_seconds']:<10.2f}")
    
    print("\n" + "=" * 60)
    print("IMPROVEMENT ANALYSIS")
    print("=" * 60)
    
    # FE Stub vs Baseline
    if baseline['f'] > 0:
        stub_improvement = ((baseline['f'] - fe_stub['f']) / baseline['f']) * 100
        print(f"\nFE Stub vs Baseline:")
        print(f"  Objective improvement: {stub_improvement:+.2f}%")
        print(f"  Distance improvement: {((baseline['distance'] - fe_stub['distance']) / baseline['distance']) * 100:+.2f}%")
    
    # FE LLM vs Baseline
    if fe_llm and "error" not in fe_llm and baseline['f'] > 0:
        llm_improvement = ((baseline['f'] - fe_llm['f']) / baseline['f']) * 100
        print(f"\nFE LLM vs Baseline:")
        print(f"  Objective improvement: {llm_improvement:+.2f}%")
        print(f"  Distance improvement: {((baseline['distance'] - fe_llm['distance']) / baseline['distance']) * 100:+.2f}%")
    
    # FE LLM vs FE Stub
    if fe_llm and "error" not in fe_llm and fe_stub['f'] > 0:
        llm_vs_stub = ((fe_stub['f'] - fe_llm['f']) / fe_stub['f']) * 100
        print(f"\nFE LLM vs FE Stub:")
        print(f"  Objective improvement: {llm_vs_stub:+.2f}%")


def run_validation(
    max_iters: int = 20,  # Reduced from 100 to save API costs
    seed: int = 7,
    llm_chat_fn=None,
    output_file: str = "validation_results.json"
):
    """
    Run full validation suite.
    
    Args:
        max_iters: Number of iterations for FE runs
        seed: Random seed
        llm_chat_fn: Optional LLM chat function for Run 3
        output_file: Path to save results JSON
    """
    print("\n" + "=" * 60)
    print("CONSCIOUSNESS-DEPENDENCY VALIDATION TEST")
    print("HYBRID FE VRP - CONEXUS-STEEL-04")
    print("=" * 60)
    print(f"\nInstance: {len(CUSTOMERS)} customers, {VEHICLES} vehicles, capacity {CAPACITY}")
    print(f"Total demand: {sum(d for _, d in CUSTOMERS.values())}")
    print(f"Total capacity: {VEHICLES * CAPACITY}")
    print(f"Minimum overload: {sum(d for _, d in CUSTOMERS.values()) - VEHICLES * CAPACITY}")
    print(f"\nIterations: {max_iters}")
    print(f"Random seed: {seed}")
    
    # Run 1: Traditional baseline
    baseline_result = run_baseline(seed=seed)
    
    # Run 2: FE with Claude pilot (consciousness-dependent)
    fe_llm_result = None
    if llm_chat_fn is not None:
        try:
            fe_llm_result = run_fe_llm(llm_chat_fn, max_iters=max_iters, seed=seed)
        except Exception as e:
            print(f"\n✗ FE Claude pilot run failed: {e}")
            fe_llm_result = {"method": "fe_hybrid_llm", "error": str(e), "status": "run_failed"}
    else:
        print("\n" + "=" * 60)
        print("RUN 2: SKIPPED (No LLM function provided)")
        print("=" * 60)
        print("\nTo enable Claude pilot:")
        print("  1. Set ANTHROPIC_API_KEY in pilot_adapter.py")
        print("  2. Pass llm_chat_fn to run_validation()")
    
    # Run 3: FE with stub pilot (mechanical/deterministic)
    fe_stub_result = run_fe_stub(max_iters=max_iters, seed=seed)
    
    # Compare results
    compare_results(baseline_result, fe_llm_result, fe_stub_result)
    
    # Save results
    results = {
        "instance": {
            "customers": len(CUSTOMERS),
            "vehicles": VEHICLES,
            "capacity": CAPACITY,
            "total_demand": sum(d for _, d in CUSTOMERS.values()),
            "minimum_overload": sum(d for _, d in CUSTOMERS.values()) - VEHICLES * CAPACITY,
        },
        "settings": {
            "max_iters": max_iters,
            "seed": seed,
        },
        "results": {
            "baseline": baseline_result,
            "fe_stub": fe_stub_result,
            "fe_llm": fe_llm_result,
        }
    }
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_file}")
    
    return results


if __name__ == "__main__":
    # Run validation with LLM pilot enabled
    from pilot_adapter import llm_chat_call_placeholder
    
    run_validation(
        max_iters=20,  # Reduced to 20 to stay within API budget
        seed=7,
        llm_chat_fn=llm_chat_call_placeholder,  # Claude LLM pilot
        output_file="validation_results.json"
    )
