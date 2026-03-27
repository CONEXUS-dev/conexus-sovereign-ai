"""
OpenClaw Gateway Bridge for SovereignNEXT.

Optional routing layer: if enabled, LLM calls are routed through the
OpenClaw Gateway HTTP endpoint. If the gateway is unavailable, falls back
to direct Gemini API calls.

This is an additive integration — no modifications to existing OpenClaw
config or SovereignNEXT governance.

Usage:
    client = OpenClawGatewayClient(gemini_model="gemini-2.0-flash")
    text = client.generate("model", "system", "user")
    vec = client.embed("text")
"""

import os
import time
import logging
import uuid
from typing import Any

from SovereignNEXT.adapters.cloud_llm.base import CloudLLMBase
from SovereignNEXT.adapters.cloud_llm.gemini_client import GeminiLLMClient

logger = logging.getLogger(__name__)

DEFAULT_GATEWAY_URL = os.getenv("OPENCLAW_GATEWAY_URL", "http://localhost:8080")


class OpenClawGatewayClient(CloudLLMBase):
    """LLM client that routes through OpenClaw Gateway with Gemini fallback.

    If the gateway is reachable, sends LLM requests to:
        POST {gateway_url}/v1/chat/completions

    If the gateway is unreachable, falls back to direct Gemini API.
    Embedding always uses Gemini directly (gateway does not provide embeddings).
    """

    def __init__(
        self,
        gateway_url: str = DEFAULT_GATEWAY_URL,
        gemini_model: str = "gemini-2.0-flash",
        timeout: float = 60.0,
    ):
        self.gateway_url = gateway_url.rstrip("/")
        self.timeout = timeout
        self._gemini_fallback = GeminiLLMClient(default_model=gemini_model)
        self._gateway_available = None
        self._route_log = []
        self._request_count = 0

        logger.info(
            "[OPENCLAW] Gateway bridge initialized — url=%s, fallback=gemini",
            self.gateway_url,
        )

    def _check_gateway(self) -> bool:
        """Check if the OpenClaw Gateway is reachable."""
        if self._gateway_available is not None:
            return self._gateway_available

        try:
            import requests
            resp = requests.get(
                f"{self.gateway_url}/health",
                timeout=5.0,
            )
            self._gateway_available = resp.status_code == 200
        except Exception:
            self._gateway_available = False

        logger.info(
            "[OPENCLAW] Gateway check: %s",
            "available" if self._gateway_available else "unavailable",
        )
        return self._gateway_available

    def generate(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temp: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        """Generate text, routing through gateway if available."""
        request_id = str(uuid.uuid4())[:8]
        self._request_count += 1

        if self._check_gateway():
            try:
                return self._generate_via_gateway(
                    model, system_prompt, user_prompt, temp, max_tokens, request_id,
                )
            except Exception as e:
                logger.warning(
                    "[OPENCLAW] req=%s gateway failed (%s), falling back to gemini",
                    request_id, e,
                )
                self._route_log.append({"req": request_id, "route": "gemini-fallback"})

        self._route_log.append({"req": request_id, "route": "gemini-direct"})
        return self._gemini_fallback.generate(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temp=temp,
            max_tokens=max_tokens,
            **kwargs,
        )

    def _generate_via_gateway(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temp: float,
        max_tokens: int,
        request_id: str,
    ) -> str:
        """Send a generate request through the OpenClaw Gateway."""
        import requests

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temp,
            "max_tokens": max_tokens,
        }

        logger.info(
            "[OPENCLAW] req=%s routing via gateway %s",
            request_id, self.gateway_url,
        )

        t0 = time.perf_counter()
        resp = requests.post(
            f"{self.gateway_url}/v1/chat/completions",
            json=payload,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        elapsed = time.perf_counter() - t0

        data = resp.json()
        text = data["choices"][0]["message"]["content"]

        logger.info(
            "[OPENCLAW] req=%s gateway responded in %.2fs, chars=%d",
            request_id, elapsed, len(text),
        )
        self._route_log.append({"req": request_id, "route": "openclaw-gateway"})
        return text

    def embed(self, text: str | list[str]) -> list[float] | list[list[float]]:
        """Embeddings always go through Gemini directly."""
        return self._gemini_fallback.embed(text)

    def close(self) -> None:
        """Release resources."""
        self._gemini_fallback.close()
        gateway_count = sum(1 for r in self._route_log if r["route"] == "openclaw-gateway")
        direct_count = sum(1 for r in self._route_log if "gemini" in r["route"])
        logger.info(
            "[OPENCLAW] Bridge closed — %d total requests (gateway=%d, gemini=%d)",
            self._request_count, gateway_count, direct_count,
        )

    def stats(self) -> dict:
        """Return routing statistics."""
        gateway_count = sum(1 for r in self._route_log if r["route"] == "openclaw-gateway")
        direct_count = sum(1 for r in self._route_log if "gemini" in r["route"])
        return {
            "total_requests": self._request_count,
            "gateway_routed": gateway_count,
            "gemini_direct": direct_count,
            "gateway_url": self.gateway_url,
            "gateway_available": self._gateway_available,
            **self._gemini_fallback.stats(),
        }
