"""
VARGAS V4 Browser — URL Reading Operations

Reads content from URLs for information retrieval. Browser operations
are Tier 1 (low-risk autonomous) — they read from the web but do
not mutate local state.

Distinct from Search: Search finds URLs. Browser reads them.

Reference: Master Blueprint Section 7, Section 12.4 — browser.py
"""

import logging
from typing import Any, Dict, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Safety limits
MAX_CONTENT_LENGTH = 50000
DEFAULT_TIMEOUT = 15

# Blocked URL patterns
BLOCKED_SCHEMES = {"file", "ftp", "data", "javascript"}


class Browser:
    """URL content reading for VARGAS V4.

    Reads and extracts text content from web URLs. Does not execute
    JavaScript or render pages — text extraction only.

    Trust tier: 1 (low-risk autonomous)

    Attributes:
        timeout: Default request timeout.
        max_content_length: Maximum content to read per URL.
    """

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        max_content_length: int = MAX_CONTENT_LENGTH,
    ):
        self.timeout = timeout
        self.max_content_length = max_content_length
        self._available = self._check_dependencies()
        logger.info("[BROWSER] Initialized: available=%s timeout=%d", self._available, timeout)

    @staticmethod
    def _check_dependencies() -> bool:
        """Check if HTTP client dependencies are available."""
        try:
            import httpx  # noqa: F401
            return True
        except ImportError:
            try:
                import requests  # noqa: F401
                return True
            except ImportError:
                return False

    def _validate_url(self, url: str) -> Optional[str]:
        """Validate a URL for safety.

        Args:
            url: URL to validate.

        Returns:
            Error message if invalid, None if valid.
        """
        try:
            parsed = urlparse(url)
        except Exception:
            return f"Invalid URL: {url}"

        if not parsed.scheme:
            return f"URL missing scheme: {url}"

        if parsed.scheme.lower() in BLOCKED_SCHEMES:
            return f"Blocked URL scheme: {parsed.scheme}"

        if not parsed.netloc:
            return f"URL missing host: {url}"

        return None

    def read_url(self, url: str) -> Dict[str, Any]:
        """Read content from a URL.

        Trust tier: 1 (low-risk autonomous)

        Args:
            url: URL to read.

        Returns:
            Dict with content, status code, and metadata.
        """
        # Validate URL
        error = self._validate_url(url)
        if error:
            return {"success": False, "url": url, "error": error}

        if not self._available:
            return {
                "success": False,
                "url": url,
                "error": "No HTTP client available. Install httpx or requests.",
            }

        logger.info("[BROWSER] Reading: %s", url[:200])

        try:
            # Try httpx first, fall back to requests
            try:
                import httpx
                response = httpx.get(url, timeout=self.timeout, follow_redirects=True)
                status_code = response.status_code
                content = response.text[:self.max_content_length]
                content_type = response.headers.get("content-type", "")
            except ImportError:
                import requests
                response = requests.get(url, timeout=self.timeout, allow_redirects=True)
                status_code = response.status_code
                content = response.text[:self.max_content_length]
                content_type = response.headers.get("content-type", "")

            success = 200 <= status_code < 400

            return {
                "success": success,
                "url": url,
                "status_code": status_code,
                "content": content,
                "content_type": content_type,
                "content_length": len(content),
                "truncated": len(response.text) > self.max_content_length,
            }

        except Exception as e:
            logger.error("[BROWSER] Read failed for %s: %s", url[:200], e)
            return {
                "success": False,
                "url": url,
                "error": str(e),
            }

    def summary(self) -> Dict[str, Any]:
        """Return browser status summary."""
        return {
            "available": self._available,
            "timeout": self.timeout,
            "max_content_length": self.max_content_length,
        }
