"""
Project Vargas V2 — Agent Loop

Plan → Execute → Observe → Iterate cycle for multi-step task execution.

Simple questions still go through the existing single-shot respond() path.
Complex tasks get decomposed into steps, each executed with tool calls,
with observation and failure handling between steps.

The LLM decides what tools to use and how to interpret results.
The loop enforces safety gates and tracks execution state.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.executor import ToolExecutor, ToolCall, SafetyLevel

logger = logging.getLogger(__name__)

# Maximum iterations to prevent infinite loops
MAX_LOOP_ITERATIONS = 15
MAX_PLAN_STEPS = 10


@dataclass
class TaskStep:
    """A single step in a task plan."""
    id: int
    description: str
    tool_name: Optional[str] = None
    tool_action: Optional[str] = None
    tool_params: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, running, completed, failed, skipped
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0


@dataclass
class TaskPlan:
    """A multi-step task plan."""
    goal: str
    steps: List[TaskStep] = field(default_factory=list)
    status: str = "draft"  # draft, approved, running, completed, failed
    current_step: int = 0
    observations: List[str] = field(default_factory=list)


class AgentLoop:
    """Plan → Execute → Observe → Iterate agent loop.

    Works with the LLM to decompose tasks, execute tool calls,
    and handle failures. The LLM is the brain; this is the execution engine.
    """

    def __init__(self, executor: ToolExecutor, llm_client: Any):
        self._executor = executor
        self._llm = llm_client
        self._active_plans: Dict[str, TaskPlan] = {}  # channel_id -> plan
        logger.info("[AGENT_LOOP] Agent loop initialized")

    def has_active_plan(self, channel_id: str) -> bool:
        """Check if there's an active plan for this channel."""
        plan = self._active_plans.get(channel_id)
        return plan is not None and plan.status in ("approved", "running")

    def get_plan_summary(self, channel_id: str) -> Optional[str]:
        """Get a human-readable summary of the current plan."""
        plan = self._active_plans.get(channel_id)
        if not plan:
            return None

        lines = [f"**Task:** {plan.goal}", f"**Status:** {plan.status}", "**Steps:**"]
        for step in plan.steps:
            status_icon = {
                "pending": "⏳", "running": "🔄", "completed": "✅",
                "failed": "❌", "skipped": "⏭️",
            }.get(step.status, "❓")
            lines.append(f"  {status_icon} Step {step.id}: {step.description}")
            if step.error:
                lines.append(f"     Error: {step.error}")

        if plan.observations:
            lines.append("**Observations:**")
            for obs in plan.observations[-3:]:
                lines.append(f"  - {obs}")

        return "\n".join(lines)

    async def analyze_complexity(self, user_message: str, system_prompt: str) -> Dict[str, Any]:
        """Ask the LLM whether this task needs a multi-step plan or single-shot response.

        Returns:
            {"needs_plan": bool, "plan": [{"description": str, "tool": str, "action": str, "params": dict}], "reasoning": str}
        """
        analysis_prompt = (
            "You are Vargas's task analyzer. Given a user request, decide:\n"
            "1. Can this be answered in a single conversational reply? (needs_plan: false)\n"
            "2. Does it require multiple tool actions? (needs_plan: true)\n\n"
            "Available tools:\n"
            "- browser: open, snapshot, click, fill, type, press, get_text, get_url, screenshot, scroll, back, forward\n"
            "- shell: run (execute shell commands)\n"
            "- file: read_file, write_file, append_file, list_dir, file_exists, delete_file, create_dir\n"
            "- web_search: search (Google search)\n"
            "- url_reader: read (fetch a single URL)\n\n"
            "If needs_plan is true, provide steps. Each step needs:\n"
            "- description: what this step does\n"
            "- tool: which tool to use (browser, shell, file, web_search, url_reader)\n"
            "- action: which action on that tool\n"
            "- params: parameters dict for the action\n\n"
            "Respond in EXACT JSON format:\n"
            '{"needs_plan": false, "reasoning": "Simple conversational question"}\n'
            "OR:\n"
            '{"needs_plan": true, "reasoning": "...", "plan": [{"description": "...", "tool": "...", "action": "...", "params": {...}}, ...]}\n\n'
            f"User request: {user_message}"
        )

        try:
            result = self._llm.generate(
                model=self._llm.default_model,
                system_prompt="You are a task complexity analyzer. Respond only in valid JSON.",
                user_prompt=analysis_prompt,
                temp=0.2,
                max_tokens=1500,
            ).strip()

            # Parse JSON — handle markdown code blocks
            if result.startswith("```"):
                result = result.split("\n", 1)[1] if "\n" in result else result
                result = result.rsplit("```", 1)[0]
            result = result.strip()

            parsed = json.loads(result)
            logger.info("[AGENT_LOOP] Complexity analysis: needs_plan=%s", parsed.get("needs_plan"))
            return parsed

        except (json.JSONDecodeError, Exception) as e:
            logger.warning("[AGENT_LOOP] Complexity analysis failed: %s", e)
            return {"needs_plan": False, "reasoning": "Analysis failed, defaulting to single-shot"}

    def create_plan(self, channel_id: str, goal: str, steps_data: List[Dict]) -> TaskPlan:
        """Create a task plan from analyzed steps."""
        steps = []
        for i, s in enumerate(steps_data[:MAX_PLAN_STEPS]):
            steps.append(TaskStep(
                id=i + 1,
                description=s.get("description", f"Step {i + 1}"),
                tool_name=s.get("tool"),
                tool_action=s.get("action"),
                tool_params=s.get("params", {}),
            ))

        plan = TaskPlan(goal=goal, steps=steps, status="draft")
        self._active_plans[channel_id] = plan
        logger.info("[AGENT_LOOP] Created plan: %s (%d steps)", goal[:60], len(steps))
        return plan

    def approve_plan(self, channel_id: str) -> bool:
        """Mark a plan as approved for execution."""
        plan = self._active_plans.get(channel_id)
        if plan and plan.status == "draft":
            plan.status = "approved"
            return True
        return False

    def cancel_plan(self, channel_id: str) -> bool:
        """Cancel the active plan."""
        if channel_id in self._active_plans:
            self._active_plans[channel_id].status = "failed"
            del self._active_plans[channel_id]
            return True
        return False

    async def execute_plan(self, channel_id: str, progress_callback=None) -> TaskPlan:
        """Execute all steps in the approved plan.

        Args:
            channel_id: The channel this plan belongs to
            progress_callback: async def callback(channel_id, message) for progress updates

        Returns:
            The completed plan with results
        """
        plan = self._active_plans.get(channel_id)
        if not plan or plan.status not in ("approved", "running"):
            return plan

        plan.status = "running"
        iterations = 0

        while plan.current_step < len(plan.steps) and iterations < MAX_LOOP_ITERATIONS:
            iterations += 1
            step = plan.steps[plan.current_step]
            step.status = "running"

            logger.info(
                "[AGENT_LOOP] Executing step %d/%d: %s",
                step.id, len(plan.steps), step.description[:60],
            )

            if progress_callback:
                await progress_callback(
                    channel_id,
                    f"⚙️ Step {step.id}/{len(plan.steps)}: {step.description}",
                )

            # Execute the tool call
            if step.tool_name and step.tool_action:
                safety = self._get_safety_level(step.tool_name, step.tool_action)
                call = ToolCall(
                    tool_name=step.tool_name,
                    action=step.tool_action,
                    params=step.tool_params or {},
                    safety_level=safety,
                    description=step.description,
                    channel_id=channel_id,
                )

                result = await self._executor.execute(call)

                if result.error:
                    step.error = result.error
                    step.retry_count += 1

                    if step.retry_count < 2:
                        # Retry once
                        plan.observations.append(
                            f"Step {step.id} failed ({result.error}), retrying..."
                        )
                        logger.info("[AGENT_LOOP] Retrying step %d", step.id)
                        continue
                    else:
                        step.status = "failed"
                        plan.observations.append(
                            f"Step {step.id} failed after retry: {result.error}"
                        )
                        # Continue to next step instead of aborting entire plan
                        plan.current_step += 1
                        continue
                else:
                    step.result = result.result
                    step.status = "completed"
                    plan.observations.append(
                        f"Step {step.id} completed: {step.description}"
                    )
            else:
                # No tool — just a planning/thinking step
                step.status = "completed"

            plan.current_step += 1

        # Determine final status
        completed = sum(1 for s in plan.steps if s.status == "completed")
        failed = sum(1 for s in plan.steps if s.status == "failed")

        if failed == 0:
            plan.status = "completed"
        elif completed > 0:
            plan.status = "completed"  # Partial success is still completed
            plan.observations.append(f"{completed}/{len(plan.steps)} steps completed, {failed} failed")
        else:
            plan.status = "failed"

        logger.info(
            "[AGENT_LOOP] Plan finished: %s (%d completed, %d failed)",
            plan.status, completed, failed,
        )

        return plan

    def _get_safety_level(self, tool_name: str, action: str) -> SafetyLevel:
        """Determine safety level for a tool+action combination."""
        # Browser read-only actions
        if tool_name == "browser" and action in (
            "open", "snapshot", "get_text", "get_url", "get_title", "screenshot",
            "back", "forward", "reload", "wait",
        ):
            return SafetyLevel.AUTO

        # File read-only actions
        if tool_name == "file" and action in ("read_file", "list_dir", "file_exists"):
            return SafetyLevel.AUTO

        # Web search and URL read are always auto
        if tool_name in ("web_search", "url_reader"):
            return SafetyLevel.AUTO

        # Shell read-only — handled by ShellTool internally, but default to gated here
        if tool_name == "shell":
            return SafetyLevel.GATED

        # Everything else is gated
        return SafetyLevel.GATED

    def build_results_context(self, channel_id: str) -> str:
        """Build a context block from plan results for prompt injection."""
        plan = self._active_plans.get(channel_id)
        if not plan:
            return ""

        lines = [f"[TASK EXECUTION RESULTS — goal: {plan.goal}]"]
        for step in plan.steps:
            if step.status == "completed" and step.result:
                result_str = str(step.result)
                if len(result_str) > 2000:
                    result_str = result_str[:2000] + "\n[Truncated]"
                lines.append(f"\nStep {step.id} ({step.description}):\n{result_str}")
            elif step.status == "failed":
                lines.append(f"\nStep {step.id} ({step.description}): FAILED — {step.error}")

        lines.append("[END TASK EXECUTION RESULTS]")
        lines.append(
            "Summarize the results naturally. If some steps failed, mention what worked "
            "and what didn't. Do not dump raw data — interpret and present it clearly."
        )
        return "\n".join(lines)

    def get_screenshot_paths(self, channel_id: str) -> List[str]:
        """Extract screenshot file paths from completed plan steps."""
        plan = self._active_plans.get(channel_id)
        if not plan:
            return []
        paths = []
        for step in plan.steps:
            if (step.status == "completed"
                    and step.tool_name == "browser"
                    and step.tool_action == "screenshot"
                    and step.result):
                result = step.result
                if isinstance(result, dict):
                    path = result.get("path") or result.get("data", "")
                else:
                    path = str(result)
                if path and Path(path).exists():
                    paths.append(path)
        return paths

    def cleanup(self, channel_id: str):
        """Remove completed/failed plans."""
        plan = self._active_plans.get(channel_id)
        if plan and plan.status in ("completed", "failed"):
            del self._active_plans[channel_id]
