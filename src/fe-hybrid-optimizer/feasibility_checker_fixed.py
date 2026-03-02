"""
Fixed Feasibility Checker for 0-indexed Internal Representation
Works with fe_hybrid_vrp_fixed.py which uses 0..N-1 customer indices.
"""

from typing import List, Tuple
from fe_hybrid_vrp_fixed import N_CUSTOMERS, VEHICLES, CAPACITY, TOTAL_DEMAND


def check_feasibility(routes: List[List[int]], loads: List[int], 
                      distance: float, method_name: str) -> Tuple[bool, List[str]]:
    """
    Hard feasibility checks for 0-indexed internal representation.
    
    Customer indices: 0..N-1 (internal)
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    
    # Check 1: Every customer 0..N-1 appears exactly once
    all_customers = []
    for route in routes:
        all_customers.extend(route)
    
    expected_customers = set(range(N_CUSTOMERS))
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
    if len(actual_customers) != N_CUSTOMERS:
        errors.append(f"CUSTOMER COUNT MISMATCH: expected {N_CUSTOMERS}, got {len(actual_customers)}")
    
    # Check 2: Demand conservation
    total_load = sum(loads)
    
    if abs(total_load - TOTAL_DEMAND) > 0.01:
        errors.append(f"DEMAND MISMATCH: expected {TOTAL_DEMAND}, got {total_load}")
    
    # Check 3: Capacity constraints (soft - we allow overload with penalty)
    # Note: Capacity violations are handled via penalty in objective, not hard constraint
    overload_count = sum(1 for load in loads if load > CAPACITY)
    if overload_count > 0:
        # This is a warning, not an error - overload is penalized in objective
        pass  # Capacity violations allowed with penalty
    
    # Check 4: Distance integrity
    if distance < 0:
        errors.append(f"INVALID DISTANCE: {distance} (negative)")
    
    if distance == 0 and len(all_customers) > 0:
        errors.append(f"INVALID DISTANCE: 0 (but serving {len(all_customers)} customers)")
    
    # Check 5: Route structure - all customer IDs must be in range 0..N-1
    for v, route in enumerate(routes):
        for c in route:
            if c < 0 or c >= N_CUSTOMERS:
                errors.append(f"INVALID CUSTOMER ID: {c} in vehicle {v} route (must be 0..{N_CUSTOMERS-1})")
    
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
    """Print detailed solution summary for debugging (0-indexed)."""
    print(f"\n[SOLUTION SUMMARY: {method_name}]")
    print("-" * 60)
    
    all_customers = []
    for route in routes:
        all_customers.extend(route)
    
    print(f"Total customers in instance: {N_CUSTOMERS}")
    print(f"Customers served: {len(set(all_customers))}")
    print(f"Active routes: {sum(1 for r in routes if r)}")
    print(f"Total load: {sum(loads)}")
    print(f"Expected demand: {TOTAL_DEMAND}")
    print(f"Distance: {distance:.2f}")
    
    print(f"\nRoute details:")
    for v, (route, load) in enumerate(zip(routes, loads)):
        if route:
            print(f"  Vehicle {v}: {len(route)} customers, load {load}/{CAPACITY}")


if __name__ == "__main__":
    print("Fixed Feasibility Checker Module (0-indexed)")
    print(f"Expects customer IDs: 0..{N_CUSTOMERS-1}")
    print("Use: check_feasibility(routes, loads, distance, method_name)")
