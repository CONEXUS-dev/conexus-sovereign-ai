"""
SovereignNEXT — Paradox
A stateful computational unit representing a tension held as "both/and" rather than
resolved to one pole. Paradox objects are the computational heart of SovereignNEXT.

Paradoxes carry their own emoji vector, metrics, history, and links.
History entries include raw rubric scores for forensic auditability (Pylo adjustment).
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


_paradox_counter = 0


def _next_paradox_id() -> str:
    global _paradox_counter
    _paradox_counter += 1
    return f"paradox_{_paradox_counter:04d}"


PARADOX_STATUSES = (
    "open",              # Tension identified but not yet held
    "collapsed_to_a",    # Collapse committed to pole A
    "collapsed_to_b",    # Collapse committed to pole B
    "paradox_held",      # ParadoxHold is active — both poles maintained
    "integrated",        # Sovereign resolved at a higher level
)


@dataclass
class Pole:
    """One side of a paradox."""

    id: str              # Semantic label, e.g. "autonomy"
    emoji: str = ""      # Pole-anchor emoji, e.g. "🧭"
    confidence: float = 0.5  # Independent pole confidence (0-1)

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "emoji": self.emoji, "confidence": self.confidence}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Pole":
        return cls(
            id=d["id"],
            emoji=d.get("emoji", ""),
            confidence=d.get("confidence", 0.5),
        )


@dataclass
class ParadoxConstraints:
    """Veto constraints that make paradox computationally binding.

    When collapse_veto is True, the Collapse operator must not commit
    any tension linked to this paradox, provided the associated emoji
    vector's entropy and pole_balance satisfy the thresholds below.
    """

    collapse_veto: bool = False
    veto_reason: str = ""
    entropy_threshold: float = 0.70
    balance_window: Tuple[float, float] = (0.35, 0.65)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "collapse_veto": self.collapse_veto,
            "veto_reason": self.veto_reason,
            "entropy_threshold": self.entropy_threshold,
            "balance_window": list(self.balance_window),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ParadoxConstraints":
        bw = d.get("balance_window", [0.35, 0.65])
        return cls(
            collapse_veto=d.get("collapse_veto", False),
            veto_reason=d.get("veto_reason", ""),
            entropy_threshold=d.get("entropy_threshold", 0.70),
            balance_window=tuple(bw) if isinstance(bw, list) else bw,
        )


@dataclass
class ParadoxMetrics:
    """Paradox-level metrics (distinct from emoji-vector metrics)."""

    tension_strength: float = 0.5      # How contradictory the poles are (0-1)
    resolution_pressure: float = 0.0   # How much Collapse wants to commit (0-1)
    paradox_stability: float = 0.0     # How well the paradox is being maintained (0-1)
    agent_divergence: float = 0.0      # How differently Collapse and Become treat this (0-1)

    def to_dict(self) -> Dict[str, float]:
        return {
            "tension_strength": self.tension_strength,
            "resolution_pressure": self.resolution_pressure,
            "paradox_stability": self.paradox_stability,
            "agent_divergence": self.agent_divergence,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, float]) -> "ParadoxMetrics":
        return cls(
            tension_strength=d.get("tension_strength", 0.5),
            resolution_pressure=d.get("resolution_pressure", 0.0),
            paradox_stability=d.get("paradox_stability", 0.0),
            agent_divergence=d.get("agent_divergence", 0.0),
        )


@dataclass
class Paradox:
    """A stateful computational unit representing a held dual-truth."""

    pole_a: Pole
    pole_b: Pole
    status: str = "open"  # One of PARADOX_STATUSES
    id: str = field(default_factory=_next_paradox_id)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Paradox-level metrics
    metrics: ParadoxMetrics = field(default_factory=ParadoxMetrics)

    # Veto constraints (Phase 5: moves veto authority into state)
    constraints: ParadoxConstraints = field(default_factory=ParadoxConstraints)

    # Associated emoji vector ID (the actual EmojiVector lives in SystemState.emoji_fields)
    emoji_vector_id: Optional[str] = None

    # Chronological record of all transformations
    history: List[Dict[str, Any]] = field(default_factory=list)

    # Rubric scores from Collapse evaluations (forensic auditability per Pylo)
    rubric_scores: List[Dict[str, Any]] = field(default_factory=list)

    # Links to other objects
    claim_ids: List[str] = field(default_factory=list)
    mission_ids: List[str] = field(default_factory=list)
    memory_hash: Optional[str] = None
    related_paradox_ids: List[str] = field(default_factory=list)

    def record_event(
        self, event: str, operator: str, entropy: Optional[float] = None, **kwargs: Any
    ) -> None:
        """Append an event to history."""
        entry: Dict[str, Any] = {
            "event": event,
            "operator": operator,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if entropy is not None:
            entry["entropy"] = entropy
        entry.update(kwargs)
        self.history.append(entry)

    def record_rubric(self, scores: Dict[str, Any], decision: str) -> None:
        """Log raw rubric scores for forensic auditability."""
        self.rubric_scores.append({
            "scores": scores,
            "decision": decision,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "poles": {
                "a": self.pole_a.to_dict(),
                "b": self.pole_b.to_dict(),
            },
            "status": self.status,
            "metrics": self.metrics.to_dict(),
            "constraints": self.constraints.to_dict(),
            "emoji_vector_id": self.emoji_vector_id,
            "history": self.history,
            "rubric_scores": self.rubric_scores,
            "links": {
                "claims": self.claim_ids,
                "missions": self.mission_ids,
                "memory_hash": self.memory_hash,
                "related_paradoxes": self.related_paradox_ids,
            },
            "timestamp": self.timestamp,
        }

    def content_hash(self) -> str:
        """Compute SHA-256 hash of the canonical serialized form.

        This enables snapshot integrity verification and forensic
        auditability. The hash covers all fields including constraints.
        """
        canonical = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Paradox":
        poles = d.get("poles", {})
        links = d.get("links", {})
        return cls(
            pole_a=Pole.from_dict(poles.get("a", {"id": ""})),
            pole_b=Pole.from_dict(poles.get("b", {"id": ""})),
            status=d.get("status", "open"),
            id=d["id"],
            timestamp=d.get("timestamp", ""),
            metrics=ParadoxMetrics.from_dict(d.get("metrics", {})),
            constraints=ParadoxConstraints.from_dict(d.get("constraints", {})),
            emoji_vector_id=d.get("emoji_vector_id"),
            history=d.get("history", []),
            rubric_scores=d.get("rubric_scores", []),
            claim_ids=links.get("claims", []),
            mission_ids=links.get("missions", []),
            memory_hash=links.get("memory_hash"),
            related_paradox_ids=links.get("related_paradoxes", []),
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Paradox):
            return self.id == other.id
        return NotImplemented
