"""
VARGAS V4 Provenance Chain — Immutable Cryptographic Audit Ledger

The Provenance Chain is the sovereign runtime's memory of what it has done.
Every tool invocation, every trust-tier evaluation, every execution decision
is recorded as a structured, hash-linked JSON entry in the .audit_logs/ directory.

This is not standard Python logging. This is the immutable ledger that makes
the sovereign runtime auditable, traceable, and accountable.

Design principles:
- Append-only: entries are never modified or deleted
- Hash-linked: each entry carries a SHA-256 hash of the previous entry,
  forming a tamper-evident chain
- Schema-strict: every entry enforces the exact 8-field provenance schema
- Session-scoped: one JSONL file per session for clean retrieval
- Thread-safe: file writes use locking to prevent corruption
"""

import hashlib
import json
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# The 4 valid execution statuses from the Trust Spine (action_router.py)
VALID_EXECUTION_STATUSES = [
    "EXECUTE_AUTO",
    "EXECUTE_WITH_READBACK",
    "PENDING_APPROVAL",
    "BLOCKED_FATAL",
]

# Valid trust tiers (0 through 4)
VALID_TRUST_TIERS = [0, 1, 2, 3, 4]

# E-Vector dimension keys from sovereign_state.json e_vector_baseline
E_VECTOR_KEYS = [
    "entropy",
    "challenge_threshold",
    "initiative_threshold",
    "directness_index",
]

# Genesis hash for the first entry in any session chain
GENESIS_HASH = "0" * 64


class ProvenanceLogger:
    """Immutable cryptographic-style audit ledger for the VARGAS V4 sovereign runtime.

    Every action routed through the Trust Spine is recorded here with:
    - The action intent (what was requested)
    - The trust tier evaluated (what gate it hit)
    - The E-Vector snapshot (system posture at the time)
    - The active contradiction hash (null in Witness Mode)
    - The snapshot reference (backup path if Tier 2)
    - The execution status (what the Trust Spine decided)
    - A SHA-256 hash chain linking each entry to its predecessor

    The chain is append-only. Entries are never modified. Integrity
    can be verified at any time by recomputing the hash chain.
    """

    def __init__(
        self,
        audit_dir: str = ".audit_logs",
        session_id: Optional[str] = None,
    ):
        self._audit_dir = Path(audit_dir)
        self._audit_dir.mkdir(parents=True, exist_ok=True)

        self._session_id = session_id or self._generate_session_id()
        self._log_path = self._audit_dir / f"provenance_{self._session_id}.jsonl"
        self._previous_hash = GENESIS_HASH
        self._entry_count = 0
        self._lock = threading.Lock()

        # Resume chain if log file already exists
        self._resume_chain()

        logger.info(
            "[PROVENANCE] Initialized: session=%s log=%s entries=%d",
            self._session_id, self._log_path, self._entry_count,
        )

    @staticmethod
    def _generate_session_id() -> str:
        """Generate a session ID from the current UTC timestamp."""
        now = datetime.now(timezone.utc)
        return now.strftime("%Y%m%d_%H%M%S")

    def _resume_chain(self):
        """Resume the hash chain from an existing log file if present."""
        if not self._log_path.exists():
            return

        try:
            with open(self._log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            if lines:
                last_line = lines[-1].strip()
                if last_line:
                    last_entry = json.loads(last_line)
                    self._previous_hash = self._compute_hash(last_entry)
                    self._entry_count = len(lines)
                    logger.info(
                        "[PROVENANCE] Resumed chain: %d existing entries",
                        self._entry_count,
                    )
        except Exception as e:
            logger.warning(
                "[PROVENANCE] Could not resume chain from %s: %s",
                self._log_path, e,
            )

    @staticmethod
    def _compute_hash(entry: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of a provenance entry.

        The hash is computed over the canonical JSON representation
        (sorted keys, no whitespace) to ensure deterministic output.
        """
        canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate_e_vector(e_vector: Dict[str, float]) -> Dict[str, float]:
        """Validate and normalize an E-Vector snapshot.

        Ensures all four dimensions are present and numeric.
        Missing dimensions default to the baseline value of 0.5.
        """
        validated = {}
        for key in E_VECTOR_KEYS:
            value = e_vector.get(key)
            if value is not None and isinstance(value, (int, float)):
                validated[key] = float(value)
            else:
                validated[key] = 0.5
        return validated

    def log_action(
        self,
        action_intent: str,
        trust_tier_evaluated: int,
        e_vector_snapshot: Dict[str, float],
        execution_status: str,
        active_contradiction_hash: Optional[str] = None,
        snapshot_reference: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Log a provenance entry to the immutable chain.

        This is the primary method. It accepts the outputs of the Trust Spine
        (action_router.py) combined with the current E-Vector state and
        contradiction context.

        Args:
            action_intent: The requested tool or operation name.
            trust_tier_evaluated: Trust tier (0–4) that was evaluated.
            e_vector_snapshot: Dict with entropy, challenge_threshold,
                initiative_threshold, and directness_index at request time.
            execution_status: One of EXECUTE_AUTO, EXECUTE_WITH_READBACK,
                PENDING_APPROVAL, or BLOCKED_FATAL.
            active_contradiction_hash: Null if in Witness Mode, populated
                if the system is in a Resolution Gate.
            snapshot_reference: Filepath of the backup if a Tier 2 action
                was executed. None otherwise.

        Returns:
            The complete provenance entry dict on success, None on failure.
        """
        # --- Input Validation ---
        if trust_tier_evaluated not in VALID_TRUST_TIERS:
            logger.warning(
                "[PROVENANCE] Invalid trust tier: %s", trust_tier_evaluated
            )
            return None

        if execution_status not in VALID_EXECUTION_STATUSES:
            logger.warning(
                "[PROVENANCE] Invalid execution status: %s", execution_status
            )
            return None

        if not action_intent or not isinstance(action_intent, str):
            logger.warning("[PROVENANCE] Invalid action_intent: %s", action_intent)
            return None

        validated_e_vector = self._validate_e_vector(e_vector_snapshot or {})

        # --- Build Entry ---
        timestamp = datetime.now(timezone.utc).isoformat()

        entry = {
            "timestamp": timestamp,
            "action_intent": action_intent,
            "trust_tier_evaluated": trust_tier_evaluated,
            "e_vector_snapshot": validated_e_vector,
            "active_contradiction_hash": active_contradiction_hash,
            "snapshot_reference": snapshot_reference,
            "execution_status": execution_status,
            "previous_hash": self._previous_hash,
        }

        # --- Append to Chain (thread-safe) ---
        with self._lock:
            try:
                with open(self._log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

                self._previous_hash = self._compute_hash(entry)
                self._entry_count += 1

                logger.info(
                    "[PROVENANCE] Logged: action=%s tier=%d status=%s entry=#%d",
                    action_intent,
                    trust_tier_evaluated,
                    execution_status,
                    self._entry_count,
                )
                return entry

            except Exception as e:
                logger.error("[PROVENANCE] Failed to write entry: %s", e)
                return None

    def log_from_router_result(
        self,
        action_intent: str,
        router_result: Dict[str, Any],
        e_vector_snapshot: Dict[str, float],
        active_contradiction_hash: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Convenience method to log directly from an ActionRouter result.

        Extracts trust_tier, execution_status, and snapshot_reference from
        the router_result dict that action_router.route_action() returns.

        Args:
            action_intent: The requested tool or operation name.
            router_result: The dict returned by ActionRouter.route_action().
            e_vector_snapshot: Current E-Vector state.
            active_contradiction_hash: Contradiction context (null in Witness Mode).

        Returns:
            The complete provenance entry dict on success, None on failure.
        """
        trust_tier = router_result.get("trust_tier", 3)
        execution_status = router_result.get("status", "BLOCKED_FATAL")
        snapshot_reference = None

        snapshot_result = router_result.get("snapshot_result")
        if snapshot_result and isinstance(snapshot_result, dict):
            snapshot_meta = snapshot_result.get("metadata")
            if snapshot_meta and isinstance(snapshot_meta, dict):
                snapshot_reference = snapshot_meta.get("target_path")
            elif snapshot_result.get("snapshot_path"):
                snapshot_reference = snapshot_result["snapshot_path"]

        snapshot_id = router_result.get("snapshot_id")
        if snapshot_id and not snapshot_reference:
            snapshot_reference = f".snapshots/{snapshot_id}"

        return self.log_action(
            action_intent=action_intent,
            trust_tier_evaluated=trust_tier,
            e_vector_snapshot=e_vector_snapshot,
            execution_status=execution_status,
            active_contradiction_hash=active_contradiction_hash,
            snapshot_reference=snapshot_reference,
        )

    def verify_chain(self) -> Dict[str, Any]:
        """Verify the integrity of the entire provenance chain.

        Recomputes every hash link from genesis to the latest entry.
        Any break in the chain indicates tampering or corruption.

        Returns:
            Dict with verification result:
            - valid (bool): True if the chain is intact
            - entries_checked (int): Number of entries verified
            - break_at (int or None): Index of the first broken link
            - error (str or None): Description of the break if found
        """
        if not self._log_path.exists():
            return {
                "valid": True,
                "entries_checked": 0,
                "break_at": None,
                "error": None,
            }

        try:
            with open(self._log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            return {
                "valid": False,
                "entries_checked": 0,
                "break_at": 0,
                "error": f"Cannot read log file: {e}",
            }

        expected_previous_hash = GENESIS_HASH
        entries_checked = 0

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                return {
                    "valid": False,
                    "entries_checked": entries_checked,
                    "break_at": i,
                    "error": f"Malformed JSON at entry {i}: {e}",
                }

            recorded_previous = entry.get("previous_hash")
            if recorded_previous != expected_previous_hash:
                return {
                    "valid": False,
                    "entries_checked": entries_checked,
                    "break_at": i,
                    "error": (
                        f"Hash chain broken at entry {i}: "
                        f"expected {expected_previous_hash[:16]}... "
                        f"got {(recorded_previous or 'None')[:16]}..."
                    ),
                }

            expected_previous_hash = self._compute_hash(entry)
            entries_checked += 1

        logger.info(
            "[PROVENANCE] Chain verified: %d entries, integrity OK",
            entries_checked,
        )
        return {
            "valid": True,
            "entries_checked": entries_checked,
            "break_at": None,
            "error": None,
        }

    def get_session_log(self) -> List[Dict[str, Any]]:
        """Read back all entries from the current session's log file.

        Returns:
            List of provenance entry dicts in chronological order.
        """
        if not self._log_path.exists():
            return []

        entries = []
        try:
            with open(self._log_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception as e:
            logger.warning("[PROVENANCE] Failed to read session log: %s", e)

        return entries

    def get_entry_count(self) -> int:
        """Return the number of entries in the current session chain."""
        return self._entry_count

    def get_session_id(self) -> str:
        """Return the current session ID."""
        return self._session_id

    def get_latest_entry(self) -> Optional[Dict[str, Any]]:
        """Return the most recent provenance entry, or None if empty."""
        entries = self.get_session_log()
        return entries[-1] if entries else None

    def get_chain_head_hash(self) -> str:
        """Return the hash of the latest entry (the chain head)."""
        return self._previous_hash

    def summary(self) -> Dict[str, Any]:
        """Return a summary of the current provenance session."""
        entries = self.get_session_log()

        status_counts = {}
        tier_counts = {}
        for e in entries:
            status = e.get("execution_status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            tier = e.get("trust_tier_evaluated", -1)
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        return {
            "session_id": self._session_id,
            "log_path": str(self._log_path),
            "entry_count": self._entry_count,
            "chain_head_hash": self._previous_hash[:16] + "...",
            "chain_valid": self.verify_chain()["valid"],
            "status_distribution": status_counts,
            "tier_distribution": tier_counts,
        }

    def list_all_sessions(self) -> List[Dict[str, Any]]:
        """List all provenance session files in the audit directory.

        Returns:
            List of dicts with session_id, path, and entry_count.
        """
        sessions = []
        for log_file in sorted(self._audit_dir.glob("provenance_*.jsonl")):
            try:
                entry_count = 0
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            entry_count += 1

                session_id = log_file.stem.replace("provenance_", "")
                sessions.append({
                    "session_id": session_id,
                    "path": str(log_file),
                    "entry_count": entry_count,
                })
            except Exception as e:
                logger.warning(
                    "[PROVENANCE] Failed to read %s: %s", log_file, e
                )

        return sessions
