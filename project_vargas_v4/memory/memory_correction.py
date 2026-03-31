"""
VARGAS V4 Memory Correction Module — Unified Corrigibility Interface

All memory is corrigible. The user has ultimate authority over what the system
remembers. This module provides a single entry point for three correction actions
across all three ECP stores:

    - forget: Permanently remove a memory by ID
    - correct: Supersede a memory with updated content (provenance preserved)
    - resolve: Mark a contradiction as resolved (ecp_contradiction only)

Every correction action is logged to an internal session audit trail so that
the Provenance Logger can record what was changed, when, and why.

This module does not contain business logic. It delegates to ECPMemoryClient
and ContradictionStore methods built in Phase 2.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from memory.memory_client import ECPMemoryClient
from memory.contradiction_store import ContradictionStore

logger = logging.getLogger(__name__)

# Valid correction action types
ACTION_FORGET = "forget"
ACTION_CORRECT = "correct"
ACTION_RESOLVE = "resolve"


class MemoryCorrector:
    """Unified corrigibility interface for VARGAS V4 ECP memory.

    Wraps forget, correct, and resolve operations across all three ECP stores
    with session-scoped audit logging.

    Usage:
        client = ECPMemoryClient()
        corrector = MemoryCorrector(client)

        corrector.forget("mem_id_123", reason="user requested removal")
        corrector.correct("mem_id_456", "updated content", reason="factual error")
        corrector.resolve("mem_id_789", resolution_notes="no longer in tension")

        log = corrector.audit_log()
    """

    def __init__(self, client: ECPMemoryClient):
        """Initialize with a shared ECPMemoryClient.

        Args:
            client: The ECP memory client instance used by the runtime.
        """
        self._client = client
        self._contradiction_store = ContradictionStore(client)
        self._session_log: List[Dict[str, Any]] = []

        logger.info("[MEMORY_CORRECTION] Initialized")

    def forget(
        self,
        memory_id: str,
        collection: Optional[str] = None,
        reason: str = "",
    ) -> bool:
        """Permanently remove a memory by ID.

        Delegates to ECPMemoryClient.forget(). The user has ultimate authority
        over what the system remembers — no memory is sacred.

        Args:
            memory_id: The ID of the memory to remove.
            collection: Specific collection to search, or None to search all.
            reason: Why this memory is being removed (for audit trail).

        Returns:
            True if the memory was found and removed, False otherwise.
        """
        result = self._client.forget(memory_id, collection)

        self._log_action(
            action=ACTION_FORGET,
            memory_id=memory_id,
            collection=collection,
            reason=reason,
            success=result,
        )

        if result:
            logger.info(
                "[MEMORY_CORRECTION] Forgot: id=%s collection=%s reason=%s",
                memory_id, collection or "all", reason,
            )
        else:
            logger.warning(
                "[MEMORY_CORRECTION] Forget failed: id=%s not found", memory_id
            )

        return result

    def correct(
        self,
        memory_id: str,
        new_content: str,
        collection: Optional[str] = None,
        reason: str = "user_correction",
    ) -> Optional[str]:
        """Supersede a memory with corrected content.

        The old memory is removed and a new one is created with the updated
        content. Provenance metadata is preserved — the new memory carries
        a 'supersedes' reference to the old memory ID.

        Args:
            memory_id: The ID of the memory to correct.
            new_content: The corrected content to store.
            collection: Specific collection, or None to search all.
            reason: Why this correction is being made (for audit trail).

        Returns:
            The new memory ID on success, None on failure.
        """
        new_id = self._client.correct(memory_id, new_content, collection, reason)

        self._log_action(
            action=ACTION_CORRECT,
            memory_id=memory_id,
            collection=collection,
            reason=reason,
            success=new_id is not None,
            new_memory_id=new_id,
        )

        if new_id:
            logger.info(
                "[MEMORY_CORRECTION] Corrected: old=%s new=%s reason=%s",
                memory_id, new_id, reason,
            )
        else:
            logger.warning(
                "[MEMORY_CORRECTION] Correct failed: id=%s not found", memory_id
            )

        return new_id

    def resolve(
        self,
        memory_id: str,
        resolution_notes: str = "",
    ) -> Optional[str]:
        """Mark a contradiction as resolved.

        Only valid for the ecp_contradiction collection. The contradiction
        is not deleted — its status is changed to 'resolved' and the
        resolution notes are appended.

        Args:
            memory_id: The ID of the contradiction to resolve.
            resolution_notes: Explanation of why this is no longer in tension.

        Returns:
            The new memory ID on success, None on failure.
        """
        new_id = self._contradiction_store.resolve(memory_id, resolution_notes)

        self._log_action(
            action=ACTION_RESOLVE,
            memory_id=memory_id,
            collection="ecp_contradiction",
            reason=resolution_notes,
            success=new_id is not None,
            new_memory_id=new_id,
        )

        if new_id:
            logger.info(
                "[MEMORY_CORRECTION] Resolved: old=%s new=%s notes=%s",
                memory_id, new_id, resolution_notes,
            )
        else:
            logger.warning(
                "[MEMORY_CORRECTION] Resolve failed: id=%s not found", memory_id
            )

        return new_id

    def audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return the session correction audit trail.

        Every forget, correct, and resolve action is recorded with its
        timestamp, memory ID, collection, reason, and outcome.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            List of audit entries, most recent last.
        """
        return self._session_log[-limit:] if self._session_log else []

    def audit_summary(self) -> Dict[str, Any]:
        """Return a summary of correction actions this session.

        Returns:
            Dict with counts per action type and total.
        """
        counts: Dict[str, int] = {
            ACTION_FORGET: 0,
            ACTION_CORRECT: 0,
            ACTION_RESOLVE: 0,
        }
        success_count = 0
        failure_count = 0

        for entry in self._session_log:
            action = entry.get("action", "")
            if action in counts:
                counts[action] += 1
            if entry.get("success"):
                success_count += 1
            else:
                failure_count += 1

        return {
            "total_actions": len(self._session_log),
            "successful": success_count,
            "failed": failure_count,
            "by_type": counts,
        }

    def _log_action(
        self,
        action: str,
        memory_id: str,
        collection: Optional[str],
        reason: str,
        success: bool,
        new_memory_id: Optional[str] = None,
    ) -> None:
        """Record a correction action to the session audit trail.

        Args:
            action: One of ACTION_FORGET, ACTION_CORRECT, ACTION_RESOLVE.
            memory_id: The target memory ID.
            collection: The collection searched.
            reason: Why the action was taken.
            success: Whether the action succeeded.
            new_memory_id: The replacement ID (for correct/resolve).
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "memory_id": memory_id,
            "collection": collection or "all",
            "reason": reason,
            "success": success,
        }
        if new_memory_id:
            entry["new_memory_id"] = new_memory_id

        self._session_log.append(entry)
