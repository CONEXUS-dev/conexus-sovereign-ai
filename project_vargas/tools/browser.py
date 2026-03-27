"""
Project Vargas V2 — Browser Tool

Wraps the agent-browser CLI binary for headless browser automation.
Uses the agent-browser-win32-x64.exe already present in the OpenClaw skills directory.

Capabilities:
  - Navigate to URLs
  - Take accessibility snapshots (get interactive elements with refs)
  - Click, fill, type using element refs
  - Take screenshots
  - Extract text from elements
  - Navigate back/forward/reload
  - Manage tabs

Safety classification:
  - AUTO: open, snapshot, get_text, get_url, screenshot (read-only)
  - GATED: click, fill, type, press, select, execute JS (interactive/write)
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Locate the agent-browser binary
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # CONEXUS_REPO/
_BROWSER_BIN = _PROJECT_ROOT / "openclaw" / "skills" / "agent-browser" / "bin" / "agent-browser-win32-x64.exe"
_BROWSER_JS_FALLBACK = _PROJECT_ROOT / "openclaw" / "skills" / "agent-browser" / "bin" / "agent-browser.js"

# Command timeout
_CMD_TIMEOUT = 30  # seconds
_NAV_TIMEOUT = 45  # longer for page loads

# Read-only actions (auto-approved)
AUTO_ACTIONS = {
    "open", "snapshot", "get", "is", "find",
    "get_text", "get_url", "get_title", "get_html",
    "screenshot", "tab_list", "cookies_get",
    "back", "forward", "reload", "wait",
}

# Write/interactive actions (human-gated)
GATED_ACTIONS = {
    "click", "dblclick", "fill", "type", "press",
    "select", "check", "uncheck", "hover", "scroll",
    "upload", "drag", "eval", "tab_new", "tab_close",
    "cookies_set", "cookies_clear",
}


class BrowserTool:
    """Headless browser automation via agent-browser CLI."""

    def __init__(self):
        self._available = False
        self._bin_path: Optional[str] = None
        self._session = "vargas"
        self._initialize()

    def _initialize(self):
        """Locate the agent-browser binary."""
        if _BROWSER_BIN.exists():
            self._bin_path = str(_BROWSER_BIN)
            self._available = True
            logger.info("[BROWSER] agent-browser binary found: %s", self._bin_path)
        elif _BROWSER_JS_FALLBACK.exists():
            self._bin_path = f"node {_BROWSER_JS_FALLBACK}"
            self._available = True
            logger.info("[BROWSER] Using Node.js fallback: %s", _BROWSER_JS_FALLBACK)
        else:
            logger.warning("[BROWSER] agent-browser binary not found — browser tool disabled")

    @property
    def available(self) -> bool:
        return self._available

    def get_safety_level(self, action: str) -> str:
        """Return 'auto', 'gated', or 'blocked' for an action."""
        if action in AUTO_ACTIONS:
            return "auto"
        if action in GATED_ACTIONS:
            return "gated"
        return "gated"  # default to gated for unknown actions

    async def _run_cmd(self, args: List[str], timeout: int = _CMD_TIMEOUT) -> Dict[str, Any]:
        """Execute an agent-browser command and return parsed output."""
        if not self._available:
            return {"success": False, "error": "Browser tool not available"}

        cmd_parts = [self._bin_path, "--session", self._session, "--json"] + args

        # If using Node.js fallback, split the command properly
        if self._bin_path and self._bin_path.startswith("node "):
            cmd_str = f"{self._bin_path} --session {self._session} --json {' '.join(args)}"
        else:
            cmd_str = " ".join(cmd_parts)

        logger.info("[BROWSER] Running: %s", cmd_str[:200])

        try:
            proc = await asyncio.create_subprocess_shell(
                cmd_str,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(_PROJECT_ROOT),
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )

            stdout_text = stdout.decode("utf-8", errors="replace").strip()
            stderr_text = stderr.decode("utf-8", errors="replace").strip()

            if proc.returncode != 0:
                error_msg = stderr_text or stdout_text or f"Exit code {proc.returncode}"
                logger.warning("[BROWSER] Command failed: %s", error_msg[:200])
                return {"success": False, "error": error_msg[:500]}

            # Try to parse JSON output
            if stdout_text:
                try:
                    return json.loads(stdout_text)
                except json.JSONDecodeError:
                    return {"success": True, "data": stdout_text[:4000]}

            return {"success": True, "data": ""}

        except asyncio.TimeoutError:
            logger.warning("[BROWSER] Command timeout (%ds): %s", timeout, cmd_str[:100])
            return {"success": False, "error": f"Command timed out after {timeout}s"}
        except Exception as e:
            logger.error("[BROWSER] Command error: %s", e)
            return {"success": False, "error": str(e)}

    # --- Public API ---

    async def open(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        return await self._run_cmd(["open", url], timeout=_NAV_TIMEOUT)

    async def snapshot(self, interactive_only: bool = True, compact: bool = True) -> Dict[str, Any]:
        """Get accessibility tree with element refs."""
        args = ["snapshot"]
        if interactive_only:
            args.append("-i")
        if compact:
            args.append("-c")
        return await self._run_cmd(args)

    async def click(self, ref: str) -> Dict[str, Any]:
        """Click an element by ref."""
        return await self._run_cmd(["click", ref])

    async def fill(self, ref: str, text: str) -> Dict[str, Any]:
        """Clear and fill an input by ref."""
        return await self._run_cmd(["fill", ref, text])

    async def type_text(self, ref: str, text: str) -> Dict[str, Any]:
        """Type text into an element by ref."""
        return await self._run_cmd(["type", ref, text])

    async def press(self, key: str) -> Dict[str, Any]:
        """Press a key."""
        return await self._run_cmd(["press", key])

    async def get_text(self, ref: str) -> Dict[str, Any]:
        """Get text content of an element."""
        return await self._run_cmd(["get", "text", ref])

    async def get_url(self) -> Dict[str, Any]:
        """Get current page URL."""
        return await self._run_cmd(["get", "url"])

    async def get_title(self) -> Dict[str, Any]:
        """Get current page title."""
        return await self._run_cmd(["get", "title"])

    async def screenshot(self, path: Optional[str] = None, full_page: bool = False) -> Dict[str, Any]:
        """Take a screenshot."""
        args = ["screenshot"]
        if path:
            args.append(path)
        if full_page:
            args.append("--full")
        return await self._run_cmd(args)

    async def scroll(self, direction: str = "down", pixels: int = 500) -> Dict[str, Any]:
        """Scroll the page."""
        return await self._run_cmd(["scroll", direction, str(pixels)])

    async def back(self) -> Dict[str, Any]:
        """Go back."""
        return await self._run_cmd(["back"])

    async def forward(self) -> Dict[str, Any]:
        """Go forward."""
        return await self._run_cmd(["forward"])

    async def reload(self) -> Dict[str, Any]:
        """Reload page."""
        return await self._run_cmd(["reload"])

    async def wait_for(self, selector: Optional[str] = None, text: Optional[str] = None,
                       ms: Optional[int] = None) -> Dict[str, Any]:
        """Wait for element, text, or time."""
        args = ["wait"]
        if selector:
            args.append(selector)
        elif text:
            args.extend(["--text", text])
        elif ms:
            args.append(str(ms))
        return await self._run_cmd(args)

    async def close(self) -> Dict[str, Any]:
        """Close the browser."""
        return await self._run_cmd(["close"])

    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Generic execute interface for the ToolExecutor."""
        method_map = {
            "open": lambda p: self.open(p.get("url", "")),
            "snapshot": lambda p: self.snapshot(
                interactive_only=p.get("interactive_only", True),
                compact=p.get("compact", True),
            ),
            "click": lambda p: self.click(p.get("ref", "")),
            "fill": lambda p: self.fill(p.get("ref", ""), p.get("text", "")),
            "type": lambda p: self.type_text(p.get("ref", ""), p.get("text", "")),
            "press": lambda p: self.press(p.get("key", "")),
            "get_text": lambda p: self.get_text(p.get("ref", "")),
            "get_url": lambda _: self.get_url(),
            "get_title": lambda _: self.get_title(),
            "screenshot": lambda p: self.screenshot(p.get("path"), p.get("full_page", False)),
            "scroll": lambda p: self.scroll(p.get("direction", "down"), p.get("pixels", 500)),
            "back": lambda _: self.back(),
            "forward": lambda _: self.forward(),
            "reload": lambda _: self.reload(),
            "close": lambda _: self.close(),
        }

        handler = method_map.get(action)
        if not handler:
            return {"success": False, "error": f"Unknown browser action: {action}"}

        return await handler(params)

    def format_snapshot(self, result: Dict[str, Any]) -> str:
        """Format a snapshot result for prompt injection."""
        if not result.get("success"):
            return f"Browser snapshot failed: {result.get('error', 'unknown error')}"

        data = result.get("data", "")
        if isinstance(data, dict):
            snapshot_text = data.get("snapshot", str(data))
        else:
            snapshot_text = str(data)

        # Truncate if too long
        if len(snapshot_text) > 6000:
            snapshot_text = snapshot_text[:6000] + "\n[Snapshot truncated]"

        return snapshot_text
