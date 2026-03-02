"""
OpenAI Pilot - GPT backend for calibrated AI pilot
"""

import os
import json
from typing import Dict, Any, Optional
from ..schema import IterationPacket, PilotDecision
from ..calibration import CalibrationGate


class OpenAIPilot:
    """
    GPT-based pilot using OpenAI API.
    
    Requires OPENAI_API_KEY environment variable.
    """
    
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.calibration_gate = CalibrationGate()
        self.calibrated = False
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def calibrate(self, spec: str) -> Dict[str, Any]:
        """Perform calibration handshake with GPT."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"{spec}\n\nPlease respond with the calibration JSON to confirm you understand your role as a pilot."
                }
            ],
            temperature=0
        )
        
        response_text = response.choices[0].message.content
        
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                response_dict = json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            raise ValueError(f"Failed to parse calibration response: {e}\nResponse: {response_text}")
        
        is_calibrated, msg = self.calibration_gate.validate_calibration_response(response_dict)
        
        if not is_calibrated:
            raise RuntimeError(f"Calibration failed: {msg}")
        
        self.calibrated = True
        return response_dict
    
    def decide(self, packet: IterationPacket) -> PilotDecision:
        """Get decision from GPT pilot."""
        if not self.calibrated:
            raise RuntimeError("Pilot not calibrated. Call calibrate() first.")
        
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            
            response_text = response.choices[0].message.content
            
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
            print(f"Warning: Pilot decision failed: {e}")
            return PilotDecision(
                action='APPLY_OPERATOR',
                operator='swap',
                rationale=f'Fallback due to error: {str(e)[:100]}'
            )
