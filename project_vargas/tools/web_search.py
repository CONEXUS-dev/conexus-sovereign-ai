"""
Project Vargas — Web Search Tool

Google Custom Search API wrapper. Returns top-N results as text.
Falls back gracefully if API keys are not set.

Requires environment variables:
  GOOGLE_CSE_API_KEY — Google API key with Custom Search enabled
  GOOGLE_CSE_ID — Programmable Search Engine ID
"""

import os
import logging
from typing import Dict, List

import aiohttp

logger = logging.getLogger(__name__)

CSE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"


class WebSearchTool:
    """Google Custom Search wrapper for Vargas."""

    def __init__(self):
        self._api_key = os.getenv("GOOGLE_CSE_API_KEY", "")
        self._cse_id = os.getenv("GOOGLE_CSE_ID", "")
        self._available = bool(self._api_key and self._cse_id)
        if not self._available:
            logger.warning("[WEB] Google CSE not configured — web search disabled")
        else:
            logger.info("[WEB] Google Custom Search initialized")

    @property
    def available(self) -> bool:
        return self._available

    async def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Search Google and return a list of results.

        Returns:
            List of {"title": str, "url": str, "snippet": str}
        """
        if not self._available:
            logger.warning("[WEB] Search requested but CSE not configured")
            return []

        params = {
            "key": self._api_key,
            "cx": self._cse_id,
            "q": query,
            "num": min(num_results, 10),
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    CSE_ENDPOINT,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        logger.warning("[WEB] CSE returned status %d", resp.status)
                        return []

                    data = await resp.json()
                    items = data.get("items", [])
                    results = []
                    for item in items[:num_results]:
                        results.append({
                            "title": item.get("title", ""),
                            "url": item.get("link", ""),
                            "snippet": item.get("snippet", ""),
                        })

                    logger.info("[WEB] Search '%s' returned %d results", query[:50], len(results))
                    return results

        except Exception as e:
            logger.error("[WEB] Search failed: %s", e)
            return []

    def format_results(self, results: List[Dict[str, str]]) -> str:
        """Format search results into a text block for prompt injection."""
        if not results:
            return "No web results found."

        lines = ["Web search results:"]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['title']}")
            lines.append(f"   {r['url']}")
            lines.append(f"   {r['snippet']}")
            lines.append("")

        return "\n".join(lines)

    def sync_search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Synchronous search wrapper for non-async contexts."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(
                        asyncio.run, self.search(query, num_results)
                    ).result()
            else:
                return loop.run_until_complete(self.search(query, num_results))
        except RuntimeError:
            return asyncio.run(self.search(query, num_results))
