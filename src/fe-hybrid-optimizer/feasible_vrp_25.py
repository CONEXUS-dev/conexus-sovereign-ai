"""
Feasible 25-Customer VRP Instance
Realistic problem: enough capacity, pure distance optimization.
This matches the complexity crossover point from TSP validation.
"""

# 25-customer feasible VRP instance
DEPOT = (50, 50)

CUSTOMERS_25 = {
    1: ((20, 30), 12),
    2: ((80, 90), 15),
    3: ((30, 70), 8),
    4: ((90, 20), 18),
    5: ((40, 40), 10),
    6: ((70, 60), 14),
    7: ((25, 85), 9),
    8: ((85, 15), 13),
    9: ((35, 55), 16),
    10: ((75, 75), 11),
    11: ((15, 45), 7),
    12: ((65, 35), 12),
    13: ((45, 80), 15),
    14: ((95, 50), 8),
    15: ((50, 20), 17),
    16: ((30, 65), 10),
    17: ((70, 25), 14),
    18: ((20, 90), 9),
    19: ((85, 70), 13),
    20: ((40, 10), 11),
    21: ((60, 55), 12),
    22: ((10, 60), 8),
    23: ((90, 40), 15),
    24: ((55, 75), 10),
    25: ((25, 20), 14),
}

# 5 vehicles with 80 capacity each = 400 total
# Total demand = 12+15+8+18+10+14+9+13+16+11+7+12+15+8+17+10+14+9+13+11+12+8+15+10+14 = 300
# FEASIBLE: 400 capacity > 300 demand

VEHICLES_25 = 5
CAPACITY_25 = 80

print("25-Customer Feasible VRP Instance")
print("=" * 60)
print(f"Customers: {len(CUSTOMERS_25)}")
print(f"Vehicles: {VEHICLES_25}")
print(f"Capacity per vehicle: {CAPACITY_25}")
print(f"Total capacity: {VEHICLES_25 * CAPACITY_25}")
print(f"Total demand: {sum(d for _, d in CUSTOMERS_25.values())}")
print(f"Feasible: {VEHICLES_25 * CAPACITY_25 > sum(d for _, d in CUSTOMERS_25.values())}")
print("\nThis is a REALISTIC problem:")
print("- No artificial overload penalty")
print("- Pure distance optimization")
print("- Matches TSP crossover complexity (~25-30 nodes)")
print("- Should show FE advantage if it exists")
