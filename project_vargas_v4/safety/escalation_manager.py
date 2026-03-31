"""
VARGAS V4 Escalation Manager — Permission Escalation Orchestration

Manages the workflow when an action requires approval: formats the
request, presents it to the user, tracks the approval state, and
records the outcome in the approval log.

Reference: Master Blueprint Section 9, Section 12.4 — escalation_manager.py
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Escalation states
ESCALATION_PENDING = "PENDING"
ESCALATION_APPROVED = "APPROVED"
ESCALATION_DENIED = "DENIED"
ESCALATION_TIMEOUT = "TIMEOUT"
ESCALATION_CANCELLED = "CANCELLED"

# Default timeout
DEFAULT_TIMEOUT = 300


class EscalationRequest:
    """A single escalation request awaiting user approval.

    Attributes:
        request_id: Unique identifier.
        tool_name: Tool requiring approval.
        trust_tier: Effective trust tier.
        description: Human-readable description of what will happen.
        parameters: Sanitized tool parameters.
        status: Current escalation status.
    """

    def __init__(
        self,
        tool_name: str,
        trust_tier: int,
        description: str,
        parameters: Dict[str, Any],
    ):
        self.request_id = str(uuid.uuid4())
        self.tool_name = tool_name
        self.trust_tier = trust_tier
        self.description = description
        self.parameters = parameters
        self.status = ESCALATION_PENDING
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.resolved_at: Optional[str] = None
        self.resolved_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "request_id": self.request_id,
            "tool_name": self.tool_name,
            "trust_tier": self.trust_tier,
            "description": self.description,
            "parameters": self.parameters,
            "status": self.status,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
            "resolved_by": self.resolved_by,
        }


class EscalationManager:
    """Manages the approval escalation workflow.

    Workflow:
    1. Action is blocked by TrustModel (needs approval)
    2. EscalationManager creates a request
    3. Request is presented to user (via Discord or other interface)
    4. User approves/denies
    5. Result is recorded and action proceeds (or is blocked)

    Attributes:
        pending: Dict of pending escalation requests by ID.
        history: List of resolved escalation requests.
        timeout: Default timeout in seconds.
    """

    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.pending: Dict[str, EscalationRequest] = {}
        self.history: List[EscalationRequest] = []
        self.timeout = timeout
        logger.info("[ESCALATION] Initialized: timeout=%ds", timeout)

    def create_request(
        self,
        tool_name: str,
        trust_tier: int,
        description: str,
        parameters: Dict[str, Any],
    ) -> EscalationRequest:
        """Create a new escalation request.

        Args:
            tool_name: Tool requiring approval.
            trust_tier: Effective trust tier.
            description: What the tool will do.
            parameters: Sanitized parameters.

        Returns:
            The created EscalationRequest.
        """
        request = EscalationRequest(tool_name, trust_tier, description, parameters)
        self.pending[request.request_id] = request

        logger.info(
            "[ESCALATION] Request created: %s for %s (tier=%d)",
            request.request_id[:8], tool_name, trust_tier,
        )

        return request

    def approve(self, request_id: str, responder: str = "user") -> Optional[EscalationRequest]:
        """Approve a pending escalation request.

        Args:
            request_id: ID of the request to approve.
            responder: Who approved.

        Returns:
            The approved request, or None if not found.
        """
        request = self.pending.pop(request_id, None)
        if not request:
            logger.warning("[ESCALATION] Approve failed: request %s not found", request_id[:8])
            return None

        request.status = ESCALATION_APPROVED
        request.resolved_at = datetime.now(timezone.utc).isoformat()
        request.resolved_by = responder
        self.history.append(request)

        logger.info("[ESCALATION] Approved: %s by %s", request_id[:8], responder)
        return request

    def deny(self, request_id: str, responder: str = "user") -> Optional[EscalationRequest]:
        """Deny a pending escalation request.

        Args:
            request_id: ID of the request to deny.
            responder: Who denied.

        Returns:
            The denied request, or None if not found.
        """
        request = self.pending.pop(request_id, None)
        if not request:
            logger.warning("[ESCALATION] Deny failed: request %s not found", request_id[:8])
            return None

        request.status = ESCALATION_DENIED
        request.resolved_at = datetime.now(timezone.utc).isoformat()
        request.resolved_by = responder
        self.history.append(request)

        logger.info("[ESCALATION] Denied: %s by %s", request_id[:8], responder)
        return request

    def get_pending(self) -> List[Dict[str, Any]]:
        """Return all pending escalation requests."""
        return [r.to_dict() for r in self.pending.values()]

    def has_pending(self) -> bool:
        """Check if any escalation requests are pending."""
        return len(self.pending) > 0

    def summary(self) -> Dict[str, Any]:
        """Return escalation manager status summary."""
        return {
            "pending_count": len(self.pending),
            "history_count": len(self.history),
            "timeout": self.timeout,
        }
