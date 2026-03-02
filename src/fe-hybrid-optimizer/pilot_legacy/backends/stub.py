"""
Stub Pilot - Deterministic mechanical pilot for testing
"""

import random
from typing import Dict, Any
from ..schema import IterationPacket, PilotDecision


class StubPilot:
    """
    Deterministic stub pilot for testing and baseline comparisons.
    
    Makes simple rule-based decisions without AI.
    Useful for:
    - Testing engine mechanics
    - Baseline comparisons
    - Replay validation
    """
    
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.calibrated = True  # Stub is always "calibrated"
    
    def decide(self, packet: IterationPacket) -> PilotDecision:
        """
        Make deterministic decision based on simple rules.
        
        Rules:
        - If stagnating (>10 steps), diversify
        - If overloaded, repair capacity
        - Otherwise, apply random operator
        """
        # Rule 1: High stagnation -> diversify
        if packet.stagnation_steps > 10:
            return PilotDecision(
                action='DIVERSIFY',
                rationale='Stub: High stagnation, diversifying'
            )
        
        # Rule 2: Overload -> repair
        if packet.overload > 0:
            return PilotDecision(
                action='REPAIR_CAPACITY',
                rationale='Stub: Capacity violation detected'
            )
        
        # Rule 3: Default -> random operator
        operators = ['swap', 'relocate', 'cross_exchange']
        operator = self.rng.choice(operators)
        
        return PilotDecision(
            action='APPLY_OPERATOR',
            operator=operator,
            rationale=f'Stub: Applying {operator}'
        )
    
    def calibrate(self, spec: str) -> Dict[str, Any]:
        """Stub always accepts calibration."""
        return {
            "calibrated": True,
            "spec_version": "CONEXUS-STEEL-04",
            "understood": "Stub pilot: deterministic rule-based decisions"
        }


if __name__ == "__main__":
    # Test stub pilot
    pilot = StubPilot(seed=42)
    
    # Test packet
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
        recent_moves=[],
        paradox_size=3,
        paradox_best_alt=1245.67,
        feasible=True,
        overload=0
    )
    
    decision = pilot.decide(packet)
    print("Stub Decision:")
    print(decision.to_json())
    
    # Test with stagnation
    packet.stagnation_steps = 15
    decision = pilot.decide(packet)
    print("\nWith stagnation:")
    print(decision.to_json())
    
    # Test with overload
    packet.stagnation_steps = 5
    packet.overload = 20
    decision = pilot.decide(packet)
    print("\nWith overload:")
    print(decision.to_json())
