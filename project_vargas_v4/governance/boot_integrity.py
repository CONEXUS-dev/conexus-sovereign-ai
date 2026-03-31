"""
VARGAS V4 Boot Integrity — Startup Verification Protocol

Orchestrates the boot sequence: loads constitution, verifies hashes,
and determines whether the runtime should proceed normally, enter
degraded mode, or enter quiescent mode.

Reference: Master Blueprint Section 10 — Boot Integrity Protocol
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict

from governance.constitution_loader import ConstitutionLoader
from governance.hash_verifier import HashVerifier

logger = logging.getLogger(__name__)

# Boot states
BOOT_NORMAL = "NORMAL"
BOOT_DEGRADED = "DEGRADED"
BOOT_QUIESCENT = "QUIESCENT"


class BootIntegrity:
    """Orchestrates the VARGAS V4 boot integrity protocol.

    The boot sequence:
    1. Load constitutional documents via ConstitutionLoader
    2. Verify constitutional hashes via HashVerifier
    3. Determine boot mode based on results
    4. Seal constitution hash if this is a first boot

    Boot modes:
        NORMAL: All checks pass. Full runtime available.
        DEGRADED: Some non-critical checks fail. Reduced capability.
        QUIESCENT: Critical checks fail. Read-only mode until fixed.

    Attributes:
        constitution: The loaded constitutional documents.
        verifier: The hash verifier instance.
        boot_mode: Current boot mode after checks.
        boot_report: Full report of all checks performed.
    """

    def __init__(self, project_root: str = "."):
        """Run the full boot integrity protocol.

        Args:
            project_root: Root directory of the VARGAS V4 project.
        """
        self.project_root = project_root
        self.constitution: ConstitutionLoader = ConstitutionLoader(project_root)
        self.verifier: HashVerifier = HashVerifier(project_root)
        self.boot_mode: str = BOOT_QUIESCENT
        self.boot_report: Dict[str, Any] = {}
        self._boot_timestamp = datetime.now(timezone.utc).isoformat()

        self._run_checks()

    def _run_checks(self) -> None:
        """Execute all boot integrity checks and determine boot mode."""
        checks = {
            "constitution_valid": self.constitution.valid,
            "sovereign_state_loaded": bool(self.constitution.sovereign_state),
            "trust_tiers_loaded": bool(self.constitution.trust_tiers),
            "tool_manifest_loaded": bool(self.constitution.tool_manifest),
            "memory_schema_loaded": bool(self.constitution.memory_schema),
        }

        # Verify hash integrity
        hash_result = self.verifier.verify()
        checks["hash_valid"] = hash_result["valid"]
        checks["first_boot"] = hash_result.get("first_boot", False)
        checks["tampered"] = hash_result.get("tampered_or_corrupted", False)

        # Determine boot mode
        if checks["tampered"]:
            self.boot_mode = BOOT_QUIESCENT
            logger.error("[BOOT] Constitution tampered — entering QUIESCENT mode")
        elif not checks["sovereign_state_loaded"]:
            self.boot_mode = BOOT_QUIESCENT
            logger.error("[BOOT] sovereign_state.json missing — entering QUIESCENT mode")
        elif not checks["constitution_valid"]:
            self.boot_mode = BOOT_DEGRADED
            logger.warning("[BOOT] Constitution incomplete — entering DEGRADED mode")
        else:
            self.boot_mode = BOOT_NORMAL
            logger.info("[BOOT] All checks passed — NORMAL mode")

        # Seal on first boot
        if checks["first_boot"] and checks["sovereign_state_loaded"]:
            seal_result = self.verifier.seal()
            checks["sealed"] = seal_result.get("sealed", False)
            logger.info("[BOOT] First boot — constitution sealed")

        self.boot_report = {
            "boot_mode": self.boot_mode,
            "timestamp": self._boot_timestamp,
            "checks": checks,
            "constitution_hash": self.verifier.canonical_hash,
            "constitution_summary": self.constitution.summary(),
        }

        logger.info(
            "[BOOT] Boot complete: mode=%s hash=%s",
            self.boot_mode,
            (self.verifier.canonical_hash or "")[:16],
        )

    def is_normal(self) -> bool:
        """Check if the runtime booted normally."""
        return self.boot_mode == BOOT_NORMAL

    def is_degraded(self) -> bool:
        """Check if the runtime is in degraded mode."""
        return self.boot_mode == BOOT_DEGRADED

    def is_quiescent(self) -> bool:
        """Check if the runtime is in quiescent mode."""
        return self.boot_mode == BOOT_QUIESCENT

    def get_allowed_tiers(self) -> list:
        """Return the maximum allowed trust tiers for current boot mode.

        Returns:
            List of allowed tier names.
        """
        if self.boot_mode == BOOT_NORMAL:
            return ["tier_0", "tier_1", "tier_2", "tier_3"]
        elif self.boot_mode == BOOT_DEGRADED:
            return ["tier_0", "tier_1"]
        else:
            return ["tier_0"]

    def summary(self) -> Dict[str, Any]:
        """Return boot integrity summary for diagnostics."""
        return self.boot_report
