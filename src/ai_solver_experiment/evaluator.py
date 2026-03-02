"""
Deterministic VRP Evaluator.

Pure Python. No AI. Computes:
  - Total route distance
  - Per-vehicle loads
  - Capacity constraint violations
  - Feasibility flag
  - Numeric fitness score

All routes are lists of 0-indexed customer IDs.
Depot is implicit (start and end of every route).
"""

import math
from typing import List, Tuple, Dict, Any


def euclid(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Euclidean distance between two points."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def route_distance(
    route: List[int],
    depot: Tuple[float, float],
    locations: List[Tuple[float, float]],
) -> float:
    """Total distance for one route: depot -> customers -> depot."""
    if not route:
        return 0.0
    d = euclid(depot, locations[route[0]])
    for i in range(len(route) - 1):
        d += euclid(locations[route[i]], locations[route[i + 1]])
    d += euclid(locations[route[-1]], depot)
    return d


def evaluate_solution(
    routes: List[List[int]],
    depot: Tuple[float, float],
    locations: List[Tuple[float, float]],
    demands: List[int],
    capacity: int,
    n_customers: int,
    overload_penalty: float = 1000.0,
) -> Dict[str, Any]:
    """
    Evaluate a VRP solution.

    Args:
        routes: list of routes, each a list of 0-indexed customer IDs
        depot: (x, y) depot location
        locations: list of (x, y) per customer, indexed 0..N-1
        demands: list of demand per customer, indexed 0..N-1
        capacity: vehicle capacity
        n_customers: expected number of customers
        overload_penalty: penalty multiplier for capacity violations

    Returns:
        dict with keys: distance, loads, overload, feasible, fitness,
                        violations, served_customers, missing_customers,
                        duplicate_customers
    """
    total_dist = 0.0
    loads = []
    violations = []
    served = set()
    duplicates = []

    for v_idx, route in enumerate(routes):
        # Distance
        total_dist += route_distance(route, depot, locations)

        # Load
        load = sum(demands[c] for c in route)
        loads.append(load)

        # Capacity check
        if load > capacity:
            violations.append({
                "type": "capacity",
                "vehicle": v_idx,
                "load": load,
                "capacity": capacity,
                "excess": load - capacity,
            })

        # Track served customers
        for c in route:
            if c in served:
                duplicates.append(c)
            served.add(c)

    # Missing customers
    expected = set(range(n_customers))
    missing = expected - served

    if missing:
        violations.append({
            "type": "missing_customers",
            "count": len(missing),
            "ids": sorted(missing),
        })

    if duplicates:
        violations.append({
            "type": "duplicate_customers",
            "count": len(duplicates),
            "ids": sorted(set(duplicates)),
        })

    overload = sum(max(0, ld - capacity) for ld in loads)
    feasible = overload == 0 and len(missing) == 0 and len(duplicates) == 0
    fitness = total_dist + overload_penalty * overload

    return {
        "distance": total_dist,
        "loads": loads,
        "overload": overload,
        "feasible": feasible,
        "fitness": fitness,
        "violations": violations,
        "served_customers": len(served),
        "missing_customers": sorted(missing),
        "duplicate_customers": sorted(set(duplicates)),
    }


def format_feedback(eval_result: Dict[str, Any], iteration: int) -> str:
    """
    Format evaluation result as plain-text feedback for the AI proposer.
    No metaphysical framing. Just numbers.
    """
    lines = [
        f"=== Iteration {iteration} Evaluation ===",
        f"Total distance: {eval_result['distance']:.2f}",
        f"Feasible: {eval_result['feasible']}",
        f"Overload: {eval_result['overload']}",
        f"Fitness (lower=better): {eval_result['fitness']:.2f}",
        f"Customers served: {eval_result['served_customers']}",
    ]

    if eval_result["missing_customers"]:
        lines.append(f"MISSING customers: {eval_result['missing_customers']}")

    if eval_result["duplicate_customers"]:
        lines.append(f"DUPLICATE customers: {eval_result['duplicate_customers']}")

    for v in eval_result["violations"]:
        if v["type"] == "capacity":
            lines.append(
                f"  Vehicle {v['vehicle']}: load {v['load']}/{v['capacity']} "
                f"(+{v['excess']} over)"
            )

    lines.append(f"Loads per vehicle: {eval_result['loads']}")
    return "\n".join(lines)
