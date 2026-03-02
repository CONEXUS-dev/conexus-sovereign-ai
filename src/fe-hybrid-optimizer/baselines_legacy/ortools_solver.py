"""
OR-Tools VRP Solver - Gold Standard Baseline
"""

import time
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from engine.vrp_instance import VRPInstance
from engine.candidate import Candidate


class ORToolsSolver:
    """
    OR-Tools VRP solver for baseline comparison.
    
    Uses Google's state-of-the-art constraint programming solver
    with guided local search metaheuristic.
    """
    
    def __init__(self, instance: VRPInstance):
        self.instance = instance
    
    def solve(self, time_limit_seconds: int = 30) -> Candidate:
        """
        Solve VRP using OR-Tools.
        
        Args:
            time_limit_seconds: Time limit for solver
        
        Returns:
            Candidate with OR-Tools solution (0-indexed)
        """
        n = self.instance.n_customers
        n_vehicles = self.instance.n_vehicles
        capacity = self.instance.vehicle_capacity
        
        # Build distance matrix: depot + customers
        locations = [self.instance.depot] + self.instance.customer_locations
        num_locations = len(locations)
        
        distance_matrix = []
        for i in range(num_locations):
            row = []
            for j in range(num_locations):
                if i == 0:
                    loc_i = self.instance.depot
                else:
                    loc_i = self.instance.customer_locations[i - 1]
                
                if j == 0:
                    loc_j = self.instance.depot
                else:
                    loc_j = self.instance.customer_locations[j - 1]
                
                dist = ((loc_i[0] - loc_j[0])**2 + (loc_i[1] - loc_j[1])**2)**0.5
                row.append(int(dist * 1000))
            distance_matrix.append(row)
        
        # Build demand array: depot (0) + customers
        demands = [0] + self.instance.customer_demands
        
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(num_locations, n_vehicles, 0)
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
            [capacity] * n_vehicles,
            True,
            'Capacity'
        )
        
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
        start_time = time.time()
        solution = routing.SolveWithParameters(search_parameters)
        elapsed = time.time() - start_time
        
        if solution is None:
            raise RuntimeError("OR-Tools VRP solver failed to find solution")
        
        # Extract solution (convert to 0-indexed customer IDs)
        routes = []
        total_distance = 0.0
        loads = []
        
        for vehicle_id in range(n_vehicles):
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
        assignment = [0] * n
        for vehicle_id, route in enumerate(routes):
            for customer_idx in route:
                assignment[customer_idx] = vehicle_id
        
        # Calculate overload
        overload = sum(max(0, load - capacity) for load in loads)
        
        # Create candidate
        candidate = Candidate(
            id="ortools_baseline",
            assignment=assignment,
            routes=routes,
            distance=total_distance,
            overload=overload,
            loads=loads,
            objective=total_distance,
            feasible=(overload == 0)
        )
        
        return candidate


if __name__ == "__main__":
    # Test OR-Tools solver
    instance = VRPInstance.generate_random(
        name="test_ortools",
        n_customers=25,
        n_vehicles=5,
        vehicle_capacity=100,
        seed=42
    )
    
    solver = ORToolsSolver(instance)
    
    print("Running OR-Tools solver...")
    result = solver.solve(time_limit_seconds=10)
    
    print(f"\nOR-Tools Results:")
    print(f"  Distance: {result.distance:.2f}")
    print(f"  Overload: {result.overload}")
    print(f"  Objective: {result.objective:.2f}")
    print(f"  Feasible: {result.feasible}")
    print(f"  Active routes: {sum(1 for r in result.routes if r)}")
