"""
VARGAS V4 File I/O — Local Filesystem Operations

Provides read, write, modify, delete, and list operations for the
local filesystem. All mutation operations require snapshot-first
protection. All operations are bounded to the project workspace.

Reference: Master Blueprint Section 7, Section 12.4 — file_io.py
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Default workspace boundary
DEFAULT_WORKSPACE = "."


class FileIO:
    """Local filesystem operations with workspace boundary enforcement.

    All operations are restricted to the configured workspace root.
    Path traversal beyond the workspace is blocked.

    Attributes:
        workspace_root: Absolute path to the workspace boundary.
    """

    def __init__(self, workspace_root: str = DEFAULT_WORKSPACE):
        self.workspace_root = Path(workspace_root).resolve()
        logger.info("[FILE_IO] Initialized: workspace=%s", self.workspace_root)

    def _validate_path(self, path: str) -> Path:
        """Validate and resolve a path within the workspace.

        Args:
            path: Relative or absolute path to validate.

        Returns:
            Resolved absolute Path.

        Raises:
            ValueError: If the path escapes the workspace boundary.
        """
        resolved = Path(path).resolve()

        # Check workspace containment
        try:
            resolved.relative_to(self.workspace_root)
        except ValueError:
            raise ValueError(
                f"Path escapes workspace boundary: {path} "
                f"(workspace: {self.workspace_root})"
            )

        return resolved

    def read_file(self, path: str) -> Dict[str, Any]:
        """Read a file's contents.

        Trust tier: 0 (passive observation)

        Args:
            path: Path to the file.

        Returns:
            Dict with content, size, and metadata.
        """
        try:
            resolved = self._validate_path(path)

            if not resolved.exists():
                return {"success": False, "error": f"File not found: {path}"}

            if not resolved.is_file():
                return {"success": False, "error": f"Not a file: {path}"}

            content = resolved.read_text(encoding="utf-8")
            stat = resolved.stat()

            return {
                "success": True,
                "content": content,
                "path": str(resolved),
                "size": stat.st_size,
                "modified": stat.st_mtime,
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error("[FILE_IO] Read failed for %s: %s", path, e)
            return {"success": False, "error": str(e)}

    def list_directory(
        self, path: str, recursive: bool = False
    ) -> Dict[str, Any]:
        """List files and directories at a path.

        Trust tier: 0 (passive observation)

        Args:
            path: Directory path.
            recursive: Whether to list recursively.

        Returns:
            Dict with entries list.
        """
        try:
            resolved = self._validate_path(path)

            if not resolved.exists():
                return {"success": False, "error": f"Directory not found: {path}"}

            if not resolved.is_dir():
                return {"success": False, "error": f"Not a directory: {path}"}

            entries: List[Dict[str, Any]] = []
            iterator = resolved.rglob("*") if recursive else resolved.iterdir()

            for entry in sorted(iterator):
                try:
                    rel = entry.relative_to(resolved)
                    stat = entry.stat()
                    entries.append({
                        "name": str(rel),
                        "type": "file" if entry.is_file() else "directory",
                        "size": stat.st_size if entry.is_file() else None,
                    })
                except (OSError, PermissionError):
                    continue

            return {
                "success": True,
                "path": str(resolved),
                "count": len(entries),
                "entries": entries,
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error("[FILE_IO] List failed for %s: %s", path, e)
            return {"success": False, "error": str(e)}

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to a file. Creates parent directories as needed.

        Trust tier: 2 (snapshot-first mutation)

        Args:
            path: Target file path.
            content: Content to write.

        Returns:
            Dict with write result.
        """
        try:
            resolved = self._validate_path(path)
            resolved.parent.mkdir(parents=True, exist_ok=True)
            resolved.write_text(content, encoding="utf-8")

            logger.info("[FILE_IO] Written: %s (%d bytes)", resolved, len(content))
            return {
                "success": True,
                "path": str(resolved),
                "bytes_written": len(content),
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error("[FILE_IO] Write failed for %s: %s", path, e)
            return {"success": False, "error": str(e)}

    def modify_file(
        self, path: str, old_content: str, new_content: str
    ) -> Dict[str, Any]:
        """Replace a string in a file.

        Trust tier: 2 (snapshot-first mutation)

        Args:
            path: Target file path.
            old_content: String to find.
            new_content: Replacement string.

        Returns:
            Dict with modification result.
        """
        try:
            resolved = self._validate_path(path)

            if not resolved.exists():
                return {"success": False, "error": f"File not found: {path}"}

            current = resolved.read_text(encoding="utf-8")
            if old_content not in current:
                return {"success": False, "error": "old_content not found in file"}

            updated = current.replace(old_content, new_content, 1)
            resolved.write_text(updated, encoding="utf-8")

            logger.info("[FILE_IO] Modified: %s", resolved)
            return {
                "success": True,
                "path": str(resolved),
                "replacements": 1,
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error("[FILE_IO] Modify failed for %s: %s", path, e)
            return {"success": False, "error": str(e)}

    def delete_file(self, path: str) -> Dict[str, Any]:
        """Delete a file.

        Trust tier: 3 (explicit approval required)

        Args:
            path: File to delete.

        Returns:
            Dict with deletion result.
        """
        try:
            resolved = self._validate_path(path)

            if not resolved.exists():
                return {"success": False, "error": f"File not found: {path}"}

            if not resolved.is_file():
                return {"success": False, "error": f"Not a file (will not delete directories): {path}"}

            size = resolved.stat().st_size
            resolved.unlink()

            logger.info("[FILE_IO] Deleted: %s (%d bytes)", resolved, size)
            return {
                "success": True,
                "path": str(resolved),
                "bytes_deleted": size,
            }

        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error("[FILE_IO] Delete failed for %s: %s", path, e)
            return {"success": False, "error": str(e)}

    def summary(self) -> Dict[str, Any]:
        """Return file I/O status summary."""
        return {
            "workspace_root": str(self.workspace_root),
        }
