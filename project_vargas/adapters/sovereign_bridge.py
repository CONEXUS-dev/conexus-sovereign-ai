"""
Project Vargas V3 — Sovereign Governance Bridge (Phase 4A)

Read-only bridge to SovereignNEXT. Allows Vargas to:
  - Load the sealed V5 baseline snapshot
  - Run the Sovereign Observer against it
  - Surface governance reports, anomaly flags, and health summaries
  - Answer user questions about Sovereign state

Hard constraint: this bridge is READ-ONLY. It never mutates Sovereign state.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Paths relative to CONEXUS_REPO
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SOVEREIGN_DIR = _REPO_ROOT / "SovereignNEXT"
_PIPELINE_DIR = _SOVEREIGN_DIR / "pipeline"
_GOVERNANCE_DIR = _SOVEREIGN_DIR / "governance"

# Known artifact paths
_SEALED_SNAPSHOT = _PIPELINE_DIR / "v5_final_state_snapshot.json"
_SEAL_FILE = _PIPELINE_DIR / "Sovereign-V5-Anchor.seal.json"
_CANONICAL_REPORT = _PIPELINE_DIR / "v5_canonical_report.json"


class SovereignBridge:
    """Read-only bridge to SovereignNEXT governance system."""

    def __init__(self):
        self._available = False
        self._state = None
        self._last_report = None
        self._seal_metadata = None
        self._initialize()

    def _initialize(self):
        """Check that SovereignNEXT artifacts exist and can be loaded."""
        if not _SOVEREIGN_DIR.exists():
            logger.warning("[SOVEREIGN-BRIDGE] SovereignNEXT directory not found")
            return

        if _SEALED_SNAPSHOT.exists():
            logger.info("[SOVEREIGN-BRIDGE] Sealed snapshot found: %s", _SEALED_SNAPSHOT)
            self._available = True
        else:
            logger.warning("[SOVEREIGN-BRIDGE] No sealed snapshot at %s", _SEALED_SNAPSHOT)

        if _SEAL_FILE.exists():
            try:
                self._seal_metadata = json.loads(_SEAL_FILE.read_text(encoding="utf-8"))
                logger.info("[SOVEREIGN-BRIDGE] Seal metadata loaded")
            except Exception as e:
                logger.warning("[SOVEREIGN-BRIDGE] Failed to load seal: %s", e)

    @property
    def available(self) -> bool:
        return self._available

    def load_state(self) -> bool:
        """Load the sealed V5 snapshot into SystemState. Returns True on success."""
        if not self._available:
            return False

        try:
            from SovereignNEXT.state.system_state import SystemState
            snapshot_data = json.loads(_SEALED_SNAPSHOT.read_text(encoding="utf-8"))
            self._state = SystemState.from_snapshot(snapshot_data)
            logger.info(
                "[SOVEREIGN-BRIDGE] State loaded: %d claims, %d tensions, %d paradoxes",
                len(self._state.claims), len(self._state.tensions), len(self._state.paradoxes),
            )
            return True
        except ImportError:
            logger.error("[SOVEREIGN-BRIDGE] Cannot import SovereignNEXT.state.system_state")
            return False
        except Exception as e:
            logger.error("[SOVEREIGN-BRIDGE] Failed to load state: %s", e)
            return False

    def run_observer(self) -> Optional[Dict[str, Any]]:
        """Run the Sovereign Observer against the loaded state. Returns report dict."""
        if self._state is None:
            if not self.load_state():
                return None

        try:
            from SovereignNEXT.operators.sovereign_observer import sovereign_observe
            report = sovereign_observe(self._state)
            self._last_report = report

            result = {
                "timestamp": report.timestamp,
                "state_hash": report.state_hash,
                "paradox_counts": report.paradox_counts_by_status,
                "entropy_distribution": report.entropy_band_distribution,
                "veto_summary": report.veto_summary,
                "attestations": report.integrity_attestations,
                "anomaly_flags": report.anomaly_flags,
                "anomaly_count": len(report.anomaly_flags),
                "operator_ledgers": [
                    {"operator": l.operator_name, "actions": dict(l.action_counts)}
                    for l in report.operator_ledgers
                ],
                "belief_stratification": report.belief_stratification,
            }
            logger.info(
                "[SOVEREIGN-BRIDGE] Observer report: %d anomalies, %d attestations",
                len(report.anomaly_flags), len(report.integrity_attestations),
            )
            return result
        except ImportError:
            logger.error("[SOVEREIGN-BRIDGE] Cannot import sovereign_observe")
            return None
        except Exception as e:
            logger.error("[SOVEREIGN-BRIDGE] Observer failed: %s", e)
            return None

    def get_health_summary(self) -> Dict[str, Any]:
        """Get a concise health summary suitable for Vargas prompt injection."""
        if _CANONICAL_REPORT.exists():
            try:
                report = json.loads(_CANONICAL_REPORT.read_text(encoding="utf-8"))
                health = report.get("health_summary", {})
                if health:
                    return health
            except Exception:
                pass

        # Fallback: run observer
        obs = self.run_observer()
        if obs:
            warnings = [f for f in obs["anomaly_flags"] if "warning" in f.lower() or "VIOLATION" in f]
            return {
                "anomalies_total": obs["anomaly_count"],
                "warnings_total": len(warnings),
                "attestations": obs["attestations"],
                "health_statement": "healthy: no warnings" if not warnings else "warnings present: review anomalies",
            }

        return {"health_statement": "unavailable — Sovereign state not loaded"}

    def get_governance_contracts(self) -> List[Dict[str, str]]:
        """List available governance contracts."""
        contracts = []
        if _GOVERNANCE_DIR.exists():
            for md_file in sorted(_GOVERNANCE_DIR.glob("*.md")):
                contracts.append({
                    "name": md_file.stem,
                    "path": str(md_file),
                    "size_bytes": md_file.stat().st_size,
                })
        return contracts

    def get_seal_metadata(self) -> Optional[Dict[str, Any]]:
        """Return the seal metadata for the current baseline."""
        return self._seal_metadata

    def get_state_summary(self) -> Dict[str, Any]:
        """Get a quick summary of the loaded state without running the observer."""
        if self._state is None:
            if not self.load_state():
                return {"error": "State not available"}

        return {
            "claims": len(self._state.claims),
            "tensions": len(self._state.tensions),
            "paradoxes": len(self._state.paradoxes),
            "emoji_vectors": len(self._state.emoji_field) if hasattr(self._state, 'emoji_field') else 0,
            "iteration": getattr(self._state, 'iteration', 'unknown'),
        }

    def format_for_prompt(self) -> str:
        """Format Sovereign state as context for Vargas's system prompt."""
        health = self.get_health_summary()
        seal = self.get_seal_metadata()

        parts = ["[SOVEREIGN STATE — read-only governance context]"]

        if seal:
            parts.append(f"Baseline: {seal.get('baseline_id', 'unknown')}")
            parts.append(f"Sealed by: {seal.get('sealed_by', 'unknown')}")
            parts.append(f"Snapshot hash: {seal.get('snapshot_hash', 'unknown')[:16]}...")

        parts.append(f"Health: {health.get('health_statement', 'unknown')}")

        if health.get("anomalies_total") is not None:
            parts.append(f"Anomalies: {health['anomalies_total']} total, {health.get('warnings_total', 0)} warnings")

        if health.get("attestations"):
            for att in health["attestations"]:
                parts.append(f"  - {att}")

        parts.append("[END SOVEREIGN STATE]")
        return "\n".join(parts)
