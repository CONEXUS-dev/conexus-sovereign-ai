"""
VRP instance generation and loading.
"""

import random
from .types import Instance


def generate_instance(
    n_customers: int,
    n_vehicles: int,
    capacity: int,
    seed: int = 42,
    grid_size: int = 100,
    demand_range: tuple = (5, 25),
    name: str = "",
) -> Instance:
    """
    Generate a random Euclidean VRP instance.
    Customers indexed 0..N-1, depot at grid centre.
    Capacity is set so the instance is feasible.
    """
    rng = random.Random(seed)
    depot = (grid_size / 2.0, grid_size / 2.0)
    locations = [(rng.uniform(0, grid_size), rng.uniform(0, grid_size))
                 for _ in range(n_customers)]
    demands = [rng.randint(*demand_range) for _ in range(n_customers)]

    if not name:
        name = f"vrp_{n_customers}_{n_vehicles}_s{seed}"

    return Instance(
        name=name,
        n_customers=n_customers,
        n_vehicles=n_vehicles,
        capacity=capacity,
        depot=depot,
        locations=locations,
        demands=demands,
        seed=seed,
    )


def auto_capacity(n_customers: int, n_vehicles: int, seed: int = 42,
                   demand_range: tuple = (5, 25)) -> int:
    """Compute a capacity that makes the instance feasible with ~20% slack."""
    rng = random.Random(seed)
    total = sum(rng.randint(*demand_range) for _ in range(n_customers))
    # ~20 % slack
    return int(1.2 * total / n_vehicles) + 1
