"""
SovereignNEXT — SystemState
The central, inspectable internal state that all operators transform.

SystemState is a pure container with query helpers. It holds Claims, Tensions,
Paradoxes, EmojiFields, and MemoryRefs. No LLM calls, no routing logic,
no operator execution lives here.
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.tension import Tension
from SovereignNEXT.state.paradox import Paradox
from SovereignNEXT.state.emoji_vector import EmojiVector


@dataclass
class MemoryRef:
    """A pointer into episodic/semantic memory with integrity hash."""

    namespace: str          # "episodic", "semantic", etc.
    point_id: str           # Qdrant point ID
    memory_hash: str = ""   # SHA-256 of the stored text
    mission_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespace": self.namespace,
            "point_id": self.point_id,
            "memory_hash": self.memory_hash,
            "mission_id": self.mission_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MemoryRef":
        return cls(
            namespace=d.get("namespace", ""),
            point_id=d.get("point_id", ""),
            memory_hash=d.get("memory_hash", ""),
            mission_id=d.get("mission_id", ""),
            metadata=d.get("metadata", {}),
        )


@dataclass
class SystemState:
    """The shared internal state that all operators read and transform.

    S = { Claims C, Tensions T, Paradoxes P, EmojiFields E, MemoryRefs M }
    """

    claims: List[Claim] = field(default_factory=list)
    tensions: List[Tension] = field(default_factory=list)
    paradoxes: List[Paradox] = field(default_factory=list)
    emoji_fields: List[EmojiVector] = field(default_factory=list)
    memory_refs: List[MemoryRef] = field(default_factory=list)

    # Mission context
    mission_id: Optional[str] = None
    iteration: int = 0

    # ------------------------------------------------------------------
    # Claims
    # ------------------------------------------------------------------

    def add_claim(self, claim: Claim) -> None:
        self.claims.append(claim)

    def get_claim(self, claim_id: str) -> Optional[Claim]:
        for c in self.claims:
            if c.id == claim_id:
                return c
        return None

    def claims_by_operator(self, operator: str) -> List[Claim]:
        return [c for c in self.claims if c.operator == operator]

    def claims_above_confidence(self, threshold: float) -> List[Claim]:
        return [c for c in self.claims if c.confidence >= threshold]

    # ------------------------------------------------------------------
    # Tensions
    # ------------------------------------------------------------------

    def add_tension(self, tension: Tension) -> None:
        self.tensions.append(tension)

    def get_tension(self, tension_id: str) -> Optional[Tension]:
        for t in self.tensions:
            if t.id == tension_id:
                return t
        return None

    def open_tensions(self) -> List[Tension]:
        return [t for t in self.tensions if t.status == "open"]

    def high_priority_tensions(self, strength_threshold: float = 0.3) -> List[Tension]:
        """Tensions that are open and above the strength threshold."""
        return [
            t for t in self.tensions
            if t.status == "open" and t.metrics.tension_strength > strength_threshold
        ]

    # ------------------------------------------------------------------
    # Paradoxes
    # ------------------------------------------------------------------

    def add_paradox(self, paradox: Paradox) -> None:
        self.paradoxes.append(paradox)

    def get_paradox(self, paradox_id: str) -> Optional[Paradox]:
        for p in self.paradoxes:
            if p.id == paradox_id:
                return p
        return None

    def held_paradoxes(self) -> List[Paradox]:
        return [p for p in self.paradoxes if p.status == "paradox_held"]

    # ------------------------------------------------------------------
    # Emoji Fields
    # ------------------------------------------------------------------

    def add_emoji_field(self, ev: EmojiVector) -> None:
        self.emoji_fields.append(ev)

    def get_emoji_field(self, ev_id: str) -> Optional[EmojiVector]:
        for e in self.emoji_fields:
            if e.id == ev_id:
                return e
        return None

    # ------------------------------------------------------------------
    # Memory Refs
    # ------------------------------------------------------------------

    def add_memory_ref(self, ref: MemoryRef) -> None:
        self.memory_refs.append(ref)

    # ------------------------------------------------------------------
    # Summaries
    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """Quick overview of current state for logging/debugging."""
        return {
            "mission_id": self.mission_id,
            "iteration": self.iteration,
            "claims": len(self.claims),
            "tensions_total": len(self.tensions),
            "tensions_open": len(self.open_tensions()),
            "paradoxes_total": len(self.paradoxes),
            "paradoxes_held": len(self.held_paradoxes()),
            "emoji_fields": len(self.emoji_fields),
            "memory_refs": len(self.memory_refs),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "iteration": self.iteration,
            "claims": [c.to_dict() for c in self.claims],
            "tensions": [t.to_dict() for t in self.tensions],
            "paradoxes": [p.to_dict() for p in self.paradoxes],
            "emoji_fields": [e.to_dict() for e in self.emoji_fields],
            "memory_refs": [m.to_dict() for m in self.memory_refs],
        }

    def content_hash(self) -> str:
        """Compute SHA-256 hash of the full serialized state.

        This enables verifying that serialize -> deserialize -> re-serialize
        produces identical state (deterministic roundtrip).
        """
        canonical = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SystemState":
        """Deserialize a SystemState from a dict (e.g. JSON snapshot).

        Resets global ID counters to max IDs found in the loaded state
        so that new objects created after loading won't collide.
        """
        import SovereignNEXT.state.claim as _claim_mod
        import SovereignNEXT.state.tension as _tension_mod
        import SovereignNEXT.state.paradox as _paradox_mod
        import SovereignNEXT.state.emoji_vector as _ev_mod

        claims = [Claim.from_dict(c) for c in d.get("claims", [])]
        tensions = [Tension.from_dict(t) for t in d.get("tensions", [])]
        paradoxes = [Paradox.from_dict(p) for p in d.get("paradoxes", [])]
        emoji_fields = [EmojiVector.from_dict(e) for e in d.get("emoji_fields", [])]
        memory_refs = [MemoryRef.from_dict(m) for m in d.get("memory_refs", [])]

        # Reset global counters to max IDs to prevent collisions
        def _max_id(items, prefix):
            max_val = 0
            for item in items:
                try:
                    num = int(item.id.replace(prefix + "_", ""))
                    if num > max_val:
                        max_val = num
                except (ValueError, AttributeError):
                    pass
            return max_val

        _claim_mod._claim_counter = _max_id(claims, "claim")
        _tension_mod._tension_counter = _max_id(tensions, "tension")
        _paradox_mod._paradox_counter = _max_id(paradoxes, "paradox")
        _ev_mod._ev_counter = _max_id(emoji_fields, "ev")

        return cls(
            claims=claims,
            tensions=tensions,
            paradoxes=paradoxes,
            emoji_fields=emoji_fields,
            memory_refs=memory_refs,
            mission_id=d.get("mission_id"),
            iteration=d.get("iteration", 0),
        )
