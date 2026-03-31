"""
VARGAS V4 Challenge Engine — Evidence-Based Pushback

Generates evidence-based challenges when contradictions are detected
and the E-Vector posture supports challenge mode. The challenge engine
does not challenge from opinion or moral judgment — only from evidence.

Challenge conditions (from sovereign_state.json):
- contradiction_observed: true
- high_confidence: true
- persisted_across_interactions: true
- serves_long_term_goals: true

Prohibited ground: opinion, moral_judgment, therapy, spiritual_authority

Reference: Master Blueprint Section 8, Section 12.4 — challenge_engine.py
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Challenge eligibility thresholds
MIN_SEVERITY_FOR_CHALLENGE = 0.4
MIN_CONFIDENCE_FOR_CHALLENGE = 0.6
MAX_CHALLENGE_THRESHOLD_FOR_ELIGIBILITY = 0.6

# Prohibited challenge ground
PROHIBITED_GROUND = {"opinion", "moral_judgment", "therapy", "spiritual_authority"}


class ChallengeEngine:
    """Generates evidence-based challenges from detected contradictions.

    The challenge engine evaluates whether a contradiction warrants
    active pushback based on:
    1. Severity of the contradiction
    2. Confidence in the evidence
    3. Current E-Vector challenge threshold
    4. Whether the contradiction persists across interactions

    It produces structured challenge objects, not free-form text.
    The response synthesizer converts these into conversational language.

    Attributes:
        min_severity: Minimum severity to consider challenge.
        min_confidence: Minimum confidence to challenge.
    """

    def __init__(
        self,
        min_severity: float = MIN_SEVERITY_FOR_CHALLENGE,
        min_confidence: float = MIN_CONFIDENCE_FOR_CHALLENGE,
    ):
        self.min_severity = min_severity
        self.min_confidence = min_confidence
        self._challenges_generated: int = 0
        self._challenges_suppressed: int = 0
        logger.info(
            "[CHALLENGE_ENGINE] Initialized: min_severity=%.2f min_confidence=%.2f",
            min_severity, min_confidence,
        )

    def evaluate_challenge(
        self,
        contradiction: Dict[str, Any],
        e_vector: Dict[str, float],
        truth_context: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Evaluate whether a contradiction warrants a challenge.

        Args:
            contradiction: The contradiction data (from detector or store).
            e_vector: Current E-Vector posture.
            truth_context: Supporting truth memories for evidence.

        Returns:
            Challenge object dict if warranted, None otherwise.
        """
        severity = float(contradiction.get("severity_score", contradiction.get("severity", 0.0)))
        confidence = float(contradiction.get("confidence", 0.5))
        challenge_threshold = e_vector.get("challenge_threshold", 0.7)

        # Check eligibility
        if severity < self.min_severity:
            self._challenges_suppressed += 1
            return None

        if confidence < self.min_confidence:
            self._challenges_suppressed += 1
            return None

        # E-Vector gating: lower threshold = more willing to challenge
        if challenge_threshold > MAX_CHALLENGE_THRESHOLD_FOR_ELIGIBILITY:
            self._challenges_suppressed += 1
            logger.info(
                "[CHALLENGE_ENGINE] Suppressed: challenge_threshold=%.2f > %.2f",
                challenge_threshold, MAX_CHALLENGE_THRESHOLD_FOR_ELIGIBILITY,
            )
            return None

        # Build evidence packet
        evidence = self._build_evidence(contradiction, truth_context)

        challenge = {
            "type": "evidence_based_challenge",
            "severity": round(severity, 4),
            "confidence": round(confidence, 4),
            "challenge_threshold": round(challenge_threshold, 4),
            "statement_a": contradiction.get("statement_a", ""),
            "statement_b": contradiction.get("statement_b", ""),
            "evidence": evidence,
            "requires_continuity": True,
            "prohibited_ground": list(PROHIBITED_GROUND),
        }

        self._challenges_generated += 1
        logger.info(
            "[CHALLENGE_ENGINE] Challenge generated: severity=%.2f confidence=%.2f",
            severity, confidence,
        )

        return challenge

    def _build_evidence(
        self,
        contradiction: Dict[str, Any],
        truth_context: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """Build an evidence packet for the challenge.

        Evidence must come from stored truths, not from opinion.

        Args:
            contradiction: The contradiction being challenged.
            truth_context: Supporting truths.

        Returns:
            List of evidence items with source and content.
        """
        evidence = []

        # Include the contradiction itself as primary evidence
        stmt_a = contradiction.get("statement_a", "")
        stmt_b = contradiction.get("statement_b", "")
        if stmt_a and stmt_b:
            evidence.append({
                "source": "contradiction_store",
                "content": f"Previous: {stmt_a[:200]} | Current: {stmt_b[:200]}",
            })

        # Include supporting truths
        for truth in truth_context[:3]:
            content = truth.get("content", "")
            if content:
                evidence.append({
                    "source": "truth_store",
                    "content": content[:200],
                })

        return evidence

    def batch_evaluate(
        self,
        contradictions: List[Dict[str, Any]],
        e_vector: Dict[str, float],
        truth_context: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Evaluate multiple contradictions for challenge eligibility.

        Args:
            contradictions: List of contradiction dicts.
            e_vector: Current E-Vector posture.
            truth_context: Supporting truths.

        Returns:
            List of challenge objects (only those that passed eligibility).
        """
        challenges = []
        for c in contradictions:
            challenge = self.evaluate_challenge(c, e_vector, truth_context)
            if challenge:
                challenges.append(challenge)
        return challenges

    def summary(self) -> Dict[str, Any]:
        """Return challenge engine status summary."""
        return {
            "min_severity": self.min_severity,
            "min_confidence": self.min_confidence,
            "challenges_generated": self._challenges_generated,
            "challenges_suppressed": self._challenges_suppressed,
        }
