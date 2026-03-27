"""
SovereignNEXT — Canonical V5 Pipeline

Authoritative execution path for the Sovereign cognitive architecture.
Runs LLM-driven Become passes with Phase 5 operators injected after each
pass, under Sovereign observation.

Pipeline per pass:
  1. LLM claim expansion (expand_claim via local LLM)
  2. LLM tension detection (detect_tensions via local LLM)
  3. Paradox promotion (promote_all_eligible)
  4. Emoji vector mutation (mutate_become)
  5. Phase 5 Collapse (collapse_pure, seed=42)
  6. Phase 5 Become (become_pure, seed=42)
  7. Phase 5 Paradox-Hold (paradox_hold_pure, seed=42)
  8. Sovereign observation (sovereign_observe — logged, never fed back)
  9. Per-pass snapshot saved

Default starting state: v3_final_state_snapshot.json
Hashes: recorded per pass and at completion
Status: canonical — lineage-extending, evidence-bearing

Promoted from experiments/v5_integration_run.py without logic changes.
Original experimental version preserved in experiments/ for lineage.

Usage:
  python -m SovereignNEXT.pipeline.run_sovereign_pipeline_v5
  python -m SovereignNEXT.pipeline.run_sovereign_pipeline_v5 --snapshot path/to/snapshot.json
  python -m SovereignNEXT.pipeline.run_sovereign_pipeline_v5 --phase 4
  python -m SovereignNEXT.pipeline.run_sovereign_pipeline_v5 --passes 5 --seed 99
"""

import sys
import json
import hashlib
import logging
import time
import argparse
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.become_expander import (
    expand_claim,
    select_targeted_claims,
    analyze_pass3_strategy,
    MAX_CLAIMS_TO_EXPAND,
    MAX_TARGETED_EXPANSIONS,
    MAX_BROAD_CLAIMS,
    HYBRID_TARGETED_BUDGET,
    HYBRID_BROAD_BUDGET,
)
from SovereignNEXT.operators.tension_detector import detect_tensions
from SovereignNEXT.operators.emoji_mutator import mutate_become
from SovereignNEXT.operators.paradox_promoter import promote_all_eligible

# Phase 5 operators
from SovereignNEXT.operators.collapse_operator import collapse_pure
from SovereignNEXT.operators.become_expander import become_pure
from SovereignNEXT.operators.paradox_hold_operator import paradox_hold_pure
from SovereignNEXT.operators.sovereign_observer import sovereign_observe, SovereignReport

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants (defaults — overridable via CLI)
# ---------------------------------------------------------------------------

SNAPSHOT_DIR = REPO_ROOT / "SovereignNEXT" / "tests"
DEFAULT_SNAPSHOT = SNAPSHOT_DIR / "v3_final_state_snapshot.json"
OUTPUT_DIR = REPO_ROOT / "SovereignNEXT" / "pipeline"

DEFAULT_PASSES = 3
DEFAULT_SEED = 42
COLLAPSED_STATUSES = {"collapsed_to_a", "collapsed_to_b", "collapsed"}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class V5PassRecord:
    """What happened in one pass. Descriptive only."""
    pass_number: int
    # LLM pipeline metrics
    claims_before: int = 0
    claims_after: int = 0
    new_claims: int = 0
    tensions_before: int = 0
    tensions_after: int = 0
    new_tensions: int = 0
    paradoxes_before: int = 0
    paradoxes_after: int = 0
    new_promotions: int = 0
    # Phase 5 operator summaries
    collapse_summary: Dict[str, Any] = field(default_factory=dict)
    become_summary: Dict[str, Any] = field(default_factory=dict)
    hold_summary: Dict[str, Any] = field(default_factory=dict)
    # Sovereign report
    sovereign_report: Optional[SovereignReport] = None
    # State after pass
    state_hash: str = ""
    paradox_statuses: Dict[str, str] = field(default_factory=dict)
    veto_states: Dict[str, bool] = field(default_factory=dict)
    held_count: int = 0
    vetoed_count: int = 0
    # Timing
    llm_duration_sec: float = 0.0
    phase5_duration_sec: float = 0.0


@dataclass
class V5Result:
    """Full result of the canonical pipeline run."""
    starting_snapshot: str = ""
    input_content_hash: str = ""
    file_bytes_hash: str = ""
    pass_records: List[V5PassRecord] = field(default_factory=list)
    final_state_hash: str = ""
    final_report: Optional[SovereignReport] = None
    # Structural deltas
    baseline_claims: int = 0
    baseline_tensions: int = 0
    baseline_paradoxes: int = 0
    baseline_emoji: int = 0
    final_claims: int = 0
    final_tensions: int = 0
    final_paradoxes: int = 0
    final_emoji: int = 0
    # Observations
    observations: List[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    total_duration_sec: float = 0.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _result_summary(result_obj) -> Dict[str, Any]:
    """Extract numeric summary fields from any operator result dataclass."""
    if hasattr(result_obj, "summary"):
        return result_obj.summary()
    summary = {}
    for fld in result_obj.__dataclass_fields__:
        val = getattr(result_obj, fld)
        if isinstance(val, (int, float)):
            summary[fld] = val
    return summary


def _get_active_emoji_context(state):
    """Get the highest-entropy EmojiVector from state, or None."""
    if not state.emoji_fields:
        return None
    return max(state.emoji_fields, key=lambda ev: ev.entropy)


def _broad_select(state, max_claims=MAX_BROAD_CLAIMS):
    """Select zero/low-tension claims for broad expansion."""
    scored = []
    for c in state.claims:
        if "limit_case" in c.tags:
            continue
        td = sum(1 for t in state.tensions if c.id in t.source_claims)
        if td > 1:
            continue
        score = 10.0 if td == 0 else 2.0
        if c.parent_id is not None:
            score += 1.0
        scored.append((c, score))

    scored.sort(key=lambda x: (-x[1], x[0].confidence))
    return [c for c, _ in scored[:max_claims]]


def _save_snapshot(state, label, output_dir=None):
    """Save state snapshot to disk."""
    d = output_dir or OUTPUT_DIR
    path = Path(d) / f"v5_{label}_state_snapshot.json"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as sf:
            json.dump(state.to_dict(), sf, indent=2, ensure_ascii=False)
        print(f"  Snapshot saved: {path.name}")
    except Exception as e:
        print(f"  WARNING: snapshot save failed ({label}): {e}")


# ---------------------------------------------------------------------------
# Load snapshot
# ---------------------------------------------------------------------------

def load_snapshot(snapshot_path=None):
    """Load a state snapshot and verify integrity.

    Returns:
        (state, input_content_hash, file_bytes_hash)
    """
    path = Path(snapshot_path) if snapshot_path else DEFAULT_SNAPSHOT

    if not path.exists():
        raise FileNotFoundError(f"Snapshot not found: {path}")

    with open(path, "rb") as f:
        file_bytes = f.read()

    file_bytes_hash = hashlib.sha256(file_bytes).hexdigest()
    snapshot_dict = json.loads(file_bytes.decode("utf-8"))
    state = SystemState.from_dict(snapshot_dict)
    input_content_hash = state.content_hash()

    print(f"  Loaded: {len(state.claims)} claims, {len(state.tensions)} tensions, "
          f"{len(state.paradoxes)} paradoxes, {len(state.emoji_fields)} emoji vectors")

    return state, input_content_hash, file_bytes_hash


# ---------------------------------------------------------------------------
# LLM pass (duplicated from V3 pattern — not shared code)
# ---------------------------------------------------------------------------

def _run_llm_pass(state, llm, model, pass_number, embedding_cache):
    """Run one LLM-driven Become pass (claim expansion + tension detection +
    paradox promotion + emoji mutation).

    This is duplicated orchestration from the V3 pipeline. It is NOT shared
    code — it exists only in this file and can be discarded.
    """
    emoji_ctx = _get_active_emoji_context(state)
    if emoji_ctx:
        print(f"  Active emoji context: {emoji_ctx.id} "
              f"(entropy={emoji_ctx.entropy:.3f})")

    pre_existing = list(state.claims)

    # --- Claim selection (varies by pass) ---
    if pass_number == 1:
        # Pass 1: Broad expansion (same as V3 pass 1)
        eligible = [c for c in state.claims if c.parent_id is None]
        eligible.sort(key=lambda c: c.confidence, reverse=True)
        selected = eligible[:MAX_CLAIMS_TO_EXPAND]
    elif pass_number == 2:
        # Pass 2: Targeted expansion (same as V3 pass 2)
        selected = select_targeted_claims(state)
    else:
        # Pass 3: Adaptive expansion (same as V3 pass 3)
        analysis = analyze_pass3_strategy(state)
        strategy = analysis["strategy"]
        print(f"  Strategy: {strategy}")
        print(f"  Rationale: {analysis['rationale']}")

        if strategy == "targeted":
            selected = select_targeted_claims(state)
        elif strategy == "broad":
            selected = _broad_select(state)
        else:
            t_picks = select_targeted_claims(
                state, max_claims=HYBRID_TARGETED_BUDGET,
            )
            b_picks = _broad_select(state, max_claims=HYBRID_BROAD_BUDGET)
            seen = set()
            selected = []
            for c in t_picks + b_picks:
                if c.id not in seen:
                    selected.append(c)
                    seen.add(c.id)

    print(f"  Selected {len(selected)} claims for expansion")

    # --- Expand claims ---
    all_expansions = []
    for claim in selected:
        expansions = expand_claim(claim, llm, model, emoji_field=emoji_ctx)
        if pass_number >= 2:
            expansions = expansions[:MAX_TARGETED_EXPANSIONS]
        all_expansions.extend(expansions)

    for exp in all_expansions:
        state.add_claim(exp)

    print(f"  Expanded → {len(all_expansions)} new claims (total: {len(state.claims)})")

    # --- Detect tensions ---
    new_tensions = []
    if all_expansions and pre_existing:
        new_tensions = detect_tensions(
            new_claims=all_expansions,
            existing_claims=pre_existing,
            llm=llm,
            model=model,
            embedding_cache=embedding_cache,
            emoji_context=emoji_ctx,
        )
        for t in new_tensions:
            state.add_tension(t)

    print(f"  Detected {len(new_tensions)} new tensions (total: {len(state.tensions)})")

    state.iteration += 1

    # --- Paradox promotion ---
    seed_offset = 45 + pass_number  # 46, 47, 48 — same as V3
    promoted = promote_all_eligible(state, seed=seed_offset)
    print(f"  Promoted {len(promoted)} new paradoxes (total: {len(state.paradoxes)})")

    # --- Emoji mutation ---
    mutation_seed = 300 + (pass_number * 100)  # 400, 500, 600 — same as V3
    for ev in state.emoji_fields:
        mutate_become(ev, seed=mutation_seed)
    print(f"  Emoji vectors mutated: {len(state.emoji_fields)} vectors")

    return len(all_expansions), len(new_tensions), len(promoted)


# ---------------------------------------------------------------------------
# Operator pass (Phase 4 or Phase 5)
# ---------------------------------------------------------------------------

def _run_operators(state, phase, seed=DEFAULT_SEED):
    """Run the operator sequence on current state.

    Phase 5: Collapse → Become → Paradox-Hold → Sovereign observe.
    Phase 4: LLM pipeline only — no Phase 5 operators, observation only.

    Returns (collapse_summary, become_summary, hold_summary, sovereign_report).
    """
    if phase == 5:
        c_out = collapse_pure(state, seed=seed)
        b_out = become_pure(state, seed=seed)
        h_out = paradox_hold_pure(state, seed=seed)
        report = sovereign_observe(state)

        return (
            _result_summary(c_out),
            _result_summary(b_out),
            _result_summary(h_out),
            report,
        )
    else:
        # Phase 4: observe only, no Phase 5 operators
        report = sovereign_observe(state)
        return ({}, {}, {}, report)


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------

def run_canonical_pipeline(
    snapshot_path=None,
    phase=5,
    passes=DEFAULT_PASSES,
    seed=DEFAULT_SEED,
    model_override=None,
    output_dir=None,
):
    """Execute the canonical Sovereign pipeline.

    Loads a starting snapshot, runs N passes of (LLM pipeline + operators),
    records everything, saves artifacts.

    Args:
        snapshot_path: Path to starting snapshot (default: v3_final_state_snapshot.json).
        phase: Operator phase — 5 (default) or 4 (LLM only, no Phase 5 operators).
        passes: Number of LLM + operator passes (default: 3).
        seed: RNG seed for Phase 5 operators (default: 42).
        model_override: Model name string to use for all LLM calls (default: SWAY_MODEL).
        output_dir: Directory for output artifacts (default: OUTPUT_DIR).
    """
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    phase_label = f"Phase {phase}"

    print("\n" + "=" * 60)
    print("SOVEREIGN CANONICAL PIPELINE — V5")
    print(f"{phase_label} enabled | {passes} passes | seed={seed}")
    print("=" * 60)

    print("\n  TOGGLES:")
    print("    LLM claim expansion: ENABLED")
    print("    LLM tension detection: ENABLED")
    print("    Paradox promotion: ACTIVE")
    print("    Emoji mutation: ACTIVE")
    print(f"    Phase 5 Collapse: {'ENABLED' if phase == 5 else 'DISABLED'} (after each LLM pass)")
    print(f"    Phase 5 Become: {'ENABLED' if phase == 5 else 'DISABLED'} (after each LLM pass)")
    print(f"    Phase 5 Paradox-Hold: {'ENABLED' if phase == 5 else 'DISABLED'} (after each LLM pass)")
    print("    Sovereign observation: ENABLED (logged, never fed back)")
    print("    Canonical: YES")

    # --- Load snapshot ---
    snapshot_name = Path(snapshot_path).name if snapshot_path else DEFAULT_SNAPSHOT.name
    print(f"\n--- Loading snapshot: {snapshot_name} ---")
    run_start = time.perf_counter()
    state, input_content_hash, file_bytes_hash = load_snapshot(snapshot_path)
    state.mission_id = "M1_v5_canonical"

    result = V5Result(
        starting_snapshot=snapshot_name,
        input_content_hash=input_content_hash,
        file_bytes_hash=file_bytes_hash,
        baseline_claims=len(state.claims),
        baseline_tensions=len(state.tensions),
        baseline_paradoxes=len(state.paradoxes),
        baseline_emoji=len(state.emoji_fields),
    )

    print(f"  State loaded: {state.summary()}")
    print(f"  Content hash: {input_content_hash[:16]}...")
    print(f"  File bytes hash: {file_bytes_hash[:16]}...")

    # --- LLM client ---
    try:
        from agents.llm_client import LLMClient, SWAY_MODEL
        llm = LLMClient()
    except Exception as e:
        print(f"\n  ABORTED — LLM client init failed: {e}")
        return None

    active_model = model_override or SWAY_MODEL
    active_output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    print(f"  Active LLM model: {active_model}")
    print(f"  Output directory: {active_output_dir}")

    try:
        embedding_cache = {}

        for pass_num in range(1, passes + 1):
            pass_label = {1: "Broad", 2: "Targeted", 3: "Adaptive"}.get(
                pass_num, f"Pass-{pass_num}",
            )

            print(f"\n{'='*60}")
            print(f"PASS {pass_num}: {pass_label} expansion + {phase_label}")
            print(f"{'='*60}")

            rec = V5PassRecord(pass_number=pass_num)
            rec.claims_before = len(state.claims)
            rec.tensions_before = len(state.tensions)
            rec.paradoxes_before = len(state.paradoxes)

            # ---- LLM pipeline ----
            print(f"\n--- LLM pipeline (Pass {pass_num}) ---")
            llm_start = time.perf_counter()

            new_claims, new_tensions, new_promos = _run_llm_pass(
                state, llm, active_model, pass_num, embedding_cache,
            )

            rec.llm_duration_sec = time.perf_counter() - llm_start
            rec.new_claims = new_claims
            rec.new_tensions = new_tensions
            rec.new_promotions = new_promos
            rec.claims_after = len(state.claims)
            rec.tensions_after = len(state.tensions)

            print(f"  LLM pipeline: {rec.llm_duration_sec:.1f}s")

            # ---- Operators ----
            print(f"\n--- {phase_label} operators (Pass {pass_num}) ---")
            p5_start = time.perf_counter()

            (rec.collapse_summary, rec.become_summary,
             rec.hold_summary, rec.sovereign_report) = _run_operators(
                state, phase=phase, seed=seed,
            )

            rec.phase5_duration_sec = time.perf_counter() - p5_start

            # Record post-operator state
            rec.state_hash = state.content_hash()
            rec.paradox_statuses = {p.id: p.status for p in state.paradoxes}
            rec.veto_states = {
                p.id: p.constraints.collapse_veto for p in state.paradoxes
            }
            rec.paradoxes_after = len(state.paradoxes)
            rec.held_count = sum(
                1 for p in state.paradoxes if p.status == "paradox_held"
            )
            rec.vetoed_count = sum(
                1 for p in state.paradoxes
                if p.constraints.collapse_veto is True
            )

            result.pass_records.append(rec)

            print(f"  Operators: {rec.phase5_duration_sec:.1f}s")
            print(f"  Collapse: {rec.collapse_summary}")
            print(f"  Become: {rec.become_summary}")
            print(f"  Hold: {rec.hold_summary}")
            print(f"  Held: {rec.held_count}, Vetoed: {rec.vetoed_count}")
            print(f"  State hash: {rec.state_hash[:16]}...")

            if rec.sovereign_report:
                attest = len(rec.sovereign_report.integrity_attestations)
                anomalies = len(rec.sovereign_report.anomaly_flags)
                print(f"  Sovereign: attestations={attest}, "
                      f"anomalies={anomalies}")

            # Save per-pass snapshot
            _save_snapshot(state, f"pass{pass_num}", output_dir=active_output_dir)

        # --- Final Sovereign observation ---
        result.final_report = sovereign_observe(state)
        result.final_state_hash = state.content_hash()
        result.final_claims = len(state.claims)
        result.final_tensions = len(state.tensions)
        result.final_paradoxes = len(state.paradoxes)
        result.final_emoji = len(state.emoji_fields)
        result.total_duration_sec = time.perf_counter() - run_start

        # --- Structural observations ---
        _collect_observations(state, result, passes)

        # --- Print results ---
        _print_results(state, result)

        # --- Save final artifacts ---
        _save_snapshot(state, "final", output_dir=active_output_dir)
        _save_report(result, phase=phase, passes=passes, seed=seed,
                     output_dir=active_output_dir)

        print(f"\n{'='*60}")
        print("CANONICAL PIPELINE RUN COMPLETE")
        print(f"Total duration: {result.total_duration_sec:.1f}s "
              f"({result.total_duration_sec/60:.1f}m)")
        print(f"{'='*60}")

        return result

    except Exception as e:
        print(f"\n  PIPELINE FAILED: {e}")
        import traceback
        traceback.print_exc()
        # Save whatever state we have
        _save_snapshot(state, "final_safe", output_dir=active_output_dir)
        raise

    finally:
        llm.close()


# ---------------------------------------------------------------------------
# Observations (descriptive only)
# ---------------------------------------------------------------------------

def _collect_observations(state, result: V5Result, passes: int):
    """Collect structural observations from the run. Not pass/fail —
    these are things to look at."""
    obs = result.observations

    # Did Phase 5 crash?
    obs.append(f"All {passes} passes completed without operator crash")

    # Newly promoted paradoxes
    total_new_promos = sum(r.new_promotions for r in result.pass_records)
    obs.append(f"Total new paradox promotions across all passes: {total_new_promos}")

    # Held/veto progression
    for rec in result.pass_records:
        obs.append(
            f"Pass {rec.pass_number}: "
            f"{rec.held_count} held, {rec.vetoed_count} vetoed "
            f"(of {rec.paradoxes_after} total paradoxes)"
        )

    # Did any vetoed paradox collapse?
    for i, rec in enumerate(result.pass_records):
        if i == 0:
            continue
        prev = result.pass_records[i - 1]
        prev_vetoed = {
            pid for pid, v in prev.veto_states.items() if v is True
        }
        for pid in prev_vetoed:
            status = rec.paradox_statuses.get(pid, "unknown")
            if status in COLLAPSED_STATUSES:
                obs.append(
                    f"WARNING: {pid} collapsed in pass {rec.pass_number} "
                    f"despite veto in pass {prev.pass_number}"
                )

    # Hub concentration
    claim_tension_count = defaultdict(int)
    for t in state.tensions:
        for cid in t.source_claims:
            claim_tension_count[cid] += 1
    if claim_tension_count:
        sorted_hubs = sorted(
            claim_tension_count.items(), key=lambda x: -x[1],
        )
        top3_vals = [v for _, v in sorted_hubs[:3]]
        total_refs = sum(claim_tension_count.values())
        top3_pct = sum(top3_vals) / total_refs * 100 if total_refs > 0 else 0
        obs.append(f"Hub concentration: top-3 claims hold {top3_pct:.1f}% of tension refs")


def _print_results(state, result: V5Result):
    """Print final structural comparison."""
    print(f"\n{'='*60}")
    print("RESULTS (vs baseline)")
    print(f"{'='*60}")

    print(f"\n  Claims: {result.final_claims} "
          f"(baseline: {result.baseline_claims}, delta: +{result.final_claims - result.baseline_claims})")
    print(f"  Tensions: {result.final_tensions} "
          f"(baseline: {result.baseline_tensions}, delta: +{result.final_tensions - result.baseline_tensions})")
    print(f"  Paradoxes: {result.final_paradoxes} "
          f"(baseline: {result.baseline_paradoxes}, delta: +{result.final_paradoxes - result.baseline_paradoxes})")
    print(f"  Emoji vectors: {result.final_emoji} "
          f"(baseline: {result.baseline_emoji}, delta: +{result.final_emoji - result.baseline_emoji})")

    # Tension type breakdown
    type_counts = defaultdict(int)
    for t in state.tensions:
        type_counts[t.relation_type] += 1
    print("\n  Tension breakdown:")
    for ttype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"    {ttype}: {count}")

    # Paradox status breakdown
    status_counts = Counter(p.status for p in state.paradoxes)
    print("\n  Paradox status breakdown:")
    for status, count in status_counts.most_common():
        print(f"    {status}: {count}")

    # Veto summary
    vetoed = sum(1 for p in state.paradoxes if p.constraints.collapse_veto)
    print(f"\n  Vetoed paradoxes: {vetoed} / {len(state.paradoxes)}")

    # Hub concentration
    claim_tension_count = defaultdict(int)
    for t in state.tensions:
        for cid in t.source_claims:
            claim_tension_count[cid] += 1
    sorted_hubs = sorted(claim_tension_count.items(), key=lambda x: -x[1])
    top3_vals = [v for _, v in sorted_hubs[:3]]
    total_refs = sum(claim_tension_count.values())
    top3_pct = sum(top3_vals) / total_refs * 100 if total_refs > 0 else 0
    print(f"\n  Hub concentration: top-3 claims hold {top3_pct:.1f}% of tension refs")
    for cid, cnt in sorted_hubs[:5]:
        print(f"    {cid}: {cnt} tensions ({cnt/len(state.tensions)*100:.1f}%)")

    # Observations
    print("\n  Observations:")
    for o in result.observations:
        print(f"    - {o}")

    print(f"\n  Final state: {state.summary()}")


# ---------------------------------------------------------------------------
# Health summary (governance contract v1)
# ---------------------------------------------------------------------------

def _build_health_summary(result: V5Result, passes: int) -> Dict[str, Any]:
    """Build the canonical health summary from existing observer output.

    Uses result.final_report.anomaly_flags (captured during the run).
    Does NOT re-run the observer. Reads only.

    Schema defined in observer_governance_contract_v1.md.
    """
    summary: Dict[str, Any] = {
        "run_id": result.starting_snapshot,
        "snapshot_hash_start": result.input_content_hash,
        "snapshot_hash_end": result.final_state_hash,
        "passes_completed": passes,
        "anomalies_total": 0,
        "warnings_total": 0,
        "regulated_total": 0,
        "warnings_by_type": {},
        "health_statement": "healthy: no warnings",
    }

    if result.final_report is None:
        summary["health_statement"] = "missing observation"
        return summary

    flags = result.final_report.anomaly_flags
    summary["anomalies_total"] = len(flags)

    # Parse anomaly types from flag strings (format: "type: ...")
    type_counts: Dict[str, int] = {}
    for flag in flags:
        atype = flag.split(":")[0].strip()
        type_counts[atype] = type_counts.get(atype, 0) + 1

    regulated = type_counts.pop("regulated", 0)
    summary["regulated_total"] = regulated
    summary["warnings_total"] = sum(type_counts.values())
    summary["warnings_by_type"] = type_counts

    if summary["warnings_total"] == 0:
        summary["health_statement"] = "healthy: no warnings"
    else:
        summary["health_statement"] = "warnings present: review anomalies"

    return summary


# ---------------------------------------------------------------------------
# Save artifacts
# ---------------------------------------------------------------------------

def _save_report(result: V5Result, phase: int = 5, passes: int = 3, seed: int = 42,
                 output_dir=None):
    """Save canonical pipeline report JSON."""
    # --- Compute health summary from existing observer output ---
    health_summary = _build_health_summary(result, passes)

    report = {
        "experiment": "Canonical V5 Pipeline Run",
        "status": "canonical",
        "phase": phase,
        "passes": passes,
        "seed": seed,
        "timestamp": result.timestamp,
        "starting_snapshot": result.starting_snapshot,
        "input_content_hash": result.input_content_hash,
        "file_bytes_hash": result.file_bytes_hash,
        "final_state_hash": result.final_state_hash,
        "total_duration_sec": result.total_duration_sec,
        "health_summary": health_summary,
        "baseline": {
            "claims": result.baseline_claims,
            "tensions": result.baseline_tensions,
            "paradoxes": result.baseline_paradoxes,
            "emoji_vectors": result.baseline_emoji,
        },
        "final_state": {
            "claims": result.final_claims,
            "tensions": result.final_tensions,
            "paradoxes": result.final_paradoxes,
            "emoji_vectors": result.final_emoji,
        },
        "deltas": {
            "claims": result.final_claims - result.baseline_claims,
            "tensions": result.final_tensions - result.baseline_tensions,
            "paradoxes": result.final_paradoxes - result.baseline_paradoxes,
            "emoji_vectors": result.final_emoji - result.baseline_emoji,
        },
        "per_pass": [],
        "observations": result.observations,
    }

    for rec in result.pass_records:
        pass_data = {
            "pass": rec.pass_number,
            "state_hash": rec.state_hash,
            "claims_before": rec.claims_before,
            "claims_after": rec.claims_after,
            "new_claims": rec.new_claims,
            "tensions_before": rec.tensions_before,
            "tensions_after": rec.tensions_after,
            "new_tensions": rec.new_tensions,
            "paradoxes_before": rec.paradoxes_before,
            "paradoxes_after": rec.paradoxes_after,
            "new_promotions": rec.new_promotions,
            "collapse": rec.collapse_summary,
            "become": rec.become_summary,
            "hold": rec.hold_summary,
            "held_count": rec.held_count,
            "vetoed_count": rec.vetoed_count,
            "paradox_status_counts": dict(
                Counter(rec.paradox_statuses.values())
            ),
            "llm_duration_sec": rec.llm_duration_sec,
            "phase5_duration_sec": rec.phase5_duration_sec,
        }
        report["per_pass"].append(pass_data)

    report_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    path = report_dir / "v5_canonical_report.json"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"  Report saved: {path.name}")
    except Exception as e:
        print(f"  WARNING: report save failed: {e}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="SovereignNEXT Canonical V5 Pipeline",
    )
    parser.add_argument(
        "--snapshot",
        type=str,
        default=None,
        help="Path to starting snapshot (default: v3_final_state_snapshot.json)",
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[4, 5],
        default=5,
        help="Operator phase: 5 (default) runs Phase 5 operators, 4 runs LLM only",
    )
    parser.add_argument(
        "--passes",
        type=int,
        default=DEFAULT_PASSES,
        help=f"Number of LLM + operator passes (default: {DEFAULT_PASSES})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"RNG seed for Phase 5 operators (default: {DEFAULT_SEED})",
    )

    args = parser.parse_args()

    run_canonical_pipeline(
        snapshot_path=args.snapshot,
        phase=args.phase,
        passes=args.passes,
        seed=args.seed,
    )
