"""
100-Customer VRP Instance (4x Complexity)
Realistic large-scale problem to test FE scaling advantage.
"""

import random
import math

# Set seed for reproducibility
random.seed(42)

DEPOT = (50, 50)

# Generate 100 customers with random locations and demands
CUSTOMERS_100 = {}
for i in range(1, 101):
    # Random location in 100x100 grid
    x = random.uniform(0, 100)
    y = random.uniform(0, 100)
    
    # Random demand between 5 and 25
    demand = random.randint(5, 25)
    
    CUSTOMERS_100[i] = ((x, y), demand)

# Calculate total demand
total_demand = sum(d for _, d in CUSTOMERS_100.values())

# 20 vehicles with 100 capacity each = 2000 total capacity
# Make it feasible with some slack (~400 capacity buffer)
VEHICLES_100 = 20
CAPACITY_100 = 100

total_capacity = VEHICLES_100 * CAPACITY_100

print("100-Customer VRP Instance (4x Complexity)")
print("=" * 60)
print(f"Customers: {len(CUSTOMERS_100)}")
print(f"Vehicles: {VEHICLES_100}")
print(f"Capacity per vehicle: {CAPACITY_100}")
print(f"Total capacity: {total_capacity}")
print(f"Total demand: {total_demand}")
print(f"Feasible: {total_capacity >= total_demand}")
print(f"Capacity slack: {total_capacity - total_demand}")

# Calculate problem complexity metrics
def euclid(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# Average distance from depot
avg_dist_from_depot = sum(euclid(DEPOT, loc) for loc, _ in CUSTOMERS_100.values()) / len(CUSTOMERS_100)

# Average distance between customers
distances = []
customer_locs = [loc for loc, _ in CUSTOMERS_100.values()]
for i in range(len(customer_locs)):
    for j in range(i + 1, len(customer_locs)):
        distances.append(euclid(customer_locs[i], customer_locs[j]))
avg_customer_dist = sum(distances) / len(distances)

print(f"\nComplexity Metrics:")
print(f"  Average distance from depot: {avg_dist_from_depot:.2f}")
print(f"  Average inter-customer distance: {avg_customer_dist:.2f}")
print(f"  Search space size: ~{VEHICLES_100}^{len(CUSTOMERS_100)} (astronomical)")

print(f"\nThis is a COMPLEX problem:")
print(f"  - 4x larger than 25-customer instance")
print(f"  - Should show FE advantage if it exists")
print(f"  - Matches TSP crossover complexity threshold")
print(f"  - Clarke-Wright may struggle with local optima")
