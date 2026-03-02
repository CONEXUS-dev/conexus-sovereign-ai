"""
Naive Baseline VRP Solver
Simple greedy + nearest neighbor approach for comparison baseline.
Target: ~690 distance for 20-customer infeasible instance.
"""

import math
from typing import List, Tuple, Dict
from fe_hybrid_vrp import DEPOT, CUSTOMERS, VEHICLES, CAPACITY, Candidate


def euclid(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Euclidean distance."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def naive_greedy_vrp() -> Candidate:
    """
    Naive greedy VRP solver: nearest neighbor with simple capacity handling.
    
    Algorithm:
    1. Start each vehicle at depot
    2. Greedily add nearest unvisited customer
    3. If capacity exceeded, continue anyway (infeasible problem)
    4. No optimization, no backtracking
    
    Returns:
        Candidate with assignment and metrics
    """
    customers = list(CUSTOMERS.keys())
    unvisited = set(customers)
    
    # Assignment: which vehicle serves which customer
    assignment = [0] * len(customers)  # 0-indexed vehicles
    
    # Build routes greedily
    for v in range(VEHICLES):
        current_pos = DEPOT
        vehicle_load = 0
        
        while unvisited:
            # Find nearest unvisited customer
            nearest = None
            nearest_dist = float('inf')
            
            for cust_id in unvisited:
                loc, demand = CUSTOMERS[cust_id]
                dist = euclid(current_pos, loc)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest = cust_id
            
            if nearest is None:
                break
            
            # Assign to this vehicle
            assignment[nearest - 1] = v
            unvisited.remove(nearest)
            
            # Update position and load
            loc, demand = CUSTOMERS[nearest]
            current_pos = loc
            vehicle_load += demand
            
            # Simple stopping rule: if we've visited enough customers for this vehicle
            customers_per_vehicle = len(customers) // VEHICLES
            if len([c for c in range(len(assignment)) if assignment[c] == v]) >= customers_per_vehicle:
                break
    
    # Assign any remaining customers to last vehicle
    for cust_id in unvisited:
        assignment[cust_id - 1] = VEHICLES - 1
    
    # Build routes from assignment
    routes = [[] for _ in range(VEHICLES)]
    for cust_idx, vehicle in enumerate(assignment):
        routes[vehicle].append(cust_idx + 1)
    
    # Calculate metrics
    total_distance = 0.0
    loads = []
    
    for v, route in enumerate(routes):
        if not route:
            loads.append(0)
            continue
        
        # Calculate route distance (depot -> customers -> depot)
        route_dist = 0.0
        current = DEPOT
        
        for cust_id in route:
            loc, _ = CUSTOMERS[cust_id]
            route_dist += euclid(current, loc)
            current = loc
        
        # Return to depot
        route_dist += euclid(current, DEPOT)
        total_distance += route_dist
        
        # Calculate load
        load = sum(CUSTOMERS[cid][1] for cid in route)
        loads.append(load)
    
    # Calculate overload
    total_demand = sum(d for _, d in CUSTOMERS.values())
    total_capacity = VEHICLES * CAPACITY
    overload = max(0, total_demand - total_capacity)
    
    # Create candidate
    candidate = Candidate(
        cid="naive_baseline",
        assign=assignment,
        routes=routes,
        distance=total_distance,
        overload=overload,
        loads=loads,
        f=total_distance + 1000 * overload
    )
    
    return candidate


if __name__ == "__main__":
    print("Running naive greedy baseline...")
    result = naive_greedy_vrp()
    
    print(f"\nNaive Baseline Results:")
    print(f"  Distance: {result.distance:.2f}")
    print(f"  Overload: {result.overload}")
    print(f"  Objective (f): {result.f:.2f}")
    print(f"  Loads: {result.loads}")
    print(f"\nRoutes:")
    for v, route in enumerate(result.routes):
        print(f"  Vehicle {v}: {route}")
