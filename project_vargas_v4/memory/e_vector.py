# e_vector.py
"""
E-Vector System for V4 Architecture
Implements the 4-dimensional E-Vector from the blueprint specification.
"""

import numpy as np
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

@dataclass
class EVector:
    """E-Vector with 4 core dimensions from blueprint specification."""
    entropy_level: float = 0.5          # System complexity tolerance
    chaos_threshold: float = 0.5        # Contradiction tolerance
    challenge_threshold: float = 0.7    # Intervention readiness
    initiative_timer: float = 30.0      # Action timing (seconds)
    
    def __post_init__(self):
        """Ensure all values are within valid ranges."""
        self.entropy_level = np.clip(self.entropy_level, 0.0, 1.0)
        self.chaos_threshold = np.clip(self.chaos_threshold, 0.0, 1.0)
        self.challenge_threshold = np.clip(self.challenge_threshold, 0.0, 1.0)
        self.initiative_timer = np.clip(self.initiative_timer, 5.0, 300.0)  # 5s to 5min
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for storage/transmission."""
        return asdict(self)
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array for mathematical operations."""
        return np.array([
            self.entropy_level,
            self.chaos_threshold,
            self.challenge_threshold,
            self.initiative_timer / 300.0  # Normalize timer to 0-1 range
        ])
    
    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'EVector':
        """Create from numpy array (inverse of to_array)."""
        if len(arr) != 4:
            raise ValueError("E-Vector array must have exactly 4 elements")
        
        return cls(
            entropy_level=float(np.clip(arr[0], 0.0, 1.0)),
            chaos_threshold=float(np.clip(arr[1], 0.0, 1.0)),
            challenge_threshold=float(np.clip(arr[2], 0.0, 1.0)),
            initiative_timer=float(np.clip(arr[3] * 300.0, 5.0, 300.0))  # Denormalize timer
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EVector':
        """Create from dictionary."""
        return cls(
            entropy_level=float(data.get('entropy_level', 0.5)),
            chaos_threshold=float(data.get('chaos_threshold', 0.5)),
            challenge_threshold=float(data.get('challenge_threshold', 0.7)),
            initiative_timer=float(data.get('initiative_timer', 30.0))
        )
    
    def apply_delta(self, delta: Dict[str, float]) -> 'EVector':
        """Apply a delta to create a new E-Vector."""
        new_values = self.to_dict()
        
        for dim, delta_val in delta.items():
            if dim in new_values:
                if dim == 'initiative_timer':
                    # Special handling for timer (not normalized)
                    new_values[dim] = np.clip(new_values[dim] + delta_val, 5.0, 300.0)
                else:
                    # Normalized dimensions
                    new_values[dim] = np.clip(new_values[dim] + delta_val, 0.0, 1.0)
        
        return EVector(**new_values)
    
    def reset_to_baseline(self, baseline: 'EVector') -> 'EVector':
        """Reset to baseline values (for session reset)."""
        return EVector(
            entropy_level=baseline.entropy_level,
            chaos_threshold=baseline.chaos_threshold,
            challenge_threshold=baseline.challenge_threshold,
            initiative_timer=baseline.initiative_timer
        )

class EVectorSystem:
    """
    Manages E-Vector state and operations for V4 architecture.
    
    Handles:
    - E-Vector state management
    - Delta application and session reset
    - Calibration and validation
    - Logging and audit trails
    """
    
    def __init__(self, baseline_config: Optional[Dict[str, float]] = None):
        """Initialize with baseline configuration from sovereign state."""
        # Blueprint default baseline
        default_baseline = {
            "entropy_level": 0.5,
            "chaos_threshold": 0.5,
            "challenge_threshold": 0.7,
            "initiative_timer": 30.0
        }
        
        baseline_values = baseline_config or default_baseline
        self.baseline = EVector(**baseline_values)
        self.current = EVector(**baseline_values)
        
        # State tracking
        self.session_start = datetime.now(timezone.utc)
        self.delta_history: List[Dict[str, Any]] = []
        self.last_update = None
        
        logger.info(f"[E_VECTOR] System initialized with baseline: {self.baseline.to_dict()}")
    
    def apply_delta(self, delta: Dict[str, float], source: str = "unknown") -> bool:
        """
        Apply an E-Vector delta to current state.
        
        Args:
            delta: Dictionary of dimension changes
            source: Source of the delta (for logging)
            
        Returns:
            True if delta was applied, False if invalid
        """
        try:
            old_state = self.current.to_dict()
            self.current = self.current.apply_delta(delta)
            new_state = self.current.to_dict()
            
            # Log the change
            delta_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": source,
                "delta": delta,
                "old_state": old_state,
                "new_state": new_state,
                "session_age_seconds": (datetime.now(timezone.utc) - self.session_start).total_seconds()
            }
            
            self.delta_history.append(delta_entry)
            self.last_update = delta_entry["timestamp"]
            
            logger.info(f"[E_VECTOR] Delta applied from {source}: {delta}")
            return True
            
        except Exception as e:
            logger.error(f"[E_VECTOR] Failed to apply delta from {source}: {e}")
            return False
    
    def reset_to_baseline(self, reason: str = "session_end") -> EVector:
        """
        Reset current state to baseline (for session reset).
        
        Args:
            reason: Reason for reset (for logging)
            
        Returns:
            The new current state (baseline)
        """
        old_state = self.current.to_dict()
        self.current = self.current.reset_to_baseline(self.baseline)
        
        # Log the reset
        reset_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "reset_to_baseline",
            "reason": reason,
            "old_state": old_state,
            "new_state": self.current.to_dict(),
            "session_age_seconds": (datetime.now(timezone.utc) - self.session_start).total_seconds()
        }
        
        self.delta_history.append(reset_entry)
        self.last_update = reset_entry["timestamp"]
        
        logger.info(f"[E_VECTOR] Reset to baseline: {reason}")
        return self.current
    
    def get_current_state(self) -> EVector:
        """Get current E-Vector state."""
        return self.current
    
    def get_baseline(self) -> EVector:
        """Get baseline E-Vector."""
        return self.baseline
    
    def calculate_distance_from_baseline(self) -> float:
        """Calculate Euclidean distance from baseline."""
        current_array = self.current.to_array()
        baseline_array = self.baseline.to_array()
        return float(np.linalg.norm(current_array - baseline_array))
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get comprehensive state summary."""
        return {
            "current": self.current.to_dict(),
            "baseline": self.baseline.to_dict(),
            "distance_from_baseline": self.calculate_distance_from_baseline(),
            "session_start": self.session_start.isoformat(),
            "last_update": self.last_update,
            "total_deltas": len(self.delta_history),
            "session_age_seconds": (datetime.now(timezone.utc) - self.session_start).total_seconds()
        }
    
    def get_delta_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent delta history."""
        return self.delta_history[-limit:] if self.delta_history else []
    
    def validate_state(self) -> Dict[str, Any]:
        """Validate current E-Vector state."""
        current_dict = self.current.to_dict()
        baseline_dict = self.baseline.to_dict()
        
        validation_results = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check ranges
        for dim, value in current_dict.items():
            if dim == 'initiative_timer':
                if not (5.0 <= value <= 300.0):
                    validation_results["issues"].append(f"{dim} out of range: {value}")
                    validation_results["valid"] = False
            else:
                if not (0.0 <= value <= 1.0):
                    validation_results["issues"].append(f"{dim} out of range: {value}")
                    validation_results["valid"] = False
        
        # Check for extreme deviations from baseline
        for dim, current_val in current_dict.items():
            if dim == 'initiative_timer':
                baseline_val = baseline_dict[dim]
                deviation = abs(current_val - baseline_val) / baseline_val
                if deviation > 2.0:  # More than 200% deviation
                    validation_results["warnings"].append(f"{dim} extreme deviation: {deviation:.2f}x")
            else:
                baseline_val = baseline_dict[dim]
                deviation = abs(current_val - baseline_val)
                if deviation > 0.8:  # More than 0.8 absolute deviation
                    validation_results["warnings"].append(f"{dim} extreme deviation: {deviation:.3f}")
        
        return validation_results
    
    def calibrate_baseline(self, new_baseline: Dict[str, float], reason: str = "manual_calibration") -> bool:
        """
        Update baseline configuration.
        
        Args:
            new_baseline: New baseline values
            reason: Reason for calibration
            
        Returns:
            True if calibration successful
        """
        try:
            old_baseline = self.baseline.to_dict()
            self.baseline = EVector(**new_baseline)
            
            # Log the calibration
            calibration_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "baseline_calibration",
                "reason": reason,
                "old_baseline": old_baseline,
                "new_baseline": self.baseline.to_dict()
            }
            
            self.delta_history.append(calibration_entry)
            self.last_update = calibration_entry["timestamp"]
            
            logger.info(f"[E_VECTOR] Baseline calibrated: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"[E_VECTOR] Failed to calibrate baseline: {e}")
            return False
    
    def export_state(self) -> Dict[str, Any]:
        """Export complete state for persistence."""
        return {
            "baseline": self.baseline.to_dict(),
            "current": self.current.to_dict(),
            "session_start": self.session_start.isoformat(),
            "last_update": self.last_update,
            "delta_history": self.delta_history
        }
    
    def import_state(self, state_data: Dict[str, Any]) -> bool:
        """Import state from persisted data."""
        try:
            self.baseline = EVector.from_dict(state_data["baseline"])
            self.current = EVector.from_dict(state_data["current"])
            self.session_start = datetime.fromisoformat(state_data["session_start"])
            self.last_update = state_data.get("last_update")
            self.delta_history = state_data.get("delta_history", [])
            
            logger.info("[E_VECTOR] State imported successfully")
            return True
            
        except Exception as e:
            logger.error(f"[E_VECTOR] Failed to import state: {e}")
            return False
