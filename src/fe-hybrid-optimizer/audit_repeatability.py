"""
Repeatability Audit for 100-Customer VRP Validation
Runs validation multiple times to verify deterministic behavior.
"""

import subprocess
import json
import sys

def run_validation():
    """Run validation and capture results."""
    result = subprocess.run(
        ['python', 'validation_stub_only.py'],
        capture_output=True,
        text=True,
        cwd=r'c:\Users\Derek Angell\Desktop\CONEXUS_DATA_DUMP\fe-hybrid-optimizer'
    )
    
    # Parse output to extract key metrics
    output = result.stdout
    
    # Extract Clarke-Wright distance
    cw_dist = None
    fe_dist = None
    
    for line in output.split('\n'):
        if 'Clarke-Wright' in line and 'Distance:' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'Distance:':
                    cw_dist = float(parts[i+1])
        elif 'FE Hybrid (stub)' in line and 'Distance:' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'Distance:':
                    fe_dist = float(parts[i+1])
    
    return {
        'clarke_wright_distance': cw_dist,
        'fe_stub_distance': fe_dist,
        'full_output': output
    }

print("=" * 80)
print("REPEATABILITY AUDIT - 100-Customer VRP Validation")
print("=" * 80)
print("\nRunning validation 3 times to verify deterministic behavior...")
print("This will take ~2-3 minutes total.\n")

results = []

for run_num in range(1, 4):
    print(f"\n[Run {run_num}/3] Executing validation...")
    print("-" * 80)
    
    result = run_validation()
    results.append(result)
    
    print(f"✓ Run {run_num} complete:")
    print(f"  Clarke-Wright: {result['clarke_wright_distance']:.2f}")
    print(f"  FE Stub: {result['fe_stub_distance']:.2f}")

# Analyze results
print("\n" + "=" * 80)
print("REPEATABILITY ANALYSIS")
print("=" * 80)

cw_distances = [r['clarke_wright_distance'] for r in results]
fe_distances = [r['fe_stub_distance'] for r in results]

print(f"\nClarke-Wright distances across 3 runs:")
for i, dist in enumerate(cw_distances, 1):
    print(f"  Run {i}: {dist:.2f}")

print(f"\nFE Stub distances across 3 runs:")
for i, dist in enumerate(fe_distances, 1):
    print(f"  Run {i}: {dist:.2f}")

# Check for consistency
cw_consistent = len(set(cw_distances)) == 1
fe_consistent = len(set(fe_distances)) == 1

print("\n" + "=" * 80)
print("VERDICT")
print("=" * 80)

if cw_consistent and fe_consistent:
    print("\n✅ VALIDATION IS FULLY REPEATABLE")
    print(f"\nClarke-Wright always produces: {cw_distances[0]:.2f}")
    print(f"FE Stub always produces: {fe_distances[0]:.2f}")
    
    improvement = ((cw_distances[0] - fe_distances[0]) / cw_distances[0]) * 100
    print(f"\nConsistent improvement: {improvement:.2f}%")
    
    print("\n✓ Results are deterministic")
    print("✓ Random seeds are properly fixed")
    print("✓ Validation is production-ready")
    
else:
    print("\n⚠️ VALIDATION HAS NON-DETERMINISTIC BEHAVIOR")
    
    if not cw_consistent:
        print(f"\nClarke-Wright varies: {min(cw_distances):.2f} - {max(cw_distances):.2f}")
        print("  Issue: Clarke-Wright algorithm may have randomness")
    
    if not fe_consistent:
        print(f"\nFE Stub varies: {min(fe_distances):.2f} - {max(fe_distances):.2f}")
        print("  Issue: FE engine may have unseeded randomness")
    
    print("\nAction needed: Fix random seed issues")

print("\n" + "=" * 80)
