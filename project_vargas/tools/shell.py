"""
Project Vargas V2 — Shell Tool

Sandboxed command execution. Runs shell commands as subprocesses
with allowlist/blocklist enforcement, timeout protection, and output capture.

Safety classification:
  - AUTO: read-only commands (dir, type, cat, ls, echo, git status, python --version)
  - GATED: all other commands (python scripts, npm, pip, etc.)
  - BLOCKED: dangerous commands (rm -rf, format, del /s, shutdown, etc.)
"""

import asyncio
import logging
import shlex
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # CONEXUS_REPO/

# Default timeout for commands
_CMD_TIMEOUT = 30  # seconds

# Commands that are always safe (read-only)
AUTO_COMMANDS = {
    "dir", "ls", "type", "cat", "echo", "pwd", "cd",
    "git status", "git log", "git diff", "git branch",
    "python --version", "python3 --version",
    "node --version", "npm --version",
    "where", "which", "whoami", "hostname",
    "pip list", "pip show",
}

# Commands/patterns that are always blocked
BLOCKED_PATTERNS = [
    "rm -rf", "rm -r /", "del /s /q",
    "format", "shutdown", "reboot", "restart-computer",
    "taskkill", "kill -9",
    "mkfs", "fdisk", "diskpart",
    "reg delete", "reg add",
    "net user", "net localgroup",
    "> /dev/null", "| rm",
    "curl | bash", "curl | sh",
    "wget | bash", "wget | sh",
    "| bash", "| sh",
    "powershell -enc", "powershell -encodedcommand",
    "invoke-expression", "iex(",
]


class ShellTool:
    """Sandboxed shell command execution."""

    def __init__(self, workspace_dir: Optional[Path] = None):
        self._workspace = workspace_dir or (_PROJECT_ROOT / "project_vargas" / "workspace")
        self._workspace.mkdir(parents=True, exist_ok=True)
        self._available = True
        logger.info("[SHELL] Shell tool initialized (workspace: %s)", self._workspace)

    @property
    def available(self) -> bool:
        return self._available

    def get_safety_level(self, command: str) -> str:
        """Classify a command's safety level."""
        cmd_lower = command.lower().strip()

        # Check blocked patterns first
        for pattern in BLOCKED_PATTERNS:
            if pattern.lower() in cmd_lower:
                return "blocked"

        # Check auto-approved commands
        for safe_cmd in AUTO_COMMANDS:
            if cmd_lower.startswith(safe_cmd):
                return "auto"

        # Everything else is gated
        return "gated"

    async def run(self, command: str, cwd: Optional[str] = None,
                  timeout: int = _CMD_TIMEOUT) -> Dict[str, Any]:
        """Execute a shell command.

        Args:
            command: The command to run
            cwd: Working directory (defaults to workspace)
            timeout: Max seconds to wait

        Returns:
            {"success": bool, "stdout": str, "stderr": str, "exit_code": int, "error": str|None}
        """
        safety = self.get_safety_level(command)
        if safety == "blocked":
            logger.warning("[SHELL] BLOCKED command: %s", command[:100])
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "error": f"Command blocked by safety policy: {command[:50]}",
            }

        work_dir = cwd or str(self._workspace)

        logger.info("[SHELL] Executing [%s]: %s (cwd: %s)", safety, command[:100], work_dir)

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )

            stdout_text = stdout.decode("utf-8", errors="replace").strip()
            stderr_text = stderr.decode("utf-8", errors="replace").strip()

            # Truncate long output
            if len(stdout_text) > 4000:
                stdout_text = stdout_text[:4000] + "\n[Output truncated]"
            if len(stderr_text) > 2000:
                stderr_text = stderr_text[:2000] + "\n[Error output truncated]"

            success = proc.returncode == 0

            logger.info(
                "[SHELL] Exit %d — stdout: %d chars, stderr: %d chars",
                proc.returncode, len(stdout_text), len(stderr_text),
            )

            return {
                "success": success,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "exit_code": proc.returncode,
                "error": None if success else f"Exit code {proc.returncode}",
            }

        except asyncio.TimeoutError:
            logger.warning("[SHELL] Timeout (%ds): %s", timeout, command[:100])
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "error": f"Command timed out after {timeout}s",
            }
        except Exception as e:
            logger.error("[SHELL] Error: %s", e)
            return {
                "success": False,
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "error": str(e),
            }

    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Generic execute interface for the ToolExecutor."""
        if action == "run":
            return await self.run(
                command=params.get("command", ""),
                cwd=params.get("cwd"),
                timeout=params.get("timeout", _CMD_TIMEOUT),
            )
        return {"success": False, "error": f"Unknown shell action: {action}"}

    def format_result(self, result: Dict[str, Any]) -> str:
        """Format shell output for prompt injection."""
        parts = []
        if result.get("stdout"):
            parts.append(result["stdout"])
        if result.get("stderr"):
            parts.append(f"[STDERR]\n{result['stderr']}")
        if result.get("error"):
            parts.append(f"[ERROR] {result['error']}")
        return "\n".join(parts) if parts else "(no output)"
