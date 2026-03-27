"""
CONEXUS Audit Log — SQLite-based audit trail for sovereign AI operations.

Logs every orchestrator action with timestamp, agent, input/output hashes,
latency, and full result metadata for provenance and accountability.
"""

import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path(__file__).parent / "audit.db"


class AuditLog:
    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                mission TEXT NOT NULL,
                mission_hash TEXT NOT NULL,
                agent TEXT,
                mode TEXT,
                gear_context TEXT,
                status TEXT,
                confidence REAL,
                output_hash TEXT,
                output_length INTEGER,
                latency_seconds REAL,
                metadata TEXT
            )
        """)
        self._conn.commit()

    def record(
        self,
        mission: str,
        result: Dict[str, Any],
        latency_seconds: float = 0.0,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Log an orchestrator action. Returns the row ID."""
        now = datetime.now(timezone.utc).isoformat()
        mission_hash = hashlib.sha256(mission.encode()).hexdigest()[:16]
        output_text = result.get("task_output", "")
        output_hash = hashlib.sha256(output_text.encode()).hexdigest()[:16]

        metadata = {}
        if result.get("provenance"):
            metadata["provenance"] = result["provenance"]
        if result.get("breakthroughs"):
            metadata["breakthroughs"] = result["breakthroughs"]
        if result.get("contradictions_resolved"):
            metadata["contradictions_resolved"] = result["contradictions_resolved"]
        if result.get("paradoxes_held"):
            metadata["paradoxes_held"] = result["paradoxes_held"]
        if result.get("gear_state"):
            metadata["gear_state"] = result["gear_state"]
        if extra_metadata:
            metadata.update(extra_metadata)

        cursor = self._conn.execute(
            """
            INSERT INTO audit_entries
                (timestamp, mission, mission_hash, agent, mode, gear_context,
                 status, confidence, output_hash, output_length,
                 latency_seconds, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now,
                mission,
                mission_hash,
                result.get("agent", "unknown"),
                result.get("agent", "unknown"),
                result.get("gear_context"),
                result.get("status", "unknown"),
                result.get("confidence"),
                output_hash,
                len(output_text),
                latency_seconds,
                json.dumps(metadata) if metadata else None,
            ),
        )
        self._conn.commit()
        row_id = cursor.lastrowid
        logger.info(
            "Audit entry #%d: agent=%s mission_hash=%s latency=%.2fs",
            row_id, result.get("agent"), mission_hash, latency_seconds,
        )
        return row_id

    def get_recent(self, limit: int = 20) -> list[Dict[str, Any]]:
        """Retrieve the most recent audit entries."""
        cursor = self._conn.execute(
            "SELECT * FROM audit_entries ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_by_agent(self, agent: str, limit: int = 20) -> list[Dict[str, Any]]:
        """Retrieve audit entries for a specific agent."""
        cursor = self._conn.execute(
            "SELECT * FROM audit_entries WHERE agent = ? ORDER BY id DESC LIMIT ?",
            (agent, limit),
        )
        return [dict(row) for row in cursor.fetchall()]

    def count(self) -> int:
        """Total number of audit entries."""
        cursor = self._conn.execute("SELECT COUNT(*) FROM audit_entries")
        return cursor.fetchone()[0]

    def close(self) -> None:
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
