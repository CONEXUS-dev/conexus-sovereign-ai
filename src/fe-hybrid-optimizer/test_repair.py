"""
Test repair function to ensure it works correctly.
"""

from fe_hybrid_vrp_fixed import repair_solution, N_CUSTOMERS, VEHICLES, CUSTOMER_DEMANDS
import random

print("Testing repair function...")
print(f"N_CUSTOMERS: {N_CUSTOMERS}")
print(f"VEHICLES: {VEHICLES}")

rng = random.Random(42)

# Test 1: Valid assignment (no repair needed)
print("\n[Test 1] Valid assignment")
assign = list(range(N_CUSTOMERS))
for i in range(N_CUSTOMERS):
    assign[i] = i % VEHICLES
print(f"Input: {len(assign)} customers, {len(set(assign))} unique vehicles")

repaired = repair_solution(assign, rng)
print(f"Output: {len(repaired)} customers")

# Check coverage
covered = set(range(N_CUSTOMERS))
assigned_indices = set(range(len(repaired)))
if covered == assigned_indices:
    print("✓ All customers covered")
else:
    missing = covered - assigned_indices
    print(f"✗ Missing: {missing}")

# Test 2: Missing customer
print("\n[Test 2] Missing customer 50")
assign = list(range(N_CUSTOMERS))
for i in range(N_CUSTOMERS):
    assign[i] = i % VEHICLES
assign[50] = assign[49]  # Duplicate customer 49's assignment

print(f"Before repair: customer 50 has same vehicle as 49")

try:
    repaired = repair_solution(assign, rng)
    print(f"After repair: {len(repaired)} customers")
    
    # Verify all customers present
    all_present = True
    for i in range(N_CUSTOMERS):
        if i >= len(repaired):
            print(f"✗ Customer {i} missing from repaired assignment")
            all_present = False
    
    if all_present:
        print("✓ All customers present after repair")
except Exception as e:
    print(f"✗ Repair failed: {e}")

# Test 3: Check actual assignment values
print("\n[Test 3] Check assignment values")
assign = [0] * N_CUSTOMERS  # All to vehicle 0
repaired = repair_solution(assign, rng)

print(f"Repaired assignment uses vehicles: {sorted(set(repaired))}")
print(f"All values in range 0..{VEHICLES-1}: {all(0 <= v < VEHICLES for v in repaired)}")

# Test 4: Check demands
print("\n[Test 4] Demand conservation")
total_demand_expected = sum(CUSTOMER_DEMANDS)
vehicle_loads = [0] * VEHICLES
for i, v in enumerate(repaired):
    vehicle_loads[v] += CUSTOMER_DEMANDS[i]

total_demand_actual = sum(vehicle_loads)
print(f"Expected demand: {total_demand_expected}")
print(f"Actual demand: {total_demand_actual}")
print(f"Match: {abs(total_demand_expected - total_demand_actual) < 0.01}")
