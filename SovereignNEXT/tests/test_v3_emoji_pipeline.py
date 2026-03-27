"""
SovereignNEXT — V3 Emoji-Vector Pipeline (Phase 3a-v3)
Loads the v2 final snapshot as starting state and runs 3 additional Become passes
with the emoji-vector substrate fully active.

Goal: Further diversify the tension field, reduce hub concentration, and stabilize
polarity before Collapse.

Toggles:
  - Emoji vectors: ENABLED in expand_claim and detect_tensions
  - Paradox promotion: ACTIVE after each pass
  - Collapse: DISABLED (not called, not reachable)
  - All v2 state (claims, tensions, paradoxes, emoji vectors): PRESERVED
"""

import sys
import json
import logging
from pathlib import Path
from collections import defaultdict

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
)
from SovereignNEXT.operators.tension_detector import detect_tensions
from SovereignNEXT.operators.emoji_mutator import mutate_become
from SovereignNEXT.operators.paradox_promoter import promote_all_eligible

logger = logging.getLogger(__name__)

SNAPSHOT_DIR = REPO_ROOT / "SovereignNEXT" / "tests"
V2_SNAPSHOT = SNAPSHOT_DIR / "v2_final_state_snapshot.json"


def _save_snapshot(state, label):
    """Save state snapshot to disk."""
    path = SNAPSHOT_DIR / f"v3_{label}_state_snapshot.json"
    try:
        with open(path, "w", encoding="utf-8") as sf:
            json.dump(state.to_dict(), sf, indent=2)
        print(f"  Snapshot saved: {path.name}")
    except Exception as e:
        print(f"  WARNING: snapshot save failed ({label}): {e}")


def _get_active_emoji_context(state):
    """Get the highest-entropy EmojiVector from state, or None if none exist."""
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


def _load_v2_snapshot():
    """Load the v2 final snapshot and verify integrity."""
    if not V2_SNAPSHOT.exists():
        raise FileNotFoundError(f"V2 snapshot not found: {V2_SNAPSHOT}")

    with open(V2_SNAPSHOT, "r", encoding="utf-8") as f:
        d = json.load(f)

    state = SystemState.from_dict(d)

    # Integrity checks
    assert len(state.claims) == 82, f"Expected 82 claims, got {len(state.claims)}"
    assert len(state.tensions) == 144, f"Expected 144 tensions, got {len(state.tensions)}"
    assert len(state.paradoxes) == 24, f"Expected 24 paradoxes, got {len(state.paradoxes)}"
    assert len(state.emoji_fields) == 24, f"Expected 24 emoji fields, got {len(state.emoji_fields)}"
    assert state.iteration == 5, f"Expected iteration 5, got {state.iteration}"

    for t in state.tensions:
        assert t.status == "open", f"Tension {t.id} not open: {t.status}"
    for p in state.paradoxes:
        assert p.status == "open", f"Paradox {p.id} not open: {p.status}"

    return state


def run_v3_pipeline():
    """Run 3 additional Become passes on top of the v2 final state."""

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("V3 EMOJI-VECTOR PIPELINE -- PHASE 3a-v3")
    print("=" * 60)

    # Confirm toggles
    print("\n  TOGGLES:")
    print("    Emoji vectors in expand_claim: ENABLED")
    print("    Emoji vectors in detect_tensions: ENABLED")
    print("    Paradox promotion: ACTIVE")
    print("    Collapse: DISABLED")
    print("    V2 state preservation: ALL claims/tensions/paradoxes/emoji preserved")

    # Load v2 snapshot
    print("\n--- Loading v2 final snapshot ---")
    state = _load_v2_snapshot()
    state.mission_id = "M1_v3"
    print(f"  V2 state loaded: {state.summary()}")
    print(f"  ID counters reset to v2 max values")

    try:
        from agents.llm_client import LLMClient, SWAY_MODEL
        llm = LLMClient()
    except Exception as e:
        print(f"  SKIPPED -- LLM client init failed: {e}")
        return

    try:
        embedding_cache = {}

        # Record pre-v3 baselines for delta comparison
        v2_claims = len(state.claims)
        v2_tensions = len(state.tensions)
        v2_paradoxes = len(state.paradoxes)
        v2_emoji = len(state.emoji_fields)

        # ---------------------------------------------------------------
        # V3 Pass 1: Broad expansion (emoji-enabled)
        # ---------------------------------------------------------------
        print("\n--- V3 Pass 1: Broad expansion (emoji-enabled) ---")
        emoji_ctx = _get_active_emoji_context(state)
        if emoji_ctx:
            print(f"  Active emoji context: {emoji_ctx.id} (entropy={emoji_ctx.entropy:.3f})")

        pre_existing = list(state.claims)
        eligible = [c for c in state.claims if c.parent_id is None]
        eligible.sort(key=lambda c: c.confidence, reverse=True)
        selected = eligible[:MAX_CLAIMS_TO_EXPAND]

        all_expansions = []
        for claim in selected:
            expansions = expand_claim(claim, llm, SWAY_MODEL, emoji_field=emoji_ctx)
            all_expansions.extend(expansions)

        for exp in all_expansions:
            state.add_claim(exp)

        if all_expansions and pre_existing:
            new_tensions = detect_tensions(
                new_claims=all_expansions,
                existing_claims=pre_existing,
                llm=llm,
                model=SWAY_MODEL,
                embedding_cache=embedding_cache,
                emoji_context=emoji_ctx,
            )
            for t in new_tensions:
                state.add_tension(t)

        state.iteration += 1
        print(f"  V3 Pass 1 complete: {state.summary()}")
        _save_snapshot(state, "pass1")

        # Promote + mutate after pass 1
        promoted = promote_all_eligible(state, seed=46)
        print(f"  V3 Pass 1 promotions: {len(promoted)} new paradoxes")
        for ev in state.emoji_fields:
            mutate_become(ev, seed=400)
        print(f"  Emoji vectors mutated: {len(state.emoji_fields)} vectors")

        # ---------------------------------------------------------------
        # V3 Pass 2: Targeted expansion (emoji-enabled)
        # ---------------------------------------------------------------
        print("\n--- V3 Pass 2: Targeted expansion (emoji-enabled) ---")
        emoji_ctx = _get_active_emoji_context(state)
        if emoji_ctx:
            print(f"  Active emoji context: {emoji_ctx.id} (entropy={emoji_ctx.entropy:.3f}, chaos={emoji_ctx.chaos_index:.3f})")

        pre_existing = list(state.claims)
        selected = select_targeted_claims(state)

        all_expansions = []
        for claim in selected:
            expansions = expand_claim(claim, llm, SWAY_MODEL, emoji_field=emoji_ctx)
            expansions = expansions[:MAX_TARGETED_EXPANSIONS]
            all_expansions.extend(expansions)

        for exp in all_expansions:
            state.add_claim(exp)

        if all_expansions and pre_existing:
            new_tensions = detect_tensions(
                new_claims=all_expansions,
                existing_claims=pre_existing,
                llm=llm,
                model=SWAY_MODEL,
                embedding_cache=embedding_cache,
                emoji_context=emoji_ctx,
            )
            for t in new_tensions:
                state.add_tension(t)

        state.iteration += 1
        print(f"  V3 Pass 2 complete: {state.summary()}")
        _save_snapshot(state, "pass2")

        # Promote + mutate after pass 2
        promoted = promote_all_eligible(state, seed=47)
        print(f"  V3 Pass 2 promotions: {len(promoted)} new paradoxes")
        for ev in state.emoji_fields:
            mutate_become(ev, seed=500)
        print(f"  Emoji vectors mutated: {len(state.emoji_fields)} vectors")

        pre_pass3_claims = len(state.claims)
        pre_pass3_tensions = len(state.tensions)

        # ---------------------------------------------------------------
        # V3 Pass 3: Adaptive expansion (emoji-enabled)
        # ---------------------------------------------------------------
        print("\n--- V3 Pass 3: Adaptive expansion (emoji-enabled) ---")
        emoji_ctx = _get_active_emoji_context(state)
        if emoji_ctx:
            print(f"  Active emoji context: {emoji_ctx.id} (entropy={emoji_ctx.entropy:.3f}, chaos={emoji_ctx.chaos_index:.3f})")

        analysis = analyze_pass3_strategy(state)
        strategy = analysis["strategy"]
        print(f"  Strategy: {strategy}")
        print(f"  Rationale: {analysis['rationale']}")

        pre_existing = list(state.claims)

        if strategy == "targeted":
            selected = select_targeted_claims(state)
        elif strategy == "broad":
            selected = _broad_select(state)
        else:
            from SovereignNEXT.operators.become_expander import HYBRID_TARGETED_BUDGET, HYBRID_BROAD_BUDGET
            t_picks = select_targeted_claims(state, max_claims=HYBRID_TARGETED_BUDGET)
            b_picks = _broad_select(state, max_claims=HYBRID_BROAD_BUDGET)
            seen = set()
            selected = []
            for c in t_picks + b_picks:
                if c.id not in seen:
                    selected.append(c)
                    seen.add(c.id)

        all_expansions = []
        for claim in selected:
            expansions = expand_claim(claim, llm, SWAY_MODEL, emoji_field=emoji_ctx)
            expansions = expansions[:MAX_TARGETED_EXPANSIONS]
            all_expansions.extend(expansions)

        for exp in all_expansions:
            state.add_claim(exp)

        if all_expansions and pre_existing:
            new_tensions = detect_tensions(
                new_claims=all_expansions,
                existing_claims=pre_existing,
                llm=llm,
                model=SWAY_MODEL,
                embedding_cache=embedding_cache,
                emoji_context=emoji_ctx,
            )
            for t in new_tensions:
                state.add_tension(t)

        state.iteration += 1
        print(f"  V3 Pass 3 complete: {state.summary()}")
        _save_snapshot(state, "pass3")

        # Final promotion
        promoted = promote_all_eligible(state, seed=48)
        print(f"  V3 Pass 3 promotions: {len(promoted)} new paradoxes")
        for ev in state.emoji_fields:
            mutate_become(ev, seed=600)

        # ---------------------------------------------------------------
        # Results comparison (v3 vs v2)
        # ---------------------------------------------------------------
        print("\n" + "=" * 60)
        print("V3 RESULTS (vs V2 baseline)")
        print("=" * 60)

        print(f"\n  Claims: {len(state.claims)} (v2: {v2_claims}, delta: +{len(state.claims) - v2_claims})")
        print(f"  Tensions: {len(state.tensions)} (v2: {v2_tensions}, delta: +{len(state.tensions) - v2_tensions})")
        print(f"  Paradoxes: {len(state.paradoxes)} (v2: {v2_paradoxes}, delta: +{len(state.paradoxes) - v2_paradoxes})")
        print(f"  Emoji vectors: {len(state.emoji_fields)} (v2: {v2_emoji}, delta: +{len(state.emoji_fields) - v2_emoji})")

        # Tension type breakdown
        type_counts = defaultdict(int)
        for t in state.tensions:
            type_counts[t.relation_type] += 1
        print(f"\n  Tension breakdown:")
        for ttype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"    {ttype}: {count}")

        # Hub concentration
        claim_tension_count = defaultdict(int)
        for t in state.tensions:
            for cid in t.source_claims:
                claim_tension_count[cid] += 1
        sorted_hubs = sorted(claim_tension_count.items(), key=lambda x: -x[1])
        top3_vals = [v for _, v in sorted_hubs[:3]]
        total_refs = sum(claim_tension_count.values())
        top3_pct = sum(top3_vals) / total_refs * 100 if total_refs > 0 else 0
        print(f"\n  Hub concentration: top-3 claims hold {top3_pct:.1f}% of tension refs (v2 was 86.1%)")
        for cid, cnt in sorted_hubs[:5]:
            print(f"    {cid}: {cnt} tensions ({cnt/len(state.tensions)*100:.1f}%)")

        # Pass-3 attachment analysis
        pass3_claims_set = {c.id for c in state.claims[pre_pass3_claims:]}
        pre_pass3_set = {c.id for c in state.claims[:pre_pass3_claims]}
        pass3_tensions = state.tensions[pre_pass3_tensions:]
        old_new = 0
        new_new = 0
        old_old = 0
        for t in pass3_tensions:
            scs = t.source_claims
            in_new = sum(1 for cid in scs if cid in pass3_claims_set)
            in_old = sum(1 for cid in scs if cid in pre_pass3_set)
            if in_new > 0 and in_old > 0:
                old_new += 1
            elif in_new >= 2:
                new_new += 1
            else:
                old_old += 1

        total_p3t = len(pass3_tensions)
        print(f"\n  V3 Pass-3 tensions: {total_p3t} total")
        if total_p3t > 0:
            print(f"    old<->new: {old_new}")
            print(f"    new<->new: {new_new}")
            print(f"    old<->old: {old_old}")

        # Paradox summary
        if state.paradoxes:
            print(f"\n  Total paradoxes: {len(state.paradoxes)}")
            for p in state.paradoxes[-10:]:
                print(f"    {p.id}: [{p.pole_a.id[:40]}] vs [{p.pole_b.id[:40]}] "
                      f"(status={p.status}, strength={p.metrics.tension_strength:.3f})")
            if len(state.paradoxes) > 10:
                print(f"    ... and {len(state.paradoxes) - 10} more")

        # Invariant checks
        for t in state.tensions:
            assert t.status == "open", f"Tension {t.id} not open"
        for p in state.paradoxes:
            assert p.status == "open", f"Paradox {p.id} not open (no Collapse ran)"

        print(f"\n  Final state: {state.summary()}")
        _save_snapshot(state, "final")

        print("\n" + "=" * 60)
        print("V3 PIPELINE COMPLETE -- HOLD")
        print("=" * 60)

    finally:
        if state is not None:
            _save_snapshot(state, "final_safe")
        llm.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    run_v3_pipeline()
