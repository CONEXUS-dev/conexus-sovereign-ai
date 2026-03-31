"""
VARGAS V4 Tool Executor — Unified Execution Gateway

Central dispatcher for all tool invocations. Every tool call passes
through the executor, which enforces trust tier checks, snapshot-first
mutation policy, provenance logging, and approval gating before
delegating to the appropriate tool module.

The executor does NOT contain tool logic — it orchestrates.

Reference: Master Blueprint Section 7, Section 12.4 — executor.py
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Execution result states
EXEC_SUCCESS = "SUCCESS"
EXEC_FAILED = "FAILED"
EXEC_BLOCKED = "BLOCKED"
EXEC_PENDING_APPROVAL = "PENDING_APPROVAL"
EXEC_FORBIDDEN = "FORBIDDEN"


class ToolExecutor:
    """Unified execution gateway for all VARGAS V4 tool invocations.

    The executor enforces:
    1. Trust tier validation before execution
    2. Snapshot-first policy for Tier 2+ mutations
    3. Approval gating for Tier 3 actions
    4. Forbidden operation blocking for Tier 4
    5. Provenance logging for every execution attempt

    Attributes:
        tool_registry: Map of tool names to handler callables.
        max_allowed_tier: Maximum tier allowed by current boot mode.
        execution_log: Recent execution history.
    """

    def __init__(self, max_allowed_tier: int = 3):
        self.max_allowed_tier = max_allowed_tier
        self.tool_registry: Dict[str, Dict[str, Any]] = {}
        self.execution_log: list = []

        # Register built-in tool families
        self._register_defaults()
        logger.info("[EXECUTOR] Initialized: max_tier=%d", max_allowed_tier)

    def _register_defaults(self) -> None:
        """Register default tool handlers."""
        # Tool registry maps tool names to their metadata
        # Actual handlers are registered by the tool modules
        default_tools = {
            "read_file": {"tier": 0, "family": "file_io", "handler": None},
            "list_directory": {"tier": 0, "family": "file_io", "handler": None},
            "search_memory": {"tier": 0, "family": "memory", "handler": None},
            "query_provenance": {"tier": 0, "family": "provenance", "handler": None},
            "get_system_status": {"tier": 0, "family": "system", "handler": None},
            "web_search": {"tier": 1, "family": "search", "handler": None},
            "read_url": {"tier": 1, "family": "browser", "handler": None},
            "store_memory": {"tier": 1, "family": "memory", "handler": None},
            "log_provenance": {"tier": 1, "family": "provenance", "handler": None},
            "write_file": {"tier": 2, "family": "file_io", "handler": None},
            "modify_file": {"tier": 2, "family": "file_io", "handler": None},
            "correct_memory": {"tier": 2, "family": "memory", "handler": None},
            "forget_memory": {"tier": 2, "family": "memory", "handler": None},
            "execute_shell": {"tier": 3, "family": "shell", "handler": None},
            "delete_file": {"tier": 3, "family": "file_io", "handler": None},
        }
        self.tool_registry.update(default_tools)

    def register_tool(
        self,
        name: str,
        tier: int,
        family: str,
        handler: Any,
    ) -> None:
        """Register a tool handler.

        Args:
            name: Tool name.
            tier: Required trust tier.
            family: Tool family.
            handler: Callable that executes the tool.
        """
        self.tool_registry[name] = {
            "tier": tier,
            "family": family,
            "handler": handler,
        }
        logger.info("[EXECUTOR] Registered tool: %s (tier=%d family=%s)", name, tier, family)

    def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        request_id: str = "",
        approval_granted: bool = False,
        snapshot_taken: bool = False,
    ) -> Dict[str, Any]:
        """Execute a tool through the trust-gated pipeline.

        Args:
            tool_name: Name of the tool to execute.
            parameters: Tool parameters.
            request_id: Provenance request ID.
            approval_granted: Whether explicit approval was given.
            snapshot_taken: Whether a pre-action snapshot exists.

        Returns:
            Execution result dict.
        """
        now = datetime.now(timezone.utc).isoformat()
        tool_def = self.tool_registry.get(tool_name)

        # Unknown tool
        if not tool_def:
            return self._log_result(tool_name, EXEC_FAILED, request_id, now,
                                    error=f"Unknown tool: {tool_name}")

        tier = tool_def["tier"]

        # Tier 4: Forbidden
        if tier >= 4:
            return self._log_result(tool_name, EXEC_FORBIDDEN, request_id, now,
                                    error=f"Forbidden operation: {tool_name}")

        # Boot mode tier check
        if tier > self.max_allowed_tier:
            return self._log_result(tool_name, EXEC_BLOCKED, request_id, now,
                                    error=f"Tier {tier} exceeds max allowed {self.max_allowed_tier}")

        # Tier 3: Requires explicit approval
        if tier >= 3 and not approval_granted:
            return self._log_result(tool_name, EXEC_PENDING_APPROVAL, request_id, now,
                                    error="Tier 3 action requires explicit approval")

        # Tier 2: Requires snapshot
        if tier >= 2 and not snapshot_taken:
            return self._log_result(tool_name, EXEC_BLOCKED, request_id, now,
                                    error="Tier 2+ action requires pre-action snapshot")

        # Execute
        handler = tool_def.get("handler")
        if handler is None:
            return self._log_result(tool_name, EXEC_FAILED, request_id, now,
                                    error=f"No handler registered for {tool_name}")

        try:
            result = handler(**parameters)
            return self._log_result(tool_name, EXEC_SUCCESS, request_id, now,
                                    result=result)
        except Exception as e:
            return self._log_result(tool_name, EXEC_FAILED, request_id, now,
                                    error=str(e))

    def _log_result(
        self,
        tool_name: str,
        status: str,
        request_id: str,
        timestamp: str,
        result: Any = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Log and return an execution result."""
        entry = {
            "tool_name": tool_name,
            "status": status,
            "request_id": request_id,
            "timestamp": timestamp,
            "result": result,
            "error": error,
        }

        self.execution_log.append(entry)

        # Keep log bounded
        if len(self.execution_log) > 100:
            self.execution_log = self.execution_log[-50:]

        if status == EXEC_SUCCESS:
            logger.info("[EXECUTOR] %s: %s", tool_name, status)
        elif status == EXEC_PENDING_APPROVAL:
            logger.info("[EXECUTOR] %s: %s", tool_name, status)
        else:
            logger.warning("[EXECUTOR] %s: %s — %s", tool_name, status, error or "")

        return entry

    def get_tool_tier(self, tool_name: str) -> int:
        """Get the trust tier for a tool.

        Args:
            tool_name: Tool to check.

        Returns:
            Trust tier (0-4), or 4 if unknown.
        """
        tool_def = self.tool_registry.get(tool_name)
        if not tool_def:
            return 4
        return tool_def["tier"]

    def is_available(self, tool_name: str) -> bool:
        """Check if a tool is available in the current boot mode."""
        tier = self.get_tool_tier(tool_name)
        return tier <= self.max_allowed_tier and tier < 4

    def summary(self) -> Dict[str, Any]:
        """Return executor status summary."""
        available = [
            name for name in self.tool_registry
            if self.is_available(name)
        ]
        return {
            "max_allowed_tier": self.max_allowed_tier,
            "registered_tools": len(self.tool_registry),
            "available_tools": len(available),
            "recent_executions": len(self.execution_log),
        }
