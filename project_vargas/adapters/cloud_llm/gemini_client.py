"""
Gemini cloud LLM adapter for Project Vargas.

Reads GEMINI_API_KEY from environment. No hardcoded keys.

Usage:
    from project_vargas.adapters.cloud_llm.gemini_client import GeminiLLMClient
    client = GeminiLLMClient()
    text = client.generate("gemini-3.1-pro-preview", "system", "hello", temp=0.7)
    vec = client.embed("some text")
"""

import os
import time
import logging
import uuid
from typing import Any

from project_vargas.adapters.cloud_llm.base import CloudLLMBase

logger = logging.getLogger(__name__)

DEFAULT_GEMINI_MODEL = "gemini-3.1-pro-preview"
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"
MAX_RETRIES = 6
INITIAL_BACKOFF_SEC = 15


class GeminiLLMClient(CloudLLMBase):
    """Cloud LLM client backed by Google Gemini via google-genai SDK."""

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = DEFAULT_GEMINI_MODEL,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ):
        self._api_key = (
            api_key
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        if not self._api_key:
            raise ValueError(
                "GEMINI_API_KEY or GOOGLE_API_KEY environment variable required. "
                "Set it before running: $env:GEMINI_API_KEY = 'your-key'"
            )

        try:
            from google import genai
            self._genai = genai
            self._client = genai.Client(api_key=self._api_key)
        except ImportError:
            raise ImportError(
                "google-genai package not installed. Run: pip install google-genai"
            )

        self.default_model = default_model
        self.embedding_model = embedding_model
        self._request_count = 0
        self._total_latency = 0.0
        logger.info(
            "[GEMINI] Client initialized — model=%s, embedding=%s",
            self.default_model, self.embedding_model,
        )

    def generate(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temp: float = 0.7,
        max_tokens: int = 2048,
        image_parts: list | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate text via Gemini API. Supports multimodal with image_parts."""
        from google.genai import types

        active_model = self.default_model
        request_id = str(uuid.uuid4())[:8]
        prompt_chars = len(system_prompt) + len(user_prompt)

        logger.info(
            "[GEMINI] generate() req=%s model=%s temp=%.2f max_tokens=%d prompt_chars=%d images=%d",
            request_id, active_model, temp, max_tokens, prompt_chars,
            len(image_parts) if image_parts else 0,
        )

        config = types.GenerateContentConfig(
            system_instruction=system_prompt if system_prompt else None,
            temperature=temp,
            max_output_tokens=max_tokens,
        )

        # Build content: text + optional images
        if image_parts:
            content = [user_prompt] + image_parts
        else:
            content = user_prompt

        t0 = time.perf_counter()
        response_text = self._call_with_retry(active_model, content, config, request_id)
        elapsed = time.perf_counter() - t0

        self._request_count += 1
        self._total_latency += elapsed

        logger.info(
            "[GEMINI] generate() req=%s completed in %.2fs, response_chars=%d",
            request_id, elapsed, len(response_text),
        )
        return response_text

    def _call_with_retry(
        self, model: str, content: Any, config: Any, request_id: str,
    ) -> str:
        """Call Gemini with exponential backoff on rate limits."""
        for attempt in range(MAX_RETRIES):
            try:
                time.sleep(0.5)  # light pacing for API courtesy
                resp = self._client.models.generate_content(
                    model=model,
                    contents=content,
                    config=config,
                )
                # Extract text — handle thinking models
                if resp.candidates and resp.candidates[0].content and resp.candidates[0].content.parts:
                    text_parts = []
                    for part in resp.candidates[0].content.parts:
                        if part.text and not getattr(part, "thought", False):
                            text_parts.append(part.text)
                    if text_parts:
                        return "".join(text_parts)
                # Fallback to resp.text for non-thinking models
                if resp.text is not None:
                    return resp.text
                raise ValueError("Gemini returned empty response")
            except Exception as e:
                if "429" in str(e) and attempt < MAX_RETRIES - 1:
                    wait = INITIAL_BACKOFF_SEC * (attempt + 1)
                    logger.warning(
                        "[GEMINI] req=%s rate limited (attempt %d/%d), retrying in %ds...",
                        request_id, attempt + 1, MAX_RETRIES, wait,
                    )
                    time.sleep(wait)
                else:
                    raise

    def embed(self, text: str | list[str]) -> list[float] | list[list[float]]:
        """Compute embeddings via Gemini embedding API."""
        single_input = isinstance(text, str)
        texts = [text] if single_input else text

        logger.info(
            "[GEMINI] embed() model=%s batch_size=%d",
            self.embedding_model, len(texts),
        )

        t0 = time.perf_counter()
        results = []
        for t in texts:
            time.sleep(0.2)  # pacing
            resp = self._client.models.embed_content(
                model=self.embedding_model,
                contents=t,
            )
            results.append(resp.embeddings[0].values)
        elapsed = time.perf_counter() - t0

        logger.info(
            "[GEMINI] embed() completed in %.2fs, dim=%d",
            elapsed, len(results[0]) if results else 0,
        )

        if single_input:
            return results[0]
        return results

    def close(self) -> None:
        """Release resources."""
        logger.info(
            "[GEMINI] Client closed — %d requests, %.1fs total latency",
            self._request_count, self._total_latency,
        )

    def stats(self) -> dict:
        """Return usage statistics."""
        return {
            "requests": self._request_count,
            "total_latency_sec": round(self._total_latency, 2),
            "avg_latency_sec": round(
                self._total_latency / max(self._request_count, 1), 2
            ),
        }
