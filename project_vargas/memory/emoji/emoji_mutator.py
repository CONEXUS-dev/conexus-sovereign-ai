"""
Project Vargas — Emoji Mutator
Copied from SovereignNEXT. Mutation rules for EmojiVector sequences.

INVARIANT: Mutation rules are the ONLY way to change an EmojiVector's
sequence. No operator may set metrics directly.

Mutation model:
  - Become appends chaos/superposition emojis (divergence pressure)
  - Collapse appends stable emojis (resolution pressure)
  - ParadoxHold appends superposition emojis (held-tension pressure)
"""

import random
from typing import List, Optional

from project_vargas.memory.emoji.emoji_vector import (
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
    """Append chaos and superposition emojis after a Become expansion pass."""
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
    """Append stable emojis after a Collapse commitment."""
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
    """Append superposition emojis after ParadoxHold maintains both poles."""
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
    """Dispatch mutation based on operator name."""
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
    """Create the initial emoji sequence when a new EmojiVector is born."""
    rng = random.Random(seed)
    pool = list(CHAOS_EMOJIS | SUPERPOSITION_EMOJIS)
    chaos_seed = [rng.choice(pool) for _ in range(initial_chaos)]
    return [pole_a_emoji, pole_b_emoji] + chaos_seed
