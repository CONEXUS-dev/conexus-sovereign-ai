"""
Baseline solver: greedy + local search. No paradox buffer, no pilot.
Used for fair comparison against FE hybrid.
"""

import random
import time
from typing import List, Dict, Any

from .types import Instance, Candidate
from .evaluate import evaluate, full_repair, compute_loads
from .operators import op_swap, op_relocate, op_cross_exchange, local_search_2opt


def baseline_solve(inst: Instance, seed: int = 42,
                   max_gens: int = 200, pop_size: int = 20,
                   stagnation_limit: int = 40) -> Dict[str, Any]:
    """
    Simple baseline: greedy init + mutation + local search.
    No paradox buffer, no pilot, no pattern injection.
    """
    rng = random.Random(seed)
    t0 = time.time()

    # Initialize population
    population: List[Candidate] = []
    for i in range(pop_size):
        if i % 2 == 0:
            assign = _greedy_init(inst, rng)
        else:
            assign = [rng.randint(0, inst.n_vehicles - 1) for _ in range(inst.n_customers)]
        assign = full_repair(inst, assign, rng)
        cand = Candidate(cid=f"bl_init_{i}", assign=assign)
        evaluate(inst, cand)
        population.append(cand)

    population.sort(key=lambda c: c.fitness)
    best = population[0]
    stagnation = 0

    for g in range(1, max_gens + 1):
        # Mutation: generate children from top half
        survivors = population[:pop_size // 2]
        children = []
        ops = [op_swap, op_relocate, op_cross_exchange]
        while len(children) < pop_size - len(survivors):
            parent = rng.choice(survivors)
            op = rng.choice(ops)
            new_assign = op(inst, parent.assign, rng)
            new_assign = full_repair(inst, new_assign, rng)
            child = Candidate(cid=f"bl_g{g}_{len(children)}", assign=new_assign)
            evaluate(inst, child)
            children.append(child)

        population = survivors + children
        population.sort(key=lambda c: c.fitness)

        # Local search on best every 10 gens
        if g % 10 == 0:
            for idx in range(min(3, len(population))):
                cand = population[idx]
                new_routes = [local_search_2opt(inst, r) for r in cand.routes]
                new_assign = list(cand.assign)
                for v, route in enumerate(new_routes):
                    for c in route:
                        new_assign[c] = v
                improved = Candidate(cid=cand.cid + "_ls", assign=new_assign)
                evaluate(inst, improved)
                if improved.fitness < cand.fitness:
                    population[idx] = improved

            population.sort(key=lambda c: c.fitness)

        if population[0].fitness < best.fitness:
            best = population[0]
            stagnation = 0
        else:
            stagnation += 1

        if g % 20 == 0 or g == 1:
            print(f"  [Baseline] Gen {g:4d}: best={best.distance:.1f} "
                  f"feasible={best.feasible} stag={stagnation}")

        if stagnation >= stagnation_limit:
            print(f"  [Baseline] Early stop at gen {g}")
            break

    elapsed = time.time() - t0
    return {
        "best_distance": best.distance,
        "best_fitness": best.fitness,
        "best_feasible": best.feasible,
        "best_overload": best.overload,
        "generations": g,
        "elapsed": elapsed,
    }


def _greedy_init(inst: Instance, rng: random.Random) -> List[int]:
    """Greedy nearest-neighbour assignment."""
    assign = [0] * inst.n_customers
    remaining = list(range(inst.n_customers))
    rng.shuffle(remaining)
    vehicle_loads = [0] * inst.n_vehicles
    for c in remaining:
        best_v = min(range(inst.n_vehicles),
                     key=lambda v: (vehicle_loads[v] + inst.demands[c] > inst.capacity,
                                    vehicle_loads[v]))
        assign[c] = best_v
        vehicle_loads[best_v] += inst.demands[c]
    return assign
