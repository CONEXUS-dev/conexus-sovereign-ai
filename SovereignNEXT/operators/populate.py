"""
SovereignNEXT — Populate
Single entry point for Phase 2: turns raw LLM text into a populated SystemState
with Claims and Tensions. No operator logic, no paradox creation, no emoji vectors.

Usage:
    state = SystemState(mission_id="M1")
    state = populate_state(raw_text, state, llm, model, source="collapse_M1")
"""

import logging
from typing import Any, Dict, List, Optional, Protocol

from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.claim_extractor import extract_claims
from SovereignNEXT.operators.tension_detector import detect_tensions

logger = logging.getLogger(__name__)


class LLMInterface(Protocol):
    """Minimal interface for the LLM client."""

    def generate(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temp: float = ...,
        max_tokens: int = ...,
        **kwargs: Any,
    ) -> str: ...

    def embed(self, text: str | list[str]) -> list[float] | list[list[float]]: ...


def populate_state(
    raw_text: str,
    state: SystemState,
    llm: LLMInterface,
    model: str,
    source: str = "",
    mission_id: Optional[str] = None,
    embedding_cache: Optional[Dict[str, List[float]]] = None,
) -> SystemState:
    """Extract claims from raw text and detect tensions against existing state.

    This is the Phase 2 entry point. It:
      1. Extracts claims from raw_text (max 10, deduplicated)
      2. Adds new claims to state
      3. Detects tensions between new claims and all existing claims
      4. Adds new tensions to state

    It does NOT create paradoxes, emoji vectors, or run any operator logic.

    Args:
        raw_text: Raw LLM output to process.
        state: Current SystemState (modified in place and returned).
        llm: LLM client with generate() and embed() methods.
        model: Model name for extraction and judging.
        source: Source label (e.g. "collapse_M1", "become_M3").
        mission_id: Current mission ID.
        embedding_cache: Shared embedding cache (populated in-place across calls).

    Returns:
        The updated SystemState.
    """
    embedding_cache = embedding_cache if embedding_cache is not None else {}
    mission_id = mission_id or state.mission_id

    # Snapshot existing claims before extraction (for tension detection)
    existing_claims = list(state.claims)

    # Step 1: Extract claims
    new_claims = extract_claims(
        text=raw_text,
        llm=llm,
        model=model,
        source=source,
        mission_id=mission_id,
        existing_claims=existing_claims,
        existing_embeddings=embedding_cache,
    )

    # Step 2: Add new claims to state
    for claim in new_claims:
        state.add_claim(claim)

    logger.info(
        "populate_state: added %d claims (total: %d, source=%s)",
        len(new_claims), len(state.claims), source,
    )

    # Step 3: Detect tensions between new claims and all existing claims
    if new_claims and existing_claims:
        new_tensions = detect_tensions(
            new_claims=new_claims,
            existing_claims=existing_claims,
            llm=llm,
            model=model,
            embedding_cache=embedding_cache,
        )

        # Step 4: Add tensions to state
        for tension in new_tensions:
            state.add_tension(tension)

        logger.info(
            "populate_state: added %d tensions (total: %d)",
            len(new_tensions), len(state.tensions),
        )

    state.iteration += 1
    logger.info("populate_state: iteration %d complete — %s", state.iteration, state.summary())
    return state
