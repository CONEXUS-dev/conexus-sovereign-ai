"""
CONEXUS Sovereign Orchestrator — Central control plane for the dual-agent system.

Routes tasks to Sway (Collapse) and/or Opie (Become), manages the sovereign loop,
stores memory, logs audit trails, and handles handoffs between agents.

Derek is the Principal Orchestrator. All missions originate from Derek.
No agent acts autonomously.
"""

import logging
import time
from typing import Any, Dict, Optional

from agents.llm_client import LLMClient
from agents.memory_client import MemoryClient
from agents.opie import OpieAgent
from agents.router import route_task
from agents.sway import SwayAgent
from sovereign.audit_log import AuditLog

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
    ) -> Dict[str, Any]:
        """
        Process a mission from Derek.

        Args:
            mission: The task/mission text.
            mode: "auto" (router decides), "collapse" (Sway only),
                  "become" (Opie only), "both" (Collapse then Become).
            gear_context: Optional Nine Gears context label.

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

        # Execute
        if agent_target == "collapse":
            result = self._run_collapse(mission, gear_context)
        elif agent_target == "become":
            result = self._run_become(mission, gear_context)
        elif agent_target == "both":
            result = self._run_sovereign_loop(mission, gear_context)
        else:
            result = self._run_collapse(mission, gear_context)

        # Memory
        if self.enable_memory and self.memory and result.get("memory_intent"):
            try:
                point_id = self.memory.store_memory_intent(result["memory_intent"])
                if point_id:
                    result["memory_stored"] = point_id
            except Exception as e:
                logger.warning("Memory storage failed: %s", e)

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
        self, mission: str, gear_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run Sway (Collapse) processing only."""
        task_data = {"task_input": mission}
        if gear_context:
            task_data["gear_context"] = gear_context
        return self.sway.process_task(task_data)

    def _run_become(
        self, mission: str, gear_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run Opie (Become) processing only."""
        task_data = {"task_input": mission}
        if gear_context:
            task_data["gear_context"] = gear_context
        return self.opie.process_task(task_data)

    def _run_sovereign_loop(
        self, mission: str, gear_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Full Collapse-Become cycle:
        DIVERGE -> COLLAPSE -> EXECUTE -> BECOME -> RETURN_TO_DIVERGE
        """
        logger.info("=== SOVEREIGN LOOP START ===")

        # DIVERGE: Opie explores the possibility space
        logger.info("PHASE: DIVERGE (Opie)")
        diverge_result = self.opie.process_task({
            "task_input": mission,
            "gear_context": gear_context or "INNOVATION_RAPPORT",
        })

        # COLLAPSE: Sway compresses into executable plan
        logger.info("PHASE: COLLAPSE (Sway)")
        collapse_result = self.sway.process_task({
            "task_input": mission,
            "context": diverge_result.get("task_output", ""),
            "gear_context": "STRATEGIC_TRUTH",
        })

        # BECOME: Opie integrates the execution output
        logger.info("PHASE: BECOME (Opie)")
        become_result = self.opie.process_task({
            "task_input": (
                f"Integrate and expand on this execution plan:\n\n"
                f"{collapse_result.get('task_output', '')}"
            ),
            "gear_context": "SUCCESS_CONTINUITY_SEAL",
        })

        logger.info("=== SOVEREIGN LOOP COMPLETE ===")

        # Merge results
        return {
            "status": "ok",
            "agent": "sovereign_loop",
            "routing": "both",
            "gear_context": gear_context,
            "task_output": collapse_result.get("task_output", ""),
            "diverge_output": diverge_result.get("task_output", ""),
            "collapse_output": collapse_result.get("task_output", ""),
            "become_output": become_result.get("task_output", ""),
            "execution_steps": collapse_result.get("execution_steps", []),
            "contradictions_resolved": collapse_result.get("contradictions_resolved", []),
            "breakthroughs": collapse_result.get("breakthroughs", []),
            "paradoxes_held": diverge_result.get("paradoxes_held", []),
            "proto_moments": become_result.get("proto_moments", []),
            "confidence": collapse_result.get("confidence", 0.5),
            "memory_intent": collapse_result.get("memory_intent"),
            "provenance": {
                "agent": "sovereign_loop",
                "phases": ["diverge", "collapse", "become"],
                "diverge_agent": "opie",
                "collapse_agent": "sway",
                "become_agent": "opie",
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
