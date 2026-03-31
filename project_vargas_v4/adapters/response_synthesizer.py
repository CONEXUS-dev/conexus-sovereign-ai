"""
VARGAS V4 Response Synthesizer — Verbal Reply Layer

Separates the conversational text from the system's telemetry metadata.
The perception loop produces a structured result containing both a verbal
response and full system state. This module extracts and formats only the
verbal portion for the forward-facing Discord presence.

Voice constraint: direct, calm, structurally clear. No pastoral, therapeutic,
or motivational cliché language. No sentience theater.

The synthesizer does not generate new content — it formats what the perception
loop already produced. If the loop's response_text is empty or malformed,
the synthesizer returns a minimal acknowledgment.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Fallback when perception loop returns no verbal content
FALLBACK_RESPONSE = "Acknowledged."

# Maximum Discord message length (Discord limit is 2000)
MAX_MESSAGE_LENGTH = 1900


class ResponseSynthesizer:
    """Extracts and formats the verbal reply from a perception loop result.

    The synthesizer is a pure formatter — no LLM calls, no state mutation,
    no business logic. It takes the structured output from
    SovereignPerceptionLoop.process_message() and returns a clean string
    suitable for a plain-text Discord message.

    Usage:
        synth = ResponseSynthesizer()
        text = synth.synthesize(loop_result)
        await channel.send(text)
    """

    def __init__(self):
        """Initialize the Response Synthesizer."""
        logger.info("[RESPONSE_SYNTH] Initialized")

    def synthesize(self, loop_result: Dict[str, Any]) -> str:
        """Extract the verbal reply from a perception loop result.

        Args:
            loop_result: The dict returned by
                SovereignPerceptionLoop.process_message().

        Returns:
            Clean string for plain-text Discord message.
        """
        response_text = loop_result.get("response_text", "")

        if not response_text or not isinstance(response_text, str):
            return FALLBACK_RESPONSE

        # Trim to Discord limit
        text = response_text.strip()
        if len(text) > MAX_MESSAGE_LENGTH:
            text = text[:MAX_MESSAGE_LENGTH] + "…"

        return text

    def should_auto_embed(self, loop_result: Dict[str, Any]) -> bool:
        """Determine whether this turn warrants an automatic State Embed.

        Automated forensic triggers:
            1. RESOLUTION_GATE is active — contradiction held
            2. Tier 3 or Tier 4 action requires approval (PENDING_APPROVAL or BLOCKED_FATAL)

        Args:
            loop_result: The dict returned by
                SovereignPerceptionLoop.process_message().

        Returns:
            True if a State Embed should be sent alongside the verbal reply.
        """
        # Trigger 1: RESOLUTION_GATE
        contradiction_info = loop_result.get("contradiction_info", {})
        if contradiction_info.get("state") == "RESOLUTION_GATE":
            logger.info("[RESPONSE_SYNTH] Auto-embed trigger: RESOLUTION_GATE")
            return True

        # Trigger 2: Tier 3/4 action requiring approval
        action_result = loop_result.get("action_result")
        if action_result:
            trust_tier = action_result.get("trust_tier", 0)
            status = action_result.get("status", "")
            if trust_tier >= 3 and status in ("PENDING_APPROVAL", "BLOCKED_FATAL"):
                logger.info(
                    "[RESPONSE_SYNTH] Auto-embed trigger: Tier %d %s",
                    trust_tier, status,
                )
                return True

        return False

    def format_approval_notice(self, action_result: Dict[str, Any]) -> str:
        """Format a brief inline notice when an action requires approval.

        Appended to the verbal reply when a Tier 3/4 action is pending.

        Args:
            action_result: The action_result dict from loop result.

        Returns:
            Short notice string, or empty string if not applicable.
        """
        if not action_result:
            return ""

        status = action_result.get("status", "")
        trust_tier = action_result.get("trust_tier", 0)

        if status == "PENDING_APPROVAL" and trust_tier >= 3:
            action_type = action_result.get("action", {}).get("action_type", "action")
            return f"\n\n⚠️ **Tier {trust_tier} action pending approval**: `{action_type}`"

        if status == "BLOCKED_FATAL":
            return "\n\n🚫 **Action blocked** — exceeds trust boundary."

        return ""
