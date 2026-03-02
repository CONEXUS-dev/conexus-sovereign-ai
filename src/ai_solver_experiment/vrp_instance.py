"""
VRP Instance generation and serialization.

Generates reproducible random Euclidean VRP instances.
Customers indexed 0..N-1, depot at grid centre.
All randomness controlled by seed.
"""

import json
import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class VRPInstance:
    """A capacitated VRP instance."""
    name: str
    n_customers: int
    n_vehicles: int
    capacity: int
    depot: Tuple[float, float]
    locations: List[Tuple[float, float]]
    demands: List[int]
    seed: int

    @property
    def total_demand(self) -> int:
        return sum(self.demands)

    @property
    def total_capacity(self) -> int:
        return self.n_vehicles * self.capacity

    def dist(self, i: int, j: int) -> float:
        """Euclidean distance. Use -1 for depot."""
        a = self.depot if i == -1 else self.locations[i]
        b = self.depot if j == -1 else self.locations[j]
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "n_customers": self.n_customers,
            "n_vehicles": self.n_vehicles,
            "capacity": self.capacity,
            "depot": list(self.depot),
            "locations": [list(loc) for loc in self.locations],
            "demands": self.demands,
            "seed": self.seed,
            "total_demand": self.total_demand,
            "total_capacity": self.total_capacity,
        }

    def to_json_for_ai(self) -> str:
        """Compact JSON representation for AI prompt injection."""
        return json.dumps({
            "n_customers": self.n_customers,
            "n_vehicles": self.n_vehicles,
            "capacity": self.capacity,
            "depot": list(self.depot),
            "customers": [
                {"id": i, "x": self.locations[i][0], "y": self.locations[i][1],
                 "demand": self.demands[i]}
                for i in range(self.n_customers)
            ],
        }, indent=None)

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "VRPInstance":
        with open(path) as f:
            d = json.load(f)
        return cls(
            name=d["name"], n_customers=d["n_customers"],
            n_vehicles=d["n_vehicles"], capacity=d["capacity"],
            depot=tuple(d["depot"]),
            locations=[tuple(loc) for loc in d["locations"]],
            demands=d["demands"], seed=d["seed"],
        )


def auto_vehicles(n_customers: int) -> int:
    """Heuristic: ~15 customers per vehicle."""
    return max(2, (n_customers + 14) // 15)


def auto_capacity(n_customers: int, n_vehicles: int, seed: int,
                  demand_range: Tuple[int, int] = (5, 25)) -> int:
    """Compute capacity with ~20% slack so instance is feasible."""
    rng = random.Random(seed)
    total = sum(rng.randint(*demand_range) for _ in range(n_customers))
    return int(1.2 * total / n_vehicles) + 1


def generate_instance(
    n_customers: int,
    seed: int,
    grid_size: int = 100,
    demand_range: Tuple[int, int] = (5, 25),
) -> VRPInstance:
    """
    Generate a random Euclidean VRP instance.
    Vehicles and capacity auto-computed for feasibility.
    """
    n_vehicles = auto_vehicles(n_customers)
    capacity = auto_capacity(n_customers, n_vehicles, seed, demand_range)

    rng = random.Random(seed)
    depot = (grid_size / 2.0, grid_size / 2.0)
    locations = [
        (rng.uniform(0, grid_size), rng.uniform(0, grid_size))
        for _ in range(n_customers)
    ]
    demands = [rng.randint(*demand_range) for _ in range(n_customers)]

    name = f"vrp_n{n_customers}_s{seed}"

    return VRPInstance(
        name=name,
        n_customers=n_customers,
        n_vehicles=n_vehicles,
        capacity=capacity,
        depot=depot,
        locations=locations,
        demands=demands,
        seed=seed,
    )
