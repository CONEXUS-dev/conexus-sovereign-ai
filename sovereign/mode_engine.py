"""
CONEXUS Mode Engine
Determines Collapse/Become mode based on protocol directives,
gear context, and task intent analysis.

The ModeEngine is an additive overlay — it does not replace the existing
router. The orchestrator uses it to determine the cognitive mode (Collapse
vs Become) independently of which agent substrate is selected.

Phase C of the v2 Architecture Evolution Roadmap (Section 13.4).
"""

from typing import Optional


class ModeEngine:
    """Protocol-driven mode determination."""

    def __init__(self, llm_client=None):
        self.llm = llm_client  # For intent analysis if needed

    def determine_initial_mode(self, mission_text: str, agent_home_mode: str) -> str:
        """Determine starting mode based on mission intent analysis.

        Returns "collapse" or "become". If signals are ambiguous,
        falls back to the agent's home mode.
        """
        collapse_signals = [
            "execute", "implement", "plan", "decide", "optimize",
            "build", "deploy", "fix", "resolve", "audit", "assess",
            "benchmark", "measure", "schedule", "prioritize",
        ]
        become_signals = [
            "explore", "imagine", "create", "reflect", "synthesize",
            "dream", "envision", "expand", "hold", "contemplate",
            "design", "invent", "wonder", "discover", "transform",
        ]

        text_lower = mission_text.lower()
        collapse_count = sum(1 for s in collapse_signals if s in text_lower)
        become_count = sum(1 for s in become_signals if s in text_lower)

        if collapse_count > become_count + 2:
            return "collapse"
        elif become_count > collapse_count + 2:
            return "become"
        else:
            return agent_home_mode  # Ambiguous → use home mode

    def evaluate_at_phase_boundary(
        self,
        gear_state,
        phase_output: str,
    ) -> Optional[str]:
        """Evaluate whether to switch modes at a phase boundary.

        Returns new mode if switch is warranted, None if no switch.
        Called between Phase II→III and Phase III→IV.
        """
        current = gear_state.active_mode

        # Phase II → Phase III transition
        if gear_state.current_phase == "gravity_well":
            if current == "become" and self._stress_likely_to_resolve(phase_output):
                return "collapse"
            elif current == "collapse" and self._deep_paradox_detected(phase_output):
                return "become"

        # Phase III → Phase IV transition
        if gear_state.current_phase == "release_forge":
            if current == "become" and self._resolution_emerged(phase_output):
                return "collapse"
            elif current == "collapse" and self._new_paradox_emerged(phase_output):
                return "become"

        return None  # No switch

    def _stress_likely_to_resolve(self, output: str) -> bool:
        """Check if held paradox is likely to break under stress."""
        resolution_markers = [
            "resolves to", "the answer is", "clearly",
            "therefore", "the solution", "must be",
        ]
        return any(m in output.lower() for m in resolution_markers)

    def _deep_paradox_detected(self, output: str) -> bool:
        """Check if a deep, unresolvable paradox was found."""
        paradox_markers = [
            "cannot be resolved", "both are true",
            "irreducible tension", "fundamental paradox",
            "no resolution", "must hold both",
        ]
        return any(m in output.lower() for m in paradox_markers)

    def _resolution_emerged(self, output: str) -> bool:
        """Check if stress/roam produced a natural resolution."""
        return self._stress_likely_to_resolve(output)

    def _new_paradox_emerged(self, output: str) -> bool:
        """Check if exploration revealed a new deep tension."""
        return self._deep_paradox_detected(output)

    # ------------------------------------------------------------------
    # Mirror Tier Selection (Phase D)
    # ------------------------------------------------------------------

    def select_mirror_tier(self, mission_text: str) -> Optional[str]:
        """Select the best Mirror Tier key for the given mission text.

        Uses word-level matching: each word in a multi-word trigger is
        checked independently (1 pt each), with a bonus (+2) if the
        full phrase appears. Also matches against core_paradox poles
        and mirror_whisper keywords.

        Returns a tier key (e.g. "mirror_01_black") or None if no tier
        matches strongly enough.
        """
        from sovereign.symbolic_fields import MIRROR_TIERS
        import re

        text_lower = mission_text.lower()
        text_words = set(re.findall(r"[a-z]+", text_lower))
        best_key = None
        best_score = 0

        for key, tier in MIRROR_TIERS.items():
            score = 0

            # Score emotional triggers (word-level + phrase bonus)
            for trigger in tier.get("emotional_triggers", []):
                trigger_lower = trigger.lower()
                trigger_words = set(re.findall(r"[a-z]+", trigger_lower))
                word_hits = len(trigger_words & text_words)
                if word_hits > 0:
                    score += word_hits
                if trigger_lower in text_lower:
                    score += 2  # Exact phrase bonus

            # Score core_paradox poles (extract words around ↔)
            paradox = tier.get("core_paradox", "")
            for pole in re.split(r"[↔,]", paradox):
                pole_words = set(re.findall(r"[a-z]+", pole.lower()))
                pole_words -= {"and", "the", "of", "in", "to", "a"}
                score += len(pole_words & text_words) * 0.5

            if score > best_score:
                best_score = score
                best_key = key

        return best_key if best_score >= 1.0 else None
