"""
SovereignNEXT — Phase 4: Collapse Validation
Back-to-back Collapse runs for controlled contrast.

Step 1 — Baseline Collapse (Control):
  Load v2_final_state_snapshot.json, run collapse_once(), save snapshot, log stats.

Step 2 — Paradox-Aware Collapse (Experimental):
  Load v3_final_state_snapshot.json, run collapse_once(), save snapshot, log stats.

Both runs use identical operator code, thresholds, and parameters.
The only variable is the input state (v2 vs v3).

Constraints:
  - No interpretation, summarization, or editorial commentary
  - No geometry inspection between runs
  - No parameter changes between runs
  - Treat as proof experiment, not optimization pass
"""

import sys
import json
import logging
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.collapse_operator import collapse_once

logger = logging.getLogger(__name__)

SNAPSHOT_DIR = REPO_ROOT / "SovereignNEXT" / "tests"
V2_SNAPSHOT = SNAPSHOT_DIR / "v2_final_state_snapshot.json"
V3_SNAPSHOT = SNAPSHOT_DIR / "v3_final_state_snapshot.json"

COLLAPSE_SEED = 700


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save_snapshot(state, label):
    """Save state snapshot to disk."""
    path = SNAPSHOT_DIR / f"{label}_snapshot.json"
    try:
        with open(path, "w", encoding="utf-8") as sf:
            json.dump(state.to_dict(), sf, indent=2)
        print(f"  Snapshot saved: {path.name}")
    except Exception as e:
        print(f"  WARNING: snapshot save failed ({label}): {e}")


def _load_snapshot(path, label):
    """Load a snapshot and return SystemState."""
    if not path.exists():
        raise FileNotFoundError(f"{label} snapshot not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        d = json.load(f)
    state = SystemState.from_dict(d)
    return state


def _print_pre_collapse_stats(state, label):
    """Print pre-collapse state stats."""
    open_t = len([t for t in state.tensions if t.status == "open"])
    held_t = len([t for t in state.tensions if t.status == "paradox_held"])
    linked = len([t for t in state.tensions if t.emoji_vector_id is not None])

    type_counts = defaultdict(int)
    for t in state.tensions:
        type_counts[t.relation_type] += 1

    print(f"\n  [{label}] Pre-Collapse State:")
    print(f"    Claims: {len(state.claims)}")
    print(f"    Tensions: {len(state.tensions)} (open={open_t}, held={held_t})")
    print(f"    Tensions with emoji link: {linked}")
    print(f"    Paradoxes: {len(state.paradoxes)}")
    print(f"    Emoji vectors: {len(state.emoji_fields)}")
    print(f"    Tension types: {dict(type_counts)}")


def _print_collapse_result(result, label):
    """Print Collapse result summary."""
    print(f"\n  [{label}] Collapse Result:")
    print(f"    Total evaluated: {result.total_open}")
    print(f"    Committed: {result.committed}")
    print(f"    Deferred: {result.deferred}")
    print(f"    Paradox-held: {result.paradox_held}")
    print(f"    Errors: {result.errors}")

    # Breakdown of commits
    commit_a = sum(1 for a in result.actions if a.decision == "commit_to_a")
    commit_b = sum(1 for a in result.actions if a.decision == "commit_to_b")
    vetoed = sum(1 for a in result.actions if a.paradox_vetoed)
    emoji_mutated = sum(1 for a in result.actions if a.emoji_mutated)

    print(f"    Commit to A: {commit_a}")
    print(f"    Commit to B: {commit_b}")
    print(f"    Paradox vetoed: {vetoed}")
    print(f"    Emoji vectors mutated: {emoji_mutated}")

    # Margin distribution
    if result.actions:
        margins = [a.margin for a in result.actions]
        avg_margin = sum(margins) / len(margins)
        min_margin = min(margins)
        max_margin = max(margins)
        print(f"    Margin: avg={avg_margin:.3f}, min={min_margin:.3f}, max={max_margin:.3f}")


def _print_post_collapse_stats(state, label):
    """Print post-collapse state stats."""
    status_counts = defaultdict(int)
    for t in state.tensions:
        status_counts[t.status] += 1

    paradox_status = defaultdict(int)
    for p in state.paradoxes:
        paradox_status[p.status] += 1

    print(f"\n  [{label}] Post-Collapse State:")
    print(f"    Tension statuses: {dict(status_counts)}")
    print(f"    Paradox statuses: {dict(paradox_status)}")
    print(f"    Final state: {state.summary()}")


def _print_comparison(v2_result, v3_result):
    """Print side-by-side comparison of both runs."""
    print("\n" + "=" * 60)
    print("SIDE-BY-SIDE COMPARISON")
    print("=" * 60)

    rows = [
        ["Total evaluated", v2_result.total_open, v3_result.total_open,
         v3_result.total_open - v2_result.total_open],
        ["Committed", v2_result.committed, v3_result.committed,
         v3_result.committed - v2_result.committed],
        ["Deferred", v2_result.deferred, v3_result.deferred,
         v3_result.deferred - v2_result.deferred],
        ["Paradox-held", v2_result.paradox_held, v3_result.paradox_held,
         v3_result.paradox_held - v2_result.paradox_held],
        ["Errors", v2_result.errors, v3_result.errors,
         v3_result.errors - v2_result.errors],
    ]

    v2_vetoed = sum(1 for a in v2_result.actions if a.paradox_vetoed)
    v3_vetoed = sum(1 for a in v3_result.actions if a.paradox_vetoed)
    rows.append(["Paradox vetoes", v2_vetoed, v3_vetoed, v3_vetoed - v2_vetoed])

    v2_emoji = sum(1 for a in v2_result.actions if a.emoji_mutated)
    v3_emoji = sum(1 for a in v3_result.actions if a.emoji_mutated)
    rows.append(["Emoji mutations", v2_emoji, v3_emoji, v3_emoji - v2_emoji])

    # Commit rate
    v2_rate = (v2_result.committed / v2_result.total_open * 100) if v2_result.total_open else 0
    v3_rate = (v3_result.committed / v3_result.total_open * 100) if v3_result.total_open else 0
    rows.append(["Commit rate %", f"{v2_rate:.1f}%", f"{v3_rate:.1f}%",
                 f"{v3_rate - v2_rate:+.1f}%"])

    # Paradox-hold rate
    v2_ph_rate = (v2_result.paradox_held / v2_result.total_open * 100) if v2_result.total_open else 0
    v3_ph_rate = (v3_result.paradox_held / v3_result.total_open * 100) if v3_result.total_open else 0
    rows.append(["Paradox-hold rate %", f"{v2_ph_rate:.1f}%", f"{v3_ph_rate:.1f}%",
                 f"{v3_ph_rate - v2_ph_rate:+.1f}%"])

    # Print table
    print(f"\n  {'Metric':<22} {'V2 Baseline':>14} {'V3 Experimental':>16} {'Delta':>10}")
    print(f"  {'-'*22} {'-'*14} {'-'*16} {'-'*10}")
    for row in rows:
        print(f"  {str(row[0]):<22} {str(row[1]):>14} {str(row[2]):>16} {str(row[3]):>10}")


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------

def _health_checks():
    """Run pre-execution health checks."""
    print("\n--- Pre-execution health checks ---")

    # Check snapshots exist
    for path, label in [(V2_SNAPSHOT, "v2"), (V3_SNAPSHOT, "v3")]:
        if path.exists():
            size = path.stat().st_size
            print(f"  {label} snapshot: OK ({size:,} bytes)")
        else:
            print(f"  {label} snapshot: MISSING -- {path}")
            return False

    # Check LLM
    try:
        from agents.llm_client import LLMClient, SWAY_MODEL
        llm = LLMClient()
        print(f"  LLM client: OK (model={SWAY_MODEL})")
        llm.close()
    except Exception as e:
        print(f"  LLM client: FAILED -- {e}")
        return False

    # Check for stale Phase 4 snapshots
    for label in ["v2_collapsed", "v3_collapsed"]:
        stale = SNAPSHOT_DIR / f"{label}_snapshot.json"
        if stale.exists():
            print(f"  WARNING: stale {label} snapshot exists, will be overwritten")

    print("  All checks passed.\n")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_phase4():
    """Execute Phase 4: back-to-back Collapse validation."""

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("PHASE 4 -- COLLAPSE VALIDATION")
    print("=" * 60)

    if not _health_checks():
        print("ABORT: health checks failed.")
        return

    from agents.llm_client import LLMClient, SWAY_MODEL
    llm = LLMClient()

    v2_result = None
    v3_result = None

    try:
        # =================================================================
        # STEP 1 — Baseline Collapse (v2)
        # =================================================================
        print("\n" + "=" * 60)
        print("STEP 1 -- BASELINE COLLAPSE (v2)")
        print("=" * 60)

        v2_state = _load_snapshot(V2_SNAPSHOT, "v2")
        _print_pre_collapse_stats(v2_state, "V2")

        print("\n  Running Collapse on v2 state...")
        v2_result = collapse_once(v2_state, llm, SWAY_MODEL, seed=COLLAPSE_SEED)
        _print_collapse_result(v2_result, "V2")
        _print_post_collapse_stats(v2_state, "V2")
        _save_snapshot(v2_state, "v2_collapsed")

        print("\n  STEP 1 COMPLETE -- BASELINE COLLAPSE DONE")

        # =================================================================
        # STEP 2 — Paradox-Aware Collapse (v3)
        # =================================================================
        print("\n" + "=" * 60)
        print("STEP 2 -- PARADOX-AWARE COLLAPSE (v3)")
        print("=" * 60)

        v3_state = _load_snapshot(V3_SNAPSHOT, "v3")
        _print_pre_collapse_stats(v3_state, "V3")

        print("\n  Running Collapse on v3 state...")
        v3_result = collapse_once(v3_state, llm, SWAY_MODEL, seed=COLLAPSE_SEED)
        _print_collapse_result(v3_result, "V3")
        _print_post_collapse_stats(v3_state, "V3")
        _save_snapshot(v3_state, "v3_collapsed")

        print("\n  STEP 2 COMPLETE -- PARADOX-AWARE COLLAPSE DONE")

        # =================================================================
        # COMPARISON
        # =================================================================
        if v2_result and v3_result:
            _print_comparison(v2_result, v3_result)

        print("\n" + "=" * 60)
        print("PHASE 4 COMPLETE -- HOLD")
        print("=" * 60)

    finally:
        if v2_result is None and v3_result is None:
            print("\n  WARNING: Both runs failed or were not reached")
        # Save safe snapshots if we have partial results
        llm.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    run_phase4()
