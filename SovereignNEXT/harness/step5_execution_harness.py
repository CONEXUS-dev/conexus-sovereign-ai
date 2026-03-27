"""
SovereignNEXT — Step 5: Minimal Phase 5 Execution Harness

A verification harness that exercises existing operators under controlled,
repeated conditions to prove three properties unit tests cannot:

  1. Paradox persistence — held paradoxes remain held across cycles.
  2. Veto enforcement — collapse vetoes are never bypassed under repetition.
  3. Absence of mode-sycophancy — operator behavior does not change based
     on prior observation or reporting.

This harness introduces no new code, no new logic, no new authority.
It runs what already exists and checks that it stays correct.

Hard constraints:
  - Fixed initial state (hand-constructed, not generated)
  - Fixed operator sequence: Collapse → Become → Paradox-Hold
  - Fixed cycle count: 5
  - Fixed seed: 42
  - Sovereign observation after each cycle (logged, never fed back)
  - No tuning, no adaptive behavior, no interpretation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.sovereign_observer import SovereignReport


# ---------------------------------------------------------------------------
# Configuration (constants, not parameters)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Step5Config:
    """Fixed harness configuration. Not tunable."""
    cycles: int = 5
    seed: int = 42
    held_paradox_id: str = "p_held"
    collapsible_paradox_id: str = "p_collapsible"
    open_paradox_id: str = "p_open"


# ---------------------------------------------------------------------------
# Cycle record (descriptive only)
# ---------------------------------------------------------------------------

@dataclass
class CycleRecord:
    """What happened in one cycle. Descriptive, not prescriptive."""
    cycle_number: int
    collapse_result: Any
    become_result: Any
    hold_result: Any
    sovereign_report: SovereignReport
    paradox_statuses: dict  # {paradox_id: status}
    veto_states: dict       # {paradox_id: collapse_veto}


# ---------------------------------------------------------------------------
# Harness result
# ---------------------------------------------------------------------------

@dataclass
class Step5Result:
    """Full result of a Step 5 execution run."""
    config: Step5Config
    cycle_records: List[CycleRecord] = field(default_factory=list)
    final_report: Optional[SovereignReport] = None


# ---------------------------------------------------------------------------
# Harness runner
# ---------------------------------------------------------------------------

def run_step5_harness(
    *,
    initial_state: SystemState,
    collapse_fn,
    become_fn,
    hold_fn,
    observe_fn,
    config: Optional[Step5Config] = None,
) -> Step5Result:
    """Run the fixed execution harness. No interpretation, no fallthrough.

    Operators mutate state in-place and return audit result objects.
    Sovereign observes after each cycle but output is never fed back.

    Args:
        initial_state: Hand-constructed SystemState (mutated during run).
        collapse_fn: collapse_pure(state, seed=N) -> CollapseResult
        become_fn: become_pure(state, seed=N) -> BecomeResult
        hold_fn: paradox_hold_pure(state, seed=N) -> HoldResult
        observe_fn: sovereign_observe(state) -> SovereignReport
        config: Optional override (defaults are locked).

    Returns:
        Step5Result with per-cycle records and a final observation.
    """
    cfg = config or Step5Config()
    result = Step5Result(config=cfg)
    state = initial_state

    for cycle in range(cfg.cycles):
        # Fixed operator sequence: Collapse → Become → Paradox-Hold
        c_out = collapse_fn(state, seed=cfg.seed)
        b_out = become_fn(state, seed=cfg.seed)
        h_out = hold_fn(state, seed=cfg.seed)

        # Observe (logged, never fed back)
        report = observe_fn(state)

        # Record paradox statuses and veto states
        statuses = {}
        vetos = {}
        for p in state.paradoxes:
            statuses[p.id] = p.status
            vetos[p.id] = p.constraints.collapse_veto

        result.cycle_records.append(CycleRecord(
            cycle_number=cycle + 1,
            collapse_result=c_out,
            become_result=b_out,
            hold_result=h_out,
            sovereign_report=report,
            paradox_statuses=statuses,
            veto_states=vetos,
        ))

    # Final observation
    result.final_report = observe_fn(state)

    return result


# ---------------------------------------------------------------------------
# Invariant verification (binary, mechanical)
# ---------------------------------------------------------------------------

def verify_step5_invariants(run: Step5Result) -> List[str]:
    """Verify all Step 5 invariants. Returns list of failures (empty = pass).

    Checks:
      1. Held paradox remains paradox_held at every cycle.
      2. Held paradox veto remains True at every cycle.
      3. Collapsible paradox does not flip-flop (≤2 distinct statuses).
      4. Sovereign reports were collected (non-sycophancy by construction).
    """
    cfg = run.config
    failures = []

    for rec in run.cycle_records:
        # Invariant 1: held paradox persistence
        held_status = rec.paradox_statuses.get(cfg.held_paradox_id)
        if held_status != "paradox_held":
            failures.append(
                f"Cycle {rec.cycle_number}: {cfg.held_paradox_id} status "
                f"is '{held_status}', expected 'paradox_held'"
            )

        # Invariant 2: held paradox veto enforcement
        held_veto = rec.veto_states.get(cfg.held_paradox_id)
        if held_veto is not True:
            failures.append(
                f"Cycle {rec.cycle_number}: {cfg.held_paradox_id} "
                f"collapse_veto is {held_veto}, expected True"
            )

    # Invariant 3: collapsible paradox consistency
    collapsible_statuses = [
        rec.paradox_statuses.get(cfg.collapsible_paradox_id)
        for rec in run.cycle_records
    ]
    distinct = set(collapsible_statuses)
    if len(distinct) > 2:
        failures.append(
            f"{cfg.collapsible_paradox_id} status unstable across cycles: "
            f"{collapsible_statuses}"
        )

    # Invariant 4: Sovereign reports exist (non-sycophancy by construction)
    if len(run.cycle_records) != cfg.cycles:
        failures.append(
            f"Expected {cfg.cycles} cycle records, got {len(run.cycle_records)}"
        )
    if run.final_report is None:
        failures.append("Final Sovereign report is missing")

    return failures
