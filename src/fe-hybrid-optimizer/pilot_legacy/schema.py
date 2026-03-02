"""
Pilot Schema - Strict JSON schemas for iteration packets and decisions
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json


@dataclass
class IterationPacket:
    """
    Structured state summary sent to pilot each iteration.
    
    This is the ONLY information the pilot receives.
    Pilot never sees raw routes or coordinates.
    """
    
    iteration: int
    best_distance: float
    route_count: int
    
    # Load statistics
    loads_min: int
    loads_max: int
    loads_mean: float
    loads_top_5: List[int]
    
    # Capacity info
    capacity_slack: int
    routes_near_capacity: int
    
    # Search state
    stagnation_steps: int
    recent_moves: List[Dict[str, Any]]
    
    # Paradox buffer
    paradox_size: int
    paradox_best_alt: Optional[float]
    
    # Feasibility
    feasible: bool
    overload: int
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class PilotDecision:
    """
    Strict JSON decision from pilot.
    
    Pilot can only select from allowed actions with bounded parameters.
    """
    
    action: str  # One of: APPLY_OPERATOR, FOCUS_ROUTE, REPAIR_CAPACITY, DIVERSIFY, INTENSIFY, STOP
    
    # Action-specific parameters
    operator: Optional[str] = None  # For APPLY_OPERATOR: swap, relocate, cross_exchange
    target_routes: Optional[List[int]] = None  # For FOCUS_ROUTE
    intensity: float = 0.5  # For INTENSIFY: 0.0-1.0
    
    # Rationale (optional, for logging only)
    rationale: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PilotDecision':
        """Create from dictionary."""
        return cls(
            action=data['action'],
            operator=data.get('operator'),
            target_routes=data.get('target_routes'),
            intensity=data.get('intensity', 0.5),
            rationale=data.get('rationale', '')
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PilotDecision':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


# Allowed actions
ALLOWED_ACTIONS = {
    'APPLY_OPERATOR',
    'FOCUS_ROUTE',
    'REPAIR_CAPACITY',
    'DIVERSIFY',
    'INTENSIFY',
    'STOP'
}

# Allowed operators
ALLOWED_OPERATORS = {
    'swap',
    'relocate',
    'cross_exchange'
}


def validate_decision(decision: PilotDecision) -> tuple[bool, str]:
    """
    Validate pilot decision against schema.
    
    Returns:
        (is_valid, error_message)
    """
    # Check action is allowed
    if decision.action not in ALLOWED_ACTIONS:
        return False, f"Invalid action '{decision.action}'. Must be one of {ALLOWED_ACTIONS}"
    
    # Validate action-specific parameters
    if decision.action == 'APPLY_OPERATOR':
        if decision.operator is None:
            return False, "APPLY_OPERATOR requires 'operator' parameter"
        if decision.operator not in ALLOWED_OPERATORS:
            return False, f"Invalid operator '{decision.operator}'. Must be one of {ALLOWED_OPERATORS}"
    
    if decision.action == 'FOCUS_ROUTE':
        if decision.target_routes is None or len(decision.target_routes) == 0:
            return False, "FOCUS_ROUTE requires 'target_routes' parameter"
    
    if decision.action == 'INTENSIFY':
        if not (0.0 <= decision.intensity <= 1.0):
            return False, f"Intensity must be in [0.0, 1.0], got {decision.intensity}"
    
    return True, ""


if __name__ == "__main__":
    # Test packet creation
    packet = IterationPacket(
        iteration=10,
        best_distance=1234.56,
        route_count=5,
        loads_min=45,
        loads_max=98,
        loads_mean=72.3,
        loads_top_5=[98, 95, 92, 88, 85],
        capacity_slack=123,
        routes_near_capacity=3,
        stagnation_steps=8,
        recent_moves=[
            {'op': 'swap', 'delta': -12.3, 'accepted': True},
            {'op': 'relocate', 'delta': 5.6, 'accepted': False}
        ],
        paradox_size=3,
        paradox_best_alt=1245.67,
        feasible=True,
        overload=0
    )
    
    print("Iteration Packet:")
    print(packet.to_json())
    
    # Test decision creation
    decision = PilotDecision(
        action='APPLY_OPERATOR',
        operator='swap',
        rationale='High stagnation, trying swap'
    )
    
    print("\nPilot Decision:")
    print(decision.to_json())
    
    # Test validation
    is_valid, msg = validate_decision(decision)
    print(f"\nValidation: {is_valid}")
    if not is_valid:
        print(f"Error: {msg}")
