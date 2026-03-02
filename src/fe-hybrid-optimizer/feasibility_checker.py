"""
Hard Feasibility Checks for VRP Solutions
Enforces must-pass constraints before any solution can be considered valid.
"""

from typing import List, Dict, Any, Tuple
from fe_hybrid_vrp import CUSTOMERS, VEHICLES, CAPACITY


def check_feasibility(routes: List[List[int]], loads: List[int], 
                      distance: float, method_name: str) -> Tuple[bool, List[str]]:
    """
    Hard feasibility checks that must pass for a valid VRP solution.
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    # Check 1: Every customer appears exactly once
    all_customers = []
    for route in routes:
        all_customers.extend(route)
    
    num_customers = len(CUSTOMERS)
    expected_customers = set(range(1, num_customers + 1))
    actual_customers = set(all_customers)
    
    # Missing customers
    missing = expected_customers - actual_customers
    if missing:
        errors.append(f"MISSING CUSTOMERS: {sorted(missing)[:10]}... ({len(missing)} total)")
    
    # Duplicate customers
    if len(all_customers) != len(actual_customers):
        from collections import Counter
        counts = Counter(all_customers)
        duplicates = {c: count for c, count in counts.items() if count > 1}
        errors.append(f"DUPLICATE CUSTOMERS: {duplicates}")
    
    # Wrong count
    if len(actual_customers) != num_customers:
        errors.append(f"CUSTOMER COUNT MISMATCH: expected {num_customers}, got {len(actual_customers)}")
    
    # Check 2: Demand conservation
    total_demand = sum(d for _, d in CUSTOMERS.values())
    total_load = sum(loads)
    
    if abs(total_load - total_demand) > 0.01:  # Allow tiny floating point error
        errors.append(f"DEMAND MISMATCH: expected {total_demand}, got {total_load}")
    
    # Check 3: Capacity constraints
    for v, load in enumerate(loads):
        if load > CAPACITY:
            errors.append(f"CAPACITY VIOLATION: Vehicle {v} has load {load} > capacity {CAPACITY}")
    
    # Check 4: Distance integrity
    if distance < 0:
        errors.append(f"INVALID DISTANCE: {distance} (negative)")
    
    if distance == 0 and len(all_customers) > 0:
        errors.append(f"INVALID DISTANCE: 0 (but serving {len(all_customers)} customers)")
    
    # Check 5: Route structure
    for v, route in enumerate(routes):
        # Check for invalid customer IDs
        for c in route:
            if c < 1 or c > num_customers:
                errors.append(f"INVALID CUSTOMER ID: {c} in vehicle {v} route")
    
    is_valid = len(errors) == 0
    
    if not is_valid:
        print("\n" + "=" * 80)
        print(f"❌ FEASIBILITY CHECK FAILED: {method_name}")
        print("=" * 80)
        for error in errors:
            print(f"  • {error}")
        print("\n" + "=" * 80)
    
    return is_valid, errors


def print_solution_summary(routes: List[List[int]], loads: List[int], 
                          distance: float, method_name: str):
    """Print detailed solution summary for debugging."""
    print(f"\n[SOLUTION SUMMARY: {method_name}]")
    print("-" * 60)
    
    all_customers = []
    for route in routes:
        all_customers.extend(route)
    
    print(f"Total customers in instance: {len(CUSTOMERS)}")
    print(f"Customers served: {len(set(all_customers))}")
    print(f"Active routes: {sum(1 for r in routes if r)}")
    print(f"Total load: {sum(loads)}")
    print(f"Expected demand: {sum(d for _, d in CUSTOMERS.values())}")
    print(f"Distance: {distance:.2f}")
    
    print(f"\nRoute details:")
    for v, (route, load) in enumerate(zip(routes, loads)):
        if route:
            print(f"  Vehicle {v}: {len(route)} customers, load {load}/{CAPACITY}")


if __name__ == "__main__":
    print("Feasibility Checker Module")
    print("Use: check_feasibility(routes, loads, distance, method_name)")
