"""
Operators - Deterministic move operators for VRP solutions
"""

import random
from typing import List, Tuple
from .vrp_instance import VRPInstance


class Operators:
    """
    Deterministic move operators for VRP.
    
    All operators work on assignment vectors (0-indexed customers).
    """
    
    def __init__(self, instance: VRPInstance, rng: random.Random):
        self.instance = instance
        self.rng = rng
    
    def swap(self, assignment: List[int]) -> List[int]:
        """
        Swap two random customers between vehicles.
        """
        n = self.instance.n_customers
        if n < 2:
            return assignment
        
        i, j = self.rng.sample(range(n), 2)
        new_assignment = list(assignment)
        new_assignment[i], new_assignment[j] = new_assignment[j], new_assignment[i]
        return new_assignment
    
    def relocate(self, assignment: List[int]) -> List[int]:
        """
        Move a random customer to a random vehicle.
        """
        n = self.instance.n_customers
        if n < 1:
            return assignment
        
        cust_idx = self.rng.randint(0, n - 1)
        new_vehicle = self.rng.randint(0, self.instance.n_vehicles - 1)
        
        new_assignment = list(assignment)
        new_assignment[cust_idx] = new_vehicle
        return new_assignment
    
    def swap_within_route(self, assignment: List[int], routes: List[List[int]]) -> List[int]:
        """
        Swap two customers within the same route (preserves vehicle assignments).
        This is useful for TSP-like improvements within routes.
        """
        # Find routes with at least 2 customers
        valid_routes = [v for v, route in enumerate(routes) if len(route) >= 2]
        
        if not valid_routes:
            return assignment
        
        vehicle = self.rng.choice(valid_routes)
        route = routes[vehicle]
        
        i, j = self.rng.sample(range(len(route)), 2)
        # Swap positions in route (but assignment vector stays same since same vehicle)
        # This operator is mainly for route ordering, handled by TSP solver
        return assignment
    
    def cross_exchange(self, assignment: List[int], routes: List[List[int]]) -> List[int]:
        """
        Exchange segments between two routes.
        """
        # Find routes with customers
        valid_routes = [v for v, route in enumerate(routes) if len(route) >= 1]
        
        if len(valid_routes) < 2:
            return assignment
        
        v1, v2 = self.rng.sample(valid_routes, 2)
        route1 = routes[v1]
        route2 = routes[v2]
        
        # Pick random customers from each route
        if not route1 or not route2:
            return assignment
        
        cust1 = self.rng.choice(route1)
        cust2 = self.rng.choice(route2)
        
        # Swap their vehicle assignments
        new_assignment = list(assignment)
        new_assignment[cust1] = v2
        new_assignment[cust2] = v1
        
        return new_assignment
    
    def apply_operator(self, operator_name: str, assignment: List[int], 
                       routes: List[List[int]] = None) -> List[int]:
        """
        Apply named operator to assignment.
        
        Args:
            operator_name: One of 'swap', 'relocate', 'cross_exchange'
            assignment: Current assignment vector
            routes: Current routes (needed for some operators)
        
        Returns:
            New assignment vector
        """
        if operator_name == 'swap':
            return self.swap(assignment)
        elif operator_name == 'relocate':
            return self.relocate(assignment)
        elif operator_name == 'cross_exchange':
            if routes is None:
                return assignment
            return self.cross_exchange(assignment, routes)
        else:
            raise ValueError(f"Unknown operator: {operator_name}")


if __name__ == "__main__":
    # Test operators
    from .vrp_instance import VRPInstance
    
    instance = VRPInstance.generate_random(
        name="test_ops",
        n_customers=10,
        n_vehicles=3,
        vehicle_capacity=50,
        seed=42
    )
    
    rng = random.Random(42)
    ops = Operators(instance, rng)
    
    # Initial assignment
    assignment = [i % 3 for i in range(10)]
    print(f"Initial assignment: {assignment}")
    
    # Test swap
    new_assignment = ops.swap(assignment)
    print(f"After swap: {new_assignment}")
    
    # Test relocate
    new_assignment = ops.relocate(assignment)
    print(f"After relocate: {new_assignment}")
    
    # Test cross exchange
    routes = [[], [], []]
    for i, v in enumerate(assignment):
        routes[v].append(i)
    
    new_assignment = ops.cross_exchange(assignment, routes)
    print(f"After cross_exchange: {new_assignment}")
