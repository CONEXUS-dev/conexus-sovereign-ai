"""
VRP Instance - Problem definition with canonical 0..N-1 indexing
"""

import json
import random
import math
from typing import List, Tuple
from dataclasses import dataclass, asdict


@dataclass
class VRPInstance:
    """
    VRP problem instance with canonical indexing.
    
    Indexing scheme:
    - Customers: 0..N-1 (internal)
    - Depot: separate constant, not in customer index range
    """
    
    name: str
    n_customers: int
    n_vehicles: int
    vehicle_capacity: int
    depot: Tuple[float, float]
    customer_locations: List[Tuple[float, float]]  # Length N, indexed 0..N-1
    customer_demands: List[int]  # Length N, indexed 0..N-1
    seed: int
    
    @property
    def total_demand(self) -> int:
        """Total demand across all customers."""
        return sum(self.customer_demands)
    
    @property
    def total_capacity(self) -> int:
        """Total capacity across all vehicles."""
        return self.n_vehicles * self.vehicle_capacity
    
    @property
    def is_feasible(self) -> bool:
        """Check if instance is feasible (capacity sufficient for demand)."""
        return self.total_capacity >= self.total_demand
    
    @property
    def capacity_slack(self) -> int:
        """Unused capacity if all vehicles fully utilized."""
        return self.total_capacity - self.total_demand
    
    def distance(self, i: int, j: int) -> float:
        """
        Euclidean distance between two locations.
        i, j can be customer indices (0..N-1) or -1 for depot.
        """
        loc_i = self.depot if i == -1 else self.customer_locations[i]
        loc_j = self.depot if j == -1 else self.customer_locations[j]
        return math.hypot(loc_i[0] - loc_j[0], loc_i[1] - loc_j[1])
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'n_customers': self.n_customers,
            'n_vehicles': self.n_vehicles,
            'vehicle_capacity': self.vehicle_capacity,
            'depot': list(self.depot),
            'customer_locations': [list(loc) for loc in self.customer_locations],
            'customer_demands': self.customer_demands,
            'seed': self.seed,
            'total_demand': self.total_demand,
            'total_capacity': self.total_capacity,
            'is_feasible': self.is_feasible,
            'capacity_slack': self.capacity_slack
        }
    
    def save(self, filepath: str):
        """Save instance to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'VRPInstance':
        """Load instance from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return cls(
            name=data['name'],
            n_customers=data['n_customers'],
            n_vehicles=data['n_vehicles'],
            vehicle_capacity=data['vehicle_capacity'],
            depot=tuple(data['depot']),
            customer_locations=[tuple(loc) for loc in data['customer_locations']],
            customer_demands=data['customer_demands'],
            seed=data['seed']
        )
    
    @classmethod
    def generate_random(
        cls,
        name: str,
        n_customers: int,
        n_vehicles: int,
        vehicle_capacity: int,
        seed: int,
        grid_size: int = 100,
        demand_min: int = 5,
        demand_max: int = 30
    ) -> 'VRPInstance':
        """
        Generate random VRP instance.
        
        Args:
            name: Instance name
            n_customers: Number of customers (will be indexed 0..N-1)
            n_vehicles: Number of vehicles
            vehicle_capacity: Capacity per vehicle
            seed: Random seed for reproducibility
            grid_size: Size of coordinate grid
            demand_min: Minimum customer demand
            demand_max: Maximum customer demand
        """
        rng = random.Random(seed)
        
        # Depot at center
        depot = (grid_size / 2, grid_size / 2)
        
        # Random customer locations
        locations = []
        for _ in range(n_customers):
            x = rng.uniform(0, grid_size)
            y = rng.uniform(0, grid_size)
            locations.append((x, y))
        
        # Random demands
        demands = [rng.randint(demand_min, demand_max) for _ in range(n_customers)]
        
        return cls(
            name=name,
            n_customers=n_customers,
            n_vehicles=n_vehicles,
            vehicle_capacity=vehicle_capacity,
            depot=depot,
            customer_locations=locations,
            customer_demands=demands,
            seed=seed
        )


if __name__ == "__main__":
    # Test instance generation
    instance = VRPInstance.generate_random(
        name="test_25",
        n_customers=25,
        n_vehicles=5,
        vehicle_capacity=100,
        seed=42
    )
    
    print(f"Instance: {instance.name}")
    print(f"Customers: {instance.n_customers} (indexed 0..{instance.n_customers-1})")
    print(f"Vehicles: {instance.n_vehicles}")
    print(f"Capacity: {instance.vehicle_capacity}")
    print(f"Total demand: {instance.total_demand}")
    print(f"Total capacity: {instance.total_capacity}")
    print(f"Feasible: {instance.is_feasible}")
    print(f"Slack: {instance.capacity_slack}")
    
    # Test distance calculation
    print(f"\nDistance depot to customer 0: {instance.distance(-1, 0):.2f}")
    print(f"Distance customer 0 to customer 1: {instance.distance(0, 1):.2f}")
