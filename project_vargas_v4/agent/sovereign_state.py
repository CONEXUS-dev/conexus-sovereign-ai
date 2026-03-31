# sovereign_state.py
"""
Sovereign State Management for Vargas V4
Handles sealed state verification, boot sequence, and quiescent mode.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class SovereignState:
    """Data class for sovereign state information"""
    version: str
    identity: Dict[str, Any]
    tone_rules: Dict[str, Any]
    challenge_ethics: Dict[str, Any]
    e_vector_baseline: Dict[str, Any]
    paradox_engine: Dict[str, Any]
    memory_constraints: Dict[str, Any]
    tool_gating: Dict[str, Any]
    failure_protocol: Dict[str, Any]
    governance_integration: Dict[str, Any]
    operational_constraints: Dict[str, Any]
    seal_metadata: Dict[str, Any]

class SovereignStateManager:
    """Manages sovereign state loading, verification, and runtime access"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.state_file = config_dir / "sovereign_state.json"
        self.hash_file = config_dir / "sovereign_state.sha256"
        self._state: Optional[SovereignState] = None
        self._quiescent_mode = False
        self._verification_failed = False
        
    def verify_and_load_state(self) -> bool:
        """
        Verify sovereign state hash and load state.
        Returns True if successful, False if verification failed (enters quiescent mode).
        """
        try:
            # Check if files exist
            if not self.state_file.exists():
                logger.error("Sovereign state file not found")
                self._enter_quiescent_mode("Missing sovereign_state.json")
                return False
                
            if not self.hash_file.exists():
                logger.error("Sovereign state hash file not found")
                self._enter_quiescent_mode("Missing sovereign_state.sha256")
                return False
            
            # Calculate actual hash
            actual_hash = self._calculate_file_hash(self.state_file)
            
            # Read expected hash
            expected_hash = self.hash_file.read_text().strip()
            
            # Verify hash
            if actual_hash != expected_hash:
                logger.error(f"Sovereign state hash mismatch: expected {expected_hash}, got {actual_hash}")
                self._enter_quiescent_mode("Hash verification failed")
                return False
            
            # Load and parse state
            state_data = json.loads(self.state_file.read_text())
            self._state = self._parse_state_data(state_data)
            
            logger.info("Sovereign state verified and loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading sovereign state: {e}")
            self._enter_quiescent_mode(f"State loading error: {e}")
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _parse_state_data(self, data: Dict[str, Any]) -> SovereignState:
        """Parse JSON data into SovereignState object"""
        return SovereignState(
            version=data["version"],
            identity=data["baseline_identity"],
            tone_rules=data["tone_rules"],
            challenge_ethics=data["challenge_ethics"],
            e_vector_baseline=data["e_vector_baseline"],
            paradox_engine=data["paradox_engine"],
            memory_constraints=data["memory_constraints"],
            tool_gating=data["tool_gating"],
            failure_protocol=data["failure_protocol"],
            governance_integration=data["governance_integration"],
            operational_constraints=data["operational_constraints"],
            seal_metadata=data["seal_metadata"]
        )
    
    def _enter_quiescent_mode(self, reason: str):
        """Enter quiescent mode due to state verification failure"""
        self._quiescent_mode = True
        self._verification_failed = True
        logger.warning(f"Entering quiescent mode: {reason}")
    
    def is_quiescent_mode(self) -> bool:
        """Check if system is in quiescent mode"""
        return self._quiescent_mode
    
    def get_state(self) -> Optional[SovereignState]:
        """Get loaded sovereign state (None if in quiescent mode)"""
        if self._quiescent_mode:
            return None
        return self._state
    
    def get_e_vector_baseline(self) -> Dict[str, float]:
        """Get E-Vector baseline values"""
        if self._quiescent_mode or not self._state:
            return {}
        return self._state.e_vector_baseline
    
    def get_tone_rules(self) -> Dict[str, Any]:
        """Get tone rules for response generation"""
        if self._quiescent_mode or not self._state:
            return {}
        return self._state.tone_rules
    
    def get_challenge_ethics(self) -> Dict[str, Any]:
        """Get challenge ethics configuration"""
        if self._quiescent_mode or not self._state:
            return {}
        return self._state.challenge_ethics
    
    def get_paradox_engine_config(self) -> Dict[str, Any]:
        """Get paradox engine configuration"""
        if self._quiescent_mode or not self._state:
            return {}
        return self._state.paradox_engine
    
    def get_tool_gating_config(self) -> Dict[str, Any]:
        """Get tool gating configuration"""
        if self._quiescent_mode or not self._state:
            return {}
        return self._state.tool_gating
    
    def get_operational_constraints(self) -> Dict[str, Any]:
        """Get operational constraints"""
        if self._quiescent_mode or not self._state:
            return {}
        return self._state.operational_constraints
    
    def validate_action_against_constraints(self, action_type: str, action_data: Dict[str, Any]) -> bool:
        """Validate if action complies with sovereign constraints"""
        if self._quiescent_mode:
            return False  # No actions allowed in quiescent mode
        
        constraints = self.get_operational_constraints()
        
        # Check workspace boundary
        if "workspace_boundary" in constraints:
            # This would be implemented based on specific action validation
            pass
        
        # Check tool gating requirements
        if action_type == "tool_execution":
            tool_gating = self.get_tool_gating_config()
            if tool_gating.get("write_actions_require_approval", True):
                if action_data.get("writes_state", False):
                    return False  # Requires approval
        
        return True
    
    def get_quiescent_status(self) -> Dict[str, Any]:
        """Get quiescent mode status information"""
        return {
            "quiescent_mode": self._quiescent_mode,
            "verification_failed": self._verification_failed,
            "state_loaded": self._state is not None,
            "reason": self._get_quiescent_reason()
        }
    
    def _get_quiescent_reason(self) -> str:
        """Get reason for quiescent mode entry"""
        if not self._quiescent_mode:
            return "Not in quiescent mode"
        if not self.state_file.exists():
            return "Missing sovereign_state.json"
        if not self.hash_file.exists():
            return "Missing sovereign_state.sha256"
        return "Hash verification failed or state loading error"

# Global instance for system-wide access
_sovereign_manager: Optional[SovereignStateManager] = None

def initialize_sovereign_state(config_dir: Path) -> SovereignStateManager:
    """Initialize sovereign state manager (called at system boot)"""
    global _sovereign_manager
    _sovereign_manager = SovereignStateManager(config_dir)
    _sovereign_manager.verify_and_load_state()
    return _sovereign_manager

def get_sovereign_manager() -> Optional[SovereignStateManager]:
    """Get global sovereign state manager instance"""
    return _sovereign_manager

def is_system_healthy() -> bool:
    """Check if system is healthy (not in quiescent mode)"""
    manager = get_sovereign_manager()
    return manager is not None and not manager.is_quiescent_mode()
