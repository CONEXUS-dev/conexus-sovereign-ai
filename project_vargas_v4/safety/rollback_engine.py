"""
VARGAS V4 Rollback Engine — Recoverable State Changes

Manages rollback of file mutations and memory changes using snapshots
taken before Tier 2+ actions. This is what allows the trust model to
open up safely — because mistakes are recoverable.

Reference: Master Blueprint Section 10, Section 12.4 — rollback_engine.py
"""

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_SNAPSHOT_DIR = ".snapshots"


class Snapshot:
    """A pre-action snapshot of file state.

    Attributes:
        snapshot_id: Unique identifier.
        action_description: What action this snapshot was taken for.
        file_path: Path to the file that was snapshotted.
        backup_path: Path to the backup copy.
        created_at: When the snapshot was taken.
        rolled_back: Whether this snapshot has been rolled back.
    """

    def __init__(
        self,
        snapshot_id: str,
        action_description: str,
        file_path: str,
        backup_path: str,
    ):
        self.snapshot_id = snapshot_id
        self.action_description = action_description
        self.file_path = file_path
        self.backup_path = backup_path
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.rolled_back = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "snapshot_id": self.snapshot_id,
            "action_description": self.action_description,
            "file_path": self.file_path,
            "backup_path": self.backup_path,
            "created_at": self.created_at,
            "rolled_back": self.rolled_back,
        }


class RollbackEngine:
    """Manages pre-action snapshots and rollback operations.

    Workflow:
    1. Before a Tier 2+ mutation, take_snapshot() copies the target
    2. The mutation proceeds
    3. If the mutation fails or user requests rollback, rollback() restores

    Attributes:
        snapshot_dir: Directory for snapshot backups.
        snapshots: Dict of snapshots by ID.
    """

    def __init__(self, snapshot_dir: str = DEFAULT_SNAPSHOT_DIR):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots: Dict[str, Snapshot] = {}
        self._snapshot_log_path = self.snapshot_dir / "snapshot_log.jsonl"
        logger.info("[ROLLBACK] Initialized: dir=%s", self.snapshot_dir)

    def take_snapshot(
        self,
        file_path: str,
        action_description: str,
        snapshot_id: Optional[str] = None,
    ) -> Optional[Snapshot]:
        """Take a pre-action snapshot of a file.

        Args:
            file_path: Path to the file to snapshot.
            action_description: What action is about to happen.
            snapshot_id: Optional custom ID.

        Returns:
            Snapshot object, or None if the file doesn't exist.
        """
        source = Path(file_path)
        if not source.exists():
            logger.info("[ROLLBACK] No file to snapshot: %s (new file)", file_path)
            return None

        sid = snapshot_id or f"snap_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{source.name}"
        backup_path = self.snapshot_dir / sid
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.copy2(str(source), str(backup_path))
        except Exception as e:
            logger.error("[ROLLBACK] Snapshot failed for %s: %s", file_path, e)
            return None

        snapshot = Snapshot(sid, action_description, str(source), str(backup_path))
        self.snapshots[sid] = snapshot
        self._log_snapshot(snapshot, "created")

        logger.info("[ROLLBACK] Snapshot taken: %s -> %s", file_path, backup_path)
        return snapshot

    def rollback(self, snapshot_id: str) -> Dict[str, Any]:
        """Rollback a file to its snapshotted state.

        Args:
            snapshot_id: ID of the snapshot to restore.

        Returns:
            Rollback result dict.
        """
        snapshot = self.snapshots.get(snapshot_id)
        if not snapshot:
            return {"success": False, "error": f"Snapshot not found: {snapshot_id}"}

        if snapshot.rolled_back:
            return {"success": False, "error": f"Snapshot already rolled back: {snapshot_id}"}

        backup = Path(snapshot.backup_path)
        if not backup.exists():
            return {"success": False, "error": f"Backup file missing: {snapshot.backup_path}"}

        target = Path(snapshot.file_path)

        try:
            shutil.copy2(str(backup), str(target))
            snapshot.rolled_back = True
            self._log_snapshot(snapshot, "rolled_back")

            logger.info("[ROLLBACK] Restored: %s from %s", target, backup)
            return {
                "success": True,
                "snapshot_id": snapshot_id,
                "file_path": snapshot.file_path,
                "restored_from": snapshot.backup_path,
            }

        except Exception as e:
            logger.error("[ROLLBACK] Rollback failed for %s: %s", snapshot_id, e)
            return {"success": False, "error": str(e)}

    def list_snapshots(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent snapshots.

        Args:
            limit: Maximum snapshots to return.

        Returns:
            List of snapshot dicts.
        """
        all_snaps = sorted(
            self.snapshots.values(),
            key=lambda s: s.created_at,
            reverse=True,
        )
        return [s.to_dict() for s in all_snaps[:limit]]

    def _log_snapshot(self, snapshot: Snapshot, event: str) -> None:
        """Write a snapshot event to the log."""
        entry = {
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **snapshot.to_dict(),
        }
        try:
            with open(self._snapshot_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str) + "\n")
        except Exception as e:
            logger.warning("[ROLLBACK] Log write failed: %s", e)

    def summary(self) -> Dict[str, Any]:
        """Return rollback engine status summary."""
        return {
            "snapshot_dir": str(self.snapshot_dir),
            "total_snapshots": len(self.snapshots),
            "rolled_back": sum(1 for s in self.snapshots.values() if s.rolled_back),
        }
