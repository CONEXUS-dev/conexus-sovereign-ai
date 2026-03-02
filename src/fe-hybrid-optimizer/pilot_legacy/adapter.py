"""
Pilot Adapter - Main interface for AI pilot control
"""

import json
from typing import Union, Optional
from .schema import IterationPacket, PilotDecision, validate_decision
from .calibration import CalibrationGate
from .backends.stub import StubPilot
from .backends.anthropic import AnthropicPilot
from .backends.openai import OpenAIPilot
from .backends.gemini import GeminiPilot


class PilotAdapter:
    """
    Main adapter for pilot control.
    
    Supports multiple backends:
    - stub: Deterministic rule-based pilot
    - anthropic: Claude
    - openai: GPT
    - gemini: Google Gemini
    
    Handles:
    - Backend selection
    - Calibration
    - Decision validation
    - Logging
    - Replay mode
    """
    
    def __init__(self, backend: str = 'stub', **kwargs):
        """
        Initialize pilot adapter.
        
        Args:
            backend: One of 'stub', 'anthropic', 'openai', 'gemini'
            **kwargs: Backend-specific parameters (model, api_key, seed)
        """
        self.backend_name = backend
        self.replay_mode = False
        self.replay_decisions = []
        self.replay_index = 0
        
        # Create backend
        if backend == 'stub':
            seed = kwargs.get('seed', 42)
            self.backend = StubPilot(seed=seed)
        elif backend == 'anthropic':
            model = kwargs.get('model', 'claude-3-5-sonnet-20241022')
            api_key = kwargs.get('api_key')
            self.backend = AnthropicPilot(model=model, api_key=api_key)
        elif backend == 'openai':
            model = kwargs.get('model', 'gpt-4')
            api_key = kwargs.get('api_key')
            self.backend = OpenAIPilot(model=model, api_key=api_key)
        elif backend == 'gemini':
            model = kwargs.get('model', 'gemini-pro')
            api_key = kwargs.get('api_key')
            self.backend = GeminiPilot(model=model, api_key=api_key)
        else:
            raise ValueError(f"Unknown backend: {backend}")
        
        self.calibration_gate = CalibrationGate()
    
    def calibrate(self) -> dict:
        """
        Perform calibration handshake.
        
        Returns:
            Calibration response dictionary
        """
        spec = self.calibration_gate.get_calibration_prompt()
        response = self.backend.calibrate(spec)
        
        is_calibrated, msg = self.calibration_gate.validate_calibration_response(response)
        
        if not is_calibrated:
            raise RuntimeError(f"Calibration failed: {msg}")
        
        return response
    
    def decide(self, packet: IterationPacket, log_file: Optional[str] = None) -> PilotDecision:
        """
        Get decision from pilot.
        
        In live mode: calls backend
        In replay mode: reads from replay trace
        
        Args:
            packet: Current iteration state
            log_file: Optional file to log decision to (JSONL format)
        
        Returns:
            Pilot decision
        """
        if self.replay_mode:
            # Replay mode: read from trace
            if self.replay_index >= len(self.replay_decisions):
                raise RuntimeError(f"Replay exhausted: index {self.replay_index} >= {len(self.replay_decisions)}")
            
            decision = self.replay_decisions[self.replay_index]
            self.replay_index += 1
            return decision
        
        # Live mode: call backend
        self.calibration_gate.require_calibration()
        
        decision = self.backend.decide(packet)
        
        # Validate decision
        is_valid, error_msg = validate_decision(decision)
        
        if not is_valid:
            print(f"Warning: Invalid decision from pilot: {error_msg}")
            print(f"Decision: {decision.to_dict()}")
            # Fallback to safe default
            decision = PilotDecision(
                action='APPLY_OPERATOR',
                operator='swap',
                rationale=f'Fallback: {error_msg}'
            )
        
        # Log decision if requested
        if log_file:
            log_entry = {
                'iteration': packet.iteration,
                'packet': packet.to_dict(),
                'decision': decision.to_dict()
            }
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        
        return decision
    
    def enable_replay(self, trace_file: str):
        """
        Enable replay mode from trace file.
        
        Args:
            trace_file: Path to pilot_trace.jsonl file
        """
        self.replay_mode = True
        self.replay_decisions = []
        self.replay_index = 0
        
        with open(trace_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                decision = PilotDecision.from_dict(entry['decision'])
                self.replay_decisions.append(decision)
        
        print(f"Replay mode enabled: {len(self.replay_decisions)} decisions loaded")
    
    def disable_replay(self):
        """Disable replay mode."""
        self.replay_mode = False
        self.replay_decisions = []
        self.replay_index = 0


if __name__ == "__main__":
    # Test adapter with stub backend
    adapter = PilotAdapter(backend='stub', seed=42)
    
    # Calibrate
    print("Calibrating...")
    response = adapter.calibrate()
    print(f"Calibration: {response}")
    
    # Test decision
    packet = IterationPacket(
        iteration=1,
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
    
    decision = adapter.decide(packet)
    print(f"\nDecision: {decision.to_json()}")
