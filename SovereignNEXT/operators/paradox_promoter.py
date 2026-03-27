"""
SovereignNEXT — Paradox Promoter
Lifecycle logic for promoting Tensions into Paradoxes with associated EmojiVectors.

A Tension is promoted to a Paradox when it meets structural criteria indicating
that the opposition is irreducible and load-bearing, not merely a surface
contradiction that Collapse could resolve.

Promotion criteria:
  1. The tension must involve claims that are hubs (appear in multiple tensions).
  2. The tension must have high tension_strength (semantic similarity in the
     productive-conflict band).
  3. The tension must be of type "polarity" OR be a "contradiction" that
     connects claims from different lineage families.

When promoted, a Paradox object is created with:
  - Poles derived from the tension's source claims
  - A new EmojiVector seeded with pole emojis and initial chaos
  - Links back to the source claims and tension

INVARIANT: Promotion does NOT resolve the tension. The tension remains "open".
The Paradox is an overlay that adds emoji-vector state on top of it.
"""

import logging
from typing import Dict, List, Optional, Tuple

from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.emoji_vector import EmojiVector
from SovereignNEXT.state.paradox import Paradox, Pole
from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.state.tension import Tension
from SovereignNEXT.operators.emoji_mutator import seed_initial_sequence

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Promotion thresholds
# ---------------------------------------------------------------------------

# Minimum number of tensions a claim must participate in to be a "hub"
HUB_TENSION_THRESHOLD = 3

# Minimum tension_strength for promotion eligibility
STRENGTH_THRESHOLD = 0.4

# Minimum number of distinct lineage roots across the tension's source claims
# for cross-family promotion of contradictions
CROSS_FAMILY_MIN_ROOTS = 2


# ---------------------------------------------------------------------------
# Emoji assignment for poles
# ---------------------------------------------------------------------------

# Default pole emojis when no domain-specific mapping is available
DEFAULT_POLE_A_EMOJI = "\u2694\ufe0f"   # ⚔️
DEFAULT_POLE_B_EMOJI = "\U0001f6e1\ufe0f"  # 🛡️


# ---------------------------------------------------------------------------
# Helper: find lineage root of a claim
# ---------------------------------------------------------------------------

def _find_root(claim_id: str, claims_by_id: Dict[str, Claim]) -> str:
    """Walk parent_id chain to find the root claim."""
    current_id = claim_id
    visited = set()
    while current_id in claims_by_id:
        claim = claims_by_id[current_id]
        if claim.parent_id is None or claim.parent_id in visited:
            return current_id
        visited.add(current_id)
        current_id = claim.parent_id
    return current_id


# ---------------------------------------------------------------------------
# Core promotion logic
# ---------------------------------------------------------------------------

def find_promotable_tensions(
    state: SystemState,
    hub_threshold: int = HUB_TENSION_THRESHOLD,
    strength_threshold: float = STRENGTH_THRESHOLD,
) -> List[Tension]:
    """Identify tensions eligible for promotion to Paradox.

    A tension is promotable if:
      1. It is still "open" (not already collapsed or held).
      2. It has no existing paradox (no emoji_vector_id set).
      3. At least one source claim is a hub (involved in >= hub_threshold tensions).
      4. tension_strength >= strength_threshold.
      5. Either:
         a. relation_type == "polarity", OR
         b. relation_type == "contradiction" AND source claims come from
            different lineage families (cross-family opposition).

    Returns list of promotable tensions, sorted by tension_strength descending.
    """
    # Build tension count per claim
    tension_count: Dict[str, int] = {}
    for t in state.tensions:
        for cid in t.source_claims:
            tension_count[cid] = tension_count.get(cid, 0) + 1

    # Build claims lookup
    claims_by_id = {c.id: c for c in state.claims}

    # Already-promoted tension IDs (tensions linked to existing paradoxes)
    promoted_tension_ids = set()
    for t in state.tensions:
        if t.emoji_vector_id is not None:
            promoted_tension_ids.add(t.id)

    promotable = []
    for t in state.tensions:
        # Skip non-open or already-promoted
        if t.status != "open":
            continue
        if t.emoji_vector_id is not None:
            continue
        if t.id in promoted_tension_ids:
            continue

        # Check strength
        if t.metrics.tension_strength < strength_threshold:
            continue

        # Check hub involvement
        has_hub = any(tension_count.get(cid, 0) >= hub_threshold for cid in t.source_claims)
        if not has_hub:
            continue

        # Check relation type
        if t.relation_type == "polarity":
            promotable.append(t)
        elif t.relation_type == "contradiction":
            # Cross-family check
            roots = set()
            for cid in t.source_claims:
                roots.add(_find_root(cid, claims_by_id))
            if len(roots) >= CROSS_FAMILY_MIN_ROOTS:
                promotable.append(t)

    # Sort by tension_strength descending
    promotable.sort(key=lambda t: t.metrics.tension_strength, reverse=True)

    logger.info(
        "Paradox promoter: %d promotable tensions from %d total",
        len(promotable), len(state.tensions),
    )
    return promotable


def promote_tension(
    tension: Tension,
    state: SystemState,
    pole_a_emoji: str = DEFAULT_POLE_A_EMOJI,
    pole_b_emoji: str = DEFAULT_POLE_B_EMOJI,
    seed: Optional[int] = None,
) -> Tuple[Paradox, EmojiVector]:
    """Promote a single tension to a Paradox with an associated EmojiVector.

    Creates:
      - An EmojiVector with a seeded initial sequence
      - A Paradox linking the two poles, the emoji vector, and the source claims

    Adds both to state. Sets tension.emoji_vector_id to link them.
    Does NOT change tension.status (remains "open").

    Args:
        tension: The tension to promote.
        state: SystemState to add the new objects to.
        pole_a_emoji: Emoji for pole A.
        pole_b_emoji: Emoji for pole B.
        seed: Optional RNG seed for reproducibility.

    Returns:
        (paradox, emoji_vector) tuple.
    """
    # Create EmojiVector
    sequence = seed_initial_sequence(pole_a_emoji, pole_b_emoji, seed=seed)
    ev = EmojiVector(
        sequence=sequence,
        pole_a_emoji=pole_a_emoji,
        pole_b_emoji=pole_b_emoji,
        role="paradox_field",
        related_claims=list(tension.source_claims),
        origin=f"promoted_from_{tension.id}",
    )

    # Create Paradox
    paradox = Paradox(
        pole_a=Pole(id=tension.pole_a[:50], emoji=pole_a_emoji),
        pole_b=Pole(id=tension.pole_b[:50], emoji=pole_b_emoji),
        status="open",
        emoji_vector_id=ev.id,
        claim_ids=list(tension.source_claims),
        mission_ids=[tension.mission_id] if tension.mission_id else [],
    )
    paradox.metrics.tension_strength = tension.metrics.tension_strength

    # Link tension to emoji vector
    tension.emoji_vector_id = ev.id

    # Record promotion event
    paradox.record_event(
        event="promoted_from_tension",
        operator="paradox_promoter",
        tension_id=tension.id,
        entropy=ev.entropy,
    )

    # Add to state
    state.add_emoji_field(ev)
    state.add_paradox(paradox)

    logger.info(
        "Promoted tension %s -> paradox %s (ev=%s, entropy=%.3f, chaos=%.3f)",
        tension.id, paradox.id, ev.id, ev.entropy, ev.chaos_index,
    )

    return paradox, ev


def promote_all_eligible(
    state: SystemState,
    max_promotions: int = 10,
    seed: Optional[int] = None,
) -> List[Tuple[Paradox, EmojiVector]]:
    """Find and promote all eligible tensions in one pass.

    Args:
        state: SystemState to analyze and mutate.
        max_promotions: Cap on promotions per call.
        seed: Optional RNG seed for reproducibility.

    Returns:
        List of (paradox, emoji_vector) tuples created.
    """
    promotable = find_promotable_tensions(state)
    results = []
    for t in promotable[:max_promotions]:
        result = promote_tension(t, state, seed=seed)
        results.append(result)

    logger.info(
        "Paradox promotion complete: %d new paradoxes, %d new emoji vectors",
        len(results), len(results),
    )
    return results
