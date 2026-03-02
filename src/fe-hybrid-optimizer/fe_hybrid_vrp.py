"""
Hybrid Forgetting Engine VRP Optimizer - Track B Implementation
Python + OR-Tools + AI Pilot with CONEXUS-STEEL-04 Calibration

Architecture:
- Python engine: candidate generation, evaluation, paradox buffer
- OR-Tools: TSP routing per vehicle
- AI Pilot: selection, paradox curation, pattern injection
- Calibration: CONEXUS-STEEL-04 Fleet Protocol gate
"""

import math
import random
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any, Optional
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# =============================
# INSTANCE DATA
# =============================

# Import 100-customer instance
from vrp_instance_100 import CUSTOMERS_100, VEHICLES_100, CAPACITY_100

DEPOT = (50, 50)
CUSTOMERS = CUSTOMERS_100
VEHICLES = VEHICLES_100
CAPACITY = CAPACITY_100
OVERLOAD_PENALTY = 1000

# =============================
# DISTANCE & ROUTING HELPERS
# =============================

def euclid(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Euclidean distance between two points."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def route_distance(order: List[int]) -> float:
    """Calculate total distance for a route (depot -> customers -> depot)."""
    if not order:
        return 0.0
    dist = 0.0
    prev = DEPOT
    for cid in order:
        dist += euclid(prev, CUSTOMERS[cid][0])
        prev = CUSTOMERS[cid][0]
    dist += euclid(prev, DEPOT)
    return dist


def tsp_ortools(nodes: List[int], time_limit_ms: int = 50) -> List[int]:
    """
    Solve TSP for a set of customers using OR-Tools.
    Returns visit order (customer ids, excluding depot).
    """
    if not nodes:
        return []
    
    # Build index map: 0 = depot, 1..n = customers
    index_to_cust = {0: None}
    for i, cid in enumerate(nodes, start=1):
        index_to_cust[i] = cid
    
    coords = [DEPOT] + [CUSTOMERS[cid][0] for cid in nodes]
    
    manager = pywrapcp.RoutingIndexManager(len(coords), 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    
    def dist_cb(from_index, to_index):
        f = manager.IndexToNode(from_index)
        t = manager.IndexToNode(to_index)
        return int(euclid(coords[f], coords[t]) * 1000)
    
    transit_idx = routing.RegisterTransitCallback(dist_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)
    
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.time_limit.FromMilliseconds(time_limit_ms)
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    
    sol = routing.SolveWithParameters(search_params)
    
    if sol is None:
        return nodes[:]
    
    # Extract route
    idx = routing.Start(0)
    order = []
    while not routing.IsEnd(idx):
        node = manager.IndexToNode(idx)
        if node != 0:
            order.append(index_to_cust[node])
        idx = sol.Value(routing.NextVar(idx))
    
    return order


# =============================
# METRICS & ANALYSIS
# =============================

def loads_from_assign(assign: List[int]) -> List[int]:
    """Calculate load per vehicle from assignment vector."""
    loads = [0] * VEHICLES
    for i, v in enumerate(assign, start=1):
        loads[v] += CUSTOMERS[i][1]
    return loads


def overload_total(loads: List[int]) -> int:
    """Total overload across all vehicles."""
    return sum(max(0, L - CAPACITY) for L in loads)


def customers_per_vehicle(assign: List[int]) -> List[int]:
    """Count customers assigned to each vehicle."""
    counts = [0] * VEHICLES
    for v in assign:
        counts[v] += 1
    return counts


def compactness_for_routes(routes: List[List[int]]) -> float:
    """Sum of average distance to centroid per route."""
    total = 0.0
    for r in routes:
        if not r:
            continue
        pts = [CUSTOMERS[c][0] for c in r]
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        total += sum(euclid((cx, cy), p) for p in pts) / len(pts)
    return total


def depot_leg_sum(routes: List[List[int]]) -> float:
    """Sum of depot->first + last->depot distances."""
    total = 0.0
    for r in routes:
        if not r:
            continue
        total += euclid(DEPOT, CUSTOMERS[r[0]][0]) + euclid(CUSTOMERS[r[-1]][0], DEPOT)
    return total


def spine_score(routes: List[List[int]], edge_thresh: float = 20.0) -> float:
    """Fraction of edges shorter than threshold."""
    short_edges = 0
    total_edges = 0
    for r in routes:
        prev = DEPOT
        for cid in r:
            total_edges += 1
            if euclid(prev, CUSTOMERS[cid][0]) < edge_thresh:
                short_edges += 1
            prev = CUSTOMERS[cid][0]
        total_edges += 1
        if euclid(prev, DEPOT) < edge_thresh:
            short_edges += 1
    return short_edges / total_edges if total_edges else 0.0


def hamming(a: List[int], b: List[int]) -> int:
    """Hamming distance between two assignment vectors."""
    return sum(1 for i in range(len(a)) if a[i] != b[i])


# =============================
# CANDIDATE DATA STRUCTURE
# =============================

@dataclass
class Candidate:
    """Represents a VRP solution candidate."""
    cid: str
    assign: List[int]  # length 20, values 0..2
    routes: List[List[int]] = None
    distance: float = 0.0
    loads: List[int] = None
    overload: int = 0
    f: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    novelty: Dict[str, float] = field(default_factory=dict)
    flags: Dict[str, bool] = field(default_factory=dict)


def evaluate_candidate(c: Candidate) -> None:
    """Evaluate a candidate: build routes, compute metrics."""
    # Build routes per vehicle using OR-Tools TSP
    routes = []
    for v in range(VEHICLES):
        nodes = [i + 1 for i, av in enumerate(c.assign) if av == v]
        order = tsp_ortools(nodes, time_limit_ms=40)
        routes.append(order)
    
    c.routes = routes
    c.distance = sum(route_distance(r) for r in routes)
    c.loads = loads_from_assign(c.assign)
    c.overload = overload_total(c.loads)
    c.f = c.distance + OVERLOAD_PENALTY * c.overload
    
    # Geometry metrics
    comp = compactness_for_routes(routes)
    dleg = depot_leg_sum(routes)
    spine = spine_score(routes)
    cpv = customers_per_vehicle(c.assign)
    
    c.metrics = {
        "compactness": comp,
        "depot_leg_sum": dleg,
        "spine_score": spine,
        "max_customers": float(max(cpv)),
        "min_customers": float(min(cpv)),
    }
    
    # Collapse trap detection
    collapse = (max(cpv) > 14) or (min(cpv) < 3)
    c.flags = {"collapse_trap": collapse}


# =============================
# OPERATORS
# =============================

def op_swap(assign: List[int], rng: random.Random) -> List[int]:
    """Swap two customers between vehicles."""
    a = assign[:]
    i, j = rng.sample(range(20), 2)
    a[i], a[j] = a[j], a[i]
    return a


def op_relocate(assign: List[int], rng: random.Random) -> List[int]:
    """Move one customer to a different vehicle."""
    a = assign[:]
    i = rng.randrange(20)
    cur = a[i]
    other = rng.choice([v for v in range(VEHICLES) if v != cur])
    a[i] = other
    return a


def reseed_kmeans_like(rng: random.Random) -> List[int]:
    """Generate new assignment using simple spatial clustering."""
    a = []
    for cid in range(1, 21):
        x, y = CUSTOMERS[cid][0]
        if x < 40:
            a.append(0 if rng.random() < 0.7 else rng.randrange(3))
        elif x > 70:
            a.append(2 if rng.random() < 0.7 else rng.randrange(3))
        else:
            a.append(1 if rng.random() < 0.7 else rng.randrange(3))
    return a


# =============================
# PATTERN OPERATIONS
# =============================

def apply_pattern_ops(assign: List[int], pattern_ops: List[Dict[str, Any]], rng: random.Random) -> List[int]:
    """Apply pattern injection operations to assignment."""
    a = assign[:]
    
    for op in pattern_ops:
        op_type = op.get("op", "")
        customers = op.get("customers", [])
        
        if op_type == "CLUSTER_LOCK" and customers:
            # Force all customers in list to same vehicle
            target_v = rng.randrange(VEHICLES)
            for cid in customers:
                if 1 <= cid <= 20:
                    a[cid - 1] = target_v
        
        elif op_type == "CAPACITY_REPAIR":
            # Move small-demand customers off overloaded vehicles
            loads = loads_from_assign(a)
            for v in range(VEHICLES):
                if loads[v] > CAPACITY:
                    # Find small customers on this vehicle
                    small_custs = [(i + 1, CUSTOMERS[i + 1][1]) for i, av in enumerate(a) if av == v and CUSTOMERS[i + 1][1] <= 15]
                    if small_custs:
                        # Move one to least loaded vehicle
                        cid, _ = rng.choice(small_custs)
                        target_v = loads.index(min(loads))
                        a[cid - 1] = target_v
                        loads = loads_from_assign(a)
        
        elif op_type == "DEPOT_LEG_MIN" and customers:
            # Move specified customers to vehicle closest to depot
            for cid in customers:
                if 1 <= cid <= 20:
                    a[cid - 1] = 0  # Simple heuristic: assign to vehicle 0
    
    return a


# =============================
# PARADOX BUFFER MANAGEMENT
# =============================

def update_paradox_buffer(
    buffer: List[Candidate],
    candidates: List[Candidate],
    paradox_k: int = 5
) -> List[Candidate]:
    """
    Update paradox buffer with useful paradox candidates.
    Buffer is memory-only (never used as parents).
    """
    # Collect eligible paradoxes
    eligible = [c for c in candidates if c.flags.get("useful_paradox_eligible", False)]
    
    # Sort by informativeness (spine_score + compactness inverse)
    eligible.sort(key=lambda x: x.metrics.get("spine_score", 0.0) - x.metrics.get("compactness", 0.0) / 100.0, reverse=True)
    
    # Merge with existing buffer
    all_paradoxes = buffer + eligible
    
    # Keep top k by informativeness, ensuring diversity
    kept = []
    for p in all_paradoxes:
        if len(kept) >= paradox_k:
            break
        # Check diversity: require min hamming distance of 3 from existing
        if not kept or all(hamming(p.assign, k.assign) >= 3 for k in kept):
            kept.append(p)
    
    return kept[:paradox_k]


# =============================
# ITERATION PACKET BUILDER
# =============================

def build_iteration_packet(
    g: int,
    candidates: List[Candidate],
    paradox_buffer: List[Candidate],
    best_seen: Optional[Candidate],
    iters_since_improve: int,
    settings: Dict[str, Any]
) -> Dict[str, Any]:
    """Build the iteration packet sent to AI pilot."""
    
    # Compute thresholds
    f_vals = [c.f for c in candidates]
    theta_f = sorted(f_vals)[len(f_vals) // 2] if f_vals else 0.0
    
    # Mark useful paradox eligibility
    overload_floor = settings.get("overload_floor", 35)
    for c in candidates:
        bad = (c.f > theta_f) or (c.overload > overload_floor)
        informative = (
            c.metrics.get("spine_score", 0.0) > 0.5 or
            c.metrics.get("compactness", 100.0) < 30.0
        )
        useful = bad and informative and not c.flags.get("collapse_trap", False)
        c.flags["useful_paradox_eligible"] = useful
    
    # Select leaders and paradox shortlist
    leaders = sorted(candidates, key=lambda x: x.f)[:5]
    paradox_shortlist = [c for c in candidates if c.flags.get("useful_paradox_eligible", False)][:5]
    
    # Build packet
    packet = {
        "g": g,
        "settings": {
            "vehicles": VEHICLES,
            "capacity": CAPACITY,
            "customers": 20,
            "overload_floor": overload_floor,
            "paradox_k": settings.get("paradox_k", 5),
        },
        "thresholds": {
            "theta_f_median": float(theta_f),
        },
        "trend": {
            "best_f_seen": float(best_seen.f) if best_seen else float("inf"),
            "best_distance_seen": float(best_seen.distance) if best_seen else float("inf"),
            "best_overload_seen": int(best_seen.overload) if best_seen else 999,
            "iters_since_best_improve": iters_since_improve,
        },
        "buffer": {
            "paradox_ids": [b.cid for b in paradox_buffer],
            "count": len(paradox_buffer),
        },
        "pool": {
            "pool_size": len(candidates),
            "leaders": [{"id": c.cid, "f": c.f, "distance": c.distance, "overload": c.overload} for c in leaders],
            "paradox_shortlist": [{"id": c.cid, "f": c.f, "spine_score": c.metrics.get("spine_score", 0.0)} for c in paradox_shortlist],
        }
    }
    
    return packet


# =============================
# BASELINE SOLVER
# =============================

def baseline_sweep_solver(seed: int = 42) -> Candidate:
    """Simple baseline: sweep clustering + TSP per cluster."""
    rng = random.Random(seed)
    assign = reseed_kmeans_like(rng)
    c = Candidate(cid="baseline", assign=assign)
    evaluate_candidate(c)
    return c


# =============================
# MAIN FE ENGINE
# =============================

def run_fe_hybrid(
    pilot_fn,
    max_iters: int = 100,
    seed: int = 7,
    settings: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Run hybrid FE optimization with AI pilot.
    
    Args:
        pilot_fn: Callable that takes (g, packet) and returns decision dict
        max_iters: Number of iterations
        seed: Random seed
        settings: Configuration dict
    
    Returns:
        Run report with best solution and logs
    """
    if settings is None:
        settings = {
            "overload_floor": 35,
            "paradox_k": 5,
            "keep_fraction": 0.30,
        }
    
    rng = random.Random(seed)
    
    # Initialize population
    pop = []
    for p in range(10):
        assign = reseed_kmeans_like(rng)
        c = Candidate(cid=f"init_{p}", assign=assign)
        evaluate_candidate(c)
        pop.append(c)
    
    paradox_buffer = []
    best_seen = None
    iters_since_improve = 0
    
    logs = []
    
    for g in range(1, max_iters + 1):
        # Generate new candidates
        candidates = list(pop)
        for k in range(10):
            parent = rng.choice(pop)
            r = rng.random()
            if r < 0.25:
                new_assign = op_swap(parent.assign, rng)
                origin = "swap"
            elif r < 0.70:
                new_assign = op_relocate(parent.assign, rng)
                origin = "relocate"
            else:
                new_assign = reseed_kmeans_like(rng)
                origin = "reseed"
            
            c = Candidate(cid=f"g{g}_k{k}_{origin}", assign=new_assign)
            evaluate_candidate(c)
            candidates.append(c)
        
        # Build packet and call pilot
        packet = build_iteration_packet(g, candidates, paradox_buffer, best_seen, iters_since_improve, settings)
        decision = pilot_fn(g, packet)
        
        # Apply decision
        keep_ids = decision.get("keep_ids", [])
        paradox_add_ids = decision.get("paradox_add_ids", [])
        pattern_ops = decision.get("pattern_ops", [])
        
        # Keep survivors
        keep_set = set(keep_ids)
        pop = [c for c in candidates if c.cid in keep_set]
        
        # Safety: ensure minimum population
        if len(pop) < 6:
            pop = sorted(candidates, key=lambda x: x.f)[:6]
        
        # Update paradox buffer
        paradox_candidates = [c for c in candidates if c.cid in paradox_add_ids]
        paradox_buffer = update_paradox_buffer(paradox_buffer, paradox_candidates, settings["paradox_k"])
        
        # Apply pattern ops to next generation (stored for next iter)
        # This would be used in next iteration's candidate generation
        
        # Track best
        cur_best = min(candidates, key=lambda x: x.f)
        if best_seen is None or cur_best.f < best_seen.f:
            best_seen = cur_best
            iters_since_improve = 0
        else:
            iters_since_improve += 1
        
        # Log iteration
        logs.append({
            "g": g,
            "best_f": cur_best.f,
            "best_distance": cur_best.distance,
            "best_overload": cur_best.overload,
            "pool_size": len(pop),
            "paradox_buffer_size": len(paradox_buffer),
        })
    
    return {
        "best_solution": {
            "id": best_seen.cid,
            "assign": best_seen.assign,
            "routes": best_seen.routes,
            "distance": best_seen.distance,
            "overload": best_seen.overload,
            "f": best_seen.f,
            "loads": best_seen.loads,
        },
        "logs": logs,
        "final_paradox_buffer": [{"id": b.cid, "f": b.f} for b in paradox_buffer],
    }


if __name__ == "__main__":
    print("FE Hybrid VRP Engine - Track B")
    print("=" * 50)
    print("\nThis module provides the core engine.")
    print("Use pilot_adapter.py to run with calibrated AI pilot.")
    print("Use validation_harness.py to run scaling tests.")
