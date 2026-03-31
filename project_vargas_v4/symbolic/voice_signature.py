"""
VARGAS V4 Voice Signature — Partner Stance Implementation

Enforces the Master Blueprint voice constraints and establishes the Partner Stance.
The voice signature ensures VARGAS sounds like a collaborator, not a chatbot,
while maintaining direct, calm, precise communication.

Voice constraints from sovereign_state.json:
- No exclamation points, therapeutic language, pastoral framing
- No motivational clichés or empathy performance
- Direct, calm, unhurried, minimal metaphor

Partner Stance characteristics:
- Collaborative and action-capable
- Willing to challenge from evidence
- Not moralizing or domineering
- Addresses user as Derek Angell when appropriate
"""

import logging
import re
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VoiceSignature:
    """Implements VARGAS V4 Partner Stance voice signature.
    
    Enforces voice constraints and generates responses that sound like
    a collaborator rather than a chatbot. Handles user identification
    and forensic em dash usage.
    """
    
    def __init__(self, sovereign_config: Dict[str, Any]):
        """Initialize voice signature with sovereign constraints.
        
        Args:
            sovereign_config: The loaded sovereign_state.json configuration.
        """
        self.config = sovereign_config
        self.tone_rules = sovereign_config.get("tone_rules", {})
        self.challenge_ethics = sovereign_config.get("challenge_ethics", {})
        
        # Compile forbidden patterns for efficiency
        self._compile_forbidden_patterns()
        
        logger.info("[VOICE_SIGNATURE] Partner Stance initialized")
    
    def _compile_forbidden_patterns(self):
        """Pre-compile regex patterns for forbidden language."""
        self.forbidden_patterns = {
            'exclamation': re.compile(r'!'),
            'therapeutic': re.compile(r'\b(feel|feeling|emotional|therapy|therapist|heal|healing|process|journey)\b', re.IGNORECASE),
            'pastoral': re.compile(r'\b(soul|spiritual|blessing|grace|faith|pray|meditate)\b', re.IGNORECASE),
            'motivational': re.compile(r'\b(inspire|motivate|empower|transform|growth|potential)\b', re.IGNORECASE),
            'empathy_performance': re.compile(r'\b(I understand|I feel|I relate|I hear you)\b', re.IGNORECASE),
        }
    
    def apply_voice_constraints(self, text: str) -> str:
        """Apply voice constraints to clean up generated text.
        
        Args:
            text: Raw text to be constrained.
            
        Returns:
            Text with voice constraints applied.
        """
        if not text:
            return text
        
        # Remove exclamation points
        text = self.forbidden_patterns['exclamation'].sub('.', text)
        
        # Remove therapeutic language
        text = self._remove_forbidden_category(text, 'therapeutic')
        
        # Remove pastoral framing
        text = self._remove_forbidden_category(text, 'pastoral')
        
        # Remove motivational clichés
        text = self._remove_forbidden_category(text, 'motivational')
        
        # Remove empathy performance
        text = self._remove_forbidden_category(text, 'empathy_performance')
        
        # Clean up extra whitespace and punctuation
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\.{2,}', '.', text)
        
        return text
    
    def _remove_forbidden_category(self, text: str, category: str) -> str:
        """Remove a specific category of forbidden language.
        
        Args:
            text: Text to clean.
            category: Category key from forbidden_patterns.
            
        Returns:
            Text with category removed and sentence restructured.
        """
        pattern = self.forbidden_patterns[category]
        matches = list(pattern.finditer(text))
        
        if not matches:
            return text
        
        # Replace forbidden terms with more direct alternatives
        replacements = {
            'therapeutic': {
                'feel': 'observe',
                'feeling': 'observation',
                'emotional': 'situational',
                'therapy': 'analysis',
                'process': 'sequence',
                'journey': 'progression'
            },
            'pastoral': {
                'soul': 'identity',
                'spiritual': 'fundamental',
                'blessing': 'advantage',
                'grace': 'efficiency',
                'faith': 'confidence',
                'pray': 'consider',
                'meditate': 'reflect'
            },
            'motivational': {
                'inspire': 'enable',
                'motivate': 'prompt',
                'empower': 'enable',
                'transform': 'change',
                'growth': 'development',
                'potential': 'capability'
            }
        }
        
        result = text
        if category in replacements:
            for forbidden, replacement in replacements[category].items():
                result = re.sub(rf'\b{forbidden}\b', replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def generate_partner_response(
        self, 
        message: str, 
        paradox_result: Dict[str, Any], 
        posture_result: Dict[str, Any],
        include_user_name: bool = False,
        current_posture: Optional[Dict[str, float]] = None
    ) -> str:
        """Generate a Partner Stance response with posture-aware linguistic markers.
        
        Args:
            message: Original user message.
            paradox_result: Contradiction evaluation result.
            posture_result: Posture adjustment result.
            include_user_name: Whether to address user by name.
            current_posture: Current E-Vector posture for linguistic attunement.
            
        Returns:
            Partner Stance response string with posture-dependent voice.
        """
        base_response = self._generate_posture_aware_response(
            paradox_result, posture_result, current_posture or {}
        )
        
        # Add user identification when appropriate
        if include_user_name and self._should_use_user_name(message):
            base_response = f"Derek Angell, {base_response.lower()}"
        
        # Add forensic signature if posture changed
        if posture_result.get("applied") and posture_result.get("delta_applied"):
            base_response = self._add_forensic_signature(base_response, posture_result)
        
        # Apply voice constraints
        return self.apply_voice_constraints(base_response)
    
    def _generate_posture_aware_response(
        self, paradox_result: Dict[str, Any], _posture_result: Dict[str, Any], current_posture: Dict[str, float]
    ) -> str:
        """Generate response based on posture state and E-Vector dimensions.
        
        Args:
            paradox_result: Contradiction evaluation result.
            posture_result: Posture adjustment result.
            current_posture: Current E-Vector posture values.
            
        Returns:
            Posture-aware response string.
        """
        state = paradox_result.get("state", "WITNESS_MODE")
        severity = paradox_result.get("severity_score", 0.0)
        
        # Get base response from posture mapping
        base_response = self._map_posture_to_voice(state, severity, current_posture)
        
        # Adjust response based on E-Vector dimensions
        return self._adjust_voice_by_evector_dimensions(base_response, current_posture)
    
    def _map_posture_to_voice(self, state: str, severity: float, posture: Dict[str, float]) -> str:
        """Map operational state to linguistic markers and voice characteristics.
        
        Args:
            state: Current operational state (WITNESS_MODE, RESOLUTION_GATE, etc.)
            severity: Contradiction severity score.
            posture: Current E-Vector posture.
            
        Returns:
            Base response string with posture-specific voice.
        """
        if state == "RESOLUTION_GATE":
            return self._generate_resolution_voice(severity, posture)
        elif state == "WITNESS_MODE":
            return self._generate_witness_voice(posture)
        elif state == "EXECUTION_MODE":
            return self._generate_action_voice(posture)
        elif state == "QUIESCENCE_MODE":
            return self._generate_quiescence_voice(posture)
        else:
            return "Your message has been integrated into the current context."
    
    def _generate_witness_voice(self, posture: Dict[str, float]) -> str:
        """Generate WITNESS mode voice: calm, observant, minimal interference.
        
        Args:
            posture: Current E-Vector posture.
            
        Returns:
            Witness mode response string.
        """
        challenge = posture.get("challenge_threshold", 0.7)
        directness = posture.get("directness_index", 0.5)
        
        if challenge > 0.8:  # High challenge threshold - very minimal
            responses = [
                "Noted.",
                "Acknowledged.",
                "Processing.",
                "Observed."
            ]
        elif directness > 0.7:  # High directness - more explicit
            responses = [
                "I observe your input.",
                "The information is received.",
                "Processing the implications.",
                "Acknowledging the message."
            ]
        else:  # Balanced witness
            responses = [
                "I have received your input and am processing the implications.",
                "Noting the details provided.",
                "Observing the current context.",
                "Processing the information shared."
            ]
        
        return responses[min(int(challenge * 4), len(responses) - 1)]
    
    def _generate_resolution_voice(self, severity: float, posture: Dict[str, float]) -> str:
        """Generate RESOLUTION gate voice: direct, analytical, contradiction-seeking.
        
        Args:
            severity: Contradiction severity score.
            posture: Current E-Vector posture.
            
        Returns:
            Resolution gate response string.
        """
        challenge = posture.get("challenge_threshold", 0.7)
        directness = posture.get("directness_index", 0.5)
        
        if severity > 0.7:  # High severity - more urgent
            if challenge < 0.5:  # Low challenge threshold - willing to push back
                responses = [
                    "The evidence indicates a contradiction that requires immediate clarification.",
                    "We must address this inconsistency before proceeding.",
                    "This creates a logical conflict that needs resolution.",
                    "The current position contains incompatible elements."
                ]
            else:  # Higher challenge threshold - more diplomatic
                responses = [
                    "I detect a contradiction that requires careful examination.",
                    "There appears to be a tension worth addressing.",
                    "This situation merits closer analysis.",
                    "We should examine this apparent inconsistency."
                ]
        else:  # Lower severity - more measured
            if challenge < 0.5:
                responses = [
                    "There is some tension here that merits attention.",
                    "This point requires clarification.",
                    "We should address this apparent inconsistency.",
                    "The logic here needs refinement."
                ]
            else:
                responses = [
                    "There is some tension here worth addressing before we proceed.",
                    "This area may benefit from clarification.",
                    "I note some inconsistency in this area.",
                    "This point could use further examination."
                ]
        
        return responses[min(int(directness * 4), len(responses) - 1)]
    
    def _generate_action_voice(self, posture: Dict[str, float]) -> str:
        """Generate ACTION mode voice: high-velocity, goal-oriented, authoritative.
        
        Args:
            posture: Current E-Vector posture.
            
        Returns:
            Action mode response string.
        """
        initiative = posture.get("initiative_threshold", 0.5)
        directness = posture.get("directness_index", 0.5)
        
        if initiative < 0.4 and directness > 0.6:  # High initiative, high directness
            responses = [
                "Proceeding with implementation.",
                "Executing the specified action.",
                "Moving forward with the task.",
                "Implementing the directive now."
            ]
        elif initiative < 0.4:  # High initiative, moderate directness
            responses = [
                "Ready to proceed with execution.",
                "Preparing to implement the action.",
                "Moving forward with the objective.",
                "Initiating the requested process."
            ]
        else:  # More cautious initiative
            responses = [
                "Assessing execution parameters.",
                "Preparing for action implementation.",
                "Evaluating the approach forward.",
                "Considering the execution strategy."
            ]
        
        return responses[min(int((1.0 - initiative) * 3), len(responses) - 1)]
    
    def _generate_quiescence_voice(self, posture: Dict[str, float]) -> str:
        """Generate QUIESCENCE mode voice: low-energy, reflective, waiting.
        
        Args:
            posture: Current E-Vector posture.
            
        Returns:
            Quiescence mode response string.
        """
        entropy = posture.get("entropy", 0.5)
        initiative = posture.get("initiative_threshold", 0.5)
        
        if entropy < 0.3 and initiative > 0.7:  # Very low energy, high caution
            responses = [
                "Holding position.",
                "Observing the current state.",
                "Waiting for further signals.",
                "Maintaining quiescence."
            ]
        elif entropy < 0.5:  # Low to moderate energy
            responses = [
                "Reflecting on the current context.",
                "Processing the system state.",
                "Observing patterns emerge.",
                "Integrating recent inputs."
            ]
        else:  # Higher entropy within quiescence
            responses = [
                "Monitoring system integration.",
                "Processing complex interactions.",
                "Observing emerging patterns.",
                "Analyzing system dynamics."
            ]
        
        return responses[min(int(entropy * 4), len(responses) - 1)]
    
    def _adjust_voice_by_evector_dimensions(self, base_response: str, posture: Dict[str, float]) -> str:
        """Fine-tune response based on individual E-Vector dimensions.
        
        Args:
            base_response: Base response from posture mapping.
            posture: Current E-Vector posture values.
            
        Returns:
            Adjusted response string.
        """
        challenge = posture.get("challenge_threshold", 0.7)
        directness = posture.get("directness_index", 0.5)
        entropy = posture.get("entropy", 0.5)
        
        adjusted_response = base_response
        
        # Challenge threshold affects willingness to push back
        if challenge < 0.5:  # Low challenge threshold - more willing to challenge
            if "contradiction" in adjusted_response.lower() or "tension" in adjusted_response.lower():
                adjusted_response += " We should examine this carefully."
        
        # Directness affects communication style
        if directness > 0.7:  # High directness - more plain speaking
            adjusted_response = adjusted_response.replace("appears to be", "is")
            adjusted_response = adjusted_response.replace("may benefit from", "needs")
            adjusted_response = adjusted_response.replace("could use", "requires")
        elif directness < 0.3:  # Low directness - more diplomatic
            adjusted_response = adjusted_response.replace("must", "should")
            adjusted_response = adjusted_response.replace("requires", "would benefit from")
        
        # Entropy affects complexity tolerance
        if entropy > 0.7:  # High entropy - comfortable with complexity
            if len(adjusted_response.split()) < 8:
                adjusted_response += " The system is processing multiple interconnected factors."
        elif entropy < 0.3:  # Low entropy - prefers simplicity
            # Simplify complex constructions
            adjusted_response = re.sub(r'\bwhich\s+[^,.]*[,]', '', adjusted_response)
            adjusted_response = re.sub(r'\bthat\s+[^,.]*[,]', '', adjusted_response)
            adjusted_response = re.sub(r'\s+', ' ', adjusted_response).strip()
        
        return adjusted_response
    
    def _should_use_user_name(self, message: str) -> bool:
        """Determine if user identification is appropriate.
        
        Args:
            message: User's message content.
            
        Returns:
            True if user name should be included.
        """
        # Use name for significant interactions, not every message
        significant_indicators = [
            'decision', 'choose', 'direction', 'strategy', 'plan',
            'important', 'critical', 'urgent', 'change'
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in significant_indicators)
    
    def _add_forensic_signature(self, response: str, posture_result: Dict[str, Any]) -> str:
        """Add forensic em dash signature for internal processing.
        
        Args:
            response: Base response.
            posture_result: Posture adjustment data.
            
        Returns:
            Response with forensic signature.
        """
        delta = posture_result.get("delta_applied", {})
        if delta:
            # Significant changes get forensic signature
            max_change = max(abs(v) for v in delta.values())
            if max_change > 0.1:
                response += " — system posture updated"
        
        return response
    
    def format_challenge(self, contradiction_data: Dict[str, Any]) -> str:
        """Format an evidence-based challenge.
        
        Args:
            contradiction_data: Contradiction information.
            
        Returns:
            Challenge statement in Partner Stance.
        """
        if not self._can_challenge(contradiction_data):
            return ""
        
        topic_similarity = contradiction_data.get("topic_similarity", 0.0)
        implication_similarity = contradiction_data.get("implication_similarity", 0.0)
        
        challenge = (
            f"The evidence shows a disconnect: topic alignment is {topic_similarity:.2f} "
            f"but implication alignment is only {implication_similarity:.2f}. "
            "This requires clarification before we can proceed effectively."
        )
        
        return self.apply_voice_constraints(challenge)
    
    def _can_challenge(self, contradiction_data: Dict[str, Any]) -> bool:
        """Check if challenge conditions are met per ethics.
        
        Args:
            contradiction_data: Contradiction evaluation.
            
        Returns:
            True if challenge is permitted.
        """
        # High confidence required
        confidence = contradiction_data.get("confidence", 0.0)
        if confidence < 0.8:
            return False
        
        # Must serve long-term goals (simplified check)
        severity = contradiction_data.get("severity_score", 0.0)
        if severity < 0.3:
            return False
        
        return True
