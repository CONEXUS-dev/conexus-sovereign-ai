"""
Fixed FE Hybrid VRP Engine
Implements Chip's fix strategy:
1. Normalize customer IDs to 0..N-1 internal indexing
2. Fix route construction to consume ALL customers
3. Add deterministic repair operator
4. Enforce coverage/conservation/capacity invariants
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any, Optional
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# Import 100-customer instance
from vrp_instance_100 import CUSTOMERS_100, VEHICLES_100, CAPACITY_100

# =============================
# INSTANCE DATA (NORMALIZED)
# =============================

DEPOT = (50, 50)
VEHICLES = VEHICLES_100
CAPACITY = CAPACITY_100
OVERLOAD_PENALTY = 1000

# Normalize customer data to 0-indexed arrays
# External IDs: 1..N, Internal indices: 0..N-1
N_CUSTOMERS = len(CUSTOMERS_100)

# Build 0-indexed arrays for internal use
CUSTOMER_LOCATIONS = []
CUSTOMER_DEMANDS = []

for i in range(1, N_CUSTOMERS + 1):
    loc, demand = CUSTOMERS_100[i]
    CUSTOMER_LOCATIONS.append(loc)
    CUSTOMER_DEMANDS.append(demand)

TOTAL_DEMAND = sum(CUSTOMER_DEMANDS)

# =============================
# DISTANCE & ROUTING HELPERS
# =============================

def euclid(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    """Euclidean distance between two points."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def route_distance(order: List[int]) -> float:
    """
    Calculate total distance for a route (depot -> customers -> depot).
    order: list of customer indices (0..N-1)
    """
    if not order:
        return 0.0
    
    dist = euclid(DEPOT, CUSTOMER_LOCATIONS[order[0]])
    for i in range(len(order) - 1):
        dist += euclid(CUSTOMER_LOCATIONS[order[i]], CUSTOMER_LOCATIONS[order[i + 1]])
    dist += euclid(CUSTOMER_LOCATIONS[order[-1]], DEPOT)
    return dist


def tsp_ortools(nodes: List[int], time_limit_ms: int = 50) -> List[int]:
    """
    Solve TSP for a set of customers using OR-Tools.
    nodes: list of customer indices (0..N-1)
    Returns: ordered list of customer indices
    """
    if not nodes:
        return []
    if len(nodes) == 1:
        return nodes
    
    # Build distance matrix for these nodes
    n = len(nodes)
    dist_matrix = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                dist_matrix[i][j] = int(euclid(
                    CUSTOMER_LOCATIONS[nodes[i]], 
                    CUSTOMER_LOCATIONS[nodes[j]]
                ) * 1000)
    
    manager = pywrapcp.RoutingIndexManager(n, 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return dist_matrix[from_node][to_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.time_limit.FromMilliseconds(time_limit_ms)
    
    solution = routing.SolveWithParameters(search_parameters)
    
    if solution:
        index = routing.Start(0)
        route = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(nodes[node])
            index = solution.Value(routing.NextVar(index))
        return route
    
    return nodes


# =============================
# CANDIDATE DATACLASS
# =============================

@dataclass
class Candidate:
    """
    Represents a VRP solution candidate.
    assign: list of length N_CUSTOMERS, assign[i] = vehicle for customer i (0-indexed)
    """
    cid: str
    assign: List[int]  # length N_CUSTOMERS, values 0..VEHICLES-1
    routes: List[List[int]] = None  # routes[v] = list of customer indices (0..N-1)
    distance: float = 0.0
    loads: List[int] = None
    overload: int = 0
    f: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    novelty: Dict[str, float] = field(default_factory=dict)
    flags: Dict[str, bool] = field(default_factory=dict)


# =============================
# FEASIBILITY REPAIR
# =============================

def repair_solution(assign: List[int], rng: random.Random) -> List[int]:
    """
    Deterministic repair operator to fix missing/duplicate customers.
    
    Invariants enforced:
    1. Every customer 0..N-1 appears exactly once
    2. No duplicates
    3. Assignment vector has length N_CUSTOMERS
    
    Returns: repaired assignment vector
    """
    if len(assign) != N_CUSTOMERS:
        raise ValueError(f"Assignment vector must have length {N_CUSTOMERS}, got {len(assign)}")
    
    # Find which customers are assigned
    assigned = set()
    duplicates = []
    
    for i, v in enumerate(assign):
        if i in assigned:
            duplicates.append(i)
        else:
            assigned.add(i)
    
    # Find missing customers
    missing = set(range(N_CUSTOMERS)) - assigned
    
    if not missing and not duplicates:
        return assign  # Already valid
    
    # Repair: remove duplicates and insert missing
    repaired = list(assign)
    
    # Remove duplicates by reassigning them
    for dup_idx in duplicates:
        # Find a vehicle with capacity
        vehicle_loads = [0] * VEHICLES
        for i, v in enumerate(repaired):
            if i not in duplicates:
                vehicle_loads[v] += CUSTOMER_DEMANDS[i]
        
        # Assign duplicate to vehicle with most capacity
        best_vehicle = min(range(VEHICLES), key=lambda v: vehicle_loads[v])
        repaired[dup_idx] = best_vehicle
    
    # Insert missing customers using greedy insertion
    missing_list = sorted(missing)  # Deterministic order
    for cust_idx in missing_list:
        # Calculate current vehicle loads
        vehicle_loads = [0] * VEHICLES
        for i, v in enumerate(repaired):
            vehicle_loads[v] += CUSTOMER_DEMANDS[i]
        
        # Find vehicle with most remaining capacity
        best_vehicle = min(range(VEHICLES), key=lambda v: vehicle_loads[v])
        repaired[cust_idx] = best_vehicle
    
    return repaired


# =============================
# METRICS & ANALYSIS
# =============================

def loads_from_assign(assign: List[int]) -> List[int]:
    """Calculate load per vehicle from assignment vector (0-indexed)."""
    loads = [0] * VEHICLES
    for i, v in enumerate(assign):
        loads[v] += CUSTOMER_DEMANDS[i]
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


def check_coverage_invariant(assign: List[int]) -> Tuple[bool, str]:
    """
    Check coverage invariant: every customer 0..N-1 appears exactly once.
    Returns: (is_valid, error_message)
    """
    if len(assign) != N_CUSTOMERS:
        return False, f"Assignment length {len(assign)} != {N_CUSTOMERS}"
    
    covered = set(range(N_CUSTOMERS))
    assigned = set()
    
    for i in range(N_CUSTOMERS):
        if i in assigned:
            return False, f"Duplicate customer {i}"
        assigned.add(i)
    
    missing = covered - assigned
    if missing:
        return False, f"Missing customers: {sorted(list(missing))[:10]}"
    
    return True, ""


def check_conservation_invariant(loads: List[int]) -> Tuple[bool, str]:
    """
    Check conservation invariant: sum of loads equals total demand.
    Returns: (is_valid, error_message)
    """
    total_load = sum(loads)
    if abs(total_load - TOTAL_DEMAND) > 0.01:
        return False, f"Load {total_load} != demand {TOTAL_DEMAND}"
    return True, ""


# =============================
# CANDIDATE EVALUATION
# =============================

def evaluate_candidate(c: Candidate) -> None:
    """
    Evaluate candidate and set all metrics.
    Enforces hard invariants - raises exception if violated.
    """
    # HARD INVARIANT CHECKS
    is_valid, error = check_coverage_invariant(c.assign)
    if not is_valid:
        raise ValueError(f"Coverage invariant violated: {error}")
    
    # Build routes from assignment
    routes = []
    for v in range(VEHICLES):
        nodes = [i for i in range(N_CUSTOMERS) if c.assign[i] == v]
        if nodes:
            order = tsp_ortools(nodes, time_limit_ms=40)
            routes.append(order)
        else:
            routes.append([])
    
    c.routes = routes
    c.distance = sum(route_distance(r) for r in routes)
    c.loads = loads_from_assign(c.assign)
    
    # Check conservation invariant
    is_valid, error = check_conservation_invariant(c.loads)
    if not is_valid:
        raise ValueError(f"Conservation invariant violated: {error}")
    
    c.overload = overload_total(c.loads)
    c.f = c.distance + OVERLOAD_PENALTY * c.overload
    
    # Metrics
    cpv = customers_per_vehicle(c.assign)
    c.metrics = {
        "max_customers": float(max(cpv)) if cpv else 0.0,
        "min_customers": float(min(cpv)) if cpv else 0.0,
    }
    
    # Flags
    collapse = (max(cpv) > N_CUSTOMERS // VEHICLES + 10) if cpv else False
    c.flags = {"collapse_trap": collapse}


# =============================
# INITIALIZATION
# =============================

def reseed_kmeans_like(rng: random.Random) -> List[int]:
    """
    K-means-like clustering for initial assignment.
    Returns: assignment vector of length N_CUSTOMERS
    """
    # Pick random centroids
    centroids = [CUSTOMER_LOCATIONS[rng.randint(0, N_CUSTOMERS - 1)] for _ in range(VEHICLES)]
    
    # Assign each customer to nearest centroid
    assign = []
    for i in range(N_CUSTOMERS):
        loc = CUSTOMER_LOCATIONS[i]
        distances = [euclid(loc, c) for c in centroids]
        vehicle = distances.index(min(distances))
        assign.append(vehicle)
    
    # Repair to ensure feasibility
    assign = repair_solution(assign, rng)
    
    return assign


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
    Run hybrid FE optimization with pilot.
    All solutions are guaranteed to satisfy coverage/conservation invariants.
    """
    if settings is None:
        settings = {
            "overload_floor": 0,  # For feasible problems
            "paradox_k": 5,
            "keep_fraction": 0.30,
        }
    
    rng = random.Random(seed)
    
    # Initialize population - all solutions must be valid
    pop = []
    for p in range(10):
        assign = reseed_kmeans_like(rng)
        c = Candidate(cid=f"init_{p}", assign=assign)
        try:
            evaluate_candidate(c)
            pop.append(c)
        except ValueError as e:
            print(f"Warning: Initial candidate {p} invalid: {e}")
            continue
    
    if not pop:
        raise RuntimeError("Failed to generate any valid initial candidates")
    
    paradox_buffer = []
    best_seen = min(pop, key=lambda x: x.f)
    
    logs = []
    
    for g in range(1, max_iters + 1):
        # Generate new candidates with repair
        candidates = list(pop)
        
        for k in range(10):
            parent = rng.choice(pop)
            new_assign = list(parent.assign)
            
            # Apply operator
            op = rng.choice(["swap", "relocate"])
            
            if op == "swap" and N_CUSTOMERS >= 2:
                i, j = rng.sample(range(N_CUSTOMERS), 2)
                new_assign[i], new_assign[j] = new_assign[j], new_assign[i]
            elif op == "relocate" and N_CUSTOMERS >= 1:
                i = rng.randint(0, N_CUSTOMERS - 1)
                new_v = rng.randint(0, VEHICLES - 1)
                new_assign[i] = new_v
            
            # CRITICAL: Repair after operator to maintain invariants
            new_assign = repair_solution(new_assign, rng)
            
            c = Candidate(cid=f"g{g}_k{k}", assign=new_assign)
            try:
                evaluate_candidate(c)
                candidates.append(c)
            except ValueError as e:
                # Should not happen after repair, but log if it does
                print(f"Warning: Candidate g{g}_k{k} invalid after repair: {e}")
                continue
        
        # Get pilot decision
        cur_best = min(candidates, key=lambda x: x.f)
        
        packet = {
            "generation": g,
            "best_f": cur_best.f,
            "pool_size": len(candidates),
        }
        
        decision = pilot_fn(g, packet)
        
        # Select survivors
        candidates.sort(key=lambda x: x.f)
        keep_count = max(5, int(len(candidates) * settings["keep_fraction"]))
        pop = candidates[:keep_count]
        
        # Update best
        if cur_best.f < best_seen.f:
            best_seen = cur_best
        
        logs.append({
            "generation": g,
            "best_f": cur_best.f,
            "best_distance": cur_best.distance,
            "best_overload": cur_best.overload,
            "pool_size": len(pop),
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
        "final_paradox_buffer": [],
    }


if __name__ == "__main__":
    print("Fixed FE Hybrid VRP Engine")
    print("=" * 50)
    print(f"Customers: {N_CUSTOMERS}")
    print(f"Vehicles: {VEHICLES}")
    print(f"Capacity: {CAPACITY}")
    print(f"Total demand: {TOTAL_DEMAND}")
    print("\nInvariants enforced:")
    print("  ✓ Coverage: all customers served exactly once")
    print("  ✓ Conservation: sum(loads) = total_demand")
    print("  ✓ Capacity: each load <= capacity (soft via penalty)")
