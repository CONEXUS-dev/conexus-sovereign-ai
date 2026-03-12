"""
SovereignNEXT — Tension
An explicit contradiction or opposition between two poles (claims/concepts).
Tensions are the routing substrate — their metrics determine which operator acts next.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


_tension_counter = 0


def _next_tension_id() -> str:
    global _tension_counter
    _tension_counter += 1
    return f"tension_{_tension_counter:04d}"


RELATION_TYPES = ("contradiction", "tradeoff", "polarity", "uncertainty")

TENSION_STATUSES = (
    "open",              # Identified but not yet processed
    "collapsed_to_a",    # Collapse committed to pole A
    "collapsed_to_b",    # Collapse committed to pole B
    "paradox_held",      # ParadoxHold is active
    "integrated",        # Sovereign resolved at a higher level
    "skipped",           # Tension strength too low to process
)


@dataclass
class TensionMetrics:
    """Metrics that drive operator routing decisions."""

    tension_strength: float = 0.5      # How contradictory the poles are (0-1)
    resolution_pressure: float = 0.0   # How much Collapse wants to commit (0-1)
    divergence_pressure: float = 0.0   # How much Become wants to expand (0-1)
    agent_divergence: float = 0.0      # How differently Collapse and Become treat this (0-1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tension_strength": self.tension_strength,
            "resolution_pressure": self.resolution_pressure,
            "divergence_pressure": self.divergence_pressure,
            "agent_divergence": self.agent_divergence,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TensionMetrics":
        return cls(
            tension_strength=d.get("tension_strength", 0.5),
            resolution_pressure=d.get("resolution_pressure", 0.0),
            divergence_pressure=d.get("divergence_pressure", 0.0),
            agent_divergence=d.get("agent_divergence", 0.0),
        )


@dataclass
class Tension:
    """An explicit contradiction or opposition between two poles."""

    pole_a: str
    pole_b: str
    relation_type: str = "contradiction"  # One of RELATION_TYPES
    status: str = "open"                  # One of TENSION_STATUSES
    metrics: TensionMetrics = field(default_factory=TensionMetrics)
    id: str = field(default_factory=_next_tension_id)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Back-references
    source_claims: List[str] = field(default_factory=list)  # Claim IDs
    mission_id: Optional[str] = None
    emoji_vector_id: Optional[str] = None  # Link to associated EmojiVector

    # History of operator actions on this tension
    history: List[Dict[str, Any]] = field(default_factory=list)

    # Rubric scores from Collapse scoring (logged for forensic auditability per Pylo)
    rubric_scores: List[Dict[str, Any]] = field(default_factory=list)

    def record_event(self, event: str, operator: str, **kwargs: Any) -> None:
        """Append an event to history."""
        entry = {
            "event": event,
            "operator": operator,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
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
            "pole_a": self.pole_a,
            "pole_b": self.pole_b,
            "relation_type": self.relation_type,
            "status": self.status,
            "metrics": self.metrics.to_dict(),
            "source_claims": self.source_claims,
            "mission_id": self.mission_id,
            "emoji_vector_id": self.emoji_vector_id,
            "history": self.history,
            "rubric_scores": self.rubric_scores,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Tension":
        return cls(
            pole_a=d["pole_a"],
            pole_b=d["pole_b"],
            relation_type=d.get("relation_type", "contradiction"),
            status=d.get("status", "open"),
            metrics=TensionMetrics.from_dict(d.get("metrics", {})),
            id=d["id"],
            timestamp=d.get("timestamp", ""),
            source_claims=d.get("source_claims", []),
            mission_id=d.get("mission_id"),
            emoji_vector_id=d.get("emoji_vector_id"),
            history=d.get("history", []),
            rubric_scores=d.get("rubric_scores", []),
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Tension):
            return self.id == other.id
        return NotImplemented
