"""
VARGAS V4 Constitution Loader — Sacred Path Protection

Loads and validates the constitutional documents that govern the runtime.
The constitution is the law above all implementation. If these files are
missing, corrupted, or tampered with, the system must enter degraded mode.

Reference: Master Blueprint Section 9, Foundational Invariant Declaration
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)

# Constitutional files that must be present and valid
CONSTITUTIONAL_FILES = [
    "config/sovereign_state.json",
    "config/trust_tiers.yaml",
    "config/tool_manifest.yaml",
    "config/memory_schema.yaml",
]

# The sovereign state is the primary constitutional document
SOVEREIGN_STATE_PATH = "config/sovereign_state.json"


class ConstitutionLoader:
    """Loads, validates, and provides access to constitutional documents.

    The Constitution Loader is the first thing that runs at boot.
    It ensures the runtime knows what it is, what it can do, and
    what it must not do before any other component initializes.

    Attributes:
        sovereign_state: The primary constitutional document.
        trust_tiers: Trust tier definitions.
        tool_manifest: Tool capability registry.
        memory_schema: Memory structure definitions.
        constitution_hash: SHA-256 hash of all constitutional files combined.
        valid: Whether the constitution passed validation.
    """

    def __init__(self, project_root: str = "."):
        """Initialize and load all constitutional documents.

        Args:
            project_root: Root directory of the VARGAS V4 project.
        """
        self.project_root = Path(project_root)
        self.sovereign_state: Dict[str, Any] = {}
        self.trust_tiers: Dict[str, Any] = {}
        self.tool_manifest: Dict[str, Any] = {}
        self.memory_schema: Dict[str, Any] = {}
        self.constitution_hash: str = ""
        self.valid: bool = False
        self._missing_files: list = []
        self._load_errors: list = []

        self._load_all()

    def _load_all(self) -> None:
        """Load all constitutional documents and compute integrity hash."""
        self._load_sovereign_state()
        self._load_trust_tiers()
        self._load_tool_manifest()
        self._load_memory_schema()
        self._compute_constitution_hash()
        self._validate()

    def _load_sovereign_state(self) -> None:
        """Load sovereign_state.json — the primary constitutional document."""
        path = self.project_root / SOVEREIGN_STATE_PATH
        if not path.exists():
            self._missing_files.append(SOVEREIGN_STATE_PATH)
            logger.error("[CONSTITUTION] sovereign_state.json NOT FOUND")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.sovereign_state = json.load(f)
            logger.info("[CONSTITUTION] sovereign_state.json loaded")
        except Exception as e:
            self._load_errors.append(f"sovereign_state.json: {e}")
            logger.error("[CONSTITUTION] sovereign_state.json load failed: %s", e)

    def _load_trust_tiers(self) -> None:
        """Load trust_tiers.yaml."""
        path = self.project_root / "config/trust_tiers.yaml"
        if not path.exists():
            self._missing_files.append("config/trust_tiers.yaml")
            logger.warning("[CONSTITUTION] trust_tiers.yaml not found")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.trust_tiers = yaml.safe_load(f) or {}
            logger.info("[CONSTITUTION] trust_tiers.yaml loaded")
        except Exception as e:
            self._load_errors.append(f"trust_tiers.yaml: {e}")
            logger.error("[CONSTITUTION] trust_tiers.yaml load failed: %s", e)

    def _load_tool_manifest(self) -> None:
        """Load tool_manifest.yaml."""
        path = self.project_root / "config/tool_manifest.yaml"
        if not path.exists():
            self._missing_files.append("config/tool_manifest.yaml")
            logger.warning("[CONSTITUTION] tool_manifest.yaml not found")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.tool_manifest = yaml.safe_load(f) or {}
            logger.info("[CONSTITUTION] tool_manifest.yaml loaded")
        except Exception as e:
            self._load_errors.append(f"tool_manifest.yaml: {e}")
            logger.error("[CONSTITUTION] tool_manifest.yaml load failed: %s", e)

    def _load_memory_schema(self) -> None:
        """Load memory_schema.yaml."""
        path = self.project_root / "config/memory_schema.yaml"
        if not path.exists():
            self._missing_files.append("config/memory_schema.yaml")
            logger.warning("[CONSTITUTION] memory_schema.yaml not found")
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                self.memory_schema = yaml.safe_load(f) or {}
            logger.info("[CONSTITUTION] memory_schema.yaml loaded")
        except Exception as e:
            self._load_errors.append(f"memory_schema.yaml: {e}")
            logger.error("[CONSTITUTION] memory_schema.yaml load failed: %s", e)

    def _compute_constitution_hash(self) -> None:
        """Compute SHA-256 hash of all constitutional files combined."""
        hasher = hashlib.sha256()

        for rel_path in CONSTITUTIONAL_FILES:
            path = self.project_root / rel_path
            if path.exists():
                try:
                    content = path.read_bytes()
                    hasher.update(content)
                except Exception as e:
                    logger.warning("[CONSTITUTION] Hash read failed for %s: %s", rel_path, e)

        self.constitution_hash = hasher.hexdigest()
        logger.info("[CONSTITUTION] Hash computed: %s", self.constitution_hash[:16])

    def _validate(self) -> None:
        """Validate that the constitution is complete and coherent."""
        errors = []

        if not self.sovereign_state:
            errors.append("sovereign_state.json is empty or missing")

        if self.sovereign_state.get("seal_metadata", {}).get("immutable_at_runtime") is not True:
            errors.append("sovereign_state.json must be immutable at runtime")

        if not self.sovereign_state.get("trust_tiers"):
            errors.append("trust_tiers section missing from sovereign_state.json")

        if not self.sovereign_state.get("e_vector_baseline"):
            errors.append("e_vector_baseline missing from sovereign_state.json")

        if self._missing_files:
            errors.append(f"Missing files: {', '.join(self._missing_files)}")

        if self._load_errors:
            errors.append(f"Load errors: {', '.join(self._load_errors)}")

        self.valid = len(errors) == 0

        if self.valid:
            logger.info("[CONSTITUTION] Validation PASSED — constitution is intact")
        else:
            for err in errors:
                logger.error("[CONSTITUTION] Validation FAILED: %s", err)

    def get_trust_tier(self, tier_name: str) -> Optional[Dict[str, Any]]:
        """Look up a trust tier by name.

        Args:
            tier_name: e.g. 'tier_0', 'tier_3'

        Returns:
            Tier definition dict or None.
        """
        tiers = self.trust_tiers.get("tiers", {})
        return tiers.get(tier_name)

    def get_tool_definition(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Look up a tool by name from the manifest.

        Args:
            tool_name: e.g. 'read_file', 'execute_shell'

        Returns:
            Tool definition dict or None.
        """
        tools = self.tool_manifest.get("tools", {})
        return tools.get(tool_name)

    def is_forbidden(self, tool_name: str) -> bool:
        """Check if a tool is constitutionally forbidden.

        Args:
            tool_name: Tool to check.

        Returns:
            True if the tool is Tier 4 / forbidden.
        """
        tool = self.get_tool_definition(tool_name)
        if not tool:
            return False
        return tool.get("trust_tier") == 4 or tool.get("forbidden", False)

    def summary(self) -> Dict[str, Any]:
        """Return constitution status summary."""
        return {
            "valid": self.valid,
            "constitution_hash": self.constitution_hash[:16] + "...",
            "sovereign_state_loaded": bool(self.sovereign_state),
            "trust_tiers_loaded": bool(self.trust_tiers),
            "tool_manifest_loaded": bool(self.tool_manifest),
            "memory_schema_loaded": bool(self.memory_schema),
            "missing_files": self._missing_files,
            "load_errors": self._load_errors,
        }
