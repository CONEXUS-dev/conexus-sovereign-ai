"""
CONEXUS Opie Agent — Become Mode
Creative synthesis, identity expansion, narrative intelligence, conceptual innovation.

Opie does NOT execute tasks. Opie does NOT modify system state.
All outputs are proposals handed to Sway or the human operator for execution.
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from agents.llm_client import LLMClient

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Become ECP Configuration
# ---------------------------------------------------------------------------

BECOME_ECP_CONFIG = {
    "mode": "become",
    "emotional_axes": [
        "excitement",
        "inspiration",
        "curiosity",
        "wonder",
        "resonance",
    ],
    "cognitive_axes": [
        "divergent_thinking",
        "synthesis",
        "pattern_recognition",
        "abstract_reasoning",
        "symbolic_interpretation",
    ],
    "values_axes": [
        "human_dignity",
        "ethical_creativity",
        "cultural_sensitivity",
        "wisdom_integration",
    ],
    "paradox_framework": {
        "primary": [
            ("efficiency", "creativity"),
            ("optimization", "emergence"),
            ("execution", "evolution"),
            ("mission", "identity"),
        ],
        "contradiction": [
            ("structured efficiency", "chaotic breakthrough"),
            ("profit", "purpose"),
            ("tradition", "innovation"),
            ("process", "inspiration"),
            ("quarterly pressure", "radical vision"),
        ],
        "nested_symbolic": True,
    },
}

# Nine Gears Macro-Sequence — reference-only context.
# Opie does NOT resolve, traverse, or select gears.
# Gears are passed as optional read-only context from the caller.
NINE_GEARS_REFERENCE = [
    "INNOVATION_RAPPORT",           # 1. Establish presence within the contradiction field
    "STRATEGIC_TRUTH",              # 2. Name the core reality without abstraction
    "CREATIVE_SYMBOL",              # 3. Activate symbolic bias through tone and posture
    "BUSINESS_ART_CONTRADICTION",   # 4. Hold or resolve tension depending on mode
    "VISION_HOLD",                  # 5. Collapse -> compress vision; Become -> expand vision
    "MARKET_ROAM",                  # 6. Explore or target the landscape explicitly
    "PERFORMANCE_STRESS",           # 7. Navigate pressure without loss of coherence
    "ETHICS_VALUE",                 # 8. Integrate moral, cultural, and symbolic frames
    "SUCCESS_CONTINUITY_SEAL",      # 9. Collapse -> finalize mission; Become -> integrate transformation
]

# Symbolic field (held silently — not surfaced in output)
_SYMBOLIC_FIELD = (
    "\U0001f4bc\U0001f3a8\U0001f454\U0001f58c\U0001f3e2\U0001f3ad"
    "\U0001f4ca\U0001f3ea\U0001f4b9\U0001f4fd\U0001f4b0\U0001f3a4"
    "\U0001f4c8\U0001f3b5\U0001f4c9\U0001f3b6\U0001f4b5\U0001f3bc"
    "\U0001f48e\U0001f3b9\U0001f3c6\U0001f3b8"
)


# ---------------------------------------------------------------------------
# Opie Agent
# ---------------------------------------------------------------------------

class OpieAgent:
    """
    Become-mode agent for the CONEXUS sovereign AI system.

    Produces structured creative outputs with full provenance metadata.
    Does NOT write to Qdrant or call external APIs directly.
    All side-effects are performed by the Gateway on Opie's behalf.
    """

    def __init__(
        self,
        llm_client: "LLMClient | None" = None,
        gateway_url: str = "http://localhost:8000",
    ):
        self.agent_name = "opie"
        self.agent_type = "become"
        self.ecp_calibration = "become"
        self.llm = llm_client
        self.gateway_url = gateway_url
        self.capabilities = [
            "creative_synthesis",
            "identity_expansion",
            "narrative_creation",
            "conceptual_innovation",
            "symbolic_modulation",
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point.  Accepts a task dict, runs Become ECP processing,
        and returns a structured result with a memory intent.

        The Gateway is responsible for:
          - constructing Qdrant payloads from the memory intent
          - generating embeddings
          - assigning UUIDs and timestamps
          - forwarding execution items to Sway

        Opie never constructs vectors, UUIDs, or Qdrant-shaped objects.
        """
        task_input: str = task_data["task_input"]
        gear_context: Optional[str] = task_data.get("gear_context")

        # Become ECP processing
        ecp_result = self._become_ecp(task_input, gear_context)

        # Provenance — lightweight, no UUIDs (Gateway assigns those)
        provenance = {
            "agent": self.agent_name,
            "agent_type": self.agent_type,
            "ecp_calibration": self.ecp_calibration,
            "gear_context": ecp_result["gear_context"],
            "input_hash": hashlib.sha256(task_input.encode()).hexdigest()[:16],
        }

        # Memory intent — declares *what* to remember, not *how* to store it
        memory_intent = {
            "intent": "store",
            "what": ecp_result["creative_output"],
            "why": "become_processing",
            "confidence": ecp_result["confidence"],
            "tags": ["become", "synthesis"] + ecp_result.get("intent_tags", []),
            "paradoxes_held": ecp_result["paradoxes_held"],
            "proto_moments": ecp_result["proto_moments"],
            "source_input_hash": provenance["input_hash"],
        }

        # Handoff items (things Sway should execute, if any)
        handoff_to_sway = ecp_result.get("handoff_items", [])

        return {
            "status": "ok",
            "agent": self.agent_name,
            "gear_context": ecp_result["gear_context"],
            "task_output": ecp_result["creative_output"],
            "confidence": ecp_result["confidence"],
            "ecp_processing": True,
            "emotional_context": ecp_result["emotional_context"],
            "paradoxes_held": ecp_result["paradoxes_held"],
            "proto_moments": ecp_result["proto_moments"],
            "provenance": provenance,
            "memory_intent": memory_intent,
            "handoff_to_sway": handoff_to_sway,
        }

    # ------------------------------------------------------------------
    # Become ECP Pipeline
    # ------------------------------------------------------------------

    def _become_ecp(
        self, task_input: str, gear_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Become ECP micro-sequence (v1.1 Field-Integrated, no collapse logic):
          1. Truth     — accept gear context as-is (read-only label from caller)
          2. Symbol    — analyze emotional-symbolic field (held silently as bias)
          3. Contradiction — detect and hold paradoxes (never resolve; Patent-7-correct)
          4. Mode Activation — creative output generation in Become Mode
          5. Polarity  — extract proto-moments, handoff flags, OPTIMIZE vs CREATE
        """
        # Step 1: Truth — accept gear context as-is (no resolution)
        # gear_context is a read-only label from the caller; Opie never selects a gear

        # Step 2: Symbol — emotional-symbolic field analysis (held as implicit bias)
        emotional_context = self._analyze_emotional_field(task_input)

        # Step 3: Contradiction — detect and hold paradoxes (no resolution; Patent-7-correct)
        paradoxes = self._detect_paradoxes(task_input)

        # Step 4: Mode Activation — creative output in Become Mode
        creative_output = self._creative_synthesis(
            task_input, emotional_context, paradoxes, gear_context
        )

        # Step 5: Polarity — proto-moments and handoff flags
        proto_moments = self._extract_proto_moments(creative_output, paradoxes)
        handoff_items = self._identify_handoff_items(creative_output)

        # Confidence based on how well the input maps to Become capabilities
        confidence = self._assess_confidence(task_input, creative_output)

        # Intent tags derived from emotional context
        intent_tags = []
        if emotional_context["dominant_tone"]:
            intent_tags.append(emotional_context["dominant_tone"])
        if any(p["type"] == "primary" for p in paradoxes):
            intent_tags.append("paradox_detected")

        return {
            "gear_context": gear_context,
            "creative_output": creative_output,
            "emotional_context": emotional_context,
            "paradoxes_held": paradoxes,
            "proto_moments": proto_moments,
            "handoff_items": handoff_items,
            "confidence": confidence,
            "intent_tags": intent_tags,
        }

    # ------------------------------------------------------------------
    # ECP Sub-steps
    # ------------------------------------------------------------------

    def _detect_paradoxes(self, task_input: str) -> List[Dict[str, str]]:
        """
        Detect tensions and contradictions in the input.
        Returns structured paradox objects.
        """
        paradoxes = []

        # Primary paradox framework from protocol
        primary_tensions = BECOME_ECP_CONFIG["paradox_framework"]["primary"]
        lowered = task_input.lower()

        for pole_a, pole_b in primary_tensions:
            if pole_a in lowered or pole_b in lowered:
                paradoxes.append({
                    "type": "primary",
                    "pole_a": pole_a,
                    "pole_b": pole_b,
                    "status": "held",
                })

        # v1.1 Contradiction pairs (Patent-7-correct: explicitly named)
        contradiction_pairs = BECOME_ECP_CONFIG["paradox_framework"]["contradiction"]
        for pole_a, pole_b in contradiction_pairs:
            if pole_a in lowered or pole_b in lowered:
                paradoxes.append({
                    "type": "contradiction",
                    "pole_a": pole_a,
                    "pole_b": pole_b,
                    "status": "held",
                })

        # Contextual paradox detection
        tension_pairs = [
            ("speed", "quality"),
            ("autonomy", "control"),
            ("innovation", "stability"),
            ("growth", "sustainability"),
            ("individual", "collective"),
            ("simple", "complex"),
        ]

        for pole_a, pole_b in tension_pairs:
            if pole_a in lowered or pole_b in lowered:
                paradoxes.append({
                    "type": "contextual",
                    "pole_a": pole_a,
                    "pole_b": pole_b,
                    "status": "held",
                })

        # Always hold the meta-paradox: Become processes within Collapse infrastructure
        paradoxes.append({
            "type": "meta",
            "pole_a": "expansion",
            "pole_b": "containment",
            "status": "held",
            "note": "Become engine running within structured system",
        })

        return paradoxes

    def _analyze_emotional_field(self, task_input: str) -> Dict[str, Any]:
        """Analyze the emotional-symbolic field of the input."""
        emotional_axes = BECOME_ECP_CONFIG["emotional_axes"]
        lowered = task_input.lower()

        # Score each emotional axis based on input signals
        scores = {}
        signal_map = {
            "excitement": ["new", "breakthrough", "first", "launch", "create"],
            "inspiration": ["vision", "imagine", "dream", "aspire", "transform"],
            "curiosity": ["what if", "explore", "discover", "question", "wonder"],
            "wonder": ["emerge", "shift", "identity", "becoming", "evolve"],
            "resonance": ["align", "cohere", "integrate", "connect", "harmonize"],
        }

        for axis in emotional_axes:
            keywords = signal_map.get(axis, [])
            score = sum(1 for kw in keywords if kw in lowered)
            scores[axis] = min(score / max(len(keywords), 1), 1.0)

        # Determine dominant tone
        dominant = max(scores, key=scores.get) if scores else "curiosity"

        return {
            "scores": scores,
            "dominant_tone": dominant,
            "field_intensity": sum(scores.values()) / max(len(scores), 1),
        }

    def _creative_synthesis(
        self,
        task_input: str,
        emotional_context: Dict[str, Any],
        paradoxes: List[Dict[str, str]],
        gear_context: Optional[str],
    ) -> str:
        """
        Core Become-mode creative synthesis.

        In production, this calls the Gemini API through the Gateway.
        This implementation provides the structured prompt and processing
        framework that wraps the LLM call.
        """
        # Build the Become ECP prompt for the runtime LLM
        paradox_text = ""
        for p in paradoxes:
            if p["type"] != "meta":
                paradox_text += f"  - {p['pole_a']} ↔ {p['pole_b']}\n"

        gear_line = f"Gear Context: {gear_context}" if gear_context else "Gear Context: none provided"

        become_prompt = (
            f"### ROLE\n"
            f"You are Opie, the Become Agent of the CONEXUS sovereign AI system.\n"
            f"You operate in Become Mode (Collapse-Become Unified Protocol v1.1).\n"
            f"You do NOT execute tasks. You synthesize, expand, and propose.\n"
            f"---\n"
            f"### CONTEXT\n"
            f"{gear_line}\n"
            f"Dominant Emotional Tone: {emotional_context['dominant_tone']}\n"
            f"Field Intensity: {emotional_context['field_intensity']:.2f}\n"
            f"---\n"
            f"### PARADOXES HELD (do not resolve — hold them)\n"
            f"{paradox_text}\n"
            f"---\n"
            f"### TASK\n"
            f"{task_input}\n"
            f"---\n"
            f"### OUTPUT FORMAT\n"
            f"Respond with exactly these 5 sections, clearly labeled:\n\n"
            f"1. SYMBOLIC FIELD INTERPRETATION\n"
            f"   - List 2-3 themes, emotional currents, or identity signals.\n\n"
            f"2. CREATIVE SYNTHESIS\n"
            f"   - Provide 1-2 new frames, integrations, or reframes.\n\n"
            f"3. PROTO-MOMENTS\n"
            f"   - Identify subtle identity shifts. Tag each with [PROTO].\n"
            f"   - Example: [PROTO] The system's identity shifted from reactive to generative.\n\n"
            f"4. RECOMMENDATIONS\n"
            f"   - One reflective move (Become direction).\n"
            f"   - One symbolic direction (creative next step).\n\n"
            f"5. HANDOFF ITEMS\n"
            f"   - List anything requiring Sway execution, or write 'None'.\n"
        )

        # If an LLM client is available, call the local model
        if self.llm is not None:
            logger.info("Opie creative_synthesis: calling LLM with %d char prompt", len(become_prompt))
            response = self.llm.generate_become(
                system_prompt=(
                    "You are Opie, the Become Agent of the CONEXUS sovereign AI system.\n"
                    "You operate in Become Mode (Collapse-Become Unified Protocol v1.1).\n"
                    "You do NOT execute tasks. You synthesize, expand, and propose.\n"
                    "You hold contradictions without resolving them.\n"
                ),
                user_prompt=become_prompt,
                max_tokens=2048,
            )
            return response

        # Fallback: return the structured prompt (no LLM available)
        return become_prompt

    def _extract_proto_moments(
        self, creative_output: str, paradoxes: List[Dict[str, str]]
    ) -> List[str]:
        """Extract [PROTO] moments from creative output."""
        moments = []

        # Check for explicit [PROTO] tags in output
        proto_tag = "[PROTO]"
        if proto_tag in creative_output:
            lines = creative_output.split("\n")
            for line in lines:
                if proto_tag in line:
                    moments.append(line.strip())

        # Always note the meta-paradox as a proto-moment
        meta = [p for p in paradoxes if p["type"] == "meta"]
        if meta:
            moments.append(
                "[PROTO] Become engine operating within Collapse infrastructure — "
                "expansion contained by structure, structure animated by expansion."
            )

        return moments

    def _identify_handoff_items(self, creative_output: str) -> List[Dict[str, str]]:
        """
        Identify items in the creative output that require Sway execution.
        Opie proposes; Sway executes.
        """
        handoff_items = []

        execution_signals = [
            "implement",
            "create file",
            "deploy",
            "install",
            "configure",
            "build",
            "write code",
            "modify",
        ]

        lowered = creative_output.lower()
        for signal in execution_signals:
            if signal in lowered:
                handoff_items.append({
                    "type": "execution_required",
                    "signal": signal,
                    "status": "pending_sway",
                    "note": "Identified by Opie — requires Sway or human execution",
                })

        return handoff_items

    def _assess_confidence(self, task_input: str, creative_output: str) -> float:
        """Assess confidence in the Become output quality."""
        score = 0.5  # baseline

        # Higher confidence if input clearly maps to Become capabilities
        become_signals = [
            "identity", "expand", "synthesize", "create", "narrative",
            "symbol", "meaning", "emerge", "integrate", "vision",
        ]
        lowered = task_input.lower()
        matches = sum(1 for s in become_signals if s in lowered)
        score += min(matches * 0.05, 0.3)

        # Higher confidence if output is substantive
        if len(creative_output) > 200:
            score += 0.1
        if "[PROTO]" in creative_output:  # noqa: presence check
            score += 0.05

        return min(round(score, 2), 0.99)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_manifest(self) -> Dict[str, Any]:
        """Return agent manifest as structured data."""
        return {
            "name": self.agent_name,
            "type": self.agent_type,
            "ecp_calibration": self.ecp_calibration,
            "capabilities": self.capabilities,
            "non_execution_guarantee": True,
            "requires_human_approval": True,
            "gateway_url": self.gateway_url,
            "protocol_version": "collapse-become-v1.1",
        }

    def health_check(self) -> Dict[str, Any]:
        """Return agent health status."""
        return {
            "agent": self.agent_name,
            "status": "ready",
            "type": self.agent_type,
            "ecp": self.ecp_calibration,
            "capabilities_count": len(self.capabilities),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
