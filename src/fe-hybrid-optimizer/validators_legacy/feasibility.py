"""
Feasibility Validator - Hard constraint checking for VRP solutions
"""

from typing import Tuple, List
from engine.vrp_instance import VRPInstance
from engine.candidate import Candidate


class FeasibilityValidator:
    """
    Hard feasibility validator for VRP solutions.
    
    Checks:
    1. Coverage: Every customer 0..N-1 appears exactly once
    2. Conservation: sum(loads) = total_demand
    3. Capacity: Every route load <= capacity (hard constraint)
    """
    
    def __init__(self, instance: VRPInstance):
        self.instance = instance
    
    def validate(self, candidate: Candidate) -> Tuple[bool, List[str]]:
        """
        Validate candidate against hard constraints.
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        # Check 1: Coverage
        coverage_valid, coverage_msg = self._check_coverage(candidate)
        if not coverage_valid:
            errors.append(f"COVERAGE: {coverage_msg}")
        
        # Check 2: Conservation
        conservation_valid, conservation_msg = self._check_conservation(candidate)
        if not conservation_valid:
            errors.append(f"CONSERVATION: {conservation_msg}")
        
        # Check 3: Capacity (hard constraint for investor-grade validation)
        capacity_valid, capacity_msg = self._check_capacity(candidate)
        if not capacity_valid:
            errors.append(f"CAPACITY: {capacity_msg}")
        
        is_valid = len(errors) == 0
        
        return is_valid, errors
    
    def _check_coverage(self, candidate: Candidate) -> Tuple[bool, str]:
        """Check coverage invariant."""
        n = self.instance.n_customers
        
        if len(candidate.assignment) != n:
            return False, f"Assignment length {len(candidate.assignment)} != {n}"
        
        # Check all customers present in routes
        all_customers = []
        for route in candidate.routes:
            all_customers.extend(route)
        
        expected = set(range(n))
        actual = set(all_customers)
        
        missing = expected - actual
        if missing:
            return False, f"Missing customers: {sorted(list(missing))[:10]}"
        
        # Check no duplicates
        if len(all_customers) != len(actual):
            from collections import Counter
            counts = Counter(all_customers)
            duplicates = {c: count for c, count in counts.items() if count > 1}
            return False, f"Duplicate customers: {duplicates}"
        
        return True, ""
    
    def _check_conservation(self, candidate: Candidate) -> Tuple[bool, str]:
        """Check conservation invariant."""
        total_load = sum(candidate.loads)
        expected = self.instance.total_demand
        
        if abs(total_load - expected) > 0.01:
            return False, f"Load {total_load} != demand {expected}"
        
        return True, ""
    
    def _check_capacity(self, candidate: Candidate) -> Tuple[bool, str]:
        """Check capacity constraints (hard for investor-grade)."""
        capacity = self.instance.vehicle_capacity
        violations = []
        
        for v, load in enumerate(candidate.loads):
            if load > capacity:
                violations.append(f"Vehicle {v}: {load} > {capacity}")
        
        if violations:
            return False, f"{len(violations)} violations: {violations[:3]}"
        
        return True, ""
    
    def print_summary(self, candidate: Candidate, name: str = "Solution"):
        """Print detailed solution summary."""
        print(f"\n{'='*60}")
        print(f"{name} Summary")
        print(f"{'='*60}")
        
        # Basic stats
        all_customers = []
        for route in candidate.routes:
            all_customers.extend(route)
        
        print(f"Customers served: {len(set(all_customers))}/{self.instance.n_customers}")
        print(f"Active routes: {sum(1 for r in candidate.routes if r)}")
        print(f"Total load: {sum(candidate.loads)}")
        print(f"Expected demand: {self.instance.total_demand}")
        print(f"Distance: {candidate.distance:.2f}")
        print(f"Objective: {candidate.objective:.2f}")
        
        # Feasibility
        is_valid, errors = self.validate(candidate)
        print(f"\nFeasibility: {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        if not is_valid:
            print("\nErrors:")
            for error in errors:
                print(f"  • {error}")
        
        # Route details
        print(f"\nRoute Details:")
        for v, (route, load) in enumerate(zip(candidate.routes, candidate.loads)):
            if route:
                status = "✓" if load <= self.instance.vehicle_capacity else "✗"
                print(f"  {status} Vehicle {v}: {len(route)} customers, load {load}/{self.instance.vehicle_capacity}")


if __name__ == "__main__":
    # Test validator
    from engine.vrp_instance import VRPInstance
    from engine.candidate import Candidate
    
    instance = VRPInstance.generate_random(
        name="test_validation",
        n_customers=10,
        n_vehicles=3,
        vehicle_capacity=50,
        seed=42
    )
    
    validator = FeasibilityValidator(instance)
    
    # Test valid candidate
    assignment = [i % 3 for i in range(10)]
    routes = [[], [], []]
    for i, v in enumerate(assignment):
        routes[v].append(i)
    
    loads = [0, 0, 0]
    for i, v in enumerate(assignment):
        loads[v] += instance.customer_demands[i]
    
    candidate = Candidate(
        id="test",
        assignment=assignment,
        routes=routes,
        distance=100.0,
        loads=loads,
        objective=100.0
    )
    
    validator.print_summary(candidate, "Test Candidate")
