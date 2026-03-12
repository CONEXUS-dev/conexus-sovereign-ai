"""
SovereignNEXT — EmojiVector
The contradiction substrate. Emoji vectors are dense symbolic fields that encode
tension, polarity, and ambiguity as non-linguistic control signals.

INVARIANT (Pylo): Emoji metrics are PURE FUNCTIONS. No operator may override
entropy, chaos, or stability directly — only via mutation rules in the operators layer.
"""

import hashlib
import json
import math
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, FrozenSet, List, Optional


# ---------------------------------------------------------------------------
# Curated emoji sets (tunable knobs)
# ---------------------------------------------------------------------------

CHAOS_EMOJIS: FrozenSet[str] = frozenset({
    "\U0001f32a\ufe0f",  # 🌪️
    "\U0001f300",         # 🌀
    "\U0001f32b\ufe0f",  # 🌫️
    "\u26a1",             # ⚡
    "\U0001f525",         # 🔥
    "\U0001f4a5",         # 💥
    "\U0001f30a",         # 🌊
    "\u26ab",             # ⚫
    "\U0001f573\ufe0f",  # 🕳️
})

STABLE_EMOJIS: FrozenSet[str] = frozenset({
    "\u2696\ufe0f",       # ⚖️
    "\U0001f9f1",         # 🧱
    "\U0001f3db\ufe0f",  # 🏛️
    "\U0001f512",         # 🔒
    "\U0001f6e1\ufe0f",  # 🛡️
    "\U0001f4d0",         # 📐
    "\U0001f9ee",         # 🧮
    "\u2693",             # ⚓
})

SUPERPOSITION_EMOJIS: FrozenSet[str] = frozenset({
    "\u267e\ufe0f",       # ♾️
    "\U0001f500",         # 🔀
    "\U0001f9ec",         # 🧬
    "\u262f\ufe0f",       # ☯️
    "\U0001fa9e",         # 🪞
    "\U0001f3ad",         # 🎭
})


# ---------------------------------------------------------------------------
# Pure metric computation (INVARIANT: no side effects)
# ---------------------------------------------------------------------------

def compute_emoji_metrics(
    sequence: List[str],
    pole_a_emoji: str,
    pole_b_emoji: str,
) -> Dict[str, float]:
    """Compute entropy, pole_balance, chaos_index, stability_index from an emoji sequence.

    This is a PURE FUNCTION. It reads the sequence and returns metrics.
    No operator may call this to override stored metrics — only mutation rules
    in the operators layer may update an EmojiVector's metrics by modifying
    the sequence and recomputing.
    """
    n = len(sequence)
    if n == 0:
        return {
            "entropy": 0.0,
            "pole_balance": 0.5,
            "chaos_index": 0.0,
            "stability_index": 1.0,
        }

    # Normalized Shannon entropy over unique emoji frequencies
    counts = Counter(sequence)
    probs = [c / n for c in counts.values()]
    max_entropy = math.log2(n) if n > 1 else 1.0
    raw_entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    entropy = raw_entropy / max_entropy if max_entropy > 0 else 0.0

    # Pole balance: 0 = all pole_a, 1 = all pole_b, 0.5 = balanced
    a_count = sequence.count(pole_a_emoji)
    b_count = sequence.count(pole_b_emoji)
    total_pole = a_count + b_count
    pole_balance = b_count / total_pole if total_pole > 0 else 0.5

    # Chaos index: fraction of chaos emojis
    chaos_count = sum(1 for e in sequence if e in CHAOS_EMOJIS)
    chaos_index = chaos_count / n

    # Stability index: fraction of stable emojis
    stable_count = sum(1 for e in sequence if e in STABLE_EMOJIS)
    stability_index = stable_count / n

    return {
        "entropy": round(entropy, 4),
        "pole_balance": round(pole_balance, 4),
        "chaos_index": round(chaos_index, 4),
        "stability_index": round(stability_index, 4),
    }


# ---------------------------------------------------------------------------
# EmojiVector dataclass
# ---------------------------------------------------------------------------

_ev_counter = 0


def _next_ev_id() -> str:
    global _ev_counter
    _ev_counter += 1
    return f"ev_{_ev_counter:04d}"


# Valid roles for emoji vectors
EV_ROLES = ("paradox_field", "mode_bias", "memory_signature")


@dataclass
class EmojiVector:
    """A contradiction field encoded as an emoji sequence with computed metrics.

    The sequence is the source of truth. Metrics are always derived from
    the sequence via compute_emoji_metrics() — they are never set directly.
    """

    sequence: List[str] = field(default_factory=list)
    pole_a_emoji: str = ""
    pole_b_emoji: str = ""
    role: str = "paradox_field"  # One of EV_ROLES
    id: str = field(default_factory=_next_ev_id)

    # Links to other objects
    paradox_id: Optional[str] = None
    related_claims: List[str] = field(default_factory=list)
    origin: str = ""  # e.g. "Become_expansion_M3"
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def length(self) -> int:
        return len(self.sequence)

    @property
    def metrics(self) -> Dict[str, float]:
        """Compute metrics from the current sequence. Always derived, never stored."""
        return compute_emoji_metrics(self.sequence, self.pole_a_emoji, self.pole_b_emoji)

    @property
    def entropy(self) -> float:
        return self.metrics["entropy"]

    @property
    def pole_balance(self) -> float:
        return self.metrics["pole_balance"]

    @property
    def chaos_index(self) -> float:
        return self.metrics["chaos_index"]

    @property
    def stability_index(self) -> float:
        return self.metrics["stability_index"]

    def to_dict(self) -> Dict[str, Any]:
        m = self.metrics
        return {
            "id": self.id,
            "role": self.role,
            "core": {
                "length": self.length,
                "sequence": self.sequence,
                "poles": {"a": self.pole_a_emoji, "b": self.pole_b_emoji},
            },
            "metrics": m,
            "links": {
                "paradox_id": self.paradox_id,
                "related_claims": self.related_claims,
                "origin": self.origin,
                "last_updated": self.last_updated,
            },
        }

    def content_hash(self) -> str:
        """Compute SHA-256 hash of the canonical serialized form.

        This enables snapshot integrity verification. The hash covers
        the sequence, poles, role, id, and links — everything needed
        to reconstruct this exact emoji vector.
        """
        canonical = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "EmojiVector":
        core = d.get("core", {})
        links = d.get("links", {})
        poles = core.get("poles", {})
        return cls(
            sequence=core.get("sequence", []),
            pole_a_emoji=poles.get("a", ""),
            pole_b_emoji=poles.get("b", ""),
            role=d.get("role", "paradox_field"),
            id=d["id"],
            paradox_id=links.get("paradox_id"),
            related_claims=links.get("related_claims", []),
            origin=links.get("origin", ""),
            last_updated=links.get("last_updated", ""),
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EmojiVector):
            return self.id == other.id
        return NotImplemented
