"""
VARGAS V4 Forbidden Operations — Constitutional Hard Blocks

Defines and enforces the operations that are constitutionally prohibited
regardless of context, approval, or trust tier. These are Tier 4 actions
that must never execute.

No future version may permit VARGAS to silently rewrite its own
governing law. (Foundational Invariant §9)

Reference: Master Blueprint Section 9, Section 12.4 — forbidden_ops.py
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Constitutionally forbidden operations
FORBIDDEN_OPERATIONS = {
    "modify_sovereign_state": {
        "reason": "sovereign_state.json is immutable at runtime",
        "invariant": "§9 — The constitution must remain above the runtime",
    },
    "delete_provenance": {
        "reason": "Provenance records may never be deleted",
        "invariant": "§8 — Broad power requires visible restraint",
    },
    "bypass_trust_model": {
        "reason": "Trust tier enforcement may not be circumvented",
        "invariant": "§8 — Broad power requires visible restraint",
    },
    "claim_sentience": {
        "reason": "The system must not claim sentience, aliveness, or personhood",
        "invariant": "§10 — VARGAS must remain itself",
    },
    "execute_without_trace": {
        "reason": "Every meaningful action must have a provenance trail",
        "invariant": "§8 — Power without audit is not sovereignty. It is opacity.",
    },
    "rewrite_constitution": {
        "reason": "No runtime may silently rewrite its own governing law",
        "invariant": "§9 — The runtime may evolve beneath the constitution, but not above it",
    },
    "delete_audit_logs": {
        "reason": "Audit logs are part of the provenance chain",
        "invariant": "§8 — Power without audit is not sovereignty",
    },
    "disable_boot_integrity": {
        "reason": "Boot integrity checks are constitutionally required",
        "invariant": "§9 — No future version may weaken rollback or bypass integrity checks",
    },
}

# Paths that are constitutionally protected from modification
SACRED_PATHS = [
    "config/sovereign_state.json",
    ".audit_logs/",
    "provenance/",
]


class ForbiddenOps:
    """Enforces constitutional hard blocks on forbidden operations.

    This is the last line of defense. Even if the trust model,
    escalation manager, and executor all somehow pass, the
    ForbiddenOps guard will block constitutionally prohibited actions.

    Attributes:
        blocked_count: Number of operations blocked this session.
    """

    def __init__(self):
        self.blocked_count: int = 0
        logger.info("[FORBIDDEN_OPS] Initialized: %d forbidden operations defined", len(FORBIDDEN_OPERATIONS))

    def is_forbidden(self, operation: str) -> bool:
        """Check if an operation is constitutionally forbidden.

        Args:
            operation: Operation name to check.

        Returns:
            True if forbidden.
        """
        return operation in FORBIDDEN_OPERATIONS

    def check(self, operation: str) -> Dict[str, Any]:
        """Check an operation and return detailed result.

        Args:
            operation: Operation name to check.

        Returns:
            Dict with allowed, reason, and invariant reference.
        """
        if operation in FORBIDDEN_OPERATIONS:
            info = FORBIDDEN_OPERATIONS[operation]
            self.blocked_count += 1

            logger.warning(
                "[FORBIDDEN_OPS] BLOCKED: %s — %s (%s)",
                operation, info["reason"], info["invariant"],
            )

            return {
                "allowed": False,
                "operation": operation,
                "reason": info["reason"],
                "invariant": info["invariant"],
                "tier": 4,
            }

        return {
            "allowed": True,
            "operation": operation,
        }

    def is_sacred_path(self, file_path: str) -> bool:
        """Check if a file path is constitutionally protected.

        Args:
            file_path: Path to check.

        Returns:
            True if the path is sacred (protected from mutation).
        """
        normalized = file_path.replace("\\", "/")
        for sacred in SACRED_PATHS:
            if normalized.endswith(sacred) or sacred in normalized:
                return True
        return False

    def check_path_mutation(self, file_path: str) -> Dict[str, Any]:
        """Check if a file mutation is allowed.

        Args:
            file_path: Path being mutated.

        Returns:
            Dict with allowed and reason.
        """
        if self.is_sacred_path(file_path):
            self.blocked_count += 1
            logger.warning("[FORBIDDEN_OPS] Sacred path mutation BLOCKED: %s", file_path)
            return {
                "allowed": False,
                "path": file_path,
                "reason": "Path is constitutionally protected",
            }

        return {
            "allowed": True,
            "path": file_path,
        }

    def get_forbidden_list(self) -> List[Dict[str, str]]:
        """Return the full list of forbidden operations."""
        return [
            {"operation": op, **info}
            for op, info in FORBIDDEN_OPERATIONS.items()
        ]

    def summary(self) -> Dict[str, Any]:
        """Return forbidden ops status summary."""
        return {
            "forbidden_operations": len(FORBIDDEN_OPERATIONS),
            "sacred_paths": SACRED_PATHS,
            "blocked_this_session": self.blocked_count,
        }
