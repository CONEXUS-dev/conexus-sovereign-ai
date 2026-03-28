# ecp_substrate.py

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class SubstrateMetrics:
    stage_index: int
    active_threshold: float
    paradox_count: int
    vector_magnitude: float


class ECPSubstrate:
    def __init__(self, dimensions: int = 1024, base_threshold: float = 0.618):
        self.dimensions = dimensions
        self.threshold = base_threshold
        self.paradox_archive: List[np.ndarray] = []
        self.current_stage = 1
        self.max_stages = 9
        self.state_vector = np.zeros(dimensions)
        self.calibration_history: List[float] = []

    def compute_tension_gradient(
        self, v_target: np.ndarray, v_current: np.ndarray
    ) -> float:
        diff = v_target - v_current
        l2_norm = np.linalg.norm(diff)

        dot_prod = np.dot(v_target, v_current)
        norm_prod = np.linalg.norm(v_target) * np.linalg.norm(v_current)

        if norm_prod < 1e-8:
            cosine_dist = 1.0
        else:
            cosine_dist = 1.0 - (dot_prod / norm_prod)

        tension = (0.7 * cosine_dist) + (0.3 * np.tanh(l2_norm))
        return float(tension)

    def preserve_paradox(self, unresolved_state: np.ndarray):
        self.paradox_archive.append(unresolved_state.copy())
        # Sort by vector magnitude — hardest paradoxes (largest magnitude) at the end
        self.paradox_archive.sort(key=lambda v: np.linalg.norm(v))

    def process_stage(self, input_signal: np.ndarray) -> Tuple[np.ndarray, float]:
        if self.current_stage > self.max_stages:
            self.current_stage = 1

        # Seed with the hardest unresolved paradox if one exists
        if self.paradox_archive:
            hardest_paradox = self.paradox_archive[-1]  # highest magnitude
            active_vector = (input_signal * 0.382) + (hardest_paradox * 0.618)
        else:
            active_vector = input_signal.copy()

        current_tension = self.compute_tension_gradient(active_vector, self.state_vector)

        if current_tension > self.threshold:
            # High tension: preserve the paradox, blend state toward it
            self.preserve_paradox(active_vector)
            self.state_vector = (self.state_vector + active_vector) / 2.0
        else:
            # Low tension: consensus — replace state, do not archive
            self.state_vector = active_vector.copy()

        self._calibrate_threshold(current_tension)
        self.current_stage += 1

        return self.state_vector.copy(), current_tension

    def _calibrate_threshold(self, observed_tension: float):
        self.calibration_history.append(observed_tension)

        if len(self.calibration_history) > 10:
            self.calibration_history.pop(0)

        avg_tension = sum(self.calibration_history) / len(self.calibration_history)
        adjustment_factor = (avg_tension - self.threshold) * 0.05
        self.threshold = float(np.clip(self.threshold + adjustment_factor, 0.1, 0.95))

    def pop_hardest_paradox(self) -> Optional[np.ndarray]:
        if not self.paradox_archive:
            return None
        return self.paradox_archive.pop()  # removes and returns highest magnitude

    def get_metrics(self) -> SubstrateMetrics:
        return SubstrateMetrics(
            stage_index=self.current_stage,
            active_threshold=self.threshold,
            paradox_count=len(self.paradox_archive),
            vector_magnitude=float(np.linalg.norm(self.state_vector))
        )

    def reset_stage_cycle(self):
        self.current_stage = 1

    def summary(self) -> dict:
        return {
            "stage": self.current_stage,
            "threshold": round(self.threshold, 4),
            "paradox_archive_size": len(self.paradox_archive),
            "state_vector_magnitude": round(float(np.linalg.norm(self.state_vector)), 4),
            "calibration_window": len(self.calibration_history),
            "avg_observed_tension": round(
                sum(self.calibration_history) / len(self.calibration_history), 4
            ) if self.calibration_history else 0.0
        }
