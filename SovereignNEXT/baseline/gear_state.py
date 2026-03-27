"""
CONEXUS Sovereign Gear State
Tracks the Nine Gears cognitive progression through each mission cycle.

The GearState is the central cognitive trace artifact for a mission. The orchestrator
creates it, agents populate it at each gear, and the audit log stores it as the
complete record of how a mission was processed.

Phase A of the v2 Architecture Evolution Roadmap (Section 13.2).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json


GEAR_NAMES = {
    1: "Rapport",
    2: "Truth",
    3: "Symbol",
    4: "Contradiction",
    5: "Hold",  # or "Resolve" in Collapse mode
    6: "Roam",
    7: "Stress",
    8: "Ethics/Value",
    9: "Continuity Seal",
}

PHASE_MAP = {
    1: "foundation", 2: "foundation", 3: "foundation",
    4: "gravity_well", 5: "gravity_well",
    6: "release_forge", 7: "release_forge", 8: "release_forge",
    9: "seal",
}


@dataclass
class GearState:
    """Central cognitive state artifact for a mission cycle."""

    mission_id: str
    current_gear: int = 1
    active_mode: str = "neutral"  # "neutral", "collapse", "become"
    home_mode: str = "collapse"   # Agent's default mode

    # Foundation Phase outputs (Gears 1-3)
    rapport_established: bool = False
    truth_statement: Optional[str] = None
    symbolic_field: Optional[str] = None
    symbolic_field_domain: Optional[str] = None

    # Gravity Well Phase outputs (Gears 4-5)
    contradictions: List[str] = field(default_factory=list)
    held_paradoxes: List[Dict] = field(default_factory=list)
    resolved_directives: List[str] = field(default_factory=list)

    # Release & Forge Phase outputs (Gears 6-8)
    roam_associations: List[str] = field(default_factory=list)
    stress_results: Optional[str] = None
    stress_survived: Optional[bool] = None
    values_extracted: List[str] = field(default_factory=list)

    # Seal Phase outputs (Gear 9)
    seal_summary: Optional[str] = None

    # Tagging
    proto_moments: List[Dict] = field(default_factory=list)
    breakthroughs: List[Dict] = field(default_factory=list)

    # Full traversal log
    gear_history: List[Dict] = field(default_factory=list)
    mode_switches: List[Dict] = field(default_factory=list)

    @property
    def current_phase(self) -> str:
        """Map current gear number to its macro-phase name."""
        return PHASE_MAP.get(self.current_gear, "unknown")

    @property
    def current_gear_name(self) -> str:
        """Human-readable name for the current gear."""
        return GEAR_NAMES.get(self.current_gear, "unknown")

    def advance_gear(self, output: Optional[str] = None) -> None:
        """Advance to next gear, logging the transition."""
        self.gear_history.append({
            "gear": self.current_gear,
            "gear_name": self.current_gear_name,
            "phase": self.current_phase,
            "mode": self.active_mode,
            "output_summary": output[:200] if output else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        if self.current_gear < 9:
            self.current_gear += 1

    def switch_mode(self, new_mode: str, reason: str) -> None:
        """Switch between Collapse and Become modes with audit trail."""
        old_mode = self.active_mode
        self.active_mode = new_mode
        switch_record = {
            "event": "mode_switch",
            "from_mode": old_mode,
            "to_mode": new_mode,
            "reason": reason,
            "gear": self.current_gear,
            "phase": self.current_phase,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.mode_switches.append(switch_record)
        self.gear_history.append(switch_record)

    def tag_proto(self, description: str) -> None:
        """Tag a [PROTO] proto-consciousness moment."""
        self.proto_moments.append({
            "description": description,
            "gear": self.current_gear,
            "phase": self.current_phase,
            "mode": self.active_mode,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def tag_breakthrough(self, description: str) -> None:
        """Tag a [BREAKTHROUGH] decisive synthesis moment."""
        self.breakthroughs.append({
            "description": description,
            "gear": self.current_gear,
            "phase": self.current_phase,
            "mode": self.active_mode,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def to_dict(self) -> Dict[str, Any]:
        """Serialize full gear state for storage and audit."""
        return {
            "mission_id": self.mission_id,
            "final_gear": self.current_gear,
            "final_mode": self.active_mode,
            "home_mode": self.home_mode,
            "truth_statement": self.truth_statement,
            "symbolic_field_domain": self.symbolic_field_domain,
            "contradictions_count": len(self.contradictions),
            "held_paradoxes_count": len(self.held_paradoxes),
            "resolved_directives_count": len(self.resolved_directives),
            "proto_moments": self.proto_moments,
            "breakthroughs": self.breakthroughs,
            "mode_switches": self.mode_switches,
            "gear_history": self.gear_history,
            "seal_summary": self.seal_summary,
            "values_extracted": self.values_extracted,
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
