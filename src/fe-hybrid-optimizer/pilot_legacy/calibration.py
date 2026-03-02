"""
Calibration Gate - CONEXUS-STEEL-04 handshake protocol
"""

from typing import Optional


CONEXUS_STEEL_04_SPEC = """
# CONEXUS-STEEL-04: Calibrated Fleet Pilot Specification

## Core Principle
You are a PILOT, not a solver. You steer search, you don't compute it.

## Your Role
- Receive iteration packets (structured JSON state)
- Return strict JSON decisions from allowed action set
- Never manipulate routes directly
- Never output free text in production mode

## Allowed Actions
1. APPLY_OPERATOR - Request specific operator (swap, relocate, cross_exchange)
2. FOCUS_ROUTE - Direct search to specific routes
3. REPAIR_CAPACITY - Force capacity repair
4. DIVERSIFY - Pull from paradox buffer or reseed
5. INTENSIFY - Local search on best solution
6. STOP - Signal convergence

## Constraints
- All decisions must be valid JSON
- All parameters must be bounded
- No creativity outside action space
- Engine executes all mechanics deterministically

## Success Criteria
Your goal is to steer the deterministic engine into better regions of the search space
as complexity grows. You are not competing with OR-Tools on small problems.
You are demonstrating control advantage on complex problems.

## Calibration Handshake
To accept this specification, respond with:
{
  "calibrated": true,
  "spec_version": "CONEXUS-STEEL-04",
  "understood": "I am a pilot, not a solver. I steer search through strict JSON decisions."
}
"""


class CalibrationGate:
    """
    Enforces calibration handshake before allowing pilot control.
    """
    
    def __init__(self):
        self.calibrated = False
        self.spec_version = None
    
    def get_calibration_prompt(self) -> str:
        """Get calibration specification for pilot."""
        return CONEXUS_STEEL_04_SPEC
    
    def validate_calibration_response(self, response: dict) -> tuple[bool, str]:
        """
        Validate pilot's calibration response.
        
        Returns:
            (is_calibrated, message)
        """
        if not isinstance(response, dict):
            return False, "Calibration response must be a dictionary"
        
        if not response.get('calibrated', False):
            return False, "Pilot did not accept calibration"
        
        if response.get('spec_version') != 'CONEXUS-STEEL-04':
            return False, f"Invalid spec version: {response.get('spec_version')}"
        
        if 'understood' not in response:
            return False, "Pilot did not confirm understanding"
        
        self.calibrated = True
        self.spec_version = response.get('spec_version')
        
        return True, "Calibration successful"
    
    def is_calibrated(self) -> bool:
        """Check if pilot is calibrated."""
        return self.calibrated
    
    def require_calibration(self) -> None:
        """Raise error if not calibrated."""
        if not self.calibrated:
            raise RuntimeError(
                "Pilot not calibrated. Must complete CONEXUS-STEEL-04 handshake before control."
            )


if __name__ == "__main__":
    gate = CalibrationGate()
    
    print("Calibration Specification:")
    print(gate.get_calibration_prompt())
    
    # Test valid response
    valid_response = {
        "calibrated": True,
        "spec_version": "CONEXUS-STEEL-04",
        "understood": "I am a pilot, not a solver. I steer search through strict JSON decisions."
    }
    
    is_calibrated, msg = gate.validate_calibration_response(valid_response)
    print(f"\nValidation: {is_calibrated}")
    print(f"Message: {msg}")
    
    # Test invalid response
    gate2 = CalibrationGate()
    invalid_response = {
        "calibrated": True,
        "spec_version": "WRONG-VERSION"
    }
    
    is_calibrated, msg = gate2.validate_calibration_response(invalid_response)
    print(f"\nInvalid validation: {is_calibrated}")
    print(f"Message: {msg}")
