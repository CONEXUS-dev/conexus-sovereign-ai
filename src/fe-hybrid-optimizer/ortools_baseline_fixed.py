"""
OR-Tools VRP Solver - Fixed for 0-indexed Internal Representation
Works with fe_hybrid_vrp_fixed.py
"""

from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from fe_hybrid_vrp_fixed import (
    DEPOT, N_CUSTOMERS, VEHICLES, CAPACITY, 
    CUSTOMER_LOCATIONS, CUSTOMER_DEMANDS, TOTAL_DEMAND,
    Candidate
)
import math


def euclid(p1, p2):
    """Euclidean distance."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)


def ortools_vrp_solver(time_limit_seconds: int = 30) -> Candidate:
    """
    Solve VRP using OR-Tools routing solver (gold standard baseline).
    Uses 0-indexed internal representation (customers 0..N-1).
    
    Args:
        time_limit_seconds: Time limit for solver
    
    Returns:
        Candidate with OR-Tools solution (0-indexed routes)
    """
    
    # Build distance matrix: depot + customers
    locations = [DEPOT] + CUSTOMER_LOCATIONS
    num_locations = len(locations)
    
    distance_matrix = []
    for i in range(num_locations):
        row = []
        for j in range(num_locations):
            dist = int(euclid(locations[i], locations[j]) * 1000)
            row.append(dist)
        distance_matrix.append(row)
    
    # Build demand array: depot (0) + customers
    demands = [0] + CUSTOMER_DEMANDS
    
    # Create routing model
    manager = pywrapcp.RoutingIndexManager(num_locations, VEHICLES, 0)
    routing = pywrapcp.RoutingModel(manager)
    
    # Distance callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Capacity constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]
    
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        [CAPACITY] * VEHICLES,
        True,
        'Capacity'
    )
    
    # Allow dropping nodes with penalty (for infeasible problems)
    penalty = 1000000
    for node in range(1, num_locations):
        routing.AddDisjunction([manager.NodeToIndex(node)], penalty)
    
    # Search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(time_limit_seconds)
    
    # Solve
    solution = routing.SolveWithParameters(search_parameters)
    
    if solution is None:
        raise RuntimeError("OR-Tools VRP solver failed to find solution")
    
    # Extract solution (convert to 0-indexed customer IDs)
    routes = []
    total_distance = 0.0
    loads = []
    
    for vehicle_id in range(VEHICLES):
        route = []
        index = routing.Start(vehicle_id)
        route_distance = 0
        route_load = 0
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            
            if node_index != 0:  # Not depot
                # Convert from OR-Tools node (1..N) to internal customer index (0..N-1)
                customer_idx = node_index - 1
                route.append(customer_idx)
                route_load += demands[node_index]
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        
        routes.append(route)
        total_distance += route_distance / 1000.0
        loads.append(route_load)
    
    # Build assignment vector (0-indexed)
    assignment = [0] * N_CUSTOMERS
    for vehicle_id, route in enumerate(routes):
        for customer_idx in route:
            assignment[customer_idx] = vehicle_id
    
    # Calculate overload
    overload = max(0, TOTAL_DEMAND - VEHICLES * CAPACITY)
    
    # Create candidate
    candidate = Candidate(
        cid="ortools_baseline",
        assign=assignment,
        routes=routes,
        distance=total_distance,
        overload=overload,
        loads=loads,
        f=total_distance + 1000 * overload
    )
    
    return candidate


if __name__ == "__main__":
    print("Running OR-Tools VRP solver (0-indexed)...")
    
    result = ortools_vrp_solver(time_limit_seconds=30)
    
    print(f"\nOR-Tools Results:")
    print(f"  Distance: {result.distance:.2f}")
    print(f"  Overload: {result.overload}")
    print(f"  Objective (f): {result.f:.2f}")
    print(f"  Loads: {result.loads[:5]}...")
    print(f"\nFirst route (0-indexed): {result.routes[0]}")
