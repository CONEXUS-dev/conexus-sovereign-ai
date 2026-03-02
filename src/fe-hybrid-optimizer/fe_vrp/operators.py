"""
Mutation operators + pattern injection ops for VRP candidates.
"""

import random
from typing import List, Dict, Any
from .types import Instance, Candidate, Pattern
from .evaluate import compute_loads


# ── basic mutation operators ─────────────────────────────────────

def op_swap(inst: Instance, assign: List[int], rng: random.Random) -> List[int]:
    """Swap vehicle assignments of two random customers."""
    n = inst.n_customers
    if n < 2:
        return list(assign)
    a = list(assign)
    i, j = rng.sample(range(n), 2)
    a[i], a[j] = a[j], a[i]
    return a


def op_relocate(inst: Instance, assign: List[int], rng: random.Random) -> List[int]:
    """Move a random customer to a random vehicle."""
    n = inst.n_customers
    a = list(assign)
    c = rng.randint(0, n - 1)
    v = rng.randint(0, inst.n_vehicles - 1)
    a[c] = v
    return a


def op_reverse(inst: Instance, assign: List[int], rng: random.Random,
               routes: List[List[int]] = None) -> List[int]:
    """Reverse a segment within a random route (2-opt style)."""
    # This doesn't change assignment, but we keep the interface consistent.
    # The actual 2-opt improvement is done in local_search_2opt below.
    return list(assign)


def op_cross_exchange(inst: Instance, assign: List[int], rng: random.Random) -> List[int]:
    """Exchange one customer between two different routes."""
    n = inst.n_customers
    a = list(assign)
    if n < 2:
        return a
    i, j = rng.sample(range(n), 2)
    if a[i] != a[j]:
        a[i], a[j] = a[j], a[i]
    else:
        a[j] = rng.randint(0, inst.n_vehicles - 1)
    return a


OPERATOR_MAP = {
    "swap": op_swap,
    "relocate": op_relocate,
    "reverse": op_reverse,
    "cross_exchange": op_cross_exchange,
}


def apply_operator(name: str, inst: Instance, assign: List[int],
                   rng: random.Random, **kw) -> List[int]:
    fn = OPERATOR_MAP.get(name)
    if fn is None:
        raise ValueError(f"Unknown operator: {name}")
    return fn(inst, assign, rng, **kw)


def choose_operator(mix: Dict[str, float], rng: random.Random) -> str:
    """Weighted random choice of operator from mix dict."""
    ops = list(mix.keys())
    weights = [mix[o] for o in ops]
    total = sum(weights)
    if total < 1e-9:
        return rng.choice(list(OPERATOR_MAP.keys()))
    r = rng.random() * total
    cum = 0.0
    for op, w in zip(ops, weights):
        cum += w
        if r <= cum:
            return op
    return ops[-1]


# ── pattern injection ops ────────────────────────────────────────

def inject_cluster_lock(inst: Instance, assign: List[int],
                        pattern: Pattern, rng: random.Random) -> List[int]:
    """Lock a cluster of customers onto the same vehicle."""
    a = list(assign)
    if not pattern.customers:
        return a
    # pick the vehicle that already has the most of these customers
    veh_counts: Dict[int, int] = {}
    for c in pattern.customers:
        if 0 <= c < inst.n_customers:
            v = a[c]
            veh_counts[v] = veh_counts.get(v, 0) + 1
    if not veh_counts:
        return a
    best_v = max(veh_counts, key=lambda v: veh_counts[v])
    for c in pattern.customers:
        if 0 <= c < inst.n_customers:
            a[c] = best_v
    return a


def inject_spine_split(inst: Instance, assign: List[int],
                       pattern: Pattern, rng: random.Random) -> List[int]:
    """Split a spine pattern across two vehicles to reduce long edges."""
    a = list(assign)
    custs = [c for c in pattern.customers if 0 <= c < inst.n_customers]
    if len(custs) < 4:
        return a
    mid = len(custs) // 2
    v1 = a[custs[0]]
    v2 = rng.choice([v for v in range(inst.n_vehicles) if v != v1]) if inst.n_vehicles > 1 else v1
    for c in custs[:mid]:
        a[c] = v1
    for c in custs[mid:]:
        a[c] = v2
    return a


def inject_capacity_repair(inst: Instance, assign: List[int],
                           rng: random.Random) -> List[int]:
    """Force capacity repair: move customers from overloaded routes."""
    from .evaluate import repair_capacity
    return repair_capacity(inst, assign, rng)


def inject_depot_leg_min(inst: Instance, assign: List[int],
                         rng: random.Random) -> List[int]:
    """Move the customer with the longest depot leg to a nearer vehicle."""
    a = list(assign)
    n = inst.n_customers
    if n == 0:
        return a
    # find customer with longest depot distance
    worst_c = max(range(n), key=lambda c: inst.dist(-1, c))
    # find vehicle whose centroid is nearest to this customer
    from .evaluate import build_routes
    routes = build_routes(inst, a)
    best_v, best_d = a[worst_c], float("inf")
    for v, route in enumerate(routes):
        if not route:
            continue
        cx = sum(inst.locations[c][0] for c in route) / len(route)
        cy = sum(inst.locations[c][1] for c in route) / len(route)
        d = ((inst.locations[worst_c][0] - cx) ** 2 +
             (inst.locations[worst_c][1] - cy) ** 2) ** 0.5
        if d < best_d:
            best_d = d
            best_v = v
    a[worst_c] = best_v
    return a


PATTERN_OP_MAP = {
    "CLUSTER_LOCK": inject_cluster_lock,
    "SPINE_SPLIT": inject_spine_split,
    "CAPACITY_REPAIR": lambda inst, assign, pattern, rng: inject_capacity_repair(inst, assign, rng),
    "DEPOT_LEG_MIN": lambda inst, assign, pattern, rng: inject_depot_leg_min(inst, assign, rng),
}


def apply_pattern_op(name: str, inst: Instance, assign: List[int],
                     pattern: Pattern, rng: random.Random) -> List[int]:
    fn = PATTERN_OP_MAP.get(name)
    if fn is None:
        raise ValueError(f"Unknown pattern op: {name}")
    return fn(inst, assign, pattern, rng)


# ── local search ─────────────────────────────────────────────────

def local_search_2opt(inst: Instance, route: List[int]) -> List[int]:
    """Simple 2-opt improvement on a single route."""
    if len(route) < 3:
        return list(route)
    improved = True
    route = list(route)
    while improved:
        improved = False
        for i in range(len(route) - 1):
            for j in range(i + 2, len(route)):
                # cost of current edges
                a_prev = -1 if i == 0 else route[i - 1]
                a_cur = route[i]
                b_cur = route[j]
                b_next = -1 if j == len(route) - 1 else route[j + 1]
                old = inst.dist(a_prev, a_cur) + inst.dist(b_cur, b_next)
                new = inst.dist(a_prev, b_cur) + inst.dist(a_cur, b_next)
                if new < old - 1e-9:
                    route[i:j + 1] = route[i:j + 1][::-1]
                    improved = True
    return route
