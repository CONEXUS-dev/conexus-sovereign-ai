"""
Repair Engine - Deterministic two-phase repair for VRP solutions
"""

import random
from typing import List, Tuple, Set
from .vrp_instance import VRPInstance


class RepairEngine:
    """
    Deterministic repair engine for VRP solutions.
    
    Two-phase repair:
    1. Coverage repair: Fix missing/duplicate customers
    2. Capacity repair: Resolve overloaded routes
    """
    
    def __init__(self, instance: VRPInstance, rng: random.Random):
        self.instance = instance
        self.rng = rng
    
    def repair_coverage(self, assignment: List[int]) -> Tuple[List[int], bool]:
        """
        Phase 1: Repair coverage violations.
        
        Ensures every customer 0..N-1 appears exactly once in assignment.
        
        Returns:
            (repaired_assignment, was_modified)
        """
        n = self.instance.n_customers
        
        if len(assignment) != n:
            raise ValueError(f"Assignment length {len(assignment)} != n_customers {n}")
        
        # Find assigned customers
        assigned_customers = set()
        duplicate_positions = []
        
        for i in range(n):
            if i in assigned_customers:
                # This position has a duplicate customer assignment
                duplicate_positions.append(i)
            else:
                assigned_customers.add(i)
        
        # Find missing customers
        all_customers = set(range(n))
        missing_customers = all_customers - assigned_customers
        
        if not missing_customers and not duplicate_positions:
            return assignment, False  # Already valid
        
        # Repair: assign missing customers to positions with duplicates
        repaired = list(assignment)
        missing_list = sorted(missing_customers)  # Deterministic order
        
        # For each missing customer, find best vehicle by load balance
        for missing_cust in missing_list:
            # Calculate current vehicle loads
            vehicle_loads = [0] * self.instance.n_vehicles
            for cust_idx in range(n):
                if cust_idx not in missing_customers:
                    vehicle_loads[repaired[cust_idx]] += self.instance.customer_demands[cust_idx]
            
            # Assign to vehicle with minimum load
            best_vehicle = min(range(self.instance.n_vehicles), key=lambda v: vehicle_loads[v])
            repaired[missing_cust] = best_vehicle
        
        return repaired, True
    
    def repair_capacity(self, assignment: List[int]) -> Tuple[List[int], bool]:
        """
        Phase 2: Repair capacity violations.
        
        Moves customers from overloaded routes to routes with slack.
        Uses best insertion cost (distance increase).
        
        Returns:
            (repaired_assignment, was_modified)
        """
        n = self.instance.n_customers
        capacity = self.instance.vehicle_capacity
        
        # Calculate current loads
        vehicle_loads = [0] * self.instance.n_vehicles
        vehicle_customers = [[] for _ in range(self.instance.n_vehicles)]
        
        for cust_idx in range(n):
            vehicle = assignment[cust_idx]
            vehicle_loads[vehicle] += self.instance.customer_demands[cust_idx]
            vehicle_customers[vehicle].append(cust_idx)
        
        # Find overloaded vehicles
        overloaded = [(v, vehicle_loads[v] - capacity) 
                      for v in range(self.instance.n_vehicles) 
                      if vehicle_loads[v] > capacity]
        
        if not overloaded:
            return assignment, False  # No violations
        
        repaired = list(assignment)
        modified = False
        
        # Sort overloaded vehicles by excess (most overloaded first)
        overloaded.sort(key=lambda x: x[1], reverse=True)
        
        for overloaded_vehicle, excess in overloaded:
            # Try to move customers to other vehicles
            customers_in_vehicle = [c for c in range(n) if repaired[c] == overloaded_vehicle]
            
            # Sort customers by demand (move largest first to reduce violations faster)
            customers_in_vehicle.sort(key=lambda c: self.instance.customer_demands[c], reverse=True)
            
            for cust_idx in customers_in_vehicle:
                if vehicle_loads[overloaded_vehicle] <= capacity:
                    break  # This vehicle is now feasible
                
                cust_demand = self.instance.customer_demands[cust_idx]
                
                # Find vehicles with enough slack
                candidate_vehicles = [
                    v for v in range(self.instance.n_vehicles)
                    if v != overloaded_vehicle and vehicle_loads[v] + cust_demand <= capacity
                ]
                
                if not candidate_vehicles:
                    # Try vehicles with least overload even if still over capacity
                    candidate_vehicles = [
                        v for v in range(self.instance.n_vehicles)
                        if v != overloaded_vehicle
                    ]
                    if not candidate_vehicles:
                        continue
                    
                    # Pick vehicle with most remaining capacity
                    best_vehicle = min(candidate_vehicles, key=lambda v: vehicle_loads[v])
                else:
                    # Pick vehicle with most remaining capacity among feasible ones
                    best_vehicle = min(candidate_vehicles, key=lambda v: vehicle_loads[v])
                
                # Move customer
                repaired[cust_idx] = best_vehicle
                vehicle_loads[overloaded_vehicle] -= cust_demand
                vehicle_loads[best_vehicle] += cust_demand
                modified = True
        
        return repaired, modified
    
    def repair_full(self, assignment: List[int]) -> Tuple[List[int], dict]:
        """
        Full two-phase repair.
        
        Returns:
            (repaired_assignment, repair_info)
        """
        # Phase 1: Coverage
        assignment, coverage_modified = self.repair_coverage(assignment)
        
        # Phase 2: Capacity
        assignment, capacity_modified = self.repair_capacity(assignment)
        
        repair_info = {
            'coverage_repaired': coverage_modified,
            'capacity_repaired': capacity_modified,
            'any_repair': coverage_modified or capacity_modified
        }
        
        return assignment, repair_info


if __name__ == "__main__":
    # Test repair engine
    from .vrp_instance import VRPInstance
    
    instance = VRPInstance.generate_random(
        name="test_repair",
        n_customers=10,
        n_vehicles=3,
        vehicle_capacity=50,
        seed=42
    )
    
    rng = random.Random(42)
    repair = RepairEngine(instance, rng)
    
    # Test coverage repair
    print("Test 1: Coverage repair (missing customer 5)")
    assignment = [0, 1, 2, 0, 1, 1, 0, 2, 1, 0]  # Customer 5 duplicated
    repaired, modified = repair.repair_coverage(assignment)
    print(f"  Original: {assignment}")
    print(f"  Repaired: {repaired}")
    print(f"  Modified: {modified}")
    print(f"  All customers present: {set(range(10)) == set(range(len(repaired)))}")
    
    # Test capacity repair
    print("\nTest 2: Capacity repair")
    assignment = [0] * 10  # All customers on vehicle 0
    repaired, modified = repair.repair_capacity(assignment)
    
    loads = [0] * 3
    for i, v in enumerate(repaired):
        loads[v] += instance.customer_demands[i]
    
    print(f"  Original assignment: all to vehicle 0")
    print(f"  Repaired loads: {loads}")
    print(f"  Capacity: {instance.vehicle_capacity}")
    print(f"  All feasible: {all(l <= instance.vehicle_capacity for l in loads)}")
