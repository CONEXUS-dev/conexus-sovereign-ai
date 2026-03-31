"""
VARGAS V4 Plan Manager — Multi-Step Operation Orchestration

Manages multi-step plans for complex requests. When a user request
requires more than one tool invocation or multiple sequential actions,
the Plan Manager breaks it into steps, tracks progress, and maintains
plan state across the execution lifecycle.

Plans are not executed here — they are assembled, tracked, and reported.
Execution happens through the tool executor layer.

Reference: Master Blueprint Section 12.4 — plan_manager.py
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Plan states
PLAN_DRAFT = "DRAFT"
PLAN_ACTIVE = "ACTIVE"
PLAN_COMPLETED = "COMPLETED"
PLAN_FAILED = "FAILED"
PLAN_CANCELLED = "CANCELLED"

# Step states
STEP_PENDING = "PENDING"
STEP_IN_PROGRESS = "IN_PROGRESS"
STEP_COMPLETED = "COMPLETED"
STEP_FAILED = "FAILED"
STEP_SKIPPED = "SKIPPED"


class PlanStep:
    """A single step within a plan.

    Attributes:
        step_id: Unique identifier for this step.
        description: What this step does.
        tool_name: Which tool to invoke.
        parameters: Parameters for the tool.
        trust_tier: Required trust tier.
        status: Current step status.
        result: Execution result (set after completion).
        error: Error message if failed.
    """

    def __init__(
        self,
        description: str,
        tool_name: str,
        parameters: Dict[str, Any],
        trust_tier: int = 0,
        depends_on: Optional[List[str]] = None,
    ):
        self.step_id: str = str(uuid.uuid4())[:8]
        self.description = description
        self.tool_name = tool_name
        self.parameters = parameters
        self.trust_tier = trust_tier
        self.depends_on: List[str] = depends_on or []
        self.status: str = STEP_PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize step to dict."""
        return {
            "step_id": self.step_id,
            "description": self.description,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "trust_tier": self.trust_tier,
            "depends_on": self.depends_on,
            "status": self.status,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class Plan:
    """A multi-step execution plan.

    Attributes:
        plan_id: Unique identifier for this plan.
        description: What this plan accomplishes.
        steps: Ordered list of plan steps.
        status: Current plan status.
        max_trust_tier: Highest trust tier among all steps.
    """

    def __init__(self, description: str):
        self.plan_id: str = str(uuid.uuid4())
        self.description = description
        self.steps: List[PlanStep] = []
        self.status: str = PLAN_DRAFT
        self.created_at: str = datetime.now(timezone.utc).isoformat()
        self.completed_at: Optional[str] = None

    @property
    def max_trust_tier(self) -> int:
        """Return the highest trust tier among all steps."""
        if not self.steps:
            return 0
        return max(s.trust_tier for s in self.steps)

    def add_step(
        self,
        description: str,
        tool_name: str,
        parameters: Dict[str, Any],
        trust_tier: int = 0,
        depends_on: Optional[List[str]] = None,
    ) -> PlanStep:
        """Add a step to the plan.

        Args:
            description: What the step does.
            tool_name: Tool to invoke.
            parameters: Tool parameters.
            trust_tier: Required trust tier.
            depends_on: Step IDs this step depends on.

        Returns:
            The created PlanStep.
        """
        step = PlanStep(description, tool_name, parameters, trust_tier, depends_on)
        self.steps.append(step)
        return step

    def get_next_step(self) -> Optional[PlanStep]:
        """Get the next step that is ready to execute.

        A step is ready when:
        - Its status is PENDING
        - All dependencies are COMPLETED

        Returns:
            Next ready step, or None if no step is ready.
        """
        completed_ids = {s.step_id for s in self.steps if s.status == STEP_COMPLETED}

        for step in self.steps:
            if step.status != STEP_PENDING:
                continue
            if all(dep in completed_ids for dep in step.depends_on):
                return step

        return None

    def mark_step_complete(self, step_id: str, result: Dict[str, Any] = None) -> None:
        """Mark a step as completed."""
        for step in self.steps:
            if step.step_id == step_id:
                step.status = STEP_COMPLETED
                step.result = result
                step.completed_at = datetime.now(timezone.utc).isoformat()
                break

        # Check if all steps are done
        if all(s.status in (STEP_COMPLETED, STEP_SKIPPED) for s in self.steps):
            self.status = PLAN_COMPLETED
            self.completed_at = datetime.now(timezone.utc).isoformat()

    def mark_step_failed(self, step_id: str, error: str) -> None:
        """Mark a step as failed and fail the plan."""
        for step in self.steps:
            if step.step_id == step_id:
                step.status = STEP_FAILED
                step.error = error
                step.completed_at = datetime.now(timezone.utc).isoformat()
                break

        self.status = PLAN_FAILED
        self.completed_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize plan to dict."""
        return {
            "plan_id": self.plan_id,
            "description": self.description,
            "status": self.status,
            "max_trust_tier": self.max_trust_tier,
            "steps": [s.to_dict() for s in self.steps],
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "progress": f"{sum(1 for s in self.steps if s.status == STEP_COMPLETED)}/{len(self.steps)}",
        }


class PlanManager:
    """Manages the lifecycle of execution plans.

    The Plan Manager does NOT execute plans. It:
    1. Creates plans from intent analysis
    2. Tracks step progress
    3. Reports plan status
    4. Maintains plan history

    Attributes:
        current_plan: The currently active plan (if any).
        history: List of completed/cancelled plans.
    """

    def __init__(self):
        self.current_plan: Optional[Plan] = None
        self.history: List[Plan] = []
        logger.info("[PLAN_MANAGER] Initialized")

    def create_plan(self, description: str) -> Plan:
        """Create a new plan.

        If a plan is already active, it is archived to history.

        Args:
            description: What this plan accomplishes.

        Returns:
            The new Plan instance.
        """
        if self.current_plan and self.current_plan.status == PLAN_ACTIVE:
            self.current_plan.status = PLAN_CANCELLED
            self.history.append(self.current_plan)

        plan = Plan(description)
        self.current_plan = plan
        logger.info("[PLAN_MANAGER] Plan created: %s", plan.plan_id[:8])
        return plan

    def activate_plan(self) -> bool:
        """Activate the current draft plan.

        Returns:
            True if activated successfully.
        """
        if not self.current_plan:
            return False
        if self.current_plan.status != PLAN_DRAFT:
            return False
        if not self.current_plan.steps:
            return False

        self.current_plan.status = PLAN_ACTIVE
        logger.info(
            "[PLAN_MANAGER] Plan activated: %s (%d steps, max tier %d)",
            self.current_plan.plan_id[:8],
            len(self.current_plan.steps),
            self.current_plan.max_trust_tier,
        )
        return True

    def get_next_step(self) -> Optional[PlanStep]:
        """Get the next executable step from the active plan."""
        if not self.current_plan or self.current_plan.status != PLAN_ACTIVE:
            return None
        return self.current_plan.get_next_step()

    def complete_step(self, step_id: str, result: Dict[str, Any] = None) -> None:
        """Mark a step as completed."""
        if self.current_plan:
            self.current_plan.mark_step_complete(step_id, result)
            if self.current_plan.status == PLAN_COMPLETED:
                logger.info("[PLAN_MANAGER] Plan completed: %s", self.current_plan.plan_id[:8])
                self.history.append(self.current_plan)

    def fail_step(self, step_id: str, error: str) -> None:
        """Mark a step as failed."""
        if self.current_plan:
            self.current_plan.mark_step_failed(step_id, error)
            logger.warning(
                "[PLAN_MANAGER] Step failed: %s — %s",
                step_id, error,
            )
            self.history.append(self.current_plan)

    def has_active_plan(self) -> bool:
        """Check if there is an active plan."""
        return self.current_plan is not None and self.current_plan.status == PLAN_ACTIVE

    def summary(self) -> Dict[str, Any]:
        """Return plan manager status summary."""
        return {
            "has_active_plan": self.has_active_plan(),
            "current_plan": self.current_plan.to_dict() if self.current_plan else None,
            "history_count": len(self.history),
        }
