# approval_system.py
"""
Dual Approval System for V4 Tool Gating
Implements keyword and Discord reaction-based approval mechanisms.
"""

import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

@dataclass
class ApprovalRequest:
    """Represents a pending approval request."""
    request_id: str
    tool_name: str
    action_description: str
    writes_state: bool
    user_id: str
    channel_id: str
    created_at: str
    expires_at: str
    status: str = "pending"  # pending, approved, rejected, expired
    approval_type: str = "dual"  # keyword, reaction, dual
    approval_method: Optional[str] = None  # How it was approved
    metadata: Optional[Dict[str, Any]] = None

class ApprovalSystem:
    """
    Dual approval system for bounded autonomous tool execution.
    
    Implements blueprint requirements:
    - Keyword approval (yes/approved/proceed) for semantic approval
    - Discord reaction approval (✅/❌) for UI confirmation
    - Intent surfacing for write operations
    - Post-write read-back verification
    """
    
    def __init__(self, approval_timeout_seconds: int = 300):
        """Initialize approval system with timeout settings."""
        self.approval_timeout = approval_timeout_seconds
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.approval_ledger: List[Dict[str, Any]] = []
        
        # Approval keywords from blueprint
        self.approval_keywords = ["yes", "approved", "proceed"]
        self.rejection_keywords = ["no", "rejected", "deny", "cancel"]
        
        # Discord reactions
        self.approval_reactions = ["✅", "👍", "👌"]
        self.rejection_reactions = ["❌", "👎", "🚫"]
        
        logger.info("[APPROVAL] System initialized")
    
    def request_approval(
        self,
        tool_name: str,
        action_description: str,
        writes_state: bool,
        user_id: str,
        channel_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ApprovalRequest:
        """
        Create an approval request for a tool action.
        
        Args:
            tool_name: Name of the tool requesting approval
            action_description: Clear description of the action
            writes_state: Whether this action modifies resources
            user_id: Discord user ID
            channel_id: Discord channel ID
            metadata: Additional context information
            
        Returns:
            ApprovalRequest object
        """
        request_id = str(uuid.uuid4())[:8]
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=self.approval_timeout)
        
        request = ApprovalRequest(
            request_id=request_id,
            tool_name=tool_name,
            action_description=action_description,
            writes_state=writes_state,
            user_id=user_id,
            channel_id=channel_id,
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
            metadata=metadata or {}
        )
        
        self.pending_requests[request_id] = request
        
        # Log to approval ledger
        ledger_entry = {
            "timestamp": now.isoformat(),
            "type": "request_created",
            "request_id": request_id,
            "tool_name": tool_name,
            "action_description": action_description,
            "writes_state": writes_state,
            "user_id": user_id,
            "channel_id": channel_id
        }
        self.approval_ledger.append(ledger_entry)
        
        logger.info(f"[APPROVAL] Request created: {request_id} for tool {tool_name}")
        return request
    
    def check_keyword_approval(
        self,
        request_id: str,
        user_message: str,
        user_id: str
    ) -> Optional[ApprovalRequest]:
        """
        Check if user message contains approval keywords.
        
        Args:
            request_id: Approval request ID
            user_message: User's response message
            user_id: User who sent the message
            
        Returns:
            Updated ApprovalRequest if approved/rejected, None otherwise
        """
        if request_id not in self.pending_requests:
            return None
        
        request = self.pending_requests[request_id]
        
        # Verify user ID matches
        if request.user_id != user_id:
            logger.warning(f"[APPROVAL] User mismatch for request {request_id}: {user_id} != {request.user_id}")
            return None
        
        # Check expiration
        if datetime.now(timezone.utc) > datetime.fromisoformat(request.expires_at):
            request.status = "expired"
            self._log_approval_completion(request, "expired", "keyword_timeout")
            return request
        
        # Check for approval keywords
        message_lower = user_message.lower().strip()
        
        # Check rejection first (more specific)
        for keyword in self.rejection_keywords:
            if keyword in message_lower:
                request.status = "rejected"
                request.approval_method = "keyword"
                self._log_approval_completion(request, "rejected", f"keyword_{keyword}")
                return request
        
        # Check approval keywords
        for keyword in self.approval_keywords:
            if keyword in message_lower:
                request.status = "approved"
                request.approval_method = "keyword"
                self._log_approval_completion(request, "approved", f"keyword_{keyword}")
                return request
        
        return None
    
    def check_reaction_approval(
        self,
        request_id: str,
        reaction: str,
        user_id: str
    ) -> Optional[ApprovalRequest]:
        """
        Check if Discord reaction indicates approval/rejection.
        
        Args:
            request_id: Approval request ID
            reaction: Discord reaction emoji
            user_id: User who reacted
            
        Returns:
            Updated ApprovalRequest if approved/rejected, None otherwise
        """
        if request_id not in self.pending_requests:
            return None
        
        request = self.pending_requests[request_id]
        
        # Verify user ID matches
        if request.user_id != user_id:
            logger.warning(f"[APPROVAL] User mismatch for request {request_id}: {user_id} != {request.user_id}")
            return None
        
        # Check expiration
        if datetime.now(timezone.utc) > datetime.fromisoformat(request.expires_at):
            request.status = "expired"
            self._log_approval_completion(request, "expired", "reaction_timeout")
            return request
        
        # Check reactions
        if reaction in self.approval_reactions:
            request.status = "approved"
            request.approval_method = "reaction"
            self._log_approval_completion(request, "approved", f"reaction_{reaction}")
            return request
        elif reaction in self.rejection_reactions:
            request.status = "rejected"
            request.approval_method = "reaction"
            self._log_approval_completion(request, "rejected", f"reaction_{reaction}")
            return request
        
        return None
    
    def execute_with_approval(
        self,
        tool_name: str,
        action_description: str,
        writes_state: bool,
        user_id: str,
        channel_id: str,
        execute_func: Callable,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool action with approval workflow.
        
        Args:
            tool_name: Name of the tool
            action_description: Description of the action
            writes_state: Whether this action modifies resources
            user_id: Discord user ID
            channel_id: Discord channel ID
            execute_func: Function to execute if approved
            metadata: Additional context
            
        Returns:
            Execution result with approval status
        """
        # For read-only actions, execute immediately
        if not writes_state:
            try:
                result = execute_func()
                self._log_direct_execution(tool_name, "read_only", True, None)
                return {
                    "approved": True,
                    "approval_method": "read_only",
                    "executed": True,
                    "result": result,
                    "error": None
                }
            except Exception as e:
                self._log_direct_execution(tool_name, "read_only", False, str(e))
                return {
                    "approved": True,
                    "approval_method": "read_only",
                    "executed": False,
                    "result": None,
                    "error": str(e)
                }
        
        # For write actions, require approval
        request = self.request_approval(
            tool_name=tool_name,
            action_description=action_description,
            writes_state=writes_state,
            user_id=user_id,
            channel_id=channel_id,
            metadata=metadata
        )
        
        return {
            "approved": False,
            "approval_method": None,
            "executed": False,
            "result": None,
            "error": None,
            "approval_request": request
        }
    
    def execute_approved_action(
        self,
        request_id: str,
        execute_func: Callable,
        verify_func: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute an approved action with optional verification.
        
        Args:
            request_id: Approval request ID
            execute_func: Function to execute
            verify_func: Optional verification function
            
        Returns:
            Execution result
        """
        if request_id not in self.pending_requests:
            return {
                "executed": False,
                "error": "Request not found or already processed",
                "verification": None
            }
        
        request = self.pending_requests[request_id]
        
        if request.status != "approved":
            return {
                "executed": False,
                "error": f"Request not approved: {request.status}",
                "verification": None
            }
        
        try:
            # Execute the action
            execution_result = execute_func()
            
            # Perform post-write verification if provided
            verification_result = None
            if verify_func:
                try:
                    verification_result = verify_func()
                except Exception as verify_error:
                    verification_result = {
                        "verified": False,
                        "error": str(verify_error)
                    }
            
            # Remove from pending requests
            del self.pending_requests[request_id]
            
            # Log successful execution
            self._log_approval_execution(request, True, execution_result, verification_result)
            
            return {
                "executed": True,
                "error": None,
                "result": execution_result,
                "verification": verification_result
            }
            
        except Exception as e:
            # Log failed execution
            self._log_approval_execution(request, False, None, None, str(e))
            
            return {
                "executed": False,
                "error": str(e),
                "result": None,
                "verification": None
            }
    
    def cleanup_expired_requests(self) -> int:
        """Clean up expired requests and return count cleaned."""
        now = datetime.now(timezone.utc)
        expired_requests = []
        
        for request_id, request in self.pending_requests.items():
            if now > datetime.fromisoformat(request.expires_at):
                request.status = "expired"
                expired_requests.append(request_id)
                self._log_approval_completion(request, "expired", "auto_cleanup")
        
        # Remove expired requests
        for request_id in expired_requests:
            del self.pending_requests[request_id]
        
        if expired_requests:
            logger.info(f"[APPROVAL] Cleaned up {len(expired_requests)} expired requests")
        
        return len(expired_requests)
    
    def get_pending_requests(self, user_id: Optional[str] = None) -> List[ApprovalRequest]:
        """Get pending approval requests, optionally filtered by user."""
        requests = list(self.pending_requests.values())
        
        if user_id:
            requests = [r for r in requests if r.user_id == user_id]
        
        # Sort by creation time (newest first)
        requests.sort(key=lambda r: r.created_at, reverse=True)
        return requests
    
    def get_approval_ledger(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent approval ledger entries."""
        return self.approval_ledger[-limit:] if self.approval_ledger else []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "pending_requests": len(self.pending_requests),
            "total_ledger_entries": len(self.approval_ledger),
            "approval_timeout_seconds": self.approval_timeout,
            "approval_keywords": self.approval_keywords,
            "rejection_keywords": self.rejection_keywords,
            "approval_reactions": self.approval_reactions,
            "rejection_reactions": self.rejection_reactions
        }
    
    def _log_approval_completion(self, request: ApprovalRequest, status: str, method: str):
        """Log approval completion to ledger."""
        ledger_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "approval_completed",
            "request_id": request.request_id,
            "status": status,
            "method": method,
            "tool_name": request.tool_name,
            "action_description": request.action_description,
            "writes_state": request.writes_state,
            "user_id": request.user_id,
            "channel_id": request.channel_id,
            "created_at": request.created_at,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        self.approval_ledger.append(ledger_entry)
    
    def _log_approval_execution(
        self,
        request: ApprovalRequest,
        success: bool,
        _result: Any,
        verification: Any,
        error: Optional[str] = None
    ):
        """Log approval execution to ledger."""
        ledger_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "approval_executed",
            "request_id": request.request_id,
            "success": success,
            "tool_name": request.tool_name,
            "action_description": request.action_description,
            "user_id": request.user_id,
            "channel_id": request.channel_id,
            "error": error,
            "verification": verification
        }
        self.approval_ledger.append(ledger_entry)
    
    def _log_direct_execution(
        self,
        tool_name: str,
        action_type: str,
        success: bool,
        error: Optional[str]
    ):
        """Log direct execution (read-only actions) to ledger."""
        ledger_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "direct_execution",
            "tool_name": tool_name,
            "action_type": action_type,
            "success": success,
            "error": error
        }
        self.approval_ledger.append(ledger_entry)
