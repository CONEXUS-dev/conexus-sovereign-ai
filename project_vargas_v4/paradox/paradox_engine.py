"""
VARGAS V4 Paradox Engine — The Math of Contradiction

This is the core logic component of the sovereign runtime. It detects semantic
collisions between topic vectors and implication vectors, determines whether
the system should enter a RESOLUTION_GATE state, and computes E-Vector deltas
that adjust the runtime's posture in response to contradiction.

Reference: VARGAS V4 Master Blueprint, Section 8 — Paradox/Attunement Engine
    - topic_similarity_min: 0.8
    - implication_similarity_max: 0.2
    - detection_logic: topic_proximate_but_implication_divergent
    - output_format: e_vector_delta_not_resolution

The Paradox Engine does NOT resolve contradictions. It detects them, measures
their severity, and outputs structured posture adjustments. Resolution is a
human prerogative.

The Logic Gate:
    If topic_similarity > 0.8 AND implication_similarity < 0.2:
        → RESOLUTION_GATE (contradiction detected, system must adjust posture)
    Else:
        → WITNESS_MODE (no actionable contradiction, system observes)
"""

import json
import logging
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# System states
RESOLUTION_GATE = "RESOLUTION_GATE"
WITNESS_MODE = "WITNESS_MODE"

# E-Vector dimension keys (from sovereign_state.json e_vector_baseline)
ENTROPY = "entropy"
CHALLENGE = "challenge_threshold"
INITIATIVE = "initiative_threshold"
DIRECTNESS = "directness_index"

# Delta clamp bounds — no single contradiction event can shift a
# dimension by more than 0.1 in either direction
DELTA_MAX = 0.1
DELTA_MIN = -0.1


class ParadoxEngine:
    """Semantic collision detector and E-Vector delta calculator.

    The Paradox Engine operates on pairs of embedding vectors:
    - topic_vector: the semantic embedding of what a statement is ABOUT
    - implication_vector: the semantic embedding of what a statement IMPLIES

    Two statements can be about the same topic (high topic similarity) but
    imply contradictory things (low implication similarity). That is the
    definition of a paradox in the VARGAS V4 architecture.

    The engine does not resolve paradoxes. It:
    1. Detects them via the Logic Gate
    2. Measures their severity
    3. Computes an E-Vector delta that adjusts the runtime's posture

    Attributes:
        topic_similarity_min: Threshold above which topics are considered
            proximate (default 0.8 from sovereign_state.json).
        implication_similarity_max: Threshold below which implications are
            considered divergent (default 0.2 from sovereign_state.json).
    """

    def __init__(self, config_path: str = "config/sovereign_state.json"):
        """Initialize the Paradox Engine from sovereign state configuration.

        Args:
            config_path: Path to sovereign_state.json.
        """
        self.topic_similarity_min: float = 0.8
        self.implication_similarity_max: float = 0.2
        self._load_config(config_path)

        logger.info(
            "[PARADOX_ENGINE] Initialized: topic_sim_min=%.2f implication_sim_max=%.2f",
            self.topic_similarity_min,
            self.implication_similarity_max,
        )

    def _load_config(self, config_path: str) -> None:
        """Load paradox engine thresholds from sovereign state.

        Args:
            config_path: Path to sovereign_state.json.
        """
        path = Path(config_path)
        if not path.exists():
            logger.warning(
                "[PARADOX_ENGINE] Config not found at %s — using defaults",
                config_path,
            )
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)

            paradox_config = config.get("paradox_engine", {})
            self.topic_similarity_min = float(
                paradox_config.get("topic_similarity_min", 0.8)
            )
            self.implication_similarity_max = float(
                paradox_config.get("implication_similarity_max", 0.2)
            )
        except Exception as e:
            logger.warning(
                "[PARADOX_ENGINE] Failed to load config: %s — using defaults", e
            )

    @staticmethod
    def compute_cosine_similarity(
        vec_a: List[float],
        vec_b: List[float],
    ) -> float:
        """Compute cosine similarity between two vectors.

        Cosine similarity measures the angle between two vectors in
        high-dimensional space, returning a value in [-1.0, 1.0]:
            1.0  = identical direction
            0.0  = orthogonal (no relationship)
           -1.0  = opposite direction

        Guards against zero-magnitude vectors to prevent division by zero.

        Args:
            vec_a: First embedding vector.
            vec_b: Second embedding vector.

        Returns:
            Cosine similarity as a float in [-1.0, 1.0].

        Raises:
            ValueError: If vectors have different lengths.
        """
        if len(vec_a) != len(vec_b):
            raise ValueError(
                f"Vector dimension mismatch: {len(vec_a)} vs {len(vec_b)}"
            )

        # Dot product
        dot_product: float = 0.0
        magnitude_a: float = 0.0
        magnitude_b: float = 0.0

        for a, b in zip(vec_a, vec_b):
            dot_product += a * b
            magnitude_a += a * a
            magnitude_b += b * b

        magnitude_a = math.sqrt(magnitude_a)
        magnitude_b = math.sqrt(magnitude_b)

        # Guard against zero-magnitude vectors
        if magnitude_a < 1e-10 or magnitude_b < 1e-10:
            return 0.0

        similarity = dot_product / (magnitude_a * magnitude_b)

        # Clamp to [-1.0, 1.0] to handle floating-point rounding
        return max(-1.0, min(1.0, similarity))

    @staticmethod
    def calculate_severity(
        topic_similarity: float,
        implication_similarity: float,
    ) -> float:
        """Calculate contradiction severity from similarity scores.

        Severity quantifies how strongly two statements contradict each other.
        It is highest when the topic overlap is maximal (same subject) and
        the implication divergence is maximal (opposite conclusions).

        Formula:
            severity = topic_similarity * (1.0 - implication_similarity)

        Range: [0.0, 1.0]
            0.0 = no contradiction (low topic overlap or high implication agreement)
            1.0 = maximum contradiction (identical topic, opposite implications)

        Args:
            topic_similarity: Cosine similarity of topic vectors.
            implication_similarity: Cosine similarity of implication vectors.

        Returns:
            Severity score as a float in [0.0, 1.0].
        """
        # Clamp inputs to valid range
        topic_sim = max(0.0, min(1.0, topic_similarity))
        impl_sim = max(0.0, min(1.0, implication_similarity))

        severity = topic_sim * (1.0 - impl_sim)
        return max(0.0, min(1.0, severity))

    def evaluate_contradiction(
        self,
        topic_vector: List[float],
        implication_vector: List[float],
        topic_vector_b: Optional[List[float]] = None,
        implication_vector_b: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Evaluate whether two statements form a semantic contradiction.

        This is the Logic Gate — the central decision function of the
        Paradox Engine.

        Two-vector mode (default):
            Compares a single topic_vector against a single implication_vector.
            topic_similarity = cosine_sim(topic_vector, implication_vector)
            implication_similarity is derived from the same pair.

        Four-vector mode (when *_b vectors provided):
            Compares statement A's topic against statement B's topic,
            and statement A's implication against statement B's implication.
            topic_similarity = cosine_sim(topic_vector, topic_vector_b)
            implication_similarity = cosine_sim(implication_vector, implication_vector_b)

        The Logic Gate:
            If topic_similarity > 0.8 AND implication_similarity < 0.2:
                → RESOLUTION_GATE
            Else:
                → WITNESS_MODE

        Args:
            topic_vector: Topic embedding of statement A.
            implication_vector: Implication embedding of statement A.
            topic_vector_b: Topic embedding of statement B (optional).
            implication_vector_b: Implication embedding of statement B (optional).

        Returns:
            Dict containing:
                - state: RESOLUTION_GATE or WITNESS_MODE
                - topic_similarity: float
                - implication_similarity: float
                - severity_score: float
                - thresholds: dict of configured thresholds
                - e_vector_delta: dict of posture adjustments (only if RESOLUTION_GATE)
        """
        # Four-vector mode: compare A's topic to B's topic, A's impl to B's impl
        if topic_vector_b is not None and implication_vector_b is not None:
            topic_similarity = self.compute_cosine_similarity(
                topic_vector, topic_vector_b
            )
            implication_similarity = self.compute_cosine_similarity(
                implication_vector, implication_vector_b
            )
        else:
            # Two-vector mode: topic and implication of the same pair
            topic_similarity = self.compute_cosine_similarity(
                topic_vector, implication_vector
            )
            # In two-vector mode, implication similarity is the inverse signal:
            # high topic-implication similarity means agreement (not contradiction)
            implication_similarity = topic_similarity

        severity_score = self.calculate_severity(
            topic_similarity, implication_similarity
        )

        # The Logic Gate
        is_contradiction = (
            topic_similarity > self.topic_similarity_min
            and implication_similarity < self.implication_similarity_max
        )

        state = RESOLUTION_GATE if is_contradiction else WITNESS_MODE

        result: Dict[str, Any] = {
            "state": state,
            "topic_similarity": round(topic_similarity, 6),
            "implication_similarity": round(implication_similarity, 6),
            "severity_score": round(severity_score, 6),
            "thresholds": {
                "topic_similarity_min": self.topic_similarity_min,
                "implication_similarity_max": self.implication_similarity_max,
            },
        }

        if is_contradiction:
            result["e_vector_delta"] = self.calculate_e_vector_delta(severity_score)

        logger.info(
            "[PARADOX_ENGINE] Evaluated: state=%s topic_sim=%.4f impl_sim=%.4f severity=%.4f",
            state,
            topic_similarity,
            implication_similarity,
            severity_score,
        )

        return result

    @staticmethod
    def calculate_e_vector_delta(severity: float) -> Dict[str, float]:
        """Calculate E-Vector posture adjustments from contradiction severity.

        The output format is e_vector_delta_not_resolution — the engine
        adjusts the runtime's posture, it does not resolve the contradiction.

        Delta logic (per V4 Blueprint):
            - entropy: +severity * 0.1
                Contradiction raises complexity tolerance. The system must
                hold more uncertainty.
            - challenge_threshold: -severity * 0.1
                Contradiction lowers the barrier to challenging the user.
                The system becomes more willing to surface the tension.
            - initiative_threshold: +severity * 0.05
                Mild increase in initiative caution. The system should
                slow down before acting when contradiction is present.
            - directness_index: +severity * 0.08
                Contradiction sharpens directness. The system speaks more
                plainly when holding unresolved tension.

        All deltas are clamped to [-0.1, +0.1] per event.

        Args:
            severity: Contradiction severity in [0.0, 1.0].

        Returns:
            Dict with float deltas for each E-Vector dimension.
        """
        severity = max(0.0, min(1.0, severity))

        raw_deltas = {
            ENTROPY: severity * 0.1,
            CHALLENGE: -(severity * 0.1),
            INITIATIVE: severity * 0.05,
            DIRECTNESS: severity * 0.08,
        }

        # Clamp each delta to [-0.1, +0.1]
        clamped_deltas = {
            dim: max(DELTA_MIN, min(DELTA_MAX, val))
            for dim, val in raw_deltas.items()
        }

        return {dim: round(val, 6) for dim, val in clamped_deltas.items()}

    def batch_evaluate(
        self,
        pairs: List[Tuple[List[float], List[float], List[float], List[float]]],
    ) -> List[Dict[str, Any]]:
        """Evaluate multiple contradiction pairs in batch.

        Each tuple in pairs is (topic_a, implication_a, topic_b, implication_b).

        Args:
            pairs: List of 4-tuples of embedding vectors.

        Returns:
            List of evaluation result dicts.
        """
        results = []
        for topic_a, impl_a, topic_b, impl_b in pairs:
            result = self.evaluate_contradiction(
                topic_vector=topic_a,
                implication_vector=impl_a,
                topic_vector_b=topic_b,
                implication_vector_b=impl_b,
            )
            results.append(result)
        return results

    def get_config(self) -> Dict[str, Any]:
        """Return current engine configuration."""
        return {
            "topic_similarity_min": self.topic_similarity_min,
            "implication_similarity_max": self.implication_similarity_max,
            "delta_clamp_range": [DELTA_MIN, DELTA_MAX],
            "states": [RESOLUTION_GATE, WITNESS_MODE],
            "e_vector_dimensions": [ENTROPY, CHALLENGE, INITIATIVE, DIRECTNESS],
        }

    def summary(self) -> Dict[str, Any]:
        """Return engine summary for diagnostics."""
        return {
            "engine": "ParadoxEngine",
            "version": "v4",
            "logic": "topic_proximate_but_implication_divergent",
            "output_format": "e_vector_delta_not_resolution",
            "config": self.get_config(),
        }
