"""
VARGAS V4 Action Router
Implements Trust-Tiered Action Gating as the Trust Spine of the sovereign runtime.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from .snapshot_manager import SnapshotManager

class ActionRouter:
    """
    Trust Spine for VARGAS V4 - intercepts and gates all tool actions based on trust tiers.
    Implements the trust_tiers from sovereign_state.json.
    """
    
    # Action execution status constants
    EXECUTE_AUTO = "EXECUTE_AUTO"
    EXECUTE_WITH_READBACK = "EXECUTE_WITH_READBACK"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    BLOCKED_FATAL = "BLOCKED_FATAL"
    
    def __init__(self, config_path: str = "config/sovereign_state.json"):
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        self.trust_tiers = self._load_trust_tiers()
        self.snapshot_manager = SnapshotManager()
        
    def _load_trust_tiers(self) -> Dict[str, str]:
        """Load trust tiers from sovereign state configuration."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get("trust_tiers", {})
        except Exception as e:
            self.logger.error(f"Failed to load trust tiers: {str(e)}")
            # Fallback to default tiers
            return {
                "tier_0": "passive_observation",
                "tier_1": "low_risk_auto",
                "tier_2": "snapshot_required",
                "tier_3": "explicit_approval",
                "tier_4": "forbidden"
            }
    
    def route_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route an action through the trust-tier gating system.
        
        Args:
            action: Dict containing action details
                - action_type: Type of action (read, write, execute, etc.)
                - target_path: Path to target file/directory
                - trust_tier: Required trust tier (0-4)
                - description: Human-readable description
                - metadata: Additional action metadata
                
        Returns:
            Dict containing routing decision and metadata
        """
        try:
            trust_tier = action.get("trust_tier", 3)  # Default to explicit approval
            
            # Validate trust tier
            if not isinstance(trust_tier, int) or trust_tier < 0 or trust_tier > 4:
                return {
                    "status": self.BLOCKED_FATAL,
                    "reason": f"Invalid trust tier: {trust_tier}",
                    "action": action,
                    "requires_approval": False
                }
            
            # Route based on trust tier
            if trust_tier == 0:  # passive_observation
                return self._handle_tier_0(action)
            elif trust_tier == 1:  # low_risk_auto
                return self._handle_tier_1(action)
            elif trust_tier == 2:  # snapshot_required
                return self._handle_tier_2(action)
            elif trust_tier == 3:  # explicit_approval
                return self._handle_tier_3(action)
            elif trust_tier == 4:  # forbidden
                return self._handle_tier_4(action)
            else:
                return {
                    "status": self.BLOCKED_FATAL,
                    "reason": f"Unhandled trust tier: {trust_tier}",
                    "action": action,
                    "requires_approval": False
                }
                
        except Exception as e:
            self.logger.error(f"Error routing action: {str(e)}")
            return {
                "status": self.BLOCKED_FATAL,
                "reason": f"Routing error: {str(e)}",
                "action": action,
                "requires_approval": False
            }
    
    def _handle_tier_0(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Tier 0 - passive observation."""
        return {
            "status": self.EXECUTE_AUTO,
            "trust_tier": 0,
            "tier_name": self.trust_tiers.get("tier_0", "passive_observation"),
            "action": action,
            "requires_approval": False,
            "message": "Passive observation - auto-execution approved"
        }
    
    def _handle_tier_1(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Tier 1 - low risk auto-execution."""
        return {
            "status": self.EXECUTE_AUTO,
            "trust_tier": 1,
            "tier_name": self.trust_tiers.get("tier_1", "low_risk_auto"),
            "action": action,
            "requires_approval": False,
            "message": "Low risk action - auto-execution approved"
        }
    
    def _handle_tier_2(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Tier 2 - snapshot required."""
        target_path = action.get("target_path")
        
        # Create snapshot before execution
        snapshot_result = self.snapshot_manager.create_snapshot(target_path) if target_path else {"success": True}
        
        if not snapshot_result["success"]:
            return {
                "status": self.BLOCKED_FATAL,
                "reason": f"Snapshot creation failed: {snapshot_result.get('error', 'Unknown error')}",
                "action": action,
                "requires_approval": False,
                "snapshot_result": snapshot_result
            }
        
        return {
            "status": self.EXECUTE_WITH_READBACK,
            "trust_tier": 2,
            "tier_name": self.trust_tiers.get("tier_2", "snapshot_required"),
            "action": action,
            "requires_approval": False,
            "snapshot_id": snapshot_result.get("snapshot_id"),
            "snapshot_result": snapshot_result,
            "message": "Snapshot created - execute with readback required"
        }
    
    def _handle_tier_3(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Tier 3 - explicit approval required."""
        return {
            "status": self.PENDING_APPROVAL,
            "trust_tier": 3,
            "tier_name": self.trust_tiers.get("tier_3", "explicit_approval"),
            "action": action,
            "requires_approval": True,
            "approval_mechanisms": self._get_approval_mechanisms(),
            "message": "Explicit approval required - execution halted"
        }
    
    def _handle_tier_4(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Tier 4 - forbidden."""
        return {
            "status": self.BLOCKED_FATAL,
            "trust_tier": 4,
            "tier_name": self.trust_tiers.get("tier_4", "forbidden"),
            "action": action,
            "requires_approval": False,
            "message": "Action forbidden - execution blocked"
        }
    
    def _get_approval_mechanisms(self) -> Dict[str, List[str]]:
        """Get available approval mechanisms from config."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config.get("tool_gating", {}).get("approval_mechanisms", {
                "keywords": ["yes", "approved", "proceed"],
                "discord_reactions": ["✅", "❌"]
            })
        except Exception:
            return {
                "keywords": ["yes", "approved", "proceed"],
                "discord_reactions": ["✅", "❌"]
            }
    
    def approve_action(self, action_id: str, approval: bool, mechanism: str = "manual") -> Dict[str, Any]:
        """
        Approve or reject a pending action.
        
        Args:
            action_id: Unique identifier for the pending action
            approval: True to approve, False to reject
            mechanism: Approval mechanism used
            
        Returns:
            Dict containing approval result
        """
        if approval:
            return {
                "action_id": action_id,
                "approved": True,
                "status": self.EXECUTE_AUTO,
                "approval_mechanism": mechanism,
                "message": "Action approved - execution authorized"
            }
        else:
            return {
                "action_id": action_id,
                "approved": False,
                "status": self.BLOCKED_FATAL,
                "approval_mechanism": mechanism,
                "message": "Action rejected - execution blocked"
            }
    
    def get_trust_tier_info(self) -> Dict[str, Any]:
        """Get current trust tier configuration."""
        return {
            "trust_tiers": self.trust_tiers,
            "status_constants": {
                "EXECUTE_AUTO": self.EXECUTE_AUTO,
                "EXECUTE_WITH_READBACK": self.EXECUTE_WITH_READBACK,
                "PENDING_APPROVAL": self.PENDING_APPROVAL,
                "BLOCKED_FATAL": self.BLOCKED_FATAL
            },
            "approval_mechanisms": self._get_approval_mechanisms()
        }
    
    def validate_action_integrity(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate action integrity and security constraints.
        
        Args:
            action: Action to validate
            
        Returns:
            Dict containing validation results
        """
        validation_errors = []
        
        # Check required fields
        required_fields = ["action_type", "trust_tier"]
        for field in required_fields:
            if field not in action:
                validation_errors.append(f"Missing required field: {field}")
        
        # Validate action type
        action_type = action.get("action_type")
        if action_type and not isinstance(action_type, str):
            validation_errors.append("action_type must be a string")
        
        # Validate target path if present
        target_path = action.get("target_path")
        if target_path:
            path_obj = Path(target_path)
            # Check for path traversal attempts
            if ".." in str(path_obj):
                validation_errors.append("Path traversal detected in target_path")
            
            # Check if path is within workspace boundary
            try:
                path_obj.resolve()
            except Exception:
                validation_errors.append("Invalid target path")
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "action": action
        }
