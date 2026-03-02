"""
Anthropic Pilot - Claude backend for calibrated AI pilot
"""

import os
import json
from typing import Dict, Any, Optional
from ..schema import IterationPacket, PilotDecision
from ..calibration import CalibrationGate


class AnthropicPilot:
    """
    Claude-based pilot using Anthropic API.
    
    Requires ANTHROPIC_API_KEY environment variable.
    """
    
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        self.calibration_gate = CalibrationGate()
        self.calibrated = False
        
        # Import anthropic here to avoid dependency issues
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    def calibrate(self, spec: str) -> Dict[str, Any]:
        """
        Perform calibration handshake with Claude.
        """
        import anthropic
        
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"{spec}\n\nPlease respond with the calibration JSON to confirm you understand your role as a pilot."
                }
            ]
        )
        
        # Extract JSON from response
        response_text = message.content[0].text
        
        # Try to parse JSON from response
        try:
            # Look for JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                response_dict = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            raise ValueError(f"Failed to parse calibration response: {e}\nResponse: {response_text}")
        
        # Validate calibration
        is_calibrated, msg = self.calibration_gate.validate_calibration_response(response_dict)
        
        if not is_calibrated:
            raise RuntimeError(f"Calibration failed: {msg}")
        
        self.calibrated = True
        return response_dict
    
    def decide(self, packet: IterationPacket) -> PilotDecision:
        """
        Get decision from Claude pilot.
        """
        import anthropic
        
        if not self.calibrated:
            raise RuntimeError("Pilot not calibrated. Call calibrate() first.")
        
        # Build prompt
        prompt = f"""You are a calibrated VRP pilot operating under CONEXUS-STEEL-04.

Current iteration state:
{packet.to_json()}

Based on this state, make a steering decision. Respond with ONLY a JSON decision in this format:

{{
  "action": "APPLY_OPERATOR",
  "operator": "swap",
  "rationale": "Brief explanation"
}}

Allowed actions: APPLY_OPERATOR, FOCUS_ROUTE, REPAIR_CAPACITY, DIVERSIFY, INTENSIFY, STOP
Allowed operators: swap, relocate, cross_exchange

Remember: You are steering search, not solving VRP. Make structural decisions based on the state.
"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                decision_dict = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
            
            decision = PilotDecision.from_dict(decision_dict)
            return decision
            
        except Exception as e:
            # Fallback to safe default
            print(f"Warning: Pilot decision failed: {e}")
            return PilotDecision(
                action='APPLY_OPERATOR',
                operator='swap',
                rationale=f'Fallback due to error: {str(e)[:100]}'
            )


if __name__ == "__main__":
    # Test Anthropic pilot (requires API key)
    try:
        pilot = AnthropicPilot()
        
        # Calibrate
        print("Calibrating pilot...")
        spec = pilot.calibration_gate.get_calibration_prompt()
        response = pilot.calibrate(spec)
        print(f"Calibration response: {response}")
        
        # Test decision
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
        print("\nPilot Decision:")
        print(decision.to_json())
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("This is expected if ANTHROPIC_API_KEY is not set")
