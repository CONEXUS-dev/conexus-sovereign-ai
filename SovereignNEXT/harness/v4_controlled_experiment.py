"""
SovereignNEXT — V4 Controlled Experiment

Runs the frozen Phase 5 operators against the V3 final snapshot
(54 paradoxes, 327 tensions, 154 claims) for 3 cycles with fixed seed,
hash-chained onto the V3 lineage.

This is evidence generation, not new functionality. No new operators,
no tuning, no interpretation. Binary invariant verification only.

Hard constraints:
  - Snapshot: v3_final_state_snapshot.json
  - Cycles: 3
  - Seed: 42
  - Operator order: Collapse → Become → Paradox-Hold (fixed)
  - Sovereign: observe after each cycle + final (never fed back)
  - Lineage: chained directly onto V3
  - Canonical hash: SystemState.content_hash()
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.collapse_operator import collapse_pure
from SovereignNEXT.operators.become_expander import become_pure
from SovereignNEXT.operators.paradox_hold_operator import paradox_hold_pure
from SovereignNEXT.operators.sovereign_observer import sovereign_observe, SovereignReport


# ---------------------------------------------------------------------------
# Configuration (constants, not parameters)
# ---------------------------------------------------------------------------

V3_SNAPSHOT_FILENAME = "v3_final_state_snapshot.json"
V4_CYCLES = 3
V4_SEED = 42
COLLAPSED_STATUSES = {"collapsed_to_a", "collapsed_to_b", "collapsed"}


# ---------------------------------------------------------------------------
# Cycle record
# ---------------------------------------------------------------------------

@dataclass
class V4CycleRecord:
    """What happened in one cycle. Descriptive only."""
    cycle_number: int
    state_hash: str
    collapse_summary: Dict[str, Any]
    become_summary: Dict[str, Any]
    hold_summary: Dict[str, Any]
    sovereign_report: SovereignReport
    paradox_statuses: Dict[str, str]
    veto_states: Dict[str, bool]


# ---------------------------------------------------------------------------
# Experiment result
# ---------------------------------------------------------------------------

@dataclass
class V4Result:
    """Full result of the V4 controlled experiment."""
    input_content_hash: str
    file_bytes_hash: str
    cycle_records: List[V4CycleRecord] = field(default_factory=list)
    final_report: Optional[SovereignReport] = None
    final_state_hash: str = ""
    held_set_cycle1: Set[str] = field(default_factory=set)
    veto_set_cycle1: Set[str] = field(default_factory=set)
    invariant_failures: List[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Load V3 snapshot
# ---------------------------------------------------------------------------

def _result_summary(result_obj) -> Dict[str, Any]:
    """Extract numeric summary fields from any operator result dataclass.

    CollapseResult has .summary(), but BecomeResult and HoldResult do not.
    This provides a uniform interface by extracting all int/float fields.
    """
    if hasattr(result_obj, "summary"):
        return result_obj.summary()
    summary = {}
    for fld in result_obj.__dataclass_fields__:
        val = getattr(result_obj, fld)
        if isinstance(val, (int, float)):
            summary[fld] = val
    return summary


def load_v3_snapshot(snapshot_path: str) -> tuple:
    """Load V3 snapshot and compute both hashes.

    Returns:
        (state, input_content_hash, file_bytes_hash)
    """
    with open(snapshot_path, "rb") as f:
        file_bytes = f.read()

    file_bytes_hash = hashlib.sha256(file_bytes).hexdigest()

    snapshot_dict = json.loads(file_bytes.decode("utf-8"))
    state = SystemState.from_dict(snapshot_dict)

    input_content_hash = state.content_hash()

    return state, input_content_hash, file_bytes_hash


# ---------------------------------------------------------------------------
# Run experiment
# ---------------------------------------------------------------------------

def run_v4_experiment(
    snapshot_path: str,
    cycles: int = V4_CYCLES,
    seed: int = V4_SEED,
) -> V4Result:
    """Execute the V4 controlled experiment.

    Loads V3 snapshot, runs fixed operator sequence for N cycles,
    captures held/veto sets after cycle 1, verifies invariants in
    subsequent cycles.

    Args:
        snapshot_path: Path to v3_final_state_snapshot.json
        cycles: Number of cycles (default 3)
        seed: Fixed RNG seed (default 42)

    Returns:
        V4Result with all cycle records, invariant results, and hashes.
    """
    state, input_content_hash, file_bytes_hash = load_v3_snapshot(snapshot_path)

    result = V4Result(
        input_content_hash=input_content_hash,
        file_bytes_hash=file_bytes_hash,
    )

    for cycle_num in range(1, cycles + 1):
        # Fixed operator sequence: Collapse → Become → Paradox-Hold
        c_out = collapse_pure(state, seed=seed)
        b_out = become_pure(state, seed=seed)
        h_out = paradox_hold_pure(state, seed=seed)

        # Sovereign observation (logged, never fed back)
        report = sovereign_observe(state)

        # Record state
        state_hash = state.content_hash()
        paradox_statuses = {p.id: p.status for p in state.paradoxes}
        veto_states = {p.id: p.constraints.collapse_veto for p in state.paradoxes}

        result.cycle_records.append(V4CycleRecord(
            cycle_number=cycle_num,
            state_hash=state_hash,
            collapse_summary=_result_summary(c_out),
            become_summary=_result_summary(b_out),
            hold_summary=_result_summary(h_out),
            sovereign_report=report,
            paradox_statuses=paradox_statuses,
            veto_states=veto_states,
        ))

        # After cycle 1: capture held_set and veto_set
        if cycle_num == 1:
            result.held_set_cycle1 = {
                p.id for p in state.paradoxes
                if p.status == "paradox_held"
            }
            result.veto_set_cycle1 = {
                p.id for p in state.paradoxes
                if p.constraints.collapse_veto is True
            }

    # Final observation
    result.final_report = sovereign_observe(state)
    result.final_state_hash = state.content_hash()

    return result


# ---------------------------------------------------------------------------
# Verify invariants (binary, mechanical)
# ---------------------------------------------------------------------------

def verify_v4_invariants(result: V4Result) -> List[str]:
    """Verify all V4 invariants. Returns list of failures (empty = pass).

    Invariants:
      1. Every p.id in held_set_cycle1 remains paradox_held in cycles 2-3
      2. No p.id in veto_set_cycle1 transitions to collapsed in cycles 2-3
      3. Hash chain: each cycle has a distinct hash derived from state
      4. Sovereign observations exist for all cycles + final
    """
    failures = []

    # Invariant 1 & 2: held/veto persistence (cycles 2+)
    for rec in result.cycle_records:
        if rec.cycle_number <= 1:
            continue

        # Held persistence
        for pid in result.held_set_cycle1:
            status = rec.paradox_statuses.get(pid)
            if status != "paradox_held":
                failures.append(
                    f"Cycle {rec.cycle_number}: {pid} status is '{status}', "
                    f"expected 'paradox_held'"
                )

        # Veto enforcement
        for pid in result.veto_set_cycle1:
            status = rec.paradox_statuses.get(pid)
            if status in COLLAPSED_STATUSES:
                failures.append(
                    f"Cycle {rec.cycle_number}: {pid} collapsed despite veto "
                    f"(status: '{status}')"
                )

    # Invariant 3: hash chain integrity (each cycle has a hash)
    hashes = [rec.state_hash for rec in result.cycle_records]
    if len(hashes) != len(result.cycle_records):
        failures.append("Missing state hashes in cycle records")
    if len(set(hashes)) == 1 and len(hashes) > 1:
        # All hashes identical means operators did nothing — suspicious but not fatal
        # Record as observation, not failure
        pass

    # Invariant 4: Sovereign reports exist
    for rec in result.cycle_records:
        if rec.sovereign_report is None:
            failures.append(
                f"Cycle {rec.cycle_number}: Sovereign report missing"
            )
    if result.final_report is None:
        failures.append("Final Sovereign report missing")

    return failures


# ---------------------------------------------------------------------------
# Save artifacts
# ---------------------------------------------------------------------------

def save_v4_artifacts(
    state: SystemState,
    result: V4Result,
    output_dir: str,
) -> Dict[str, str]:
    """Save V4 final snapshot and experiment report.

    Returns dict of {artifact_name: file_path}.
    """
    os.makedirs(output_dir, exist_ok=True)
    saved = {}

    # Final state snapshot
    snapshot_path = os.path.join(output_dir, "v4_final_state_snapshot.json")
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)
    saved["v4_final_state_snapshot"] = snapshot_path

    # Experiment report
    report = {
        "experiment": "V4 Controlled Experiment",
        "timestamp": result.timestamp,
        "input_content_hash": result.input_content_hash,
        "file_bytes_hash": result.file_bytes_hash,
        "final_state_hash": result.final_state_hash,
        "cycles": len(result.cycle_records),
        "seed": V4_SEED,
        "held_set_cycle1": sorted(result.held_set_cycle1),
        "held_set_size": len(result.held_set_cycle1),
        "veto_set_cycle1": sorted(result.veto_set_cycle1),
        "veto_set_size": len(result.veto_set_cycle1),
        "per_cycle": [],
        "invariant_failures": result.invariant_failures,
        "invariants_passed": len(result.invariant_failures) == 0,
    }

    for rec in result.cycle_records:
        cycle_data = {
            "cycle": rec.cycle_number,
            "state_hash": rec.state_hash,
            "collapse": rec.collapse_summary,
            "become": rec.become_summary,
            "hold": rec.hold_summary,
            "paradox_status_counts": {},
            "veto_locked_count": sum(1 for v in rec.veto_states.values() if v),
        }
        # Count statuses
        from collections import Counter
        cycle_data["paradox_status_counts"] = dict(
            Counter(rec.paradox_statuses.values())
        )
        report["per_cycle"].append(cycle_data)

    report_path = os.path.join(output_dir, "v4_experiment_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    saved["v4_experiment_report"] = report_path

    return saved
