"""
SovereignNEXT — Claim
An atomic proposition extracted from LLM output, with confidence, source, and tags.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


_claim_counter = 0


def _next_claim_id() -> str:
    global _claim_counter
    _claim_counter += 1
    return f"claim_{_claim_counter:04d}"


@dataclass
class Claim:
    """An atomic proposition in the system state."""

    text: str
    confidence: float = 0.5
    source: str = ""          # e.g. "collapse_M1", "become_M3"
    tags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    id: str = field(default_factory=_next_claim_id)

    # Optional back-references
    mission_id: Optional[str] = None
    operator: Optional[str] = None   # "collapse", "become", "sovereign"
    parent_id: Optional[str] = None  # Provenance: which claim this was expanded from

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "confidence": self.confidence,
            "source": self.source,
            "tags": self.tags,
            "timestamp": self.timestamp,
            "mission_id": self.mission_id,
            "operator": self.operator,
            "parent_id": self.parent_id,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Claim":
        return cls(
            text=d["text"],
            confidence=d.get("confidence", 0.5),
            source=d.get("source", ""),
            tags=d.get("tags", []),
            timestamp=d.get("timestamp", ""),
            id=d["id"],
            mission_id=d.get("mission_id"),
            operator=d.get("operator"),
            parent_id=d.get("parent_id"),
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Claim):
            return self.id == other.id
        return NotImplemented
