"""
VARGAS V4 Hash Verifier — Constitutional Integrity Guard

Computes and verifies SHA-256 hashes of constitutional files to detect
tampering or corruption. Used by boot_integrity.py to determine whether
the runtime should enter degraded or quiescent mode.

Reference: Master Blueprint Section 10 — Boot Integrity Protocol
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

SACRED_PATHS = [
    "config/sovereign_state.json",
    "config/trust_tiers.yaml",
    "config/tool_manifest.yaml",
    "config/memory_schema.yaml",
]

HASH_LOG_PATH = ".audit_logs/constitution_hashes.jsonl"


class HashVerifier:
    """Computes and verifies constitutional file hashes.

    The Hash Verifier provides two core operations:
    1. Seal: compute and store the canonical hash of all sacred files.
    2. Verify: recompute and compare against the stored canonical hash.

    If verification fails, the runtime must not proceed normally.

    Attributes:
        project_root: Root directory of the project.
        canonical_hash: The stored hash from the last seal operation.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.canonical_hash: Optional[str] = None
        self._load_canonical_hash()

    def _load_canonical_hash(self) -> None:
        """Load the last sealed canonical hash from the hash log."""
        log_path = self.project_root / HASH_LOG_PATH
        if not log_path.exists():
            logger.info("[HASH_VERIFIER] No canonical hash found — first boot")
            return

        try:
            lines = log_path.read_text(encoding="utf-8").strip().split("\n")
            if lines:
                last_entry = json.loads(lines[-1])
                self.canonical_hash = last_entry.get("hash")
                logger.info(
                    "[HASH_VERIFIER] Canonical hash loaded: %s",
                    self.canonical_hash[:16] if self.canonical_hash else "None",
                )
        except Exception as e:
            logger.warning("[HASH_VERIFIER] Failed to load canonical hash: %s", e)

    def compute_hash(self, paths: Optional[List[str]] = None) -> str:
        """Compute SHA-256 hash of the specified constitutional files.

        Args:
            paths: List of relative paths. Defaults to SACRED_PATHS.

        Returns:
            Hex digest of the combined hash.
        """
        target_paths = paths or SACRED_PATHS
        hasher = hashlib.sha256()

        for rel_path in sorted(target_paths):
            full_path = self.project_root / rel_path
            if full_path.exists():
                try:
                    content = full_path.read_bytes()
                    hasher.update(rel_path.encode("utf-8"))
                    hasher.update(content)
                except Exception as e:
                    logger.warning("[HASH_VERIFIER] Read failed for %s: %s", rel_path, e)
                    hasher.update(f"ERROR:{rel_path}:{e}".encode("utf-8"))
            else:
                hasher.update(f"MISSING:{rel_path}".encode("utf-8"))

        return hasher.hexdigest()

    def seal(self) -> Dict[str, Any]:
        """Seal the current constitution by storing its hash.

        Returns:
            Dict with seal result including the hash and timestamp.
        """
        current_hash = self.compute_hash()
        now = datetime.now(timezone.utc).isoformat()

        entry = {
            "event": "seal",
            "hash": current_hash,
            "timestamp": now,
            "files": SACRED_PATHS,
        }

        log_path = self.project_root / HASH_LOG_PATH
        log_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error("[HASH_VERIFIER] Failed to write seal entry: %s", e)

        self.canonical_hash = current_hash
        logger.info("[HASH_VERIFIER] Constitution sealed: %s", current_hash[:16])

        return {
            "sealed": True,
            "hash": current_hash,
            "timestamp": now,
        }

    def verify(self) -> Dict[str, Any]:
        """Verify the current constitution against the sealed hash.

        Returns:
            Dict containing:
                - valid: True if hashes match or no canonical exists (first boot)
                - current_hash: The just-computed hash
                - canonical_hash: The stored canonical hash
                - first_boot: True if no canonical hash exists
                - tampered_or_corrupted: True if mismatch detected
        """
        current_hash = self.compute_hash()

        if self.canonical_hash is None:
            logger.info("[HASH_VERIFIER] First boot — no canonical to compare")
            return {
                "valid": True,
                "current_hash": current_hash,
                "canonical_hash": None,
                "first_boot": True,
                "tampered_or_corrupted": False,
            }

        match = current_hash == self.canonical_hash

        if match:
            logger.info("[HASH_VERIFIER] Verification PASSED")
        else:
            logger.error(
                "[HASH_VERIFIER] Verification FAILED — expected %s, got %s",
                self.canonical_hash[:16],
                current_hash[:16],
            )

        now = datetime.now(timezone.utc).isoformat()
        entry = {
            "event": "verify",
            "result": "pass" if match else "fail",
            "current_hash": current_hash,
            "canonical_hash": self.canonical_hash,
            "timestamp": now,
        }

        log_path = self.project_root / HASH_LOG_PATH
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.warning("[HASH_VERIFIER] Failed to log verification: %s", e)

        return {
            "valid": match,
            "current_hash": current_hash,
            "canonical_hash": self.canonical_hash,
            "first_boot": False,
            "tampered_or_corrupted": not match,
        }

    def get_file_hashes(self) -> Dict[str, str]:
        """Return individual SHA-256 hashes for each sacred file.

        Returns:
            Dict mapping file path to its individual hash.
        """
        result = {}
        for rel_path in SACRED_PATHS:
            full_path = self.project_root / rel_path
            if full_path.exists():
                try:
                    content = full_path.read_bytes()
                    result[rel_path] = hashlib.sha256(content).hexdigest()
                except Exception:
                    result[rel_path] = "ERROR"
            else:
                result[rel_path] = "MISSING"
        return result

    def summary(self) -> Dict[str, Any]:
        """Return verifier status summary."""
        return {
            "canonical_hash": self.canonical_hash[:16] + "..." if self.canonical_hash else None,
            "sacred_paths": SACRED_PATHS,
            "file_hashes": {k: v[:16] + "..." for k, v in self.get_file_hashes().items()},
        }
