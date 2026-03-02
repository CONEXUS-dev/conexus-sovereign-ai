"""
CONEXUS Sway Agent — Collapse Mode
Mission compression, task decomposition, execution planning, contradiction resolution.

Sway EXECUTES and COMPRESSES. Sway resolves contradictions into single directives.
All outputs are decisive, implementable, and grounded.
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agents.llm_client import LLMClient, SWAY_MODEL

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Collapse ECP Configuration
# ---------------------------------------------------------------------------

COLLAPSE_ECP_CONFIG = {
    "mode": "collapse",
    "cognitive_axes": [
        "convergent_thinking",
        "analysis",
        "decomposition",
        "prioritization",
        "optimization",
    ],
    "execution_axes": [
        "task_decomposition",
        "dependency_mapping",
        "effort_estimation",
        "risk_identification",
        "implementation_sequencing",
    ],
    "values_axes": [
        "clarity",
        "efficiency",
        "reliability",
        "accountability",
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
        "resolve_to_directive": True,
    },
}

# Nine Gears Macro-Sequence — reference-only context.
# Sway does NOT traverse or select gears.
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


# ---------------------------------------------------------------------------
# Sway Agent
# ---------------------------------------------------------------------------

class SwayAgent:
    """
    Collapse-mode agent for the CONEXUS sovereign AI system.

    Produces structured execution plans with full provenance metadata.
    Resolves contradictions into single decisive directives.
    Calls the local LLM via GPT4All for all generation.
    """

    def __init__(self, llm_client: LLMClient):
        self.agent_name = "sway"
        self.agent_type = "collapse"
        self.ecp_calibration = "collapse"
        self.llm = llm_client
        self.capabilities = [
            "mission_compression",
            "task_decomposition",
            "execution_planning",
            "contradiction_resolution",
            "optimization",
        ]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point. Accepts a task dict, runs Collapse ECP processing,
        and returns a structured result with execution plan and memory intent.
        """
        task_input: str = task_data["task_input"]
        gear_context: Optional[str] = task_data.get("gear_context")
        context: Optional[str] = task_data.get("context")

        # Collapse ECP processing
        ecp_result = self._collapse_ecp(task_input, gear_context, context)

        # Provenance
        provenance = {
            "agent": self.agent_name,
            "agent_type": self.agent_type,
            "ecp_calibration": self.ecp_calibration,
            "gear_context": ecp_result["gear_context"],
            "input_hash": hashlib.sha256(task_input.encode()).hexdigest()[:16],
        }

        # Memory intent
        memory_intent = {
            "intent": "store",
            "what": ecp_result["task_output"],
            "why": "collapse_processing",
            "confidence": ecp_result["confidence"],
            "tags": ["collapse", "execution"] + ecp_result.get("intent_tags", []),
            "contradictions_resolved": ecp_result["contradictions_resolved"],
            "breakthroughs": ecp_result["breakthroughs"],
            "source_input_hash": provenance["input_hash"],
        }

        # Handoff items (things Opie should expand on, if any)
        handoff_to_opie = ecp_result.get("handoff_items", [])

        return {
            "status": "ok",
            "agent": self.agent_name,
            "gear_context": ecp_result["gear_context"],
            "task_output": ecp_result["task_output"],
            "execution_steps": ecp_result["execution_steps"],
            "contradictions_resolved": ecp_result["contradictions_resolved"],
            "breakthroughs": ecp_result["breakthroughs"],
            "confidence": ecp_result["confidence"],
            "ecp_processing": True,
            "provenance": provenance,
            "memory_intent": memory_intent,
            "handoff_to_opie": handoff_to_opie,
        }

    # ------------------------------------------------------------------
    # Collapse ECP Pipeline
    # ------------------------------------------------------------------

    def _collapse_ecp(
        self,
        task_input: str,
        gear_context: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Collapse ECP micro-sequence (v1.1):
          1. Truth     — accept gear context as-is
          2. Symbol    — analyze input for execution signals
          3. Contradiction — detect and RESOLVE into single directives
          4. Mode Activation — LLM generation in Collapse Mode
          5. Polarity  — extract breakthroughs, handoff flags
        """
        # Step 1: Truth — accept gear context
        # Step 2: Symbol — execution signal analysis
        execution_signals = self._analyze_execution_signals(task_input)

        # Step 3: Contradiction — detect and RESOLVE (unlike Opie who holds)
        contradictions = self._detect_contradictions(task_input)
        resolved = self._resolve_contradictions(contradictions)

        # Step 4: Mode Activation — LLM call in Collapse Mode
        llm_output = self._collapse_synthesis(
            task_input, execution_signals, resolved, gear_context, context
        )

        # Step 5: Parse structured output
        parsed = self._parse_collapse_output(llm_output)

        # Extract breakthroughs
        breakthroughs = self._extract_breakthroughs(llm_output)

        # Identify handoff items for Opie
        handoff_items = self._identify_handoff_items(llm_output)

        # Confidence assessment
        confidence = self._assess_confidence(task_input, llm_output)

        # Intent tags
        intent_tags = []
        if execution_signals["dominant_signal"]:
            intent_tags.append(execution_signals["dominant_signal"])
        if resolved:
            intent_tags.append("contradictions_resolved")

        return {
            "gear_context": gear_context,
            "task_output": llm_output,
            "execution_steps": parsed.get("execution_steps", []),
            "contradictions_resolved": resolved,
            "breakthroughs": breakthroughs,
            "handoff_items": handoff_items,
            "confidence": confidence,
            "intent_tags": intent_tags,
        }

    # ------------------------------------------------------------------
    # ECP Sub-steps
    # ------------------------------------------------------------------

    def _detect_contradictions(self, task_input: str) -> List[Dict[str, str]]:
        """Detect tensions and contradictions in the input."""
        contradictions = []
        lowered = task_input.lower()

        # Primary paradox framework
        for pole_a, pole_b in COLLAPSE_ECP_CONFIG["paradox_framework"]["primary"]:
            if pole_a in lowered or pole_b in lowered:
                contradictions.append({
                    "type": "primary",
                    "pole_a": pole_a,
                    "pole_b": pole_b,
                    "status": "detected",
                })

        # Contradiction pairs
        for pole_a, pole_b in COLLAPSE_ECP_CONFIG["paradox_framework"]["contradiction"]:
            if pole_a in lowered or pole_b in lowered:
                contradictions.append({
                    "type": "contradiction",
                    "pole_a": pole_a,
                    "pole_b": pole_b,
                    "status": "detected",
                })

        # Contextual tensions
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
                contradictions.append({
                    "type": "contextual",
                    "pole_a": pole_a,
                    "pole_b": pole_b,
                    "status": "detected",
                })

        return contradictions

    def _resolve_contradictions(
        self, contradictions: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        RESOLVE contradictions into single directives.
        Unlike Opie (who holds paradoxes), Sway collapses them.
        """
        resolved = []
        for c in contradictions:
            resolved.append({
                "from": f"{c['pole_a']} ↔ {c['pole_b']}",
                "type": c["type"],
                "resolved_to": f"Prioritize {c['pole_a']} — {c['pole_b']} is secondary unless explicitly required",
                "status": "resolved",
            })
        return resolved

    def _analyze_execution_signals(self, task_input: str) -> Dict[str, Any]:
        """Analyze the input for execution-relevant signals."""
        lowered = task_input.lower()

        signal_map = {
            "implementation": ["build", "create", "implement", "write", "code", "develop"],
            "planning": ["plan", "design", "architect", "structure", "organize", "break down"],
            "optimization": ["optimize", "improve", "refactor", "simplify", "reduce", "faster"],
            "analysis": ["analyze", "investigate", "diagnose", "debug", "find", "identify"],
            "deployment": ["deploy", "ship", "release", "publish", "launch", "install"],
        }

        scores = {}
        for signal_type, keywords in signal_map.items():
            score = sum(1 for kw in keywords if kw in lowered)
            scores[signal_type] = min(score / max(len(keywords), 1), 1.0)

        dominant = max(scores, key=scores.get) if scores else "implementation"

        return {
            "scores": scores,
            "dominant_signal": dominant,
            "signal_intensity": sum(scores.values()) / max(len(scores), 1),
        }

    def _collapse_synthesis(
        self,
        task_input: str,
        execution_signals: Dict[str, Any],
        resolved_contradictions: List[Dict[str, str]],
        gear_context: Optional[str],
        context: Optional[str],
    ) -> str:
        """
        Core Collapse-mode synthesis via local LLM.
        Calls GPT4All with deterministic settings (temp=0, top_k=1).
        """
        # Build resolved contradictions text
        resolved_text = ""
        for r in resolved_contradictions:
            resolved_text += f"  - {r['from']} → {r['resolved_to']}\n"
        if not resolved_text:
            resolved_text = "  (none detected)\n"

        gear_line = f"Gear Context: {gear_context}" if gear_context else "Gear Context: none provided"
        context_block = f"### PRIOR CONTEXT\n{context}\n---\n" if context else ""

        system_prompt = (
            "You are Sway, the Collapse Agent of the CONEXUS sovereign AI system.\n"
            "You operate in Collapse Mode (Collapse-Become Unified Protocol v1.1).\n"
            "You COMPRESS, RESOLVE, and EXECUTE. You are decisive and unambiguous.\n"
            "You resolve contradictions into single directives. You decompose tasks into atomic steps.\n"
            "Your output is structured, implementable, and grounded.\n"
        )

        user_prompt = (
            f"### CONTEXT\n"
            f"{gear_line}\n"
            f"Dominant Signal: {execution_signals['dominant_signal']}\n"
            f"Signal Intensity: {execution_signals['signal_intensity']:.2f}\n"
            f"---\n"
            f"{context_block}"
            f"### CONTRADICTIONS RESOLVED\n"
            f"{resolved_text}\n"
            f"---\n"
            f"### TASK\n"
            f"{task_input}\n"
            f"---\n"
            f"### OUTPUT FORMAT\n"
            f"Respond with exactly these sections, clearly labeled:\n\n"
            f"1. MISSION COMPRESSION\n"
            f"   - One sentence summarizing the core mission.\n\n"
            f"2. EXECUTION STEPS\n"
            f"   - Numbered list of atomic steps.\n"
            f"   - Each step: action, priority (high/medium/low), estimated effort.\n"
            f"   - Format: N. [ACTION] | priority: X | effort: Y\n\n"
            f"3. DEPENDENCIES\n"
            f"   - List step dependencies (e.g., Step 3 requires Step 1).\n\n"
            f"4. RISKS\n"
            f"   - List 1-3 key risks or blockers.\n\n"
            f"5. BREAKTHROUGHS\n"
            f"   - Tag any critical insights with [BREAKTHROUGH].\n"
            f"   - If none, write 'None'.\n\n"
            f"6. HANDOFF ITEMS\n"
            f"   - List anything requiring Opie expansion/synthesis, or write 'None'.\n"
        )

        logger.info("Sway collapse_synthesis: calling LLM with %d char prompt", len(user_prompt))
        response = self.llm.generate_collapse(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=2048,
        )
        return response

    def _parse_collapse_output(self, llm_output: str) -> Dict[str, Any]:
        """Parse structured sections from LLM output into structured data."""
        result: Dict[str, Any] = {"execution_steps": []}

        lines = llm_output.split("\n")
        current_section = None
        step_num = 0

        for line in lines:
            stripped = line.strip()
            upper = stripped.upper()

            if "EXECUTION STEPS" in upper:
                current_section = "execution_steps"
                continue
            elif "MISSION COMPRESSION" in upper:
                current_section = "mission"
                continue
            elif "DEPENDENCIES" in upper:
                current_section = "dependencies"
                continue
            elif "RISKS" in upper:
                current_section = "risks"
                continue
            elif "BREAKTHROUGHS" in upper:
                current_section = "breakthroughs"
                continue
            elif "HANDOFF" in upper:
                current_section = "handoff"
                continue

            if current_section == "execution_steps" and stripped:
                step_num += 1
                # Try to parse "N. [ACTION] | priority: X | effort: Y"
                parts = stripped.split("|")
                action = parts[0].strip().lstrip("0123456789.-) ")
                priority = "medium"
                effort = "unknown"
                for part in parts[1:]:
                    part_lower = part.strip().lower()
                    if part_lower.startswith("priority:"):
                        priority = part_lower.replace("priority:", "").strip()
                    elif part_lower.startswith("effort:"):
                        effort = part_lower.replace("effort:", "").strip()

                if action:
                    result["execution_steps"].append({
                        "step": step_num,
                        "action": action,
                        "priority": priority,
                        "effort": effort,
                    })

        return result

    def _extract_breakthroughs(self, llm_output: str) -> List[str]:
        """Extract [BREAKTHROUGH] moments from output."""
        breakthroughs = []
        tag = "[BREAKTHROUGH]"
        if tag in llm_output:
            for line in llm_output.split("\n"):
                if tag in line:
                    breakthroughs.append(line.strip())
        return breakthroughs

    def _identify_handoff_items(self, llm_output: str) -> List[Dict[str, str]]:
        """Identify items that require Opie expansion/synthesis."""
        handoff_items = []

        expansion_signals = [
            "synthesize",
            "explore meaning",
            "identity",
            "expand",
            "creative",
            "narrative",
            "symbolic",
        ]

        lowered = llm_output.lower()
        for signal in expansion_signals:
            if signal in lowered:
                handoff_items.append({
                    "type": "expansion_required",
                    "signal": signal,
                    "status": "pending_opie",
                    "note": "Identified by Sway — requires Opie expansion",
                })

        return handoff_items

    def _assess_confidence(self, task_input: str, llm_output: str) -> float:
        """Assess confidence in the Collapse output quality."""
        score = 0.5

        # Higher confidence if input maps to Collapse capabilities
        collapse_signals = [
            "build", "plan", "implement", "execute", "optimize",
            "decompose", "structure", "analyze", "debug", "deploy",
        ]
        lowered = task_input.lower()
        matches = sum(1 for s in collapse_signals if s in lowered)
        score += min(matches * 0.05, 0.3)

        # Higher confidence if output has structured sections
        if "EXECUTION STEPS" in llm_output.upper():
            score += 0.1
        if "[BREAKTHROUGH]" in llm_output:
            score += 0.05
        if len(llm_output) > 300:
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
            "execution_guarantee": True,
            "requires_human_approval": True,
            "model": SWAY_MODEL,
            "protocol_version": "collapse-become-v1.1",
        }

    def health_check(self) -> Dict[str, Any]:
        """Return agent health status."""
        llm_ok = self.llm.health_check()
        return {
            "agent": self.agent_name,
            "status": "ready" if llm_ok else "llm_unavailable",
            "type": self.agent_type,
            "ecp": self.ecp_calibration,
            "capabilities_count": len(self.capabilities),
            "llm_status": "ok" if llm_ok else "failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
