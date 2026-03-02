"""Debug: inspect raw Gemini response for n=100."""

from ai_solver_experiment.vrp_instance import generate_instance
from ai_solver_experiment.ai_proposal_engine import AIProposalEngine, extract_json

inst = generate_instance(n_customers=100, seed=1)
engine = AIProposalEngine(provider="gemini", temperature=0.7, pacing_delay=0)
r = engine.propose(inst, iteration=1, calibrated=False)

raw = r["raw_response"]
print(f"RAW LENGTH: {len(raw)}")
print(f"PARSE SUCCESS: {r['parse_success']}")
print()
print("=== FULL RAW RESPONSE ===")
print(raw)
print()
print("=== EXTRACT_JSON RESULT ===")
ej = extract_json(raw)
print(f"Found: {ej is not None}")
if ej:
    print(f"Length: {len(ej)}")
    print(f"First 200: {ej[:200]}")
    print(f"Last 200: {ej[-200:]}")
else:
    # Try to find why extraction failed
    brace_count = 0
    max_depth = 0
    for i, ch in enumerate(raw):
        if ch == "{":
            brace_count += 1
            max_depth = max(max_depth, brace_count)
        elif ch == "}":
            brace_count -= 1
    print(f"Unclosed braces: {brace_count}")
    print(f"Max brace depth: {max_depth}")
    print(f"Starts with ```: {raw.strip().startswith('```')}")
    print(f"Ends with ```: {raw.strip().endswith('```')}")
