"""
Lightweight unit tests for FE-VRP Optimizer.
Run: python -m fe_vrp.tests
"""

import random
import json
import sys
import time

from .types import Instance, Candidate, PilotDecision, REQUIRED_DECISION_KEYS
from .instance import generate_instance, auto_capacity
from .evaluate import evaluate, full_repair, compute_loads
from .operators import op_swap, op_relocate, op_cross_exchange
from .paradox import ParadoxBuffer, passes_all_gates, is_not_collapse_trap
from .pilot import validate_calibration, validate_decision_json, EXACT_CALIBRATION, PilotAdapter
from .pattern_mining import mine_patterns

PASS = 0
FAIL = 0


def _check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        FAIL += 1
        print(f"  ✗ {name} — {detail}")


def test_calibration_receipt():
    """Calibration receipt must be exact JSON."""
    print("\n[Test: Calibration Receipt]")

    exact = json.dumps(EXACT_CALIBRATION)
    _check("exact receipt accepted", validate_calibration(exact))

    # wrong key
    bad1 = json.dumps({"CALIBRATED": True, "protocol": "WRONG", "pilot_mode": "PARADOX_HOLD"})
    _check("wrong protocol rejected", not validate_calibration(bad1))

    # extra key
    bad2 = json.dumps({**EXACT_CALIBRATION, "extra": 1})
    _check("extra key rejected", not validate_calibration(bad2))

    # missing key
    bad3 = json.dumps({"CALIBRATED": True, "protocol": "CONEXUS-STEEL-04"})
    _check("missing key rejected", not validate_calibration(bad3))

    # not calibrated
    bad4 = json.dumps({"CALIBRATED": False, "protocol": "CONEXUS-STEEL-04", "pilot_mode": "PARADOX_HOLD"})
    _check("CALIBRATED=false rejected", not validate_calibration(bad4))

    # wrapped in markdown
    wrapped = f"```json\n{exact}\n```"
    _check("markdown-wrapped accepted", validate_calibration(wrapped))


def test_paradox_gate_collapse_trap():
    """Collapse trap must be rejected."""
    print("\n[Test: Paradox Gate — Collapse Trap]")

    inst = generate_instance(20, 4, 100, seed=1)

    # Good candidate: balanced routes
    good = Candidate(cid="good", assign=[i % 4 for i in range(20)])
    evaluate(inst, good)
    _check("balanced routes pass collapse check",
           is_not_collapse_trap(good),
           f"max={good.metrics.get('max_customers_per_vehicle')}, "
           f"min={good.metrics.get('min_customers_per_vehicle')}")

    # Bad candidate: all on one vehicle (collapse)
    bad = Candidate(cid="bad", assign=[0] * 20)
    evaluate(inst, bad)
    _check("all-on-one-vehicle fails collapse check",
           not is_not_collapse_trap(bad),
           f"max={bad.metrics.get('max_customers_per_vehicle')}")


def test_paradox_buffer_size():
    """Buffer must not exceed k."""
    print("\n[Test: Paradox Buffer Size]")

    inst = generate_instance(30, 5, 100, seed=2)
    buf = ParadoxBuffer(k=5)
    rng = random.Random(99)

    for i in range(50):
        assign = [rng.randint(0, 4) for _ in range(30)]
        assign = full_repair(inst, assign, rng)
        cand = Candidate(cid=f"test_{i}", assign=assign)
        evaluate(inst, cand)
        buf.try_add(inst, cand, median_fitness=cand.fitness * 0.9)

    _check(f"buffer size <= 5 (actual: {buf.size})", buf.size <= 5)


def test_operators_valid():
    """Operators must produce valid assignments."""
    print("\n[Test: Operators]")

    inst = generate_instance(25, 5, 100, seed=3)
    rng = random.Random(42)
    assign = [i % 5 for i in range(25)]

    for name, op_fn in [("swap", op_swap), ("relocate", op_relocate),
                         ("cross_exchange", op_cross_exchange)]:
        new_assign = op_fn(inst, assign, rng)
        _check(f"{name}: length preserved", len(new_assign) == 25)
        _check(f"{name}: valid vehicle IDs",
               all(0 <= v < 5 for v in new_assign))


def test_repair_feasibility():
    """Full repair must produce feasible solutions."""
    print("\n[Test: Repair → Feasibility]")

    inst = generate_instance(30, 5, 100, seed=4)
    rng = random.Random(42)

    for trial in range(10):
        assign = [rng.randint(0, 4) for _ in range(30)]
        repaired = full_repair(inst, assign, rng)
        cand = Candidate(cid=f"repair_{trial}", assign=repaired)
        evaluate(inst, cand)
        if not cand.feasible:
            _check(f"trial {trial}: feasible after repair", False,
                   f"overload={cand.overload}, loads={cand.loads}")
            return

    _check("all 10 trials feasible after repair", True)


def test_decision_validation():
    """Decision JSON validation."""
    print("\n[Test: Decision JSON Validation]")

    ids = ["c0", "c1", "c2", "c3", "c4"]

    good = json.dumps({
        "keep_ids": ["c0", "c1"],
        "paradox_add_ids": ["c2"],
        "operator_mix_next": {"swap": 0.5, "relocate": 0.5},
        "pattern_ops": [],
        "proto": {"moments": []},
        "rationale": {"survival_logic": "test", "paradox_logic": "test"},
    })
    _check("valid decision accepted", validate_decision_json(good, ids) is not None)

    # missing key
    bad = json.dumps({
        "keep_ids": ["c0"],
        "paradox_add_ids": [],
    })
    _check("incomplete decision rejected", validate_decision_json(bad, ids) is None)

    # unknown candidate id
    bad2 = json.dumps({
        "keep_ids": ["UNKNOWN"],
        "paradox_add_ids": [],
        "operator_mix_next": {"swap": 1.0},
        "pattern_ops": [],
        "proto": {"moments": []},
        "rationale": {"survival_logic": "", "paradox_logic": ""},
    })
    _check("unknown ID rejected", validate_decision_json(bad2, ids) is None)


def test_llm_gate_rejects_before_calibration():
    """LLM pilot must reject decision JSON before calibration."""
    print("\n[Test: LLM Gate — No Decision Before Calibration]")

    pilot = PilotAdapter(mode="llm", seed=42)
    _check("LLM pilot starts uncalibrated", not pilot.calibrated)

    # Simulate a decision request without calibration
    packet = {"iteration": 1, "best_distance": 100.0}
    ids = ["c0", "c1", "c2", "c3"]
    decision = pilot.decide(packet, ids)

    # Should fall back to stub (deterministic) since not calibrated
    _check("uncalibrated LLM returns stub decision",
           decision.rationale.get("survival_logic", "").startswith("stub"),
           f"got rationale: {decision.rationale}")
    _check("pilot stats show 0 LLM decisions", pilot.stats()["llm_decisions"] == 0)


def test_repair_stress_n200():
    """Repair must produce feasible solutions for 50 random instances at n=200."""
    print("\n[Test: Repair Stress — n=200 x 50 trials]")

    failures = 0
    for seed in range(50):
        n, v = 200, 20
        cap = auto_capacity(n, v, seed=seed)
        inst = generate_instance(n, v, cap, seed=seed)
        rng = random.Random(seed * 7 + 13)
        assign = [rng.randint(0, v - 1) for _ in range(n)]
        repaired = full_repair(inst, assign, rng)
        cand = Candidate(cid=f"stress_{seed}", assign=repaired)
        evaluate(inst, cand)
        if not cand.feasible:
            failures += 1
            if failures <= 3:
                print(f"    FAIL seed={seed}: overload={cand.overload}, loads={cand.loads}")

    _check(f"all 50 n=200 trials feasible (failures={failures})", failures == 0)


def test_time_limit():
    """Engine must respect time_limit_s."""
    print("\n[Test: Time Limit]")

    from .engine import FEEngine

    inst = generate_instance(50, 5, auto_capacity(50, 5, seed=42), seed=42)
    pilot = PilotAdapter(mode="stub", seed=42)
    engine = FEEngine(inst, pilot, seed=42, max_gens=9999, pop_size=10,
                      time_limit_s=2.0)

    t0 = time.time()
    results = engine.run()
    elapsed = time.time() - t0

    _check(f"finished within ~2s (actual: {elapsed:.1f}s)", elapsed < 5.0)
    _check("solution is feasible", results["best_feasible"])


def test_smoke_n50():
    """Smoke test: n=50 stub mode in < 30s."""
    print("\n[Test: Smoke — n=50 stub < 30s]")

    from .engine import FEEngine

    inst = generate_instance(50, 5, auto_capacity(50, 5, seed=42), seed=42)
    pilot = PilotAdapter(mode="stub", seed=42)
    engine = FEEngine(inst, pilot, seed=42, max_gens=50, pop_size=10)

    t0 = time.time()
    results = engine.run()
    elapsed = time.time() - t0

    _check(f"completed in {elapsed:.1f}s (< 30s)", elapsed < 30)
    _check("solution is feasible", results["best_feasible"])
    _check(f"distance > 0 ({results['best_distance']:.1f})", results["best_distance"] > 0)


def run_all():
    global PASS, FAIL
    PASS, FAIL = 0, 0

    print("=" * 60)
    print("FE-VRP Optimizer — Unit Tests")
    print("=" * 60)

    test_calibration_receipt()
    test_llm_gate_rejects_before_calibration()
    test_paradox_gate_collapse_trap()
    test_paradox_buffer_size()
    test_operators_valid()
    test_repair_feasibility()
    test_repair_stress_n200()
    test_decision_validation()
    test_time_limit()
    test_smoke_n50()

    print(f"\n{'='*60}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    print(f"{'='*60}")

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all()
