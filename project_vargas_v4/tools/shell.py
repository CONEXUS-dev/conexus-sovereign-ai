"""
VARGAS V4 Shell — Local Command Execution

Executes shell commands on the local machine with strict safety controls.
All shell execution is Tier 3 (explicit approval required) and requires
a pre-action snapshot. Commands are bounded by timeout and workspace.

The system must never speak past what it has actually done.
(Foundational Invariant §5)

Reference: Master Blueprint Section 7, Section 12.4 — shell.py
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Safety defaults
DEFAULT_TIMEOUT = 30
MAX_TIMEOUT = 300
MAX_OUTPUT_LENGTH = 10000


class Shell:
    """Local shell command execution with safety controls.

    All commands:
    - Require Tier 3 (explicit approval)
    - Are bounded by timeout
    - Are bounded to the workspace directory
    - Capture stdout and stderr
    - Log execution to provenance

    Attributes:
        workspace_root: Working directory for commands.
        default_timeout: Default command timeout in seconds.
    """

    def __init__(self, workspace_root: str = ".", default_timeout: int = DEFAULT_TIMEOUT):
        self.workspace_root = Path(workspace_root).resolve()
        self.default_timeout = min(default_timeout, MAX_TIMEOUT)
        logger.info("[SHELL] Initialized: workspace=%s timeout=%d", self.workspace_root, self.default_timeout)

    def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute a shell command.

        Trust tier: 3 (explicit approval required)
        Pre-action snapshot required.

        Args:
            command: The command string to execute.
            cwd: Working directory (defaults to workspace_root).
            timeout: Command timeout in seconds.

        Returns:
            Dict with stdout, stderr, return code, and metadata.
        """
        effective_timeout = min(timeout or self.default_timeout, MAX_TIMEOUT)
        effective_cwd = Path(cwd).resolve() if cwd else self.workspace_root

        # Validate cwd is within workspace
        try:
            effective_cwd.relative_to(self.workspace_root)
        except ValueError:
            return {
                "success": False,
                "error": f"Working directory escapes workspace: {cwd}",
                "command": command,
            }

        logger.info("[SHELL] Executing: %s (cwd=%s timeout=%d)", command, effective_cwd, effective_timeout)

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(effective_cwd),
                capture_output=True,
                text=True,
                timeout=effective_timeout,
            )

            stdout = result.stdout[:MAX_OUTPUT_LENGTH] if result.stdout else ""
            stderr = result.stderr[:MAX_OUTPUT_LENGTH] if result.stderr else ""

            success = result.returncode == 0

            if success:
                logger.info("[SHELL] Command succeeded: rc=%d", result.returncode)
            else:
                logger.warning("[SHELL] Command failed: rc=%d stderr=%s", result.returncode, stderr[:200])

            return {
                "success": success,
                "command": command,
                "cwd": str(effective_cwd),
                "return_code": result.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "timeout": effective_timeout,
                "truncated": len(result.stdout or "") > MAX_OUTPUT_LENGTH,
            }

        except subprocess.TimeoutExpired:
            logger.error("[SHELL] Command timed out after %ds: %s", effective_timeout, command)
            return {
                "success": False,
                "command": command,
                "error": f"Command timed out after {effective_timeout}s",
                "timeout": effective_timeout,
            }
        except Exception as e:
            logger.error("[SHELL] Command failed: %s — %s", command, e)
            return {
                "success": False,
                "command": command,
                "error": str(e),
            }

    def summary(self) -> Dict[str, Any]:
        """Return shell status summary."""
        return {
            "workspace_root": str(self.workspace_root),
            "default_timeout": self.default_timeout,
            "max_timeout": MAX_TIMEOUT,
        }
