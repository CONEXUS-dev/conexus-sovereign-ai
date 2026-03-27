"""
Project Vargas V2 — File I/O Tool

Sandboxed file operations within a workspace directory.
Vargas can only write to project_vargas/workspace/.
Read access is broader but still bounded to the repo.

Safety classification:
  - AUTO: read_file, list_dir, file_exists
  - GATED: write_file, append_file, delete_file, create_dir
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # CONEXUS_REPO/
_WORKSPACE = _PROJECT_ROOT / "project_vargas" / "workspace"
_MAX_READ_SIZE = 100_000  # 100KB max file read
_MAX_WRITE_SIZE = 50_000  # 50KB max file write


class FileIOTool:
    """Sandboxed file operations for Vargas."""

    def __init__(self, workspace_dir: Optional[Path] = None):
        self._workspace = workspace_dir or _WORKSPACE
        self._workspace.mkdir(parents=True, exist_ok=True)
        self._read_root = _PROJECT_ROOT  # Can read anywhere in repo
        self._available = True
        logger.info("[FILE_IO] File tool initialized (workspace: %s)", self._workspace)

    @property
    def available(self) -> bool:
        return self._available

    @property
    def workspace_path(self) -> str:
        return str(self._workspace)

    def _resolve_read_path(self, path: str) -> Optional[Path]:
        """Resolve a path for reading. Must be within repo root."""
        try:
            resolved = Path(path).resolve()
            if not str(resolved).startswith(str(self._read_root)):
                return None
            return resolved
        except Exception:
            return None

    def _resolve_write_path(self, path: str) -> Optional[Path]:
        """Resolve a path for writing. Must be within workspace."""
        try:
            # If relative, resolve from workspace
            p = Path(path)
            if not p.is_absolute():
                p = self._workspace / p
            resolved = p.resolve()
            if not str(resolved).startswith(str(self._workspace.resolve())):
                return None
            return resolved
        except Exception:
            return None

    def get_safety_level(self, action: str) -> str:
        """Classify an action's safety level."""
        if action in ("read_file", "list_dir", "file_exists"):
            return "auto"
        if action in ("write_file", "append_file", "delete_file", "create_dir"):
            return "gated"
        return "gated"

    async def read_file(self, path: str) -> Dict[str, Any]:
        """Read a file's contents."""
        resolved = self._resolve_read_path(path)
        if not resolved:
            return {"success": False, "error": f"Path outside repo: {path}"}
        if not resolved.exists():
            return {"success": False, "error": f"File not found: {path}"}
        if not resolved.is_file():
            return {"success": False, "error": f"Not a file: {path}"}

        try:
            size = resolved.stat().st_size
            if size > _MAX_READ_SIZE:
                content = resolved.read_text(encoding="utf-8", errors="replace")[:_MAX_READ_SIZE]
                content += f"\n[File truncated — {size} bytes total, showing first {_MAX_READ_SIZE}]"
            else:
                content = resolved.read_text(encoding="utf-8", errors="replace")

            logger.info("[FILE_IO] Read: %s (%d bytes)", resolved.name, len(content))
            return {"success": True, "content": content, "path": str(resolved), "size": size}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to a file in the workspace."""
        resolved = self._resolve_write_path(path)
        if not resolved:
            return {"success": False, "error": f"Write path must be within workspace: {path}"}

        if len(content) > _MAX_WRITE_SIZE:
            return {"success": False, "error": f"Content too large ({len(content)} bytes, max {_MAX_WRITE_SIZE})"}

        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(content, encoding="utf-8")
            logger.info("[FILE_IO] Wrote: %s (%d bytes)", resolved.name, len(content))
            return {"success": True, "path": str(resolved), "size": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def append_file(self, path: str, content: str) -> Dict[str, Any]:
        """Append content to a file in the workspace."""
        resolved = self._resolve_write_path(path)
        if not resolved:
            return {"success": False, "error": f"Write path must be within workspace: {path}"}

        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            with open(resolved, "a", encoding="utf-8") as f:
                f.write(content)
            logger.info("[FILE_IO] Appended: %s (%d bytes)", resolved.name, len(content))
            return {"success": True, "path": str(resolved), "appended": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def list_dir(self, path: Optional[str] = None) -> Dict[str, Any]:
        """List directory contents."""
        target = Path(path) if path else self._workspace
        resolved = self._resolve_read_path(str(target))
        if not resolved:
            return {"success": False, "error": f"Path outside repo: {path}"}
        if not resolved.exists():
            return {"success": False, "error": f"Directory not found: {path}"}
        if not resolved.is_dir():
            return {"success": False, "error": f"Not a directory: {path}"}

        try:
            items = []
            for item in sorted(resolved.iterdir()):
                if item.name.startswith(".") or item.name == "__pycache__":
                    continue
                entry = {
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                }
                if item.is_file():
                    entry["size"] = item.stat().st_size
                items.append(entry)

            logger.info("[FILE_IO] Listed: %s (%d items)", resolved.name, len(items))
            return {"success": True, "path": str(resolved), "items": items}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def file_exists(self, path: str) -> Dict[str, Any]:
        """Check if a file exists."""
        resolved = self._resolve_read_path(path)
        if not resolved:
            return {"success": True, "exists": False}
        return {"success": True, "exists": resolved.exists(), "is_file": resolved.is_file() if resolved.exists() else False}

    async def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file in the workspace."""
        resolved = self._resolve_write_path(path)
        if not resolved:
            return {"success": False, "error": f"Delete path must be within workspace: {path}"}
        if not resolved.exists():
            return {"success": False, "error": f"File not found: {path}"}
        if not resolved.is_file():
            return {"success": False, "error": "Can only delete files, not directories"}

        try:
            resolved.unlink()
            logger.info("[FILE_IO] Deleted: %s", resolved.name)
            return {"success": True, "path": str(resolved)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_dir(self, path: str) -> Dict[str, Any]:
        """Create a directory in the workspace."""
        resolved = self._resolve_write_path(path)
        if not resolved:
            return {"success": False, "error": f"Path must be within workspace: {path}"}

        try:
            resolved.mkdir(parents=True, exist_ok=True)
            logger.info("[FILE_IO] Created dir: %s", resolved.name)
            return {"success": True, "path": str(resolved)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute(self, action: str, params: Dict[str, Any]) -> Any:
        """Generic execute interface for the ToolExecutor."""
        method_map = {
            "read_file": lambda p: self.read_file(p.get("path", "")),
            "write_file": lambda p: self.write_file(p.get("path", ""), p.get("content", "")),
            "append_file": lambda p: self.append_file(p.get("path", ""), p.get("content", "")),
            "list_dir": lambda p: self.list_dir(p.get("path")),
            "file_exists": lambda p: self.file_exists(p.get("path", "")),
            "delete_file": lambda p: self.delete_file(p.get("path", "")),
            "create_dir": lambda p: self.create_dir(p.get("path", "")),
        }

        handler = method_map.get(action)
        if not handler:
            return {"success": False, "error": f"Unknown file action: {action}"}

        return await handler(params)
