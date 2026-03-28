# forgetting_engine.py

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional
from ecp_substrate import ECPSubstrate


@dataclass
class TensionTrace:
    vector: np.ndarray
    peak_tension: float
    cycle_born: int


class ForgettingEngine:
    def __init__(self, substrate: ECPSubstrate, retention_threshold: float = 0.3):
        self.substrate = substrate
        self.retention_threshold = retention_threshold
        self.traces: List[TensionTrace] = []
        self.current_cycle = 0
        self.deleted_count = 0
        self.promoted_count = 0

    def process_signal(self, active_vector: np.ndarray):
        self.current_cycle += 1

        tension = self.substrate.compute_tension_gradient(
            active_vector, self.substrate.state_vector
        )

        if tension >= self.retention_threshold:
            self.traces.append(TensionTrace(
                vector=active_vector.copy(),
                peak_tension=tension,
                cycle_born=self.current_cycle
            ))

        self._evaluate_and_prune()

    def _evaluate_and_prune(self):
        survivors = []

        for trace in self.traces:
            current_tension = self.substrate.compute_tension_gradient(
                trace.vector, self.substrate.state_vector
            )

            # Update peak tension if this cycle produced more contradiction
            if current_tension > trace.peak_tension:
                trace.peak_tension = current_tension

            if current_tension < self.retention_threshold:
                # Consensus reached. This trace resolved. Destroy it.
                self.deleted_count += 1
                continue

            if current_tension > self.substrate.threshold:
                # Tension exceeds substrate threshold. Promote to paradox archive.
                self.substrate.preserve_paradox(trace.vector)
                self.promoted_count += 1
                # Do not keep in survivors — it has been elevated
            else:
                # Tension maintained but not yet critical. Hold in waiting.
                survivors.append(trace)

        self.traces = survivors

    def flush_stale(self, max_age_cycles: int = 50):
        """Optional: remove traces that have lingered too long without promotion."""
        cutoff = self.current_cycle - max_age_cycles
        before = len(self.traces)
        self.traces = [t for t in self.traces if t.cycle_born >= cutoff]
        flushed = before - len(self.traces)
        if flushed:
            print(f"[ENGINE] Flushed {flushed} stale trace(s) older than {max_age_cycles} cycles.")

    def summary(self) -> dict:
        return {
            "active_traces": len(self.traces),
            "current_cycle": self.current_cycle,
            "retention_threshold": self.retention_threshold,
            "total_deleted": self.deleted_count,
            "total_promoted": self.promoted_count,
            "avg_trace_tension": round(
                float(np.mean([t.peak_tension for t in self.traces])), 4
            ) if self.traces else 0.0
        }
