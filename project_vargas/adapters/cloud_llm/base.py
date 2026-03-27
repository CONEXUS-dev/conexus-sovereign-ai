"""
Base interface for cloud LLM adapters.

Matches the LLMInterface expected by Project Vargas:
  - generate(model, system_prompt, user_prompt, temp, max_tokens, **kwargs) -> str
  - embed(text) -> list[float] | list[list[float]]
  - close() -> None

Any cloud adapter (Gemini, OpenAI, Anthropic) must subclass this.
"""

from abc import ABC, abstractmethod
from typing import Any


class CloudLLMBase(ABC):
    """Abstract base class for cloud LLM clients."""

    @abstractmethod
    def generate(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temp: float = 0.7,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> str:
        """Generate text from a prompt pair."""
        ...

    @abstractmethod
    def embed(self, text: str | list[str]) -> list[float] | list[list[float]]:
        """Return embedding vector(s) for input text(s)."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Release any resources held by the client."""
        ...

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
