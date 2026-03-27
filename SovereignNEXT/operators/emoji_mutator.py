"""
SovereignNEXT — Emoji Mutator
Mutation rules for EmojiVector sequences. Operators call these functions
to evolve an emoji vector's sequence after each pass. The sequence is the
source of truth; metrics are always recomputed from it.

INVARIANT (Pylo): Mutation rules are the ONLY way to change an EmojiVector's
sequence. No operator may set metrics directly. Metrics are pure functions
of the sequence (enforced by EmojiVector's @property design).

Mutation model:
  - Become appends chaos/superposition emojis (divergence pressure)
  - Collapse appends stable emojis (resolution pressure)
  - ParadoxHold appends superposition emojis (held-tension pressure)
"""

import random
from typing import List, Optional

from SovereignNEXT.state.emoji_vector import (
    CHAOS_EMOJIS,
    STABLE_EMOJIS,
    SUPERPOSITION_EMOJIS,
    EmojiVector,
)


# ---------------------------------------------------------------------------
# Mutation budgets (max emojis appended per operator call)
# ---------------------------------------------------------------------------

BECOME_MUTATION_BUDGET = 3
COLLAPSE_MUTATION_BUDGET = 2
PARADOXHOLD_MUTATION_BUDGET = 2


# ---------------------------------------------------------------------------
# Core mutation functions
# ---------------------------------------------------------------------------

def mutate_become(
    ev: EmojiVector,
    budget: int = BECOME_MUTATION_BUDGET,
    seed: Optional[int] = None,
) -> EmojiVector:
    """Append chaos and superposition emojis after a Become expansion pass.

    Become introduces divergence, so the mutation adds entropy and chaos
    to the emoji vector. This shifts the field away from stability and
    toward polarity-enabling conditions.

    Mutates ev.sequence in place and returns ev for chaining.
    """
    rng = random.Random(seed)
    pool = list(CHAOS_EMOJIS | SUPERPOSITION_EMOJIS)
    additions = [rng.choice(pool) for _ in range(budget)]
    ev.sequence.extend(additions)
    return ev


def mutate_collapse(
    ev: EmojiVector,
    budget: int = COLLAPSE_MUTATION_BUDGET,
    seed: Optional[int] = None,
) -> EmojiVector:
    """Append stable emojis after a Collapse commitment.

    Collapse resolves tension, so the mutation adds stability to the
    emoji vector. This shifts the field toward lower entropy and
    reduces polarity pressure.

    Mutates ev.sequence in place and returns ev for chaining.
    """
    rng = random.Random(seed)
    pool = list(STABLE_EMOJIS)
    additions = [rng.choice(pool) for _ in range(budget)]
    ev.sequence.extend(additions)
    return ev


def mutate_paradox_hold(
    ev: EmojiVector,
    budget: int = PARADOXHOLD_MUTATION_BUDGET,
    seed: Optional[int] = None,
) -> EmojiVector:
    """Append superposition emojis after ParadoxHold maintains both poles.

    ParadoxHold holds contradiction without resolving it, so the mutation
    adds superposition emojis that represent held duality. This maintains
    or increases entropy without adding pure chaos.

    Mutates ev.sequence in place and returns ev for chaining.
    """
    rng = random.Random(seed)
    pool = list(SUPERPOSITION_EMOJIS)
    additions = [rng.choice(pool) for _ in range(budget)]
    ev.sequence.extend(additions)
    return ev


# ---------------------------------------------------------------------------
# Compound mutations
# ---------------------------------------------------------------------------

def mutate_for_operator(
    ev: EmojiVector,
    operator: str,
    seed: Optional[int] = None,
) -> EmojiVector:
    """Dispatch mutation based on operator name.

    Args:
        ev: The EmojiVector to mutate.
        operator: One of "become", "collapse", "paradox_hold".
        seed: Optional RNG seed for reproducibility.

    Returns:
        The mutated EmojiVector (same object, mutated in place).

    Raises:
        ValueError: If operator is not recognized.
    """
    if operator == "become":
        return mutate_become(ev, seed=seed)
    elif operator == "collapse":
        return mutate_collapse(ev, seed=seed)
    elif operator == "paradox_hold":
        return mutate_paradox_hold(ev, seed=seed)
    else:
        raise ValueError(f"Unknown operator for emoji mutation: {operator!r}")


def seed_initial_sequence(
    pole_a_emoji: str,
    pole_b_emoji: str,
    initial_chaos: int = 2,
    seed: Optional[int] = None,
) -> List[str]:
    """Create the initial emoji sequence when a new EmojiVector is born.

    Starts with both pole emojis plus a small amount of chaos to ensure
    the field begins with nonzero entropy rather than a dead-stable state.

    Args:
        pole_a_emoji: The emoji representing pole A.
        pole_b_emoji: The emoji representing pole B.
        initial_chaos: Number of chaos/superposition emojis to seed.
        seed: Optional RNG seed for reproducibility.

    Returns:
        A new list suitable for EmojiVector.sequence.
    """
    rng = random.Random(seed)
    pool = list(CHAOS_EMOJIS | SUPERPOSITION_EMOJIS)
    chaos_seed = [rng.choice(pool) for _ in range(initial_chaos)]
    return [pole_a_emoji, pole_b_emoji] + chaos_seed
