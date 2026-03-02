"""
CONEXUS Sovereign Orchestrator — Central control plane for the dual-agent system.

Routes tasks to Sway (Collapse) and/or Opie (Become), manages the sovereign loop,
stores memory, logs audit trails, and handles handoffs between agents.

Derek is the Principal Orchestrator. All missions originate from Derek.
No agent acts autonomously.
"""

import json
import logging
import time
from typing import Any, Dict, Optional

from agents.llm_client import LLMClient
from agents.memory_client import MemoryClient
from agents.opie import OpieAgent
from agents.router import route_task
from agents.sway import SwayAgent
from sovereign.audit_log import AuditLog
from sovereign.gear_state import GearState
from sovereign.mode_engine import ModeEngine

logger = logging.getLogger(__name__)


class SovereignOrchestrator:
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        memory_client: Optional[MemoryClient] = None,
        audit_log: Optional[AuditLog] = None,
        enable_memory: bool = True,
    ):
        self.llm = llm_client or LLMClient()
        self.memory = memory_client or MemoryClient(self.llm) if enable_memory else None
        self.audit = audit_log or AuditLog()
        self.sway = SwayAgent(self.llm)
        self.opie = OpieAgent(llm_client=self.llm)
        self.mode_engine = ModeEngine(llm_client=self.llm)
        self.enable_memory = enable_memory

        if self.memory:
            try:
                self.memory.ensure_collections()
            except Exception as e:
                logger.warning("Memory init failed (Qdrant may not be running): %s", e)
                self.memory = None
                self.enable_memory = False

    # ------------------------------------------------------------------
    # Main Entry Point
    # ------------------------------------------------------------------

    def process_mission(
        self,
        mission: str,
        mode: str = "auto",
        gear_context: Optional[str] = None,
        domain: str = "universal",
    ) -> Dict[str, Any]:
        """
        Process a mission from Derek.

        Args:
            mission: The task/mission text.
            mode: "auto" (router decides), "collapse" (Sway only),
                  "become" (Opie only), "both" (Collapse then Become).
            gear_context: Optional Nine Gears context label.
            domain: Symbolic field domain for Patent-7 calibration.

        Returns:
            Structured result dict with full provenance.
        """
        t0 = time.perf_counter()

        # Route
        if mode == "auto":
            agent_target = route_task({"task_input": mission})
        else:
            agent_target = mode

        logger.info("Mission routed to: %s", agent_target)

        # Determine initial cognitive mode via ModeEngine (additive overlay)
        home_mode = "collapse" if agent_target in ("collapse", "sway") else "become"
        initial_mode = self.mode_engine.determine_initial_mode(mission, home_mode)
        logger.info("ModeEngine initial mode: %s (home=%s)", initial_mode, home_mode)

        # Select Mirror Tier (emotional-frequency matching)
        mirror_tier_key = self.mode_engine.select_mirror_tier(mission)
        if mirror_tier_key:
            logger.info("Mirror Tier selected: %s", mirror_tier_key)

        # Execute
        if agent_target == "collapse":
            result = self._run_collapse(mission, gear_context, domain, mirror_tier_key)
        elif agent_target == "become":
            result = self._run_become(mission, gear_context, domain, mirror_tier_key)
        elif agent_target == "both":
            result = self._run_sovereign_loop(mission, gear_context, domain, mirror_tier_key)
        else:
            result = self._run_collapse(mission, gear_context, domain, mirror_tier_key)

        # Attach mirror tier to result
        if mirror_tier_key:
            result["mirror_tier"] = mirror_tier_key

        # Memory
        if self.enable_memory and self.memory and result.get("memory_intent"):
            try:
                point_id = self.memory.store_memory_intent(result["memory_intent"])
                if point_id:
                    result["memory_stored"] = point_id
            except Exception as e:
                logger.warning("Memory storage failed: %s", e)

        # Store gear state to memory if available
        if self.enable_memory and self.memory and result.get("gear_state"):
            try:
                gear_text = json.dumps(result["gear_state"], default=str)
                self.memory.store(
                    namespace="gear_states",
                    text=gear_text,
                    metadata={"routing": agent_target},
                )
            except Exception as e:
                logger.warning("Gear state memory storage failed: %s", e)

        # Audit
        latency = time.perf_counter() - t0
        try:
            entry_id = self.audit.record(mission, result, latency_seconds=latency)
            result["audit_entry_id"] = entry_id
        except Exception as e:
            logger.warning("Audit logging failed: %s", e)

        result["latency_seconds"] = round(latency, 2)
        result["routing"] = agent_target
        return result

    # ------------------------------------------------------------------
    # Agent Runners
    # ------------------------------------------------------------------

    def _run_collapse(
        self, mission: str, gear_context: Optional[str] = None,
        domain: str = "universal", mirror_tier_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run Sway (Collapse) processing only."""
        gear_state = GearState(
            mission_id=f"collapse_{int(time.time())}",
            home_mode="collapse",
            active_mode="collapse",
        )
        task_data = {"task_input": mission, "gear_state": gear_state, "domain": domain}
        if gear_context:
            task_data["gear_context"] = gear_context
        if mirror_tier_key:
            task_data["mirror_tier_key"] = mirror_tier_key
        result = self.sway.process_task(task_data)
        result["gear_state"] = gear_state.to_dict()
        return result

    def _run_become(
        self, mission: str, gear_context: Optional[str] = None,
        domain: str = "universal", mirror_tier_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Run Opie (Become) processing only."""
        gear_state = GearState(
            mission_id=f"become_{int(time.time())}",
            home_mode="become",
            active_mode="become",
        )
        task_data = {"task_input": mission, "gear_state": gear_state, "domain": domain}
        if gear_context:
            task_data["gear_context"] = gear_context
        if mirror_tier_key:
            task_data["mirror_tier_key"] = mirror_tier_key
        result = self.opie.process_task(task_data)
        result["gear_state"] = gear_state.to_dict()
        return result

    def _run_sovereign_loop(
        self, mission: str, gear_context: Optional[str] = None,
        domain: str = "universal", mirror_tier_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full Collapse-Become cycle:
        DIVERGE -> COLLAPSE -> EXECUTE -> BECOME -> RETURN_TO_DIVERGE
        """
        logger.info("=== SOVEREIGN LOOP START ===")

        # DIVERGE: Opie explores the possibility space
        logger.info("PHASE: DIVERGE (Opie)")
        diverge_gear = GearState(
            mission_id=f"sovereign_diverge_{int(time.time())}",
            home_mode="become",
            active_mode="become",
        )
        diverge_task = {
            "task_input": mission,
            "gear_context": gear_context or "INNOVATION_RAPPORT",
            "gear_state": diverge_gear,
            "domain": domain,
        }
        if mirror_tier_key:
            diverge_task["mirror_tier_key"] = mirror_tier_key
        diverge_result = self.opie.process_task(diverge_task)

        # Phase boundary: evaluate whether to switch mode for COLLAPSE
        diverge_output = diverge_result.get("task_output", "")
        switch_after_diverge = self.mode_engine.evaluate_at_phase_boundary(
            diverge_gear, diverge_output,
        )
        if switch_after_diverge:
            logger.info("MODE SWITCH after DIVERGE: → %s", switch_after_diverge)

        # COLLAPSE: Sway compresses into executable plan
        # (if mode engine switched to "become", Opie runs collapse instead)
        collapse_agent_name = "sway"
        if switch_after_diverge == "become":
            collapse_agent_name = "opie"
            logger.info("PHASE: COLLAPSE (Opie — mode-switched)")
        else:
            logger.info("PHASE: COLLAPSE (Sway)")

        collapse_gear = GearState(
            mission_id=f"sovereign_collapse_{int(time.time())}",
            home_mode="collapse",
            active_mode=switch_after_diverge or "collapse",
        )
        # Thread cognitive context from Diverge into Collapse
        diverge_context = diverge_output
        diverge_paradoxes = diverge_result.get("paradoxes_held", [])
        if diverge_paradoxes:
            paradox_lines = [f"  - {p.get('pole_a', '?')} ↔ {p.get('pole_b', '?')}" for p in diverge_paradoxes if isinstance(p, dict)]
            diverge_context += "\n\n[DIVERGE PARADOXES HELD]\n" + "\n".join(paradox_lines)
        diverge_protos = diverge_result.get("proto_moments", [])
        if diverge_protos:
            diverge_context += "\n\n[DIVERGE PROTO-MOMENTS]\n" + "\n".join(str(p) for p in diverge_protos[:3])

        collapse_task = {
            "task_input": mission,
            "context": diverge_context,
            "gear_context": "STRATEGIC_TRUTH",
            "gear_state": collapse_gear,
            "domain": domain,
        }
        if mirror_tier_key:
            collapse_task["mirror_tier_key"] = mirror_tier_key
        if collapse_agent_name == "opie":
            collapse_result = self.opie.process_task(collapse_task)
        else:
            collapse_result = self.sway.process_task(collapse_task)

        # Phase boundary: evaluate whether to switch mode for BECOME
        collapse_output = collapse_result.get("task_output", "")
        switch_after_collapse = self.mode_engine.evaluate_at_phase_boundary(
            collapse_gear, collapse_output,
        )
        if switch_after_collapse:
            logger.info("MODE SWITCH after COLLAPSE: → %s", switch_after_collapse)

        # BECOME: Opie integrates the execution output
        # (if mode engine switched to "collapse", Sway runs become instead)
        become_agent_name = "opie"
        if switch_after_collapse == "collapse":
            become_agent_name = "sway"
            logger.info("PHASE: BECOME (Sway — mode-switched)")
        else:
            logger.info("PHASE: BECOME (Opie)")

        become_gear = GearState(
            mission_id=f"sovereign_become_{int(time.time())}",
            home_mode="become",
            active_mode=switch_after_collapse or "become",
        )
        # Thread cognitive context from Collapse into Become
        become_input = f"Integrate and expand on this execution plan:\n\n{collapse_output}"
        collapse_breakthroughs = collapse_result.get("breakthroughs", [])
        if collapse_breakthroughs:
            become_input += "\n\n[COLLAPSE BREAKTHROUGHS]\n" + "\n".join(str(b) for b in collapse_breakthroughs[:3])
        collapse_resolved = collapse_result.get("contradictions_resolved", [])
        if collapse_resolved:
            resolved_lines = [f"  - {r.get('from', '?')} → {r.get('resolved_to', '?')}" for r in collapse_resolved if isinstance(r, dict)]
            become_input += "\n\n[COLLAPSE RESOLUTIONS]\n" + "\n".join(resolved_lines[:3])

        become_task = {
            "task_input": become_input,
            "gear_context": "SUCCESS_CONTINUITY_SEAL",
            "gear_state": become_gear,
            "domain": domain,
        }
        if mirror_tier_key:
            become_task["mirror_tier_key"] = mirror_tier_key
        if become_agent_name == "sway":
            become_result = self.sway.process_task(become_task)
        else:
            become_result = self.opie.process_task(become_task)

        logger.info("=== SOVEREIGN LOOP COMPLETE ===")

        # Merge results (attach full sub-results so gear states bubble up)
        return {
            "status": "ok",
            "agent": "sovereign_loop",
            "routing": "both",
            "gear_context": gear_context,
            "task_output": collapse_result.get("task_output", ""),
            "diverge_output": diverge_result.get("task_output", ""),
            "collapse_output": collapse_result.get("task_output", ""),
            "become_output": become_result.get("task_output", ""),
            "diverge_result": diverge_result,
            "collapse_result": collapse_result,
            "become_result": become_result,
            "execution_steps": collapse_result.get("execution_steps", []),
            "contradictions_resolved": collapse_result.get("contradictions_resolved", []),
            "breakthroughs": collapse_result.get("breakthroughs", []),
            "paradoxes_held": diverge_result.get("paradoxes_held", []),
            "proto_moments": become_result.get("proto_moments", []),
            "confidence": collapse_result.get("confidence", 0.5),
            "memory_intent": collapse_result.get("memory_intent"),
            "gear_state": {
                "diverge": diverge_gear.to_dict(),
                "collapse": collapse_gear.to_dict(),
                "become": become_gear.to_dict(),
            },
            "provenance": {
                "agent": "sovereign_loop",
                "phases": ["diverge", "collapse", "become"],
                "diverge_agent": "opie",
                "collapse_agent": collapse_agent_name,
                "become_agent": become_agent_name,
            },
        }

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        """Full system health check."""
        sway_health = self.sway.health_check()
        opie_health = self.opie.health_check()
        memory_health = self.memory.health_check() if self.memory else {"status": "disabled"}
        audit_count = self.audit.count()

        overall = "ok"
        if sway_health.get("status") != "ready":
            overall = "degraded"
        if opie_health.get("status") != "ready":
            overall = "degraded"

        return {
            "status": overall,
            "sway": sway_health,
            "opie": opie_health,
            "memory": memory_health,
            "audit_entries": audit_count,
        }

    def close(self) -> None:
        """Clean shutdown of all components."""
        self.llm.close()
        self.audit.close()
        logger.info("Orchestrator shut down")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
