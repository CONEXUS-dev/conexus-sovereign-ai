"""
Project Vargas V2 — Tool Executor

Central dispatcher for all tool executions. Routes tool calls through
approval gates based on safety classification.

Safety levels:
  - AUTO: Read-only operations, auto-approved (search, URL read, file read, snapshot)
  - GATED: Write operations, require human approval via Discord (file write, shell, browser actions)
  - BLOCKED: Dangerous operations, always rejected (rm -rf, format, etc.)

The executor maintains a per-channel approval queue and communicates with
the Discord bot layer for human confirmation.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    AUTO = "auto"
    GATED = "gated"
    BLOCKED = "blocked"


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class ToolCall:
    """A single tool invocation request."""
    tool_name: str
    action: str
    params: Dict[str, Any]
    safety_level: SafetyLevel
    description: str  # Human-readable description for approval prompt
    channel_id: str = ""
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    result: Any = None
    error: Optional[str] = None


@dataclass
class ChannelApprovalState:
    """Per-channel approval tracking."""
    blanket_approved: bool = False  # User said "just do it" for this session
    pending_calls: Dict[str, ToolCall] = field(default_factory=dict)
    approval_events: Dict[str, asyncio.Event] = field(default_factory=dict)


class ToolExecutor:
    """Central tool dispatcher with human approval gates."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._channel_states: Dict[str, ChannelApprovalState] = {}
        self._approval_callback: Optional[Callable] = None
        self._call_counter = 0
        logger.info("[EXECUTOR] Tool executor initialized")

    def register_tool(self, name: str, handler: Callable):
        """Register a tool handler function."""
        self._tools[name] = handler
        logger.info("[EXECUTOR] Registered tool: %s", name)

    def set_approval_callback(self, callback: Callable):
        """Set the callback for requesting human approval via Discord.

        Callback signature: async def callback(channel_id: str, call_id: str, description: str) -> None
        The callback should send a message to the channel asking for approval.
        """
        self._approval_callback = callback

    def _get_channel_state(self, channel_id: str) -> ChannelApprovalState:
        if channel_id not in self._channel_states:
            self._channel_states[channel_id] = ChannelApprovalState()
        return self._channel_states[channel_id]

    def grant_blanket_approval(self, channel_id: str):
        """Grant blanket approval for all gated operations in a channel."""
        state = self._get_channel_state(channel_id)
        state.blanket_approved = True
        logger.info("[EXECUTOR] Blanket approval granted for channel %s", channel_id)

    def revoke_blanket_approval(self, channel_id: str):
        """Revoke blanket approval for a channel."""
        state = self._get_channel_state(channel_id)
        state.blanket_approved = False
        logger.info("[EXECUTOR] Blanket approval revoked for channel %s", channel_id)

    def resolve_approval(self, channel_id: str, call_id: str, approved: bool):
        """Called by Discord bot when user approves/rejects a tool call."""
        state = self._get_channel_state(channel_id)
        if call_id in state.pending_calls:
            call = state.pending_calls[call_id]
            call.approval_status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
            if call_id in state.approval_events:
                state.approval_events[call_id].set()
            logger.info(
                "[EXECUTOR] Approval resolved: %s -> %s",
                call_id, "approved" if approved else "rejected",
            )

    async def execute(self, call: ToolCall) -> ToolCall:
        """Execute a tool call, respecting safety gates.

        Returns the ToolCall with result/error populated.
        """
        # Generate unique call ID
        self._call_counter += 1
        call_id = f"tc_{self._call_counter}"

        # Check if tool exists
        if call.tool_name not in self._tools:
            call.error = f"Unknown tool: {call.tool_name}"
            logger.warning("[EXECUTOR] %s", call.error)
            return call

        # Route by safety level
        if call.safety_level == SafetyLevel.BLOCKED:
            call.error = "Operation blocked by safety policy"
            call.approval_status = ApprovalStatus.REJECTED
            logger.warning("[EXECUTOR] BLOCKED: %s — %s", call.tool_name, call.description)
            return call

        if call.safety_level == SafetyLevel.GATED:
            state = self._get_channel_state(call.channel_id)

            if not state.blanket_approved:
                # Request human approval
                call.approval_status = ApprovalStatus.PENDING
                state.pending_calls[call_id] = call
                event = asyncio.Event()
                state.approval_events[call_id] = event

                # Send approval request via Discord
                if self._approval_callback:
                    await self._approval_callback(call.channel_id, call_id, call.description)
                else:
                    logger.warning("[EXECUTOR] No approval callback set — auto-rejecting")
                    call.approval_status = ApprovalStatus.REJECTED
                    call.error = "No approval mechanism configured"
                    return call

                # Wait for approval (timeout after 120 seconds)
                try:
                    await asyncio.wait_for(event.wait(), timeout=120.0)
                except asyncio.TimeoutError:
                    call.approval_status = ApprovalStatus.TIMEOUT
                    call.error = "Approval timed out (120s)"
                    logger.warning("[EXECUTOR] Approval timeout for %s", call_id)
                    return call
                finally:
                    state.pending_calls.pop(call_id, None)
                    state.approval_events.pop(call_id, None)

                if call.approval_status == ApprovalStatus.REJECTED:
                    call.error = "User rejected this operation"
                    return call

        # Execute the tool
        try:
            handler = self._tools[call.tool_name]
            call.result = await handler(call.action, call.params)
            call.approval_status = ApprovalStatus.APPROVED
            logger.info(
                "[EXECUTOR] Executed: %s.%s [%s]",
                call.tool_name, call.action, call.safety_level.value,
            )
        except Exception as e:
            call.error = str(e)
            logger.error("[EXECUTOR] Tool error: %s.%s — %s", call.tool_name, call.action, e)

        return call

    async def execute_auto(
        self, tool_name: str, action: str, params: Dict[str, Any],
        description: str = "", channel_id: str = "",
    ) -> ToolCall:
        """Convenience: execute a read-only (auto-approved) tool call."""
        call = ToolCall(
            tool_name=tool_name,
            action=action,
            params=params,
            safety_level=SafetyLevel.AUTO,
            description=description or f"{tool_name}.{action}",
            channel_id=channel_id,
        )
        return await self.execute(call)

    async def execute_gated(
        self, tool_name: str, action: str, params: Dict[str, Any],
        description: str, channel_id: str,
    ) -> ToolCall:
        """Convenience: execute a gated (human-approved) tool call."""
        call = ToolCall(
            tool_name=tool_name,
            action=action,
            params=params,
            safety_level=SafetyLevel.GATED,
            description=description,
            channel_id=channel_id,
        )
        return await self.execute(call)
