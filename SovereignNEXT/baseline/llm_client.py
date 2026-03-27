import os
import time
import logging
from typing import Any

from gpt4all import GPT4All, Embed4All
from llama_cpp import Llama

logger = logging.getLogger(__name__)

SWAY_MODEL = "Meta-Llama-3-8B-Instruct.Q4_0.gguf"
OPIE_MODEL = "Mistral-7B-Instruct-v0.3.Q4_0.gguf"
OUTER_MODEL = "Phi-4-mini-instruct-Q4_K_M.gguf"

DEFAULT_DEVICE = os.environ.get("GPT4ALL_DEVICE", "cpu")
DEFAULT_N_CTX = int(os.environ.get("GPT4ALL_CTX", "4096"))
DEFAULT_MODEL_PATH = os.environ.get("GPT4ALL_MODEL_PATH", None)


class LLMClientError(Exception):
    pass


class ModelNotFoundError(LLMClientError):
    pass


class GenerationError(LLMClientError):
    pass


class LLMClient:
    def __init__(
        self,
        device: str = DEFAULT_DEVICE,
        n_ctx: int = DEFAULT_N_CTX,
        model_path: str | None = DEFAULT_MODEL_PATH,
        verbose: bool = False,
    ):
        self._models: dict[str, GPT4All] = {}
        self._llama_models: dict[str, Llama] = {}
        self._embedder: Embed4All | None = None
        self.device = device
        self.n_ctx = n_ctx
        self.model_path = model_path
        self.verbose = verbose

    def _get_model(self, model_name: str) -> GPT4All:
        if model_name not in self._models:
            logger.info("Loading model: %s (device=%s, n_ctx=%d)", model_name, self.device, self.n_ctx)
            t0 = time.perf_counter()
            try:
                self._models[model_name] = GPT4All(
                    model_name,
                    model_path=self.model_path,
                    device=self.device,
                    n_ctx=self.n_ctx,
                    allow_download=True,
                    verbose=self.verbose,
                )
            except Exception as e:
                raise ModelNotFoundError(f"Failed to load model '{model_name}': {e}") from e
            elapsed = time.perf_counter() - t0
            logger.info("Model %s loaded in %.2fs", model_name, elapsed)
        return self._models[model_name]

    def generate(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temp: float = 0.7,
        max_tokens: int = 2048,
        top_k: int = 40,
        top_p: float = 0.4,
        min_p: float = 0.0,
        repeat_penalty: float = 1.18,
    ) -> str:
        m = self._get_model(model)
        prompt_len = len(system_prompt) + len(user_prompt)
        logger.info(
            "generate() model=%s temp=%.2f max_tokens=%d prompt_chars=%d",
            model, temp, max_tokens, prompt_len,
        )
        t0 = time.perf_counter()
        try:
            with m.chat_session(system_prompt=system_prompt):
                response = m.generate(
                    user_prompt,
                    max_tokens=max_tokens,
                    temp=temp,
                    top_k=top_k,
                    top_p=top_p,
                    min_p=min_p,
                    repeat_penalty=repeat_penalty,
                )
        except Exception as e:
            raise GenerationError(f"Generation failed for model '{model}': {e}") from e
        elapsed = time.perf_counter() - t0
        logger.info(
            "generate() completed in %.2fs, response_chars=%d",
            elapsed, len(response),
        )
        return response

    def generate_collapse(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2048,
    ) -> str:
        return self.generate(
            model=SWAY_MODEL,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temp=0.0,
            max_tokens=max_tokens,
            top_k=1,
            top_p=1.0,
            min_p=0.0,
            repeat_penalty=1.18,
        )

    def generate_become(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2048,
    ) -> str:
        return self.generate(
            model=OPIE_MODEL,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temp=0.65,
            max_tokens=max_tokens,
            top_k=40,
            top_p=0.4,
            min_p=0.0,
            repeat_penalty=1.18,
        )

    def _get_llama_model(self, model_name: str) -> Llama:
        """Load a model via llama-cpp-python (for models GPT4All can't handle)."""
        if model_name not in self._llama_models:
            model_dir = self.model_path or os.path.join(
                os.path.expanduser("~"), ".cache", "gpt4all"
            )
            model_path = os.path.join(model_dir, model_name)
            logger.info("Loading model via llama-cpp: %s (n_ctx=%d)", model_name, self.n_ctx)
            t0 = time.perf_counter()
            try:
                self._llama_models[model_name] = Llama(
                    model_path=model_path,
                    n_ctx=self.n_ctx,
                    verbose=self.verbose,
                )
            except Exception as e:
                raise ModelNotFoundError(f"Failed to load model '{model_name}' via llama-cpp: {e}") from e
            elapsed = time.perf_counter() - t0
            logger.info("Model %s loaded via llama-cpp in %.2fs", model_name, elapsed)
        return self._llama_models[model_name]

    def generate_outer(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2048,
    ) -> str:
        """Generate using Phi-4-mini via llama-cpp-python backend."""
        m = self._get_llama_model(OUTER_MODEL)
        prompt_len = len(system_prompt) + len(user_prompt)
        approx_tokens = prompt_len // 4 + max_tokens
        if approx_tokens > self.n_ctx:
            logger.warning(
                "[OUTER] estimated tokens (%d) may exceed n_ctx (%d) — response may be truncated",
                approx_tokens, self.n_ctx,
            )
        logger.info(
            "[OUTER] generate_outer() model=%s temp=%.2f max_tokens=%d prompt_chars=%d",
            OUTER_MODEL, 0.4, max_tokens, prompt_len,
        )
        t0 = time.perf_counter()
        try:
            result = m.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.4,
                top_k=40,
                top_p=0.5,
                repeat_penalty=1.18,
            )
            response = result["choices"][0]["message"]["content"]
        except Exception as e:
            raise GenerationError(f"Generation failed for model '{OUTER_MODEL}': {e}") from e
        elapsed = time.perf_counter() - t0
        logger.info(
            "generate_outer() completed in %.2fs, response_chars=%d",
            elapsed, len(response),
        )
        return response

    def embed(self, text: str | list[str]) -> list[float] | list[list[float]]:
        if self._embedder is None:
            logger.info("Loading embedding model (all-MiniLM-L6-v2)")
            self._embedder = Embed4All()
        t0 = time.perf_counter()
        result = self._embedder.embed(text)
        elapsed = time.perf_counter() - t0
        if isinstance(text, str):
            logger.info("embed() completed in %.2fs, dim=%d", elapsed, len(result))
        else:
            logger.info("embed() completed in %.2fs, batch_size=%d", elapsed, len(text))
        return result

    def list_available_models(self) -> list[dict[str, Any]]:
        return GPT4All.list_models()

    def list_loaded_models(self) -> list[str]:
        return list(self._models.keys())

    def health_check(self) -> bool:
        try:
            if self._models:
                model_name = next(iter(self._models))
                m = self._models[model_name]
                with m.chat_session():
                    m.generate("Hi", max_tokens=5)
                return True
            test_embedder = Embed4All()
            test_embedder.embed("health check")
            test_embedder.close()
            return True
        except Exception as e:
            logger.error("Health check failed: %s", e)
            return False

    def unload_model(self, model_name: str) -> None:
        if model_name in self._models:
            logger.info("Unloading model: %s", model_name)
            self._models[model_name].close()
            del self._models[model_name]

    def close(self) -> None:
        for name in [*self._models]:
            self._models[name].close()
        self._models.clear()
        for name in [*self._llama_models]:
            del self._llama_models[name]
        self._llama_models.clear()
        if self._embedder is not None:
            self._embedder.close()
            self._embedder = None
        logger.info("LLMClient closed, all models unloaded")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    print("=" * 60)
    print("CONEXUS LLMClient — GPT4All Integration Test")
    print("=" * 60)

    with LLMClient() as client:
        print("\n--- Health Check ---")
        healthy = client.health_check()
        print(f"Health: {'OK' if healthy else 'FAILED'}")

        print(f"\n--- Testing Sway (Collapse) with {SWAY_MODEL} ---")
        t0 = time.perf_counter()
        sway_response = client.generate_collapse(
            system_prompt="You are Sway, a Collapse agent. Be concise and decisive.",
            user_prompt="Break down the task of setting up a Python project into 3 steps.",
        )
        print(f"Sway ({time.perf_counter() - t0:.2f}s):\n{sway_response}\n")

        print(f"--- Testing Opie (Become) with {OPIE_MODEL} ---")
        t0 = time.perf_counter()
        opie_response = client.generate_become(
            system_prompt="You are Opie, a Become agent. Explore and synthesize.",
            user_prompt="What does it mean for a system to hold contradictions without resolving them?",
        )
        print(f"Opie ({time.perf_counter() - t0:.2f}s):\n{opie_response}\n")

        print(f"--- Testing Outer (Phi-4-mini) with {OUTER_MODEL} ---")
        t0 = time.perf_counter()
        outer_response = client.generate_outer(
            system_prompt="You are the Outer Agent. Be concise.",
            user_prompt="State your identity in one sentence.",
        )
        print(f"Outer ({time.perf_counter() - t0:.2f}s):\n{outer_response}\n")

        print("--- Testing Embeddings ---")
        t0 = time.perf_counter()
        vec = client.embed("The Forgetting Engine amplifies complexity.")
        print(f"Embedding ({time.perf_counter() - t0:.2f}s): dim={len(vec)}, first 5={vec[:5]}\n")

        print("--- Loaded Models ---")
        print(client.list_loaded_models())

    print("\nAll tests complete.")
