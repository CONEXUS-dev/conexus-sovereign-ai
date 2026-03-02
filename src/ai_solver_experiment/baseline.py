"""
Clarke-Wright Savings Algorithm — Deterministic VRP Baseline.

Industry standard heuristic (1964). No AI, no randomness.
Used as Condition A in the experiment.
"""

from typing import List, Tuple, Dict, Any
from .vrp_instance import VRPInstance
from .evaluator import euclid, evaluate_solution


def clarke_wright_solve(instance: VRPInstance) -> Dict[str, Any]:
    """
    Clarke-Wright Savings Algorithm for capacitated VRP.

    Algorithm:
    1. Start with each customer on its own route (depot -> customer -> depot)
    2. Calculate savings s_ij = d(depot,i) + d(depot,j) - d(i,j) for all pairs
    3. Sort savings descending
    4. Merge routes if customers are at route ends and capacity allows

    Returns:
        dict with 'routes' and full evaluation results
    """
    n = instance.n_customers
    depot = instance.depot
    locs = instance.locations
    dems = instance.demands
    cap = instance.capacity
    n_veh = instance.n_vehicles

    # Step 1: Calculate all savings
    savings = []
    for i in range(n):
        for j in range(i + 1, n):
            d_0i = euclid(depot, locs[i])
            d_0j = euclid(depot, locs[j])
            d_ij = euclid(locs[i], locs[j])
            s_ij = d_0i + d_0j - d_ij
            savings.append((s_ij, i, j))

    savings.sort(reverse=True)

    # Step 2: Initialize — each customer on its own route
    routes = [[i] for i in range(n)]
    route_loads = [dems[i] for i in range(n)]
    cust_to_route = {i: i for i in range(n)}

    # Step 3: Merge routes greedily
    for s_ij, ci, cj in savings:
        ri = cust_to_route[ci]
        rj = cust_to_route[cj]

        if ri == rj:
            continue

        route_i = routes[ri]
        route_j = routes[rj]

        if not route_i or not route_j:
            continue

        # Both must be at ends of their routes
        ci_at_end = (route_i[0] == ci or route_i[-1] == ci)
        cj_at_end = (route_j[0] == cj or route_j[-1] == cj)
        if not (ci_at_end and cj_at_end):
            continue

        # Capacity check
        if route_loads[ri] + route_loads[rj] > cap:
            continue

        # Merge
        if route_i[-1] == ci and route_j[0] == cj:
            merged = route_i + route_j
        elif route_i[0] == ci and route_j[-1] == cj:
            merged = route_j + route_i
        elif route_i[-1] == ci and route_j[-1] == cj:
            merged = route_i + route_j[::-1]
        elif route_i[0] == ci and route_j[0] == cj:
            merged = route_i[::-1] + route_j
        else:
            continue

        routes[ri] = merged
        route_loads[ri] += route_loads[rj]
        routes[rj] = []
        route_loads[rj] = 0

        for c in merged:
            cust_to_route[c] = ri

    # Remove empty routes
    final_routes = [r for r in routes if r]

    # If more routes than vehicles, force-merge smallest
    while len(final_routes) > n_veh:
        loads = [sum(dems[c] for c in r) for r in final_routes]
        idx1 = loads.index(min(loads))
        loads[idx1] = float("inf")
        idx2 = loads.index(min(loads))
        final_routes[idx1].extend(final_routes[idx2])
        final_routes.pop(idx2)

    # Evaluate
    result = evaluate_solution(
        routes=final_routes,
        depot=depot,
        locations=locs,
        demands=dems,
        capacity=cap,
        n_customers=n,
    )
    result["routes"] = final_routes
    result["method"] = "clarke_wright"
    return result
