"""
SovereignNEXT — V2 Emoji-Vector Pipeline Test
Controlled experiment: same 3-pass Become pipeline as v1, but with emoji vectors
enabled in tension detection and claim expansion.

Measures three structural deltas against the v1 snapshot:
  1. Polarity emergence — do any tensions classify as polarity?
  2. Hub diffusion — does tension concentration drop below the v1 78% / 3-claim level?
  3. Pass-3 behavior — do new tensions attach across families instead of 100% reinforcement?

Toggles:
  - Emoji vectors: ENABLED in expand_claim and detect_tensions
  - Paradox promotion: ACTIVE after each pass
  - Collapse: DISABLED (not called, not reachable)
"""

import sys
import json
import logging
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.populate import populate_state
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


def _save_snapshot(state, label):
    """Save state snapshot to disk."""
    path = SNAPSHOT_DIR / f"v2_{label}_state_snapshot.json"
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
    """Select zero/low-tension claims for broad expansion (inline to avoid import issues)."""
    claims_in_tensions = set()
    for t in state.tensions:
        for cid in t.source_claims:
            claims_in_tensions.add(cid)

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


def run_v2_pipeline():
    """Run the full 3-pass pipeline with emoji vectors enabled."""

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("\n" + "=" * 60)
    print("V2 EMOJI-VECTOR PIPELINE -- CONTROLLED EXPERIMENT")
    print("=" * 60)

    # Confirm toggles
    print("\n  TOGGLES:")
    print("    Emoji vectors in expand_claim: ENABLED")
    print("    Emoji vectors in detect_tensions: ENABLED")
    print("    Paradox promotion: ACTIVE")
    print("    Collapse: DISABLED")

    m1_path = REPO_ROOT / "SOVEREIGN_PROOF" / "v2_full_missions" / "mission_1.json"
    m2_path = REPO_ROOT / "SOVEREIGN_PROOF" / "v2_full_missions" / "mission_2.json"
    if not m1_path.exists():
        print("  SKIPPED -- mission_1.json not found")
        return

    try:
        from agents.llm_client import LLMClient, SWAY_MODEL
        llm = LLMClient()
    except Exception as e:
        print(f"  SKIPPED -- LLM client init failed: {e}")
        return

    state = None
    try:
        embedding_cache = {}

        # ---------------------------------------------------------------
        # Phase 2: Rebuild base state (identical to v1)
        # ---------------------------------------------------------------
        print("\n--- Phase 2: Rebuild base state ---")
        state = SystemState(mission_id="M1_v2")
        with open(m1_path) as f:
            m1 = json.load(f)
        state = populate_state(m1.get("task_output", ""), state, llm, SWAY_MODEL,
                               source="collapse_M1", mission_id="M1", embedding_cache=embedding_cache)
        if m2_path.exists():
            with open(m2_path) as f:
                m2 = json.load(f)
            state = populate_state(m2.get("task_output", ""), state, llm, SWAY_MODEL,
                                   source="become_M2", mission_id="M2", embedding_cache=embedding_cache)
        print(f"  Phase 2 rebuilt: {state.summary()}")
        _save_snapshot(state, "phase2")

        # Promote eligible tensions after Phase 2
        promoted = promote_all_eligible(state, seed=42)
        print(f"  Phase 2 promotions: {len(promoted)} paradoxes created")

        # ---------------------------------------------------------------
        # Pass 1: Broad expansion (same as v1, but with emoji vectors)
        # ---------------------------------------------------------------
        print("\n--- Pass 1: Broad expansion (emoji-enabled) ---")
        emoji_ctx = _get_active_emoji_context(state)
        if emoji_ctx:
            print(f"  Active emoji context: {emoji_ctx.id} (entropy={emoji_ctx.entropy:.3f})")
        else:
            print("  No active emoji context yet (first pass)")

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
        print(f"  Pass 1 complete: {state.summary()}")
        _save_snapshot(state, "pass1")

        # Promote + mutate after pass 1
        promoted = promote_all_eligible(state, seed=43)
        print(f"  Pass 1 promotions: {len(promoted)} new paradoxes")
        for ev in state.emoji_fields:
            mutate_become(ev, seed=100)
        print(f"  Emoji vectors mutated: {len(state.emoji_fields)} vectors")

        # ---------------------------------------------------------------
        # Pass 2: Targeted expansion (emoji-enabled)
        # ---------------------------------------------------------------
        print("\n--- Pass 2: Targeted expansion (emoji-enabled) ---")
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
        print(f"  Pass 2 complete: {state.summary()}")
        _save_snapshot(state, "pass2")

        # Promote + mutate after pass 2
        promoted = promote_all_eligible(state, seed=44)
        print(f"  Pass 2 promotions: {len(promoted)} new paradoxes")
        for ev in state.emoji_fields:
            mutate_become(ev, seed=200)
        print(f"  Emoji vectors mutated: {len(state.emoji_fields)} vectors")

        pre_pass3_claims = len(state.claims)
        pre_pass3_tensions = len(state.tensions)

        # ---------------------------------------------------------------
        # Pass 3: Adaptive expansion (emoji-enabled)
        # ---------------------------------------------------------------
        print("\n--- Pass 3: Adaptive expansion (emoji-enabled) ---")
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
        print(f"  Pass 3 complete: {state.summary()}")
        _save_snapshot(state, "pass3")

        # Final promotion
        promoted = promote_all_eligible(state, seed=45)
        print(f"  Pass 3 promotions: {len(promoted)} new paradoxes")
        for ev in state.emoji_fields:
            mutate_become(ev, seed=300)

        # ---------------------------------------------------------------
        # Results comparison
        # ---------------------------------------------------------------
        print("\n" + "=" * 60)
        print("V2 RESULTS")
        print("=" * 60)

        print(f"\n  Claims: {len(state.claims)}")
        print(f"  Tensions: {len(state.tensions)}")
        print(f"  Paradoxes: {len(state.paradoxes)}")
        print(f"  Emoji vectors: {len(state.emoji_fields)}")

        # Tension type breakdown
        type_counts = defaultdict(int)
        for t in state.tensions:
            type_counts[t.relation_type] += 1
        print(f"\n  Tension breakdown:")
        for ttype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"    {ttype}: {count}")

        # Polarity check
        polarity_count = type_counts.get("polarity", 0)
        print(f"\n  DELTA 1 -- Polarity emergence: {polarity_count} polarity tensions")

        # Hub concentration
        claim_tension_count = defaultdict(int)
        for t in state.tensions:
            for cid in t.source_claims:
                claim_tension_count[cid] += 1
        top3 = sorted(claim_tension_count.values(), reverse=True)[:3]
        total_refs = sum(claim_tension_count.values())
        top3_pct = sum(top3) / total_refs * 100 if total_refs > 0 else 0
        print(f"  DELTA 2 -- Hub concentration: top-3 claims hold {top3_pct:.1f}% of tension refs (v1 was 78%)")

        # Pass-3 attachment
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
        print(f"  DELTA 3 -- Pass-3 tensions: {total_p3t} total")
        print(f"    old<->new: {old_new}")
        print(f"    new<->new: {new_new}")
        print(f"    old<->old: {old_old}")
        if total_p3t > 0:
            reinforce_pct = old_new / total_p3t * 100
            print(f"    Reinforcement: {reinforce_pct:.0f}% (v1 was 100%)")

        # Emoji vector metrics
        if state.emoji_fields:
            print(f"\n  Emoji vector metrics:")
            for ev in state.emoji_fields:
                print(f"    {ev.id}: entropy={ev.entropy:.3f}, chaos={ev.chaos_index:.3f}, "
                      f"stability={ev.stability_index:.3f}, balance={ev.pole_balance:.3f}, "
                      f"len={ev.length}")

        # Paradox summary
        if state.paradoxes:
            print(f"\n  Paradoxes:")
            for p in state.paradoxes:
                print(f"    {p.id}: [{p.pole_a.id[:40]}] vs [{p.pole_b.id[:40]}] "
                      f"(status={p.status}, strength={p.metrics.tension_strength:.3f})")

        # Invariant checks
        assert len(state.emoji_fields) >= 0  # emoji vectors may exist now
        for t in state.tensions:
            assert t.status == "open", f"Tension {t.id} not open"
        for p in state.paradoxes:
            assert p.status == "open", f"Paradox {p.id} not open (no Collapse ran)"

        print(f"\n  Final state: {state.summary()}")
        _save_snapshot(state, "final")

        print("\n" + "=" * 60)
        print("V2 PIPELINE COMPLETE -- HOLD")
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
    run_v2_pipeline()
