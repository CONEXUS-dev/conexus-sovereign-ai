"""
Debug script to check feasibility of current validation results.
"""

import json
from feasibility_checker import check_feasibility, print_solution_summary

# Load validation results
with open('outputs/vrp_validation_result.json', 'r') as f:
    results = json.load(f)

print("=" * 80)
print("FEASIBILITY AUDIT OF VALIDATION RESULTS")
print("=" * 80)

# Check Clarke-Wright
cw = results['results']['clarke_wright']
print("\n\n[1] CLARKE-WRIGHT BASELINE")
print_solution_summary(cw['routes'], cw['loads'], cw['distance'], "Clarke-Wright")
is_valid, errors = check_feasibility(cw['routes'], cw['loads'], cw['distance'], "Clarke-Wright")
if is_valid:
    print("\n✅ Clarke-Wright solution is VALID")
else:
    print(f"\n❌ Clarke-Wright solution is INVALID ({len(errors)} errors)")

# Check FE Stub
fe = results['results']['fe_stub']
print("\n\n[2] FE STUB")
print_solution_summary(fe['routes'], fe['loads'], fe['distance'], "FE Stub")
is_valid, errors = check_feasibility(fe['routes'], fe['loads'], fe['distance'], "FE Stub")
if is_valid:
    print("\n✅ FE Stub solution is VALID")
else:
    print(f"\n❌ FE Stub solution is INVALID ({len(errors)} errors)")

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)

if not is_valid:
    print("\n⚠️  VALIDATION RESULTS ARE INVALID")
    print("\nChip's diagnosis is correct:")
    print("  • FE is not serving all customers")
    print("  • The 67.80% improvement claim is FALSE")
    print("  • Must fix FE engine before re-running validation")
    print("\nNext steps:")
    print("  1. Fix FE to serve all 100 customers")
    print("  2. Add feasibility checks to validation pipeline")
    print("  3. Re-run validation with correct results")
    print("  4. Document honest results (even if FE loses)")
