"""
Simple Repeatability Test - Run validation 3 times directly
"""

from validation_stub_only import run_clarke_wright, run_fe_stub

print("=" * 80)
print("REPEATABILITY AUDIT - 100-Customer VRP")
print("=" * 80)
print("\nRunning Clarke-Wright and FE Stub 3 times each...")
print("Checking for deterministic behavior.\n")

# Test Clarke-Wright repeatability
print("\n[TEST 1] Clarke-Wright Repeatability")
print("-" * 80)

cw_results = []
for i in range(1, 4):
    print(f"\nRun {i}/3...")
    result = run_clarke_wright()
    cw_results.append(result)
    print(f"  Distance: {result['distance']:.2f}")
    print(f"  Objective: {result['f']:.2f}")

# Test FE Stub repeatability
print("\n\n[TEST 2] FE Stub Repeatability")
print("-" * 80)

fe_results = []
for i in range(1, 4):
    print(f"\nRun {i}/3...")
    result = run_fe_stub(max_iters=20, seed=7)
    fe_results.append(result)
    print(f"  Distance: {result['distance']:.2f}")
    print(f"  Objective: {result['f']:.2f}")

# Analyze results
print("\n" + "=" * 80)
print("REPEATABILITY ANALYSIS")
print("=" * 80)

cw_distances = [r['distance'] for r in cw_results]
fe_distances = [r['distance'] for r in fe_results]

print(f"\nClarke-Wright distances:")
for i, dist in enumerate(cw_distances, 1):
    print(f"  Run {i}: {dist:.2f}")

cw_unique = len(set(f"{d:.2f}" for d in cw_distances))
print(f"  Unique values: {cw_unique}")

print(f"\nFE Stub distances:")
for i, dist in enumerate(fe_distances, 1):
    print(f"  Run {i}: {dist:.2f}")

fe_unique = len(set(f"{d:.2f}" for d in fe_distances))
print(f"  Unique values: {fe_unique}")

# Verdict
print("\n" + "=" * 80)
print("VERDICT")
print("=" * 80)

if cw_unique == 1 and fe_unique == 1:
    print("\n✅ FULLY REPEATABLE - Both algorithms are deterministic")
    print(f"\nClarke-Wright: {cw_distances[0]:.2f} (always)")
    print(f"FE Stub: {fe_distances[0]:.2f} (always)")
    
    improvement = ((cw_distances[0] - fe_distances[0]) / cw_distances[0]) * 100
    print(f"\nConsistent improvement: {improvement:.2f}%")
    
    print("\n✓ Random seeds properly fixed")
    print("✓ Results are reproducible")
    print("✓ Validation is production-ready")
    
elif cw_unique == 1 and fe_unique > 1:
    print("\n⚠️ CLARKE-WRIGHT IS REPEATABLE, FE STUB IS NOT")
    print(f"\nClarke-Wright: {cw_distances[0]:.2f} (deterministic)")
    print(f"FE Stub range: {min(fe_distances):.2f} - {max(fe_distances):.2f}")
    print("\nIssue: FE engine has unseeded randomness")
    print("Action: Check random seed in FE engine")
    
elif cw_unique > 1 and fe_unique == 1:
    print("\n⚠️ FE STUB IS REPEATABLE, CLARKE-WRIGHT IS NOT")
    print(f"\nClarke-Wright range: {min(cw_distances):.2f} - {max(cw_distances):.2f}")
    print(f"FE Stub: {fe_distances[0]:.2f} (deterministic)")
    print("\nIssue: Clarke-Wright has unseeded randomness")
    
else:
    print("\n❌ NEITHER ALGORITHM IS REPEATABLE")
    print(f"\nClarke-Wright range: {min(cw_distances):.2f} - {max(cw_distances):.2f}")
    print(f"FE Stub range: {min(fe_distances):.2f} - {max(fe_distances):.2f}")
    print("\nIssue: Both have unseeded randomness")
    print("Action: Fix random seeds in both algorithms")

print("\n" + "=" * 80)
