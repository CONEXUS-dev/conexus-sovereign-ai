"""SovereignNEXT State — Core data structures for the system state."""

from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.tension import Tension, TensionMetrics
from SovereignNEXT.state.paradox import Paradox, Pole, ParadoxMetrics
from SovereignNEXT.state.emoji_vector import (
    EmojiVector,
    compute_emoji_metrics,
    CHAOS_EMOJIS,
    STABLE_EMOJIS,
    SUPERPOSITION_EMOJIS,
)
from SovereignNEXT.state.system_state import SystemState, MemoryRef

__all__ = [
    "Claim",
    "Tension",
    "TensionMetrics",
    "Paradox",
    "Pole",
    "ParadoxMetrics",
    "EmojiVector",
    "compute_emoji_metrics",
    "CHAOS_EMOJIS",
    "STABLE_EMOJIS",
    "SUPERPOSITION_EMOJIS",
    "SystemState",
    "MemoryRef",
]
