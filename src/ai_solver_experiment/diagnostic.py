"""Diagnostic test: verify parse + completeness for n=20, 100, 200."""

from ai_solver_experiment.vrp_instance import generate_instance
from ai_solver_experiment.ai_proposal_engine import AIProposalEngine

for n in [20, 100, 200]:
    inst = generate_instance(n_customers=n, seed=1)
    engine = AIProposalEngine(provider="gemini", temperature=0.7, pacing_delay=4.0)
    print(f"Testing n={n}, model={engine.model}")

    r1 = engine.propose(inst, iteration=1, calibrated=False)
    cust1 = sum(len(route) for route in r1["routes"]) if r1["routes"] else 0

    r2 = engine.propose(inst, iteration=1, calibrated=True)
    cust2 = sum(len(route) for route in r2["routes"]) if r2["routes"] else 0

    # Check unique customers
    u1 = len(set(c for route in r1["routes"] for c in route)) if r1["routes"] else 0
    u2 = len(set(c for route in r2["routes"] for c in route)) if r2["routes"] else 0

    p1 = str(r1["parse_success"])
    p2 = str(r2["parse_success"])
    print(f"  n={n:3} | UNCAL: parse={p1:5} served={cust1:3}/{n:3} unique={u1:3} | CAL: parse={p2:5} served={cust2:3}/{n:3} unique={u2:3}")
    print()
