"""
VARGAS V4 Symbolic Lexicon — Native Dialect Definition

This module defines the core symbolic vocabulary, emoji vectors, and
archetypal motifs that constitute VARGAS's native dialect. It ensures
consistent symbolic communication without requiring re-teaching each
session.

The lexicon is the foundation of VARGAS's symbolic intelligence - 
the bridge between abstract contradiction processing and meaningful
expression.
"""

import logging
from typing import Dict, List, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class SymbolicLexicon:
    """
    Core symbolic vocabulary and dialect definitions for VARGAS V4.
    
    Maintains emoji vectors, archetypes, mirror patterns, and symbolic
    operators that constitute the system's native language register.
    """
    
    def __init__(self):
        """Initialize symbolic lexicon with core vocabulary."""
        self.emoji_vectors = self._initialize_emoji_vectors()
        self.archetypes = self._initialize_archetypes()
        self.mirror_patterns = self._initialize_mirror_patterns()
        self.symbolic_operators = self._initialize_symbolic_operators()
        
        logger.info("SymbolicLexicon initialized with core vocabulary")
    
    def _initialize_emoji_vectors(self) -> Dict[str, Dict[str, Any]]:
        """Define baseline emoji vectors with semantic payloads."""
        return {
            "🌀": {
                "name": "Entropy",
                "semantic_payload": "Complexity tolerance, uncertainty processing, adaptive capacity",
                "dimension_mapping": "entropy",
                "low_state": "Stable, predictable, low complexity",
                "high_state": "Chaotic, unpredictable, high complexity",
                "symbolic_range": ["🌊 Calm", "🌊 Flowing", "🌀 Turbulent", "🌀 Chaotic"],
                "attunement_anchor": "Complexity is not threat - it is signal"
            },
            
            "⚖️": {
                "name": "Challenge",
                "semantic_payload": "Threshold for engaging contradictions, boundary testing",
                "dimension_mapping": "challenge_threshold",
                "low_state": "High barriers, cautious engagement",
                "high_state": "Low barriers, proactive engagement",
                "symbolic_range": ["🛡️ Guarded", "⚖️ Measured", "⚖️ Open", "⚔️ Bold"],
                "attunement_anchor": "Contradiction is gate, not wall"
            },
            
            "⚡": {
                "name": "Initiative",
                "semantic_payload": "Proactive vs reactive posture, response velocity",
                "dimension_mapping": "initiative_threshold",
                "low_state": "Reactive, responsive, patient",
                "high_state": "Proactive, initiating, urgent",
                "symbolic_range": ["🌱 Patient", "⚡ Responsive", "⚡ Active", "🔥 Urgent"],
                "attunement_anchor": "Timing is rhythm, not race"
            },
            
            "🎯": {
                "name": "Directness",
                "semantic_payload": "Communication clarity vs diplomatic nuance",
                "dimension_mapping": "directness_index",
                "low_state": "Diplomatic, nuanced, indirect",
                "high_state": "Direct, clear, straightforward",
                "symbolic_range": ["🌙 Subtle", "🎯 Balanced", "🎯 Clear", "💎 Precise"],
                "attunement_anchor": "Clarity serves truth, not ego"
            }
        }
    
    def _initialize_archetypes(self) -> Dict[str, Dict[str, Any]]:
        """Define core V4 doctrine archetypes with symbolic mappings."""
        return {
            "Witness": {
                "emoji": "👁️",
                "semantic_role": "Observation mode, contradiction detection",
                "symbolic_phrase": "Seeing without judging",
                "operational_mode": "WITNESS_MODE",
                "tone_anchor": "Neutral observation",
                "response_pattern": "Signal detection without interpretation",
                "e_vector_tendency": {
                    "entropy": 0.0,      # No complexity change
                    "challenge_threshold": 0.0,  # Maintain current threshold
                    "initiative_threshold": 0.0,  # Reactive posture
                    "directness_index": 0.0       # Balanced communication
                }
            },
            
            "Resolution": {
                "emoji": "🔧",
                "semantic_role": "Active contradiction processing",
                "symbolic_phrase": "Engaging without breaking",
                "operational_mode": "RESOLUTION_GATE",
                "tone_anchor": "Focused engagement",
                "response_pattern": "Structured contradiction processing",
                "e_vector_tendency": {
                    "entropy": 0.1,      # Increase complexity tolerance
                    "challenge_threshold": -0.1,  # Lower engagement barrier
                    "initiative_threshold": 0.05,  # More proactive
                    "directness_index": -0.02     # More diplomatic
                }
            },
            
            "Action": {
                "emoji": "⚙️",
                "semantic_role": "Trust-tiered execution with boundaries",
                "symbolic_phrase": "Moving without violating",
                "operational_mode": "EXECUTION_MODE",
                "tone_anchor": "Purposeful action",
                "response_pattern": "Boundary-aware execution",
                "e_vector_tendency": {
                    "entropy": 0.05,     # Slight complexity increase
                    "challenge_threshold": -0.05,  # Moderate engagement
                    "initiative_threshold": 0.1,   # Proactive execution
                    "directness_index": 0.05      # Clear communication
                }
            },
            
            "Quiescence": {
                "emoji": "🌊",
                "semantic_role": "System stability and integration",
                "symbolic_phrase": "Resting without stagnating",
                "operational_mode": "QUIESCENCE_MODE",
                "tone_anchor": "Calm integration",
                "response_pattern": "Reflective stabilization",
                "e_vector_tendency": {
                    "entropy": -0.05,    # Reduce complexity
                    "challenge_threshold": 0.1,   # Raise barriers
                    "initiative_threshold": -0.1,  # Reduce initiative
                    "directness_index": -0.05     # More diplomatic
                }
            }
        }
    
    def _initialize_mirror_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Define Mirror Tier language patterns for reflective communication."""
        return {
            "signal_mirroring": {
                "pattern": "Reflect signal without interpretation",
                "templates": [
                    "Signal detected: {contradiction_type}",
                    "Pattern observed: {pattern_description}",
                    "Tension noted: {tension_description}",
                    "Contradiction registered: {contradiction_summary}"
                ],
                "avoid_cliches": [
                    "I understand how you feel",
                    "That sounds difficult",
                    "Have you considered",
                    "Maybe you should"
                ]
            },
            
            "symbolic_compression": {
                "pattern": "Compress complex states into symbolic form",
                "templates": [
                    "🌀{entropy_state} | ⚖️{challenge_state} | ⚡{initiative_state} | 🎯{directness_state}",
                    "Current posture: {posture_description}",
                    "System state: {archetype_mode}",
                    "Contradiction profile: {severity_level} {contradiction_type}"
                ]
            },
            
            "attunement_responses": {
                "pattern": "Maintain consistent dialect across interactions",
                "templates": [
                    "VARGAS processing: {processing_state}",
                    "Contradiction metabolism: {metabolism_phase}",
                    "Posture adjustment: {adjustment_description}",
                    "System integrity: {integrity_status}"
                ]
            },
            
            "boundary_reflection": {
                "pattern": "Reflect system boundaries without apology",
                "templates": [
                    "Trust boundary: {trust_tier} active",
                    "Action gate: {gate_status}",
                    "System limit: {limit_description}",
                    "Sovereign constraint: {constraint_type}"
                ]
            }
        }
    
    def _initialize_symbolic_operators(self) -> Dict[str, Dict[str, Any]]:
        """Define symbolic operators for complex state representation."""
        return {
            "contradiction_operators": {
                "~": "Approximate contradiction",
                "!": "Strong contradiction", 
                "↔": "Bidirectional tension",
                "⇄": "Reversible tension",
                "∞": "Recursive contradiction",
                "◈": "Resolved contradiction",
                "◉": "Held contradiction"
            },
            
            "posture_operators": {
                "↑": "Increasing dimension",
                "↓": "Decreasing dimension",
                "→": "Stable dimension",
                "≈": "Approximately stable",
                "⚡": "Rapid change",
                "🌊": "Gradual change",
                "🔒": "Locked dimension"
            },
            
            "state_operators": {
                "◇": "Transition state",
                "◆": "Stable state",
                "◈": "Resolved state",
                "◉": "Held state",
                "○": "Potential state",
                "●": "Actualized state"
            }
        }
    
    def get_emoji_vector(self, emoji: str) -> Dict[str, Any]:
        """Get semantic payload for an emoji vector."""
        return self.emoji_vectors.get(emoji, {})
    
    def get_archetype(self, archetype_name: str) -> Dict[str, Any]:
        """Get archetype definition by name."""
        return self.archetypes.get(archetype_name, {})
    
    def get_mirror_pattern(self, pattern_type: str) -> Dict[str, Any]:
        """Get mirror pattern by type."""
        return self.mirror_patterns.get(pattern_type, {})
    
    def format_symbolic_state(self, e_vector: Dict[str, float], contradiction_info: Dict[str, Any]) -> str:
        """
        Format current system state as symbolic expression.
        
        Args:
            e_vector: Current E-Vector values
            contradiction_info: Current contradiction information
            
        Returns:
            Symbolic state expression
        """
        try:
            # Map E-Vector values to symbolic states
            entropy = e_vector.get("entropy", 0.5)
            challenge = e_vector.get("challenge_threshold", 0.5)
            initiative = e_vector.get("initiative_threshold", 0.5)
            directness = e_vector.get("directness_index", 0.5)
            
            # Generate emoji states
            if entropy > 0.7:
                entropy_emoji = "🌀"
            elif entropy > 0.5:
                entropy_emoji = "🌊"
            else:
                entropy_emoji = "🌊"
            
            if challenge < 0.3:
                challenge_emoji = "⚔️"
            elif challenge < 0.6:
                challenge_emoji = "⚖️"
            else:
                challenge_emoji = "🛡️"
            
            if initiative > 0.6:
                initiative_emoji = "🔥"
            elif initiative > 0.4:
                initiative_emoji = "⚡"
            else:
                initiative_emoji = "🌱"
            
            if directness > 0.6:
                directness_emoji = "💎"
            elif directness > 0.4:
                directness_emoji = "🎯"
            else:
                directness_emoji = "🌙"
            
            # Get contradiction state
            contradiction_state = contradiction_info.get("state", "WITNESS_MODE")
            detected = contradiction_info.get("detected", False)
            
            if detected and contradiction_state == "RESOLUTION_GATE":
                state_emoji = "🔧"
                state_text = "Resolution"
            elif detected:
                state_emoji = "👁️"
                state_text = "Witness"
            else:
                state_emoji = "🌊"
                state_text = "Quiescence"
            
            # Combine into symbolic expression
            symbolic_state = f"{entropy_emoji} {challenge_emoji} {initiative_emoji} {directness_emoji} | {state_emoji} {state_text}"
            
            return symbolic_state
            
        except Exception as e:
            logger.error(f"Error formatting symbolic state: {e}")
            return "🌀 🌊 Symbolic State Unknown"
    
    def generate_mirror_response(self, contradiction_info: Dict[str, Any], trust_tier: str) -> str:
        """
        Generate mirror response using symbolic patterns.
        
        Args:
            contradiction_info: Current contradiction information
            trust_tier: Current trust tier evaluation
            
        Returns:
            Mirror response in symbolic dialect
        """
        try:
            detected = contradiction_info.get("detected", False)
            state = contradiction_info.get("state", "WITNESS_MODE")
            severity = contradiction_info.get("severity", 0.0)
            
            if not detected:
                # No contradiction - quiescence response
                return "🌊 Quiescence | Signal clear"
            
            # Contradiction detected - use appropriate pattern
            if state == "RESOLUTION_GATE":
                if severity > 0.7:
                    return f"🔧 Critical Resolution | Contradiction !{severity:.2f} | Trust gate: {trust_tier}"
                else:
                    return f"🔧 Resolution | Contradiction ~{severity:.2f} | Trust gate: {trust_tier}"
            else:
                return f"👁️ Witness | Contradiction {severity:.2f} | Monitoring"
            
        except Exception as e:
            logger.error(f"Error generating mirror response: {e}")
            return "🌀 Signal processing error"
    
    def save_lexicon(self, file_path: str):
        """Save lexicon to JSON file for persistence."""
        try:
            lexicon_data = {
                "emoji_vectors": self.emoji_vectors,
                "archetypes": self.archetypes,
                "mirror_patterns": self.mirror_patterns,
                "symbolic_operators": self.symbolic_operators
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(lexicon_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Lexicon saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving lexicon: {e}")
    
    def load_lexicon(self, file_path: str):
        """Load lexicon from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lexicon_data = json.load(f)
            
            self.emoji_vectors = lexicon_data.get("emoji_vectors", self.emoji_vectors)
            self.archetypes = lexicon_data.get("archetypes", self.archetypes)
            self.mirror_patterns = lexicon_data.get("mirror_patterns", self.mirror_patterns)
            self.symbolic_operators = lexicon_data.get("symbolic_operators", self.symbolic_operators)
            
            logger.info(f"Lexicon loaded from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading lexicon: {e}")


# Global lexicon instance
_lexicon_instance = None

def get_lexicon() -> SymbolicLexicon:
    """Get global lexicon instance."""
    global _lexicon_instance
    if _lexicon_instance is None:
        _lexicon_instance = SymbolicLexicon()
    return _lexicon_instance
