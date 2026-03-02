"""
Fitness evaluation and geometry metrics for VRP candidates.
"""

import math
import statistics
from typing import List, Dict
from .types import Instance, Candidate

OVERLOAD_PENALTY = 1000


# ── route helpers ────────────────────────────────────────────────

def build_routes(inst: Instance, assign: List[int]) -> List[List[int]]:
    """Group customers by vehicle; order within route by nearest-neighbour."""
    routes: List[List[int]] = [[] for _ in range(inst.n_vehicles)]
    for cust, veh in enumerate(assign):
        routes[veh].append(cust)
    # cheap NN ordering per route
    for v in range(inst.n_vehicles):
        if len(routes[v]) > 1:
            routes[v] = _nn_order(inst, routes[v])
    return routes


def _nn_order(inst: Instance, custs: List[int]) -> List[int]:
    """Nearest-neighbour ordering starting from depot."""
    remaining = set(custs)
    ordered = []
    cur = -1  # depot
    while remaining:
        nxt = min(remaining, key=lambda c: inst.dist(cur, c))
        ordered.append(nxt)
        remaining.remove(nxt)
        cur = nxt
    return ordered


def route_distance(inst: Instance, route: List[int]) -> float:
    if not route:
        return 0.0
    d = inst.dist(-1, route[0])
    for i in range(len(route) - 1):
        d += inst.dist(route[i], route[i + 1])
    d += inst.dist(route[-1], -1)
    return d


def compute_loads(inst: Instance, assign: List[int]) -> List[int]:
    loads = [0] * inst.n_vehicles
    for cust, veh in enumerate(assign):
        loads[veh] += inst.demands[cust]
    return loads


# ── full evaluation ──────────────────────────────────────────────

def evaluate(inst: Instance, cand: Candidate) -> None:
    """Evaluate candidate in-place: routes, distance, loads, fitness, metrics."""
    cand.routes = build_routes(inst, cand.assign)
    cand.loads = compute_loads(inst, cand.assign)
    cand.distance = sum(route_distance(inst, r) for r in cand.routes)
    cand.overload = sum(max(0, ld - inst.capacity) for ld in cand.loads)
    cand.fitness = cand.distance + OVERLOAD_PENALTY * cand.overload
    cand.feasible = (cand.overload == 0)
    cand.metrics = geometry_metrics(inst, cand)


# ── geometry metrics (cheap, for paradox gating) ─────────────────

def geometry_metrics(inst: Instance, cand: Candidate) -> Dict[str, float]:
    """Compute cheap geometry signals used by paradox gates."""
    m: Dict[str, float] = {}
    m["overload_total"] = float(cand.overload)
    m["distance_total"] = cand.distance

    # compactness: mean intra-route distance / mean inter-route distance
    intra, inter = [], []
    for route in cand.routes:
        if len(route) < 2:
            continue
        for i in range(len(route)):
            for j in range(i + 1, len(route)):
                intra.append(inst.dist(route[i], route[j]))
    all_custs = [c for r in cand.routes for c in r]
    for i in range(len(all_custs)):
        for j in range(i + 1, min(i + 20, len(all_custs))):
            if cand.assign[all_custs[i]] != cand.assign[all_custs[j]]:
                inter.append(inst.dist(all_custs[i], all_custs[j]))
    m["compactness"] = (
        (statistics.mean(intra) / max(statistics.mean(inter), 1e-9))
        if intra and inter else 1.0
    )

    # depot leg sum
    depot_legs = 0.0
    for route in cand.routes:
        if route:
            depot_legs += inst.dist(-1, route[0]) + inst.dist(route[-1], -1)
    m["depot_leg_sum"] = depot_legs

    # turning sum (proxy for route smoothness)
    turning = 0.0
    for route in cand.routes:
        if len(route) >= 3:
            for k in range(len(route) - 2):
                a, b, c = route[k], route[k + 1], route[k + 2]
                turning += _turn_angle(inst, a, b, c)
    m["turning_sum"] = turning

    # spine score: fraction of edges that are among the shortest 20%
    all_edges = []
    for route in cand.routes:
        for k in range(len(route) - 1):
            all_edges.append(inst.dist(route[k], route[k + 1]))
    if all_edges:
        threshold = sorted(all_edges)[max(1, len(all_edges) // 5) - 1]
        m["spine_score"] = sum(1 for e in all_edges if e <= threshold) / len(all_edges)
    else:
        m["spine_score"] = 0.0

    # customers per vehicle stats
    cpv = [len(r) for r in cand.routes]
    m["max_customers_per_vehicle"] = float(max(cpv)) if cpv else 0.0
    m["min_customers_per_vehicle"] = float(min(cpv)) if cpv else 0.0

    return m


def _turn_angle(inst: Instance, a: int, b: int, c: int) -> float:
    """Absolute turn angle at b in degrees (0 = straight)."""
    ax, ay = inst.locations[a]
    bx, by = inst.locations[b]
    cx, cy = inst.locations[c]
    v1x, v1y = bx - ax, by - ay
    v2x, v2y = cx - bx, cy - by
    dot = v1x * v2x + v1y * v2y
    mag = math.hypot(v1x, v1y) * math.hypot(v2x, v2y)
    if mag < 1e-12:
        return 0.0
    cos_a = max(-1.0, min(1.0, dot / mag))
    return math.degrees(math.acos(cos_a))


# ── repair ───────────────────────────────────────────────────────

def repair_coverage(inst: Instance, assign: List[int], rng) -> List[int]:
    """Ensure every customer 0..N-1 is assigned exactly once."""
    n = inst.n_customers
    if len(assign) != n:
        assign = list(assign) + [0] * (n - len(assign))
        assign = assign[:n]
    # find missing / duplicate
    seen = {}
    for i in range(n):
        v = assign[i]
        if i not in seen:
            seen[i] = v
    # all customers must be present as indices 0..N-1
    # assign is indexed by customer, so just ensure valid vehicle ids
    assign = list(assign)
    for i in range(n):
        if assign[i] < 0 or assign[i] >= inst.n_vehicles:
            assign[i] = rng.randint(0, inst.n_vehicles - 1)
    return assign


def repair_capacity(inst: Instance, assign: List[int], rng) -> List[int]:
    """Move customers from overloaded routes to routes with slack. Multi-pass."""
    assign = list(assign)
    for _pass in range(20):
        loads = compute_loads(inst, assign)
        overloaded = [v for v in range(inst.n_vehicles) if loads[v] > inst.capacity]
        if not overloaded:
            return assign
        for ov in overloaded:
            custs = [c for c in range(inst.n_customers) if assign[c] == ov]
            custs.sort(key=lambda c: inst.demands[c], reverse=True)
            for c in custs:
                if loads[ov] <= inst.capacity:
                    break
                targets = [v for v in range(inst.n_vehicles)
                           if v != ov and loads[v] + inst.demands[c] <= inst.capacity]
                if targets:
                    best = min(targets, key=lambda v: loads[v])
                    loads[ov] -= inst.demands[c]
                    loads[best] += inst.demands[c]
                    assign[c] = best
    return assign


def _force_salvage(inst: Instance, assign: List[int]) -> List[int]:
    """Deterministic last-resort salvage: greedily move smallest customers
    from overloaded vehicles to least-loaded vehicles until feasible."""
    assign = list(assign)
    for _attempt in range(50):
        loads = compute_loads(inst, assign)
        overloaded = [v for v in range(inst.n_vehicles) if loads[v] > inst.capacity]
        if not overloaded:
            return assign
        # pick most overloaded vehicle
        worst = max(overloaded, key=lambda v: loads[v])
        custs = [c for c in range(inst.n_customers) if assign[c] == worst]
        # try smallest customer first (easier to place)
        custs.sort(key=lambda c: inst.demands[c])
        moved = False
        for c in custs:
            if loads[worst] <= inst.capacity:
                break
            # find any vehicle with room
            targets = [(v, loads[v]) for v in range(inst.n_vehicles)
                       if v != worst and loads[v] + inst.demands[c] <= inst.capacity]
            if targets:
                best_v = min(targets, key=lambda t: t[1])[0]
                loads[worst] -= inst.demands[c]
                loads[best_v] += inst.demands[c]
                assign[c] = best_v
                moved = True
        if not moved:
            # no single customer can be moved; try splitting largest customer
            # to least loaded vehicle even if it causes slight overload there
            # (this handles extreme edge cases)
            custs.sort(key=lambda c: inst.demands[c], reverse=True)
            least_loaded = min(range(inst.n_vehicles),
                              key=lambda v: loads[v] if v != worst else float('inf'))
            if custs:
                c = custs[0]
                loads[worst] -= inst.demands[c]
                loads[least_loaded] += inst.demands[c]
                assign[c] = least_loaded
    return assign


def full_repair(inst: Instance, assign: List[int], rng) -> List[int]:
    """Coverage repair → capacity repair → force salvage if still infeasible."""
    assign = repair_coverage(inst, assign, rng)
    assign = repair_capacity(inst, assign, rng)
    # Check if still infeasible; if so, force salvage
    loads = compute_loads(inst, assign)
    if any(ld > inst.capacity for ld in loads):
        assign = _force_salvage(inst, assign)
    return assign
