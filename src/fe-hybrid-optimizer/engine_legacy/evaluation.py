"""
Evaluator - Objective calculation and feasibility checking
"""

from typing import List, Tuple
from ortools.constraint_solver import pywrapcp
from .vrp_instance import VRPInstance
from .candidate import Candidate


class Evaluator:
    """
    Evaluates VRP solutions: builds routes, calculates distance, checks feasibility.
    """
    
    def __init__(self, instance: VRPInstance):
        self.instance = instance
    
    def build_routes_from_assignment(self, assignment: List[int]) -> List[List[int]]:
        """
        Build routes from assignment vector.
        Groups customers by vehicle and orders them with TSP solver.
        
        Returns:
            routes[v] = ordered list of customer indices for vehicle v
        """
        n = self.instance.n_customers
        n_vehicles = self.instance.n_vehicles
        
        # Group customers by vehicle
        vehicle_customers = [[] for _ in range(n_vehicles)]
        for cust_idx in range(n):
            vehicle = assignment[cust_idx]
            vehicle_customers[vehicle].append(cust_idx)
        
        # Order each route with TSP
        routes = []
        for customers in vehicle_customers:
            if not customers:
                routes.append([])
            elif len(customers) == 1:
                routes.append(customers)
            else:
                ordered = self._solve_tsp(customers)
                routes.append(ordered)
        
        return routes
    
    def _solve_tsp(self, customers: List[int], time_limit_ms: int = 50) -> List[int]:
        """
        Solve TSP for a set of customers using OR-Tools.
        
        Args:
            customers: List of customer indices
            time_limit_ms: Time limit in milliseconds
        
        Returns:
            Ordered list of customer indices
        """
        if len(customers) <= 1:
            return customers
        
        n = len(customers)
        
        # Build distance matrix
        dist_matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = self.instance.distance(customers[i], customers[j])
                    dist_matrix[i][j] = int(dist * 1000)
        
        # Create TSP model
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
            # Extract route
            index = routing.Start(0)
            route = []
            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                route.append(customers[node])
                index = solution.Value(routing.NextVar(index))
            return route
        
        return customers
    
    def calculate_route_distance(self, route: List[int]) -> float:
        """
        Calculate total distance for a route: depot -> customers -> depot.
        """
        if not route:
            return 0.0
        
        # Depot to first customer
        dist = self.instance.distance(-1, route[0])
        
        # Between customers
        for i in range(len(route) - 1):
            dist += self.instance.distance(route[i], route[i + 1])
        
        # Last customer to depot
        dist += self.instance.distance(route[-1], -1)
        
        return dist
    
    def calculate_loads(self, assignment: List[int]) -> List[int]:
        """
        Calculate load per vehicle from assignment.
        """
        loads = [0] * self.instance.n_vehicles
        for cust_idx, vehicle in enumerate(assignment):
            loads[vehicle] += self.instance.customer_demands[cust_idx]
        return loads
    
    def check_coverage(self, assignment: List[int]) -> Tuple[bool, str]:
        """
        Check coverage invariant: every customer 0..N-1 appears exactly once.
        """
        n = self.instance.n_customers
        
        if len(assignment) != n:
            return False, f"Assignment length {len(assignment)} != {n}"
        
        covered = set(range(n))
        assigned = set(range(len(assignment)))
        
        if covered != assigned:
            missing = covered - assigned
            extra = assigned - covered
            msg = []
            if missing:
                msg.append(f"Missing: {sorted(list(missing))[:5]}")
            if extra:
                msg.append(f"Extra: {sorted(list(extra))[:5]}")
            return False, "; ".join(msg)
        
        return True, ""
    
    def check_conservation(self, loads: List[int]) -> Tuple[bool, str]:
        """
        Check conservation invariant: sum(loads) = total_demand.
        """
        total_load = sum(loads)
        expected = self.instance.total_demand
        
        if abs(total_load - expected) > 0.01:
            return False, f"Load {total_load} != demand {expected}"
        
        return True, ""
    
    def check_capacity(self, loads: List[int]) -> Tuple[bool, int]:
        """
        Check capacity constraints.
        
        Returns:
            (all_feasible, total_overload)
        """
        capacity = self.instance.vehicle_capacity
        overload = sum(max(0, load - capacity) for load in loads)
        all_feasible = overload == 0
        return all_feasible, overload
    
    def evaluate(self, candidate: Candidate) -> None:
        """
        Full evaluation of candidate.
        Updates candidate in-place with routes, distance, loads, feasibility.
        
        Raises ValueError if hard invariants violated (coverage, conservation).
        """
        # Check coverage
        coverage_valid, coverage_msg = self.check_coverage(candidate.assignment)
        candidate.coverage_valid = coverage_valid
        if not coverage_valid:
            raise ValueError(f"Coverage violation: {coverage_msg}")
        
        # Build routes
        candidate.routes = self.build_routes_from_assignment(candidate.assignment)
        
        # Calculate distance
        candidate.distance = sum(
            self.calculate_route_distance(route) for route in candidate.routes
        )
        
        # Calculate loads
        candidate.loads = self.calculate_loads(candidate.assignment)
        
        # Check conservation
        conservation_valid, conservation_msg = self.check_conservation(candidate.loads)
        candidate.conservation_valid = conservation_valid
        if not conservation_valid:
            raise ValueError(f"Conservation violation: {conservation_msg}")
        
        # Check capacity
        capacity_valid, overload = self.check_capacity(candidate.loads)
        candidate.capacity_valid = capacity_valid
        candidate.overload = overload
        
        # Overall feasibility (hard constraints only)
        candidate.feasible = coverage_valid and conservation_valid and capacity_valid
        
        # Objective (distance only for hard-constraint mode)
        candidate.objective = candidate.distance
        
        # Metrics for pilot
        active_routes = sum(1 for route in candidate.routes if route)
        candidate.metrics = {
            'active_routes': active_routes,
            'max_load': max(candidate.loads) if candidate.loads else 0,
            'min_load': min(candidate.loads) if candidate.loads else 0,
            'mean_load': sum(candidate.loads) / len(candidate.loads) if candidate.loads else 0,
            'overload': overload
        }


if __name__ == "__main__":
    # Test evaluator
    from .vrp_instance import VRPInstance
    from .candidate import Candidate
    
    instance = VRPInstance.generate_random(
        name="test_eval",
        n_customers=10,
        n_vehicles=3,
        vehicle_capacity=50,
        seed=42
    )
    
    evaluator = Evaluator(instance)
    
    # Create test candidate
    assignment = [i % 3 for i in range(10)]
    candidate = Candidate(id="test", assignment=assignment)
    
    print("Evaluating candidate...")
    evaluator.evaluate(candidate)
    
    print(f"Distance: {candidate.distance:.2f}")
    print(f"Loads: {candidate.loads}")
    print(f"Overload: {candidate.overload}")
    print(f"Feasible: {candidate.feasible}")
    print(f"Routes: {candidate.routes}")
    print(f"Metrics: {candidate.metrics}")
