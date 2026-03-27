"""
SovereignNEXT — Tension Detector
Identifies contradictions, tradeoffs, and polarities between claims using
embedding similarity bands + LLM-as-judge confirmation.

Approach:
  1. Embed all claims via all-MiniLM-L6-v2
  2. Compute pairwise cosine similarity
  3. Keep candidate pairs in the 0.3–0.7 band (related but not identical)
  4. LLM-as-judge confirms the relationship type
  5. CONTRADICTION/TRADEOFF/POLARITY → create Tension with status="open"
"""

import logging
from typing import Any, Dict, List, Optional, Protocol

from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.emoji_vector import EmojiVector
from SovereignNEXT.state.tension import Tension

logger = logging.getLogger(__name__)

# Similarity band for candidate tension pairs
SIMILARITY_LOWER = 0.3
SIMILARITY_UPPER = 0.7

# Valid judge outputs that create tensions
TENSION_RELATIONS = {"CONTRADICTION": "contradiction", "TRADEOFF": "tradeoff", "POLARITY": "polarity"}

# Judge prompt
JUDGE_SYSTEM_PROMPT = (
    "You are a precise relationship classifier. Given two claims, determine their relationship.\n"
    "Reply with EXACTLY one word — no explanation, no punctuation:\n"
    "AGREEMENT\n"
    "CONTRADICTION\n"
    "TRADEOFF\n"
    "POLARITY\n"
    "UNRELATED"
)

JUDGE_USER_TEMPLATE = 'Claim A: "{claim_a}"\nClaim B: "{claim_b}"\n\nRelationship:'

# Entropy thresholds for polarity bias
POLARITY_ENTROPY_THRESHOLD = 0.6
POLARITY_CHAOS_THRESHOLD = 0.3

POLARITY_BIAS_INSTRUCTION = (
    "\n[CONTEXT: These claims exist within a high-entropy contradiction field. "
    "The accumulated tension structure is irreducible, not merely oppositional. "
    "Prefer POLARITY over CONTRADICTION when the opposition cannot be resolved "
    "by choosing one side. Prefer POLARITY over TRADEOFF when neither pole "
    "can be traded away without destroying the other.]"
)

CHAOS_BIAS_INSTRUCTION = (
    "\n[CONTEXT: The contradiction field surrounding these claims shows high chaos. "
    "The semantic space is actively destabilizing. POLARITY is the expected "
    "classification for genuinely irreducible structural opposition.]"
)


class LLMInterface(Protocol):
    """Minimal interface for the LLM client needed by tension detection."""

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


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _find_candidate_pairs(
    new_claims: List[Claim],
    existing_claims: List[Claim],
    new_embeddings: List[List[float]],
    existing_embeddings: List[List[float]],
) -> List[tuple]:
    """Find claim pairs in the 0.3–0.7 similarity band."""
    candidates = []
    for i, nc in enumerate(new_claims):
        for j, ec in enumerate(existing_claims):
            # Skip same-operator same-iteration pairs
            if nc.operator == ec.operator and nc.mission_id == ec.mission_id:
                continue
            sim = _cosine_similarity(new_embeddings[i], existing_embeddings[j])
            if SIMILARITY_LOWER <= sim <= SIMILARITY_UPPER:
                candidates.append((nc, ec, sim))
    return candidates


def _build_judge_prompt(
    claim_a: Claim,
    claim_b: Claim,
    emoji_context: Optional[EmojiVector] = None,
) -> tuple:
    """Build system and user prompts for the judge, with optional polarity bias.

    Returns (system_prompt, user_prompt).
    """
    system_prompt = JUDGE_SYSTEM_PROMPT
    user_prompt = JUDGE_USER_TEMPLATE.format(claim_a=claim_a.text, claim_b=claim_b.text)

    if emoji_context is not None:
        entropy = emoji_context.entropy
        chaos = emoji_context.chaos_index

        if entropy >= POLARITY_ENTROPY_THRESHOLD:
            user_prompt += POLARITY_BIAS_INSTRUCTION
            logger.debug(
                "Polarity bias applied (entropy=%.3f >= %.3f)",
                entropy, POLARITY_ENTROPY_THRESHOLD,
            )

        if chaos >= POLARITY_CHAOS_THRESHOLD:
            user_prompt += CHAOS_BIAS_INSTRUCTION
            logger.debug(
                "Chaos bias applied (chaos_index=%.3f >= %.3f)",
                chaos, POLARITY_CHAOS_THRESHOLD,
            )

    return system_prompt, user_prompt


def _judge_relationship(
    claim_a: Claim,
    claim_b: Claim,
    llm: LLMInterface,
    model: str,
    emoji_context: Optional[EmojiVector] = None,
) -> Optional[str]:
    """Ask LLM to classify the relationship between two claims.

    When emoji_context is provided with high entropy or chaos, a polarity-bias
    instruction is appended to the judge prompt. This is a prompt-level bias,
    not a hard override -- the judge still decides.

    Returns one of: "contradiction", "tradeoff", "polarity", or None (agreement/unrelated).
    """
    system_prompt, user_prompt = _build_judge_prompt(claim_a, claim_b, emoji_context)
    try:
        response = llm.generate(
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temp=0.0,
            max_tokens=16,
        )
    except Exception as e:
        logger.warning("LLM judge call failed: %s", e)
        return None

    # Parse the response — expect a single word
    word = response.strip().upper().split()[0] if response.strip() else ""
    # Strip any trailing punctuation
    word = word.rstrip(".,;:!?")
    return TENSION_RELATIONS.get(word)


def detect_tensions(
    new_claims: List[Claim],
    existing_claims: List[Claim],
    llm: LLMInterface,
    model: str,
    embedding_cache: Optional[Dict[str, List[float]]] = None,
    emoji_context: Optional[EmojiVector] = None,
) -> List[Tension]:
    """Detect tensions between new claims and existing claims.

    Args:
        new_claims: Claims just extracted in this iteration.
        existing_claims: All claims already in SystemState.
        llm: LLM client with generate() and embed() methods.
        model: Model name to use for judging.
        embedding_cache: Dict mapping claim_id -> embedding vector (populated in-place).
        emoji_context: Optional EmojiVector whose entropy/chaos biases the judge
            toward POLARITY classification. None = no bias (v1 behavior).

    Returns:
        List of new Tension objects with status="open".
    """
    embedding_cache = embedding_cache if embedding_cache is not None else {}

    if not new_claims or not existing_claims:
        logger.info("No claims to compare — skipping tension detection")
        return []

    # Step 1: Embed new claims
    new_embeddings = _get_embeddings(new_claims, llm, embedding_cache)
    if new_embeddings is None:
        return []

    # Step 2: Embed existing claims
    existing_embeddings = _get_embeddings(existing_claims, llm, embedding_cache)
    if existing_embeddings is None:
        return []

    # Step 3: Find candidate pairs in similarity band
    candidates = _find_candidate_pairs(new_claims, existing_claims, new_embeddings, existing_embeddings)
    logger.info(
        "Tension detection: %d new × %d existing → %d candidates in [%.1f, %.1f] band",
        len(new_claims), len(existing_claims), len(candidates),
        SIMILARITY_LOWER, SIMILARITY_UPPER,
    )

    if not candidates:
        return []

    # Step 4: LLM-as-judge for each candidate pair
    tensions: List[Tension] = []
    for claim_a, claim_b, sim in candidates:
        relation = _judge_relationship(claim_a, claim_b, llm, model, emoji_context)
        if relation is not None:
            t = Tension(
                pole_a=claim_a.text,
                pole_b=claim_b.text,
                relation_type=relation,
                status="open",
                source_claims=[claim_a.id, claim_b.id],
                mission_id=claim_a.mission_id or claim_b.mission_id,
            )
            t.metrics.tension_strength = sim  # Use similarity as initial tension strength
            tensions.append(t)
            logger.info(
                "Tension found: %s (%s ↔ %s, sim=%.3f)",
                relation, claim_a.text[:30], claim_b.text[:30], sim,
            )

    logger.info("Detected %d tensions from %d candidates", len(tensions), len(candidates))
    return tensions


def _get_embeddings(
    claims: List[Claim],
    llm: LLMInterface,
    cache: Dict[str, List[float]],
) -> Optional[List[List[float]]]:
    """Get embeddings for claims, using cache where available."""
    uncached_indices = []
    uncached_texts = []
    result: List[Optional[List[float]]] = [None] * len(claims)

    for i, c in enumerate(claims):
        if c.id in cache:
            result[i] = cache[c.id]
        else:
            uncached_indices.append(i)
            uncached_texts.append(c.text)

    if uncached_texts:
        try:
            vecs = llm.embed(uncached_texts)
            # Handle single vs batch
            if uncached_texts and isinstance(vecs[0], float):
                vecs = [vecs]
            for idx, vec in zip(uncached_indices, vecs):
                result[idx] = vec
                cache[claims[idx].id] = vec
        except Exception as e:
            logger.warning("Embedding failed: %s", e)
            return None

    return result  # type: ignore[return-value]
