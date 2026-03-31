"""
VARGAS V4 Contradiction Store — ECP-Native Semantic Memory

The Contradiction Store is the most important store in the V4 breakthrough.
It is where unresolved paradoxes are preserved as structured fuel for the runtime.

V4 formalizes contradiction as a first-class memory object. Contradiction is no
longer just something the system notices. It becomes something the system can
store, retrieve, rank, revisit, decay, resolve, and use to calibrate posture
and action.

CRITICAL ARCHITECTURAL CONSTRAINT:
Contradictions cannot be stored as soft, conversational text. Every contradiction
MUST be formatted as a structured JSON object containing:
    - statement_a: The first pole of the contradiction
    - statement_b: The opposing pole
    - severity_score: Float (0.0-1.0) indicating tension intensity
    - status: One of 'active', 'resolved', 'superseded', 'archived', 'decayed'
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from memory.memory_client import ECPMemoryClient, CONTRADICTION_SUBTYPES

logger = logging.getLogger(__name__)

COLLECTION = "ecp_contradiction"

VALID_STATUSES = ["active", "resolved", "superseded", "archived", "decayed"]


class ContradictionStore:
    """ECP Contradiction Store for VARGAS V4.

    Stores unresolved paradoxes as structured runtime fuel. Contradiction
    should not just flavor tone — it should change what the runtime does.

    Contradictions are stored as structured JSON objects, never as soft
    conversational text.

    What belongs here:
    - Conflict between stated goal and repeated behavior
    - Conflict between declared urgency and deferred action
    - Conflict between system claim and implementation evidence
    - Repeated architectural mismatch
    - Value conflict between two user commitments
    - Contradiction between desired autonomy and requested safety posture

    What does NOT belong here:
    - Vague feelings
    - Temporary session frustration
    - Resolved tensions (must be marked status='resolved', not deleted)
    """

    def __init__(self, client: ECPMemoryClient):
        self._client = client

    @staticmethod
    def _build_contradiction_payload(
        statement_a: str,
        statement_b: str,
        severity_score: float,
        status: str = "active",
        topic_similarity: Optional[float] = None,
        implication_similarity: Optional[float] = None,
        challenge_eligible: bool = True,
        initiative_effect: float = 0.0,
        directness_effect: float = 0.0,
        decay_score: float = 1.0,
        notes: str = "",
    ) -> str:
        """Build a structured contradiction payload as a JSON string.

        This is the enforced format. No contradiction may be stored
        without this structure.

        Args:
            statement_a: First pole of the contradiction.
            statement_b: Opposing pole.
            severity_score: Tension intensity (0.0-1.0).
            status: One of VALID_STATUSES.
            topic_similarity: Cosine similarity of topics (if computed).
            implication_similarity: Cosine similarity of implications (if computed).
            challenge_eligible: Whether this contradiction can trigger challenge mode.
            initiative_effect: Effect on initiative threshold (-1.0 to 1.0).
            directness_effect: Effect on directness index (-1.0 to 1.0).
            decay_score: Current decay value (1.0 = fresh, approaches 0.0 over time).
            notes: Optional free-text annotation.

        Returns:
            JSON string of the structured contradiction object.
        """
        if status not in VALID_STATUSES:
            status = "active"

        severity_score = max(0.0, min(1.0, severity_score))
        decay_score = max(0.0, min(1.0, decay_score))

        payload = {
            "statement_a": statement_a,
            "statement_b": statement_b,
            "severity_score": severity_score,
            "status": status,
            "topic_similarity": topic_similarity,
            "implication_similarity": implication_similarity,
            "challenge_eligible": challenge_eligible,
            "initiative_effect": initiative_effect,
            "directness_effect": directness_effect,
            "decay_score": decay_score,
            "notes": notes,
        }

        return json.dumps(payload, ensure_ascii=False)

    def store(
        self,
        statement_a: str,
        statement_b: str,
        severity_score: float,
        subtype: str,
        status: str = "active",
        confidence: float = 0.8,
        topic_similarity: Optional[float] = None,
        implication_similarity: Optional[float] = None,
        challenge_eligible: bool = True,
        initiative_effect: float = 0.0,
        directness_effect: float = 0.0,
        decay_score: float = 1.0,
        notes: str = "",
        source_request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        project_scope: str = "vargas_v4",
    ) -> Optional[str]:
        """Store a structured contradiction.

        Args:
            statement_a: First pole of the contradiction.
            statement_b: Opposing pole.
            severity_score: Tension intensity (0.0-1.0).
            subtype: One of CONTRADICTION_SUBTYPES.
            status: One of VALID_STATUSES.
            confidence: Write confidence.
            topic_similarity: Cosine similarity of topics (if computed).
            implication_similarity: Cosine similarity of implications (if computed).
            challenge_eligible: Whether this can trigger challenge mode.
            initiative_effect: Effect on initiative threshold.
            directness_effect: Effect on directness index.
            decay_score: Current decay value.
            notes: Optional annotation.
            source_request_id: Provenance link.
            session_id: Current session.
            project_scope: Scope boundary.

        Returns:
            memory_id on success, None on failure.
        """
        if subtype not in CONTRADICTION_SUBTYPES:
            logger.warning("[CONTRADICTION_STORE] Invalid subtype: %s", subtype)
            return None

        if status not in VALID_STATUSES:
            logger.warning("[CONTRADICTION_STORE] Invalid status: %s", status)
            return None

        content = self._build_contradiction_payload(
            statement_a=statement_a,
            statement_b=statement_b,
            severity_score=severity_score,
            status=status,
            topic_similarity=topic_similarity,
            implication_similarity=implication_similarity,
            challenge_eligible=challenge_eligible,
            initiative_effect=initiative_effect,
            directness_effect=directness_effect,
            decay_score=decay_score,
            notes=notes,
        )

        now = datetime.now(timezone.utc).isoformat()

        metadata = {
            "severity": severity_score,
            "first_seen": now,
            "last_seen": now,
            "active_flag": status == "active",
            "challenge_eligible": challenge_eligible,
            "initiative_effect": initiative_effect,
            "directness_effect": directness_effect,
            "decay_score": decay_score,
        }

        challenge_weight = severity_score if challenge_eligible else 0.0

        memory_id = self._client.store(
            collection=COLLECTION,
            content=content,
            subtype=subtype,
            confidence=confidence,
            source_request_id=source_request_id,
            session_id=session_id,
            project_scope=project_scope,
            challenge_weight=challenge_weight,
            metadata=metadata,
        )

        if memory_id:
            logger.info(
                "[CONTRADICTION_STORE] Stored: subtype=%s severity=%.2f status=%s id=%s",
                subtype, severity_score, status, memory_id,
            )
        return memory_id

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_subtype: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve contradictions relevant to a query.

        Returns only active contradictions by default.
        """
        results = self._client.retrieve(
            query=query,
            collection=COLLECTION,
            top_k=top_k,
            filter_subtype=filter_subtype,
            filter_status="active",
        )
        return self._enrich_results(results)

    def retrieve_fuel(
        self,
        query: str,
        top_k: int = 3,
        min_severity: float = 0.3,
        min_decay: float = 0.1,
    ) -> List[Dict[str, Any]]:
        """Retrieve contradictions as runtime fuel for the Paradox Engine.

        Filters by:
        - active status
        - challenge_eligible = True
        - severity >= min_severity
        - decay_score >= min_decay

        Sorted by severity * decay_score descending (highest fuel first).
        """
        all_active = self._client.retrieve(
            query=query,
            collection=COLLECTION,
            top_k=top_k * 5,
            filter_status="active",
        )

        fuel = []
        for r in all_active:
            meta = r.get("metadata", {})
            if not meta.get("challenge_eligible", False):
                continue
            severity = meta.get("severity", 0.0)
            decay = meta.get("decay_score", 0.0)
            if severity < min_severity or decay < min_decay:
                continue

            r["fuel_score"] = severity * decay
            fuel.append(r)

        fuel.sort(key=lambda x: x.get("fuel_score", 0), reverse=True)
        return self._enrich_results(fuel[:top_k])

    def resolve(
        self,
        memory_id: str,
        resolution_notes: str = "",
    ) -> Optional[str]:
        """Mark a contradiction as resolved.

        Does not delete — marks status as 'resolved' by storing a
        corrected version with updated status.
        """
        memories = self._client.list_memories(COLLECTION)
        for m in memories:
            if m["memory_id"] == memory_id:
                try:
                    payload = json.loads(m["content"])
                except (json.JSONDecodeError, TypeError):
                    logger.warning(
                        "[CONTRADICTION_STORE] Cannot parse content for %s",
                        memory_id,
                    )
                    return None

                payload["status"] = "resolved"
                if resolution_notes:
                    payload["notes"] = (
                        payload.get("notes", "") + f" [RESOLVED] {resolution_notes}"
                    ).strip()

                new_content = json.dumps(payload, ensure_ascii=False)
                new_id = self._client.correct(
                    memory_id=memory_id,
                    new_content=new_content,
                    collection=COLLECTION,
                    reason=f"resolved: {resolution_notes}" if resolution_notes else "resolved",
                )

                if new_id:
                    logger.info(
                        "[CONTRADICTION_STORE] Resolved: old=%s new=%s",
                        memory_id, new_id,
                    )
                return new_id

        logger.warning(
            "[CONTRADICTION_STORE] Resolve failed: memory %s not found", memory_id
        )
        return None

    def apply_decay(self, decay_factor: float = 0.95) -> int:
        """Apply decay to all active contradictions.

        Reduces decay_score by multiplying with decay_factor.
        Contradictions that reach decay_score < 0.05 are marked 'decayed'.

        Returns the number of contradictions decayed to zero.
        """
        memories = self._client.list_memories(COLLECTION)
        decayed_count = 0

        for m in memories:
            if m.get("status") != "active":
                continue

            try:
                payload = json.loads(m["content"])
            except (json.JSONDecodeError, TypeError):
                continue

            current_decay = payload.get("decay_score", 1.0)
            new_decay = current_decay * decay_factor

            if new_decay < 0.05:
                payload["status"] = "decayed"
                payload["decay_score"] = 0.0
                decayed_count += 1
            else:
                payload["decay_score"] = round(new_decay, 4)

            new_content = json.dumps(payload, ensure_ascii=False)
            self._client.correct(
                memory_id=m["memory_id"],
                new_content=new_content,
                collection=COLLECTION,
                reason="decay_pass",
            )

        if decayed_count > 0:
            logger.info(
                "[CONTRADICTION_STORE] Decay pass: %d contradictions reached zero",
                decayed_count,
            )
        return decayed_count

    @staticmethod
    def parse_contradiction(content: str) -> Optional[Dict[str, Any]]:
        """Parse a stored contradiction JSON string into a dict.

        Returns None if the content is not valid structured contradiction JSON.
        """
        try:
            payload = json.loads(content)
            if "statement_a" in payload and "statement_b" in payload:
                return payload
        except (json.JSONDecodeError, TypeError):
            pass
        return None

    def _enrich_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse the JSON content field in each result into structured fields."""
        enriched = []
        for r in results:
            parsed = self.parse_contradiction(r.get("content", ""))
            if parsed:
                r["contradiction"] = parsed
            enriched.append(r)
        return enriched

    def list_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all contradictions in the store."""
        results = self._client.list_memories(COLLECTION, limit=limit)
        return self._enrich_results(results)

    def list_active(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List only active contradictions."""
        all_memories = self.list_all(limit=limit * 2)
        active = [
            m for m in all_memories
            if m.get("status") == "active"
            or (m.get("contradiction", {}).get("status") == "active")
        ]
        return active[:limit]

    def forget(self, memory_id: str) -> bool:
        """Remove a contradiction. User has ultimate authority."""
        return self._client.forget(memory_id, COLLECTION)

    def count(self) -> int:
        """Return the number of contradictions stored."""
        return len(self._client.list_memories(COLLECTION))

    def count_active(self) -> int:
        """Return the number of active contradictions."""
        return len(self.list_active())

    def summary(self) -> Dict[str, Any]:
        """Return a summary of the contradiction store."""
        memories = self.list_all()
        subtypes = {}
        statuses = {}
        total_severity = 0.0

        for m in memories:
            st = m.get("memory_subtype", "unknown")
            subtypes[st] = subtypes.get(st, 0) + 1

            contradiction = m.get("contradiction", {})
            status = contradiction.get("status", m.get("status", "unknown"))
            statuses[status] = statuses.get(status, 0) + 1
            total_severity += contradiction.get("severity_score", 0.0)

        return {
            "collection": COLLECTION,
            "count": len(memories),
            "subtypes": subtypes,
            "statuses": statuses,
            "avg_severity": round(total_severity / max(len(memories), 1), 3),
        }
