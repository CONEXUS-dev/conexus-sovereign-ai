"""
VARGAS V4 Contradiction Detector — Semantic Collision Detection

Detects contradictions between new input and stored truths/memories.
This is the intake layer for the Paradox Engine — it identifies when
a new statement conflicts with something previously established.

Paradox is not decoration. If paradox does not change runtime truth,
it is not paradox. It is theater. (Foundational Invariant §2)

Reference: Master Blueprint Section 8, Section 12.4 — contradiction_detector.py
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Detection thresholds (aligned with ParadoxEngine)
DEFAULT_TOPIC_SIMILARITY_MIN = 0.8
DEFAULT_IMPLICATION_SIMILARITY_MAX = 0.2

# Contradiction types
TYPE_DIRECT = "direct_contradiction"
TYPE_BEHAVIORAL = "behavioral_tension"
TYPE_ARCHITECTURAL = "architectural_conflict"
TYPE_STATED_VS_OBSERVED = "stated_vs_observed"


class ContradictionCandidate:
    """A detected contradiction candidate before promotion to the store.

    Attributes:
        statement_a: The existing truth or memory.
        statement_b: The new conflicting input.
        contradiction_type: Category of contradiction.
        topic_similarity: How similar the topics are.
        implication_similarity: How similar the implications are.
        severity: Computed severity score.
        confidence: Detection confidence.
    """

    def __init__(
        self,
        statement_a: str,
        statement_b: str,
        contradiction_type: str = TYPE_DIRECT,
        topic_similarity: float = 0.0,
        implication_similarity: float = 1.0,
        severity: float = 0.0,
        confidence: float = 0.5,
        source_memory_id: str = "",
    ):
        self.statement_a = statement_a
        self.statement_b = statement_b
        self.contradiction_type = contradiction_type
        self.topic_similarity = topic_similarity
        self.implication_similarity = implication_similarity
        self.severity = severity
        self.confidence = confidence
        self.source_memory_id = source_memory_id

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for storage."""
        return {
            "statement_a": self.statement_a,
            "statement_b": self.statement_b,
            "contradiction_type": self.contradiction_type,
            "topic_similarity": round(self.topic_similarity, 6),
            "implication_similarity": round(self.implication_similarity, 6),
            "severity_score": round(self.severity, 6),
            "confidence": round(self.confidence, 6),
            "source_memory_id": self.source_memory_id,
            "status": "active",
        }

    def to_json(self) -> str:
        """Serialize to JSON string for memory storage."""
        return json.dumps(self.to_dict())


class ContradictionDetector:
    """Detects semantic collisions between new input and stored context.

    The detector operates in two modes:
    1. Vector mode: Uses embedding similarity (when Qdrant is available)
    2. Keyword mode: Uses text overlap heuristics (fallback)

    The detector does NOT resolve contradictions. It detects and measures.
    Resolution is a human prerogative.

    Attributes:
        topic_sim_min: Minimum topic similarity to consider same-topic.
        impl_sim_max: Maximum implication similarity to flag divergence.
    """

    def __init__(
        self,
        topic_similarity_min: float = DEFAULT_TOPIC_SIMILARITY_MIN,
        implication_similarity_max: float = DEFAULT_IMPLICATION_SIMILARITY_MAX,
    ):
        self.topic_sim_min = topic_similarity_min
        self.impl_sim_max = implication_similarity_max
        logger.info(
            "[CONTRADICTION_DETECTOR] Initialized: topic_min=%.2f impl_max=%.2f",
            topic_similarity_min, implication_similarity_max,
        )

    def detect(
        self,
        message: str,
        truth_context: List[Dict[str, Any]],
        contradiction_context: List[Dict[str, Any]],
    ) -> List[ContradictionCandidate]:
        """Detect contradictions between a message and stored truths.

        Args:
            message: The new input message.
            truth_context: Retrieved truth memories.
            contradiction_context: Existing active contradictions.

        Returns:
            List of ContradictionCandidate objects.
        """
        candidates: List[ContradictionCandidate] = []

        # Check against truth store
        for truth in truth_context:
            candidate = self._check_against_truth(message, truth)
            if candidate:
                candidates.append(candidate)

        # Check for escalation of existing contradictions
        for contradiction in contradiction_context:
            candidate = self._check_escalation(message, contradiction)
            if candidate:
                candidates.append(candidate)

        if candidates:
            logger.info(
                "[CONTRADICTION_DETECTOR] Detected %d candidates from %d truths, %d existing",
                len(candidates), len(truth_context), len(contradiction_context),
            )

        return candidates

    def _check_against_truth(
        self, message: str, truth: Dict[str, Any]
    ) -> Optional[ContradictionCandidate]:
        """Check if a message contradicts a stored truth.

        Uses keyword overlap as a heuristic when embeddings aren't available.
        """
        truth_content = truth.get("content", "")
        if not truth_content:
            return None

        # Compute keyword overlap as topic similarity proxy
        msg_words = set(message.lower().split())
        truth_words = set(truth_content.lower().split())

        if not msg_words or not truth_words:
            return None

        overlap = msg_words & truth_words
        topic_sim = len(overlap) / max(len(msg_words), len(truth_words))

        # Only consider if topics are similar enough
        if topic_sim < self.topic_sim_min * 0.5:
            return None

        # Check for negation signals (simple heuristic)
        negation_signals = {"not", "no", "never", "don't", "doesn't", "isn't", "aren't", "won't", "can't", "shouldn't"}
        msg_negations = msg_words & negation_signals
        truth_negations = truth_words & negation_signals

        # Divergent negation pattern suggests implication divergence
        negation_divergence = len(msg_negations) != len(truth_negations)

        if negation_divergence and topic_sim > 0.3:
            severity = topic_sim * 0.8
            return ContradictionCandidate(
                statement_a=truth_content[:300],
                statement_b=message[:300],
                contradiction_type=TYPE_DIRECT,
                topic_similarity=topic_sim,
                implication_similarity=1.0 - severity,
                severity=severity,
                confidence=min(0.7, topic_sim),
                source_memory_id=truth.get("memory_id", ""),
            )

        return None

    def _check_escalation(
        self, message: str, contradiction: Dict[str, Any]
    ) -> Optional[ContradictionCandidate]:
        """Check if a message escalates an existing contradiction."""
        content = contradiction.get("content", "")
        try:
            payload = json.loads(content) if isinstance(content, str) else content
        except (json.JSONDecodeError, TypeError):
            return None

        if not isinstance(payload, dict):
            return None

        if payload.get("status") != "active":
            return None

        # Check if message relates to the contradiction topic
        stmt_a = str(payload.get("statement_a", ""))
        stmt_b = str(payload.get("statement_b", ""))
        combined = (stmt_a + " " + stmt_b).lower()
        msg_lower = message.lower()

        msg_words = set(msg_lower.split())
        combined_words = set(combined.split())

        if not msg_words or not combined_words:
            return None

        overlap = msg_words & combined_words
        relevance = len(overlap) / max(len(msg_words), 1)

        if relevance > 0.3:
            existing_severity = float(payload.get("severity_score", 0.0))
            escalated_severity = min(1.0, existing_severity + 0.1)

            return ContradictionCandidate(
                statement_a=stmt_a[:300],
                statement_b=message[:300],
                contradiction_type=TYPE_BEHAVIORAL,
                topic_similarity=relevance,
                implication_similarity=1.0 - escalated_severity,
                severity=escalated_severity,
                confidence=min(0.8, relevance + 0.2),
                source_memory_id=contradiction.get("memory_id", ""),
            )

        return None

    def summary(self) -> Dict[str, Any]:
        """Return detector configuration summary."""
        return {
            "topic_similarity_min": self.topic_sim_min,
            "implication_similarity_max": self.impl_sim_max,
        }
