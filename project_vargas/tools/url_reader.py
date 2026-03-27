"""
Project Vargas — URL Reader Tool

Fetches a public URL and extracts readable text content.
Supports following links found on a page when directed.
GitHub URLs are handled via the GitHub API for reliable content extraction.

Not a crawler. Reads one page at a time.
"""

import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

import aiohttp
from html.parser import HTMLParser

logger = logging.getLogger(__name__)

# Max content size to prevent memory issues (2MB)
MAX_CONTENT_BYTES = 2 * 1024 * 1024
# Request timeout
REQUEST_TIMEOUT_SEC = 15


class _TextExtractor(HTMLParser):
    """Simple HTML parser that extracts visible text and links."""

    SKIP_TAGS = {"script", "style", "noscript", "meta", "head", "link", "svg"}

    def __init__(self):
        super().__init__()
        self._text_parts: List[str] = []
        self._links: List[Dict[str, str]] = []
        self._skip_depth = 0
        self._current_href: Optional[str] = None
        self._current_link_text: List[str] = []

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        if tag_lower in self.SKIP_TAGS:
            self._skip_depth += 1
        if tag_lower == "a":
            attr_dict = dict(attrs)
            href = attr_dict.get("href", "")
            if href and not href.startswith(("#", "javascript:", "mailto:")):
                self._current_href = href
                self._current_link_text = []
        if tag_lower in ("p", "br", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr"):
            self._text_parts.append("\n")

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag_lower == "a" and self._current_href:
            link_text = " ".join(self._current_link_text).strip()
            if link_text:
                self._links.append({"text": link_text, "href": self._current_href})
            self._current_href = None
            self._current_link_text = []

    def handle_data(self, data):
        if self._skip_depth > 0:
            return
        text = data.strip()
        if text:
            self._text_parts.append(text)
            if self._current_href is not None:
                self._current_link_text.append(text)

    @property
    def text(self) -> str:
        raw = " ".join(self._text_parts)
        # Collapse whitespace
        raw = re.sub(r'\n\s*\n', '\n\n', raw)
        raw = re.sub(r' +', ' ', raw)
        return raw.strip()

    @property
    def links(self) -> List[Dict[str, str]]:
        return self._links


class URLReaderTool:
    """Fetches and extracts text from public URLs."""

    def __init__(self):
        self._available = True
        logger.info("[URL_READER] URL reader initialized")

    @property
    def available(self) -> bool:
        return self._available

    def _is_github_url(self, url: str) -> bool:
        """Check if a URL points to GitHub."""
        parsed = urlparse(url)
        return parsed.hostname in ("github.com", "www.github.com")

    def _parse_github_path(self, url: str) -> Dict[str, str]:
        """Parse a GitHub URL into owner/repo/path components.

        Returns:
            {"type": "org"|"repo"|"repo_tab"|"file", "owner": str, "repo": str, "path": str}
        """
        parsed = urlparse(url)
        parts = [p for p in parsed.path.strip("/").split("/") if p]

        if not parts:
            return {"type": "unknown"}

        owner = parts[0]

        # github.com/ORG?tab=repositories
        if len(parts) == 1:
            if "tab=repositories" in (parsed.query or ""):
                return {"type": "org", "owner": owner}
            return {"type": "org", "owner": owner}

        repo = parts[1]

        # github.com/ORG/REPO — bare repo page
        if len(parts) == 2:
            return {"type": "repo", "owner": owner, "repo": repo}

        # github.com/ORG/REPO/tree/main/... or /blob/main/...
        if len(parts) >= 4 and parts[2] in ("tree", "blob"):
            file_path = "/".join(parts[4:]) if len(parts) > 4 else ""
            return {"type": "file", "owner": owner, "repo": repo, "ref": parts[3], "path": file_path}

        return {"type": "repo", "owner": owner, "repo": repo}

    async def _read_github_url(self, url: str) -> Dict[str, any]:
        """Read a GitHub URL using the GitHub API for reliable content extraction."""
        info = self._parse_github_path(url)
        gh_headers = {
            "User-Agent": "Vargas/2.1",
            "Accept": "application/vnd.github+json",
        }

        try:
            async with aiohttp.ClientSession() as session:
                if info["type"] == "org":
                    # List repos for the org/user
                    api_url = f"https://api.github.com/users/{info['owner']}/repos?per_page=30&sort=updated"
                    async with session.get(api_url, headers=gh_headers, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SEC)) as resp:
                        if resp.status != 200:
                            return {"success": False, "text": "", "links": [], "url": url, "error": f"GitHub API HTTP {resp.status}"}
                        repos = await resp.json()

                    text_parts = [f"GitHub organization/user: {info['owner']}", f"Public repositories ({len(repos)}):"]
                    links = []
                    for repo in repos[:30]:
                        name = repo.get("name", "")
                        desc = repo.get("description", "") or "No description"
                        lang = repo.get("language", "") or ""
                        stars = repo.get("stargazers_count", 0)
                        updated = repo.get("updated_at", "")[:10]
                        text_parts.append(f"\n• {name} — {desc}")
                        if lang:
                            text_parts.append(f"  Language: {lang} | Stars: {stars} | Updated: {updated}")
                        links.append({"text": name, "href": repo.get("html_url", "")})

                    text = "\n".join(text_parts)
                    logger.info("[URL_READER] GitHub org %s — %d repos", info["owner"], len(repos))
                    return {"success": True, "text": text, "links": links, "url": url, "error": None}

                elif info["type"] == "repo":
                    # Get repo metadata + README
                    api_url = f"https://api.github.com/repos/{info['owner']}/{info['repo']}"
                    readme_url = f"https://raw.githubusercontent.com/{info['owner']}/{info['repo']}/main/README.md"

                    text_parts = []
                    links = []

                    # Fetch repo metadata
                    async with session.get(api_url, headers=gh_headers, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SEC)) as resp:
                        if resp.status == 200:
                            repo_data = await resp.json()
                            name = repo_data.get("full_name", "")
                            desc = repo_data.get("description", "") or "No description"
                            lang = repo_data.get("language", "") or "Unknown"
                            stars = repo_data.get("stargazers_count", 0)
                            forks = repo_data.get("forks_count", 0)
                            topics = repo_data.get("topics", [])
                            license_info = repo_data.get("license", {})
                            license_name = license_info.get("name", "None") if license_info else "None"

                            text_parts.append(f"GitHub Repository: {name}")
                            text_parts.append(f"Description: {desc}")
                            text_parts.append(f"Language: {lang} | Stars: {stars} | Forks: {forks} | License: {license_name}")
                            if topics:
                                text_parts.append(f"Topics: {', '.join(topics)}")
                            text_parts.append("")

                            # Add useful links
                            links.append({"text": "Issues", "href": repo_data.get("html_url", "") + "/issues"})
                            links.append({"text": "Pull Requests", "href": repo_data.get("html_url", "") + "/pulls"})

                    # Fetch README
                    async with session.get(readme_url, headers={"User-Agent": "Vargas/2.1"}, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SEC)) as resp:
                        if resp.status == 200:
                            readme_text = await resp.text()
                            # Cap README at 6000 chars
                            if len(readme_text) > 6000:
                                readme_text = readme_text[:6000] + "\n\n[README truncated]"
                            text_parts.append("--- README.md ---")
                            text_parts.append(readme_text)
                        else:
                            # Try 'master' branch
                            readme_url_master = f"https://raw.githubusercontent.com/{info['owner']}/{info['repo']}/master/README.md"
                            async with session.get(readme_url_master, headers={"User-Agent": "Vargas/2.1"}, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SEC)) as resp2:
                                if resp2.status == 200:
                                    readme_text = await resp2.text()
                                    if len(readme_text) > 6000:
                                        readme_text = readme_text[:6000] + "\n\n[README truncated]"
                                    text_parts.append("--- README.md ---")
                                    text_parts.append(readme_text)
                                else:
                                    text_parts.append("(No README found)")

                    # Fetch file tree (top-level contents)
                    contents_url = f"https://api.github.com/repos/{info['owner']}/{info['repo']}/contents/"
                    async with session.get(contents_url, headers=gh_headers, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SEC)) as resp:
                        if resp.status == 200:
                            contents = await resp.json()
                            if isinstance(contents, list):
                                file_list = [f.get("name", "") for f in contents[:40]]
                                text_parts.append(f"\n--- Repository Contents ---")
                                text_parts.append(", ".join(file_list))

                    text = "\n".join(text_parts)
                    if not text.strip():
                        return {"success": False, "text": "", "links": [], "url": url, "error": "Could not read repository"}

                    logger.info("[URL_READER] GitHub repo %s/%s — %d chars", info["owner"], info["repo"], len(text))
                    return {"success": True, "text": text, "links": links, "url": url, "error": None}

                else:
                    # Unknown GitHub URL type — fall through to normal HTML fetch
                    return None

        except aiohttp.ClientError as e:
            logger.error("[URL_READER] GitHub API error for %s: %s", url[:80], e)
            return {"success": False, "text": "", "links": [], "url": url, "error": f"GitHub API error: {e}"}
        except Exception as e:
            logger.error("[URL_READER] GitHub read failed for %s: %s", url[:80], e)
            return {"success": False, "text": "", "links": [], "url": url, "error": str(e)}

    async def read_url(self, url: str) -> Dict[str, any]:
        """Fetch a URL and extract text content.

        Returns:
            {"success": bool, "text": str, "links": list, "url": str, "error": str|None}
        """
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        # GitHub URLs: use API for reliable content extraction
        if self._is_github_url(url):
            gh_result = await self._read_github_url(url)
            if gh_result is not None:
                return gh_result
            # gh_result is None means unknown GitHub URL type, fall through to HTML

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Vargas/1.0; +https://conexus.global)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SEC),
                    allow_redirects=True,
                    max_redirects=5,
                ) as resp:
                    if resp.status != 200:
                        return {
                            "success": False,
                            "text": "",
                            "links": [],
                            "url": url,
                            "error": f"HTTP {resp.status}",
                        }

                    content_type = resp.headers.get("Content-Type", "")
                    if "text/html" not in content_type and "application/xhtml" not in content_type:
                        return {
                            "success": False,
                            "text": "",
                            "links": [],
                            "url": url,
                            "error": f"Not HTML: {content_type}",
                        }

                    raw = await resp.read()
                    if len(raw) > MAX_CONTENT_BYTES:
                        raw = raw[:MAX_CONTENT_BYTES]

                    html = raw.decode("utf-8", errors="replace")

                    extractor = _TextExtractor()
                    extractor.feed(html)

                    text = extractor.text
                    links = extractor.links

                    # Resolve relative links
                    from urllib.parse import urljoin
                    links = [
                        {"text": link["text"], "href": urljoin(url, link["href"])}
                        for link in links
                    ]

                    # Truncate text if too long for prompt injection
                    if len(text) > 8000:
                        text = text[:8000] + "\n\n[Content truncated — page too long]"

                    logger.info(
                        "[URL_READER] Read %s — %d chars, %d links",
                        url[:80], len(text), len(links),
                    )

                    return {
                        "success": True,
                        "text": text,
                        "links": links[:50],  # cap at 50 links
                        "url": url,
                        "error": None,
                    }

        except aiohttp.ClientError as e:
            logger.error("[URL_READER] Connection error for %s: %s", url[:80], e)
            return {"success": False, "text": "", "links": [], "url": url, "error": str(e)}
        except Exception as e:
            logger.error("[URL_READER] Failed to read %s: %s", url[:80], e)
            return {"success": False, "text": "", "links": [], "url": url, "error": str(e)}

    def format_page_content(self, result: Dict) -> str:
        """Format page content for prompt injection."""
        if not result["success"]:
            return f"Failed to read {result['url']}: {result['error']}"

        parts = [
            f"[PAGE CONTENT from {result['url']}]",
            result["text"],
        ]

        if result["links"]:
            parts.append("\n[LINKS FOUND ON PAGE]")
            for link in result["links"][:20]:
                parts.append(f"- {link['text']}: {link['href']}")
            if len(result["links"]) > 20:
                parts.append(f"  ... and {len(result['links']) - 20} more links")

        parts.append("[END PAGE CONTENT]")
        return "\n".join(parts)
