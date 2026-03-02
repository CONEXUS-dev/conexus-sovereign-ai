"""
Clarke-Wright Savings Algorithm - Industry Standard VRP Baseline
Classic heuristic used as gold standard in VRP research and industry.
"""

import math
from typing import List, Tuple, Dict
from fe_hybrid_vrp import DEPOT, CUSTOMERS, VEHICLES, CAPACITY, Candidate


def euclid(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def clarke_wright_vrp() -> Candidate:
    """
    Clarke-Wright Savings Algorithm (1964)
    Industry standard baseline for capacitated VRP.
    
    Algorithm:
    1. Start with each customer on its own route (depot -> customer -> depot)
    2. Calculate savings s_ij = d(0,i) + d(0,j) - d(i,j) for all pairs
    3. Sort savings in descending order
    4. Merge routes if:
       - Customers i,j are on different routes
       - i,j are at ends of their routes
       - Merged route doesn't violate capacity
    
    Returns:
        Candidate with Clarke-Wright solution
    """
    
    # Get customer data
    customer_ids = sorted(CUSTOMERS.keys())
    n = len(customer_ids)
    
    # Build location and demand maps
    locations = {0: DEPOT}
    demands = {0: 0}
    for cid in customer_ids:
        loc, demand = CUSTOMERS[cid]
        locations[cid] = loc
        demands[cid] = demand
    
    # Step 1: Calculate all savings s_ij = d(0,i) + d(0,j) - d(i,j)
    savings = []
    for i in range(len(customer_ids)):
        for j in range(i + 1, len(customer_ids)):
            ci = customer_ids[i]
            cj = customer_ids[j]
            
            d_0i = euclid(DEPOT, locations[ci])
            d_0j = euclid(DEPOT, locations[cj])
            d_ij = euclid(locations[ci], locations[cj])
            
            s_ij = d_0i + d_0j - d_ij
            savings.append((s_ij, ci, cj))
    
    # Step 2: Sort savings in descending order
    savings.sort(reverse=True)
    
    # Step 3: Initialize - each customer on its own route
    routes = [[cid] for cid in customer_ids]
    route_loads = [demands[cid] for cid in customer_ids]
    
    # Track which route each customer is in and position
    customer_to_route = {cid: i for i, cid in enumerate(customer_ids)}
    
    def can_merge(ci: int, cj: int) -> bool:
        """Check if customers can be merged (must be at route ends)."""
        ri = customer_to_route[ci]
        rj = customer_to_route[cj]
        
        if ri == rj:
            return False
        
        route_i = routes[ri]
        route_j = routes[rj]
        
        # Check if ci and cj are at ends of their routes
        ci_at_end = (route_i[0] == ci or route_i[-1] == ci)
        cj_at_end = (route_j[0] == cj or route_j[-1] == cj)
        
        if not (ci_at_end and cj_at_end):
            return False
        
        # Check capacity constraint
        if route_loads[ri] + route_loads[rj] > CAPACITY:
            return False
        
        return True
    
    # Step 4: Process savings and merge routes
    for s_ij, ci, cj in savings:
        if not can_merge(ci, cj):
            continue
        
        ri = customer_to_route[ci]
        rj = customer_to_route[cj]
        
        route_i = routes[ri]
        route_j = routes[rj]
        
        # Merge routes - connect at ends
        if route_i[-1] == ci and route_j[0] == cj:
            # i's route ends with ci, j's route starts with cj
            merged = route_i + route_j
        elif route_i[0] == ci and route_j[-1] == cj:
            # j's route ends with cj, i's route starts with ci
            merged = route_j + route_i
        elif route_i[-1] == ci and route_j[-1] == cj:
            # Both end with ci, cj - reverse one
            merged = route_i + route_j[::-1]
        elif route_i[0] == ci and route_j[0] == cj:
            # Both start with ci, cj - reverse one
            merged = route_i[::-1] + route_j
        else:
            continue
        
        # Update routes
        routes[ri] = merged
        route_loads[ri] = route_loads[ri] + route_loads[rj]
        
        # Mark route j as empty
        routes[rj] = []
        route_loads[rj] = 0
        
        # Update customer_to_route mapping
        for c in merged:
            customer_to_route[c] = ri
    
    # Step 5: Remove empty routes and limit to VEHICLES
    final_routes = [r for r in routes if len(r) > 0]
    
    # If we have more routes than vehicles, merge smallest routes
    while len(final_routes) > VEHICLES:
        # Find two smallest routes by load
        loads = [sum(demands[c] for c in r) for r in final_routes]
        min_idx1 = loads.index(min(loads))
        loads[min_idx1] = float('inf')
        min_idx2 = loads.index(min(loads))
        
        # Merge them
        final_routes[min_idx1].extend(final_routes[min_idx2])
        final_routes.pop(min_idx2)
    
    # Step 6: Build assignment vector
    assignment = [0] * len(customer_ids)
    final_loads = []
    
    for vehicle_id, route in enumerate(final_routes):
        route_load = sum(demands[c] for c in route)
        final_loads.append(route_load)
        for cid in route:
            assignment[cid - 1] = vehicle_id
    
    # Pad with empty vehicles
    while len(final_loads) < VEHICLES:
        final_loads.append(0)
    
    # Step 7: Calculate total distance
    total_distance = 0.0
    for route in final_routes:
        if not route:
            continue
        
        # Depot -> first customer
        total_distance += euclid(DEPOT, locations[route[0]])
        
        # Between customers
        for i in range(len(route) - 1):
            total_distance += euclid(locations[route[i]], locations[route[i + 1]])
        
        # Last customer -> depot
        total_distance += euclid(locations[route[-1]], DEPOT)
    
    # Calculate overload
    total_demand = sum(demands.values())
    total_capacity = VEHICLES * CAPACITY
    overload = max(0, total_demand - total_capacity)
    
    # Create candidate
    candidate = Candidate(
        cid="clarke_wright",
        assign=assignment,
        routes=final_routes,
        distance=total_distance,
        overload=overload,
        loads=final_loads,
        f=total_distance + 1000 * overload
    )
    
    return candidate


if __name__ == "__main__":
    print("Running Clarke-Wright Savings Algorithm (Industry Standard)...")
    
    result = clarke_wright_vrp()
    
    print(f"\nClarke-Wright Results:")
    print(f"  Distance: {result.distance:.2f}")
    print(f"  Overload: {result.overload}")
    print(f"  Objective (f): {result.f:.2f}")
    print(f"  Loads: {result.loads}")
    print(f"\nRoutes:")
    for v, route in enumerate(result.routes):
        print(f"  Vehicle {v}: {route}")
