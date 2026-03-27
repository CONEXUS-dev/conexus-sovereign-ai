"""
SovereignNEXT — Claim Extractor
Turns raw LLM text output into a bounded set of Claim objects.

Approach: LLM-as-parser with strict JSON schema + post-processing rules.
Fallback: Sentence-splitting if JSON parse fails.
Hard cap: Max 10 claims per extraction (Pylo adjustment).
Dedup: Cosine > 0.9 against existing claims = duplicate.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Protocol

from SovereignNEXT.state.claim import Claim

logger = logging.getLogger(__name__)

# Hard cap per Pylo adjustment
MAX_CLAIMS_PER_EXTRACTION = 10

# Dedup threshold
DEDUP_COSINE_THRESHOLD = 0.9

# Extraction prompt — asks LLM to parse its own output into structured claims
EXTRACTION_SYSTEM_PROMPT = (
    "You are a precise text parser. Extract distinct claims from the given text.\n"
    "A claim is a single factual assertion, recommendation, or conclusion.\n"
    "Return ONLY a valid JSON array. No commentary, no markdown, no explanation.\n"
    "Each element: {\"text\": \"...\", \"confidence\": 0.0-1.0, \"tags\": [...]}\n"
    "Maximum 10 claims. Focus on the most substantive ones."
)

EXTRACTION_USER_TEMPLATE = "Extract all distinct claims from this text as JSON:\n\n{text}"


class LLMInterface(Protocol):
    """Minimal interface for the LLM client needed by claim extraction."""

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


def _parse_json_claims(response: str) -> Optional[List[Dict[str, Any]]]:
    """Try to parse LLM response as JSON array of claims."""
    # Strip markdown code fences if present
    cleaned = response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        # Remove first and last fence lines
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    # Try direct parse
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # Try to find JSON array within the text
    match = re.search(r'\[.*\]', cleaned, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    return None


def _fallback_sentence_split(text: str) -> List[Dict[str, Any]]:
    """Fallback: split text into sentences and create claims with default confidence."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    claims = []
    for s in sentences:
        s = s.strip()
        if len(s) > 20 and not s.startswith("[") and not s.startswith("*"):
            claims.append({
                "text": s,
                "confidence": 0.5,
                "tags": ["fallback_extraction"],
            })
    return claims[:MAX_CLAIMS_PER_EXTRACTION]


def extract_claims(
    text: str,
    llm: LLMInterface,
    model: str,
    source: str = "",
    mission_id: Optional[str] = None,
    existing_claims: Optional[List[Claim]] = None,
    existing_embeddings: Optional[Dict[str, List[float]]] = None,
) -> List[Claim]:
    """Extract claims from raw LLM text output.

    Args:
        text: Raw text to extract claims from.
        llm: LLM client with generate() and embed() methods.
        model: Model name to use for extraction (e.g. Sway model).
        source: Source label (e.g. "collapse_M1").
        mission_id: Current mission ID.
        existing_claims: Claims already in SystemState (for dedup).
        existing_embeddings: Pre-computed embeddings for existing claims, keyed by claim ID.

    Returns:
        List of new, deduplicated Claim objects (max 10).
    """
    existing_claims = existing_claims or []
    existing_embeddings = existing_embeddings or {}

    # Truncate very long text to avoid blowing the context window
    max_input_chars = 3000
    if len(text) > max_input_chars:
        text_for_prompt = text[:max_input_chars] + "\n[...truncated...]"
    else:
        text_for_prompt = text

    # Step 1: Ask LLM to parse text into structured claims
    user_prompt = EXTRACTION_USER_TEMPLATE.format(text=text_for_prompt)
    try:
        response = llm.generate(
            model=model,
            system_prompt=EXTRACTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temp=0.0,
            max_tokens=1024,
        )
        raw_claims = _parse_json_claims(response)
    except Exception as e:
        logger.warning("LLM claim extraction failed: %s — using fallback", e)
        raw_claims = None

    # Step 2: Fallback to sentence splitting if JSON parse failed
    if raw_claims is None:
        logger.info("JSON parse failed, falling back to sentence splitting")
        raw_claims = _fallback_sentence_split(text)

    # Step 3: Enforce hard cap
    raw_claims = raw_claims[:MAX_CLAIMS_PER_EXTRACTION]

    # Step 4: Convert to Claim objects
    new_claims: List[Claim] = []
    for rc in raw_claims:
        if not isinstance(rc, dict) or "text" not in rc:
            continue
        claim_text = str(rc["text"]).strip()
        if not claim_text:
            continue
        confidence = float(rc.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))
        tags = rc.get("tags", [])
        if not isinstance(tags, list):
            tags = []
        tags = [str(t) for t in tags]

        new_claims.append(Claim(
            text=claim_text,
            confidence=confidence,
            source=source,
            tags=tags,
            mission_id=mission_id,
            operator=source.split("_")[0] if "_" in source else source,
        ))

    # Step 5: Dedup against existing claims
    if existing_claims and new_claims:
        new_claims = _dedup_claims(new_claims, existing_claims, llm, existing_embeddings)

    logger.info(
        "Extracted %d claims from %d chars (source=%s, mission=%s)",
        len(new_claims), len(text), source, mission_id,
    )
    return new_claims


def _dedup_claims(
    new_claims: List[Claim],
    existing_claims: List[Claim],
    llm: LLMInterface,
    existing_embeddings: Dict[str, List[float]],
) -> List[Claim]:
    """Remove new claims that are too similar to existing ones (cosine > 0.9)."""
    # Embed new claims
    new_texts = [c.text for c in new_claims]
    try:
        new_vecs = llm.embed(new_texts)
        if isinstance(new_vecs[0], float):
            # Single text was embedded (shouldn't happen with list input, but safety)
            new_vecs = [new_vecs]
    except Exception as e:
        logger.warning("Embedding for dedup failed: %s — skipping dedup", e)
        return new_claims

    # Get or compute embeddings for existing claims
    existing_vecs: List[List[float]] = []
    for ec in existing_claims:
        if ec.id in existing_embeddings:
            existing_vecs.append(existing_embeddings[ec.id])
        else:
            try:
                vec = llm.embed(ec.text)
                existing_vecs.append(vec)
                existing_embeddings[ec.id] = vec
            except Exception:
                continue

    if not existing_vecs:
        return new_claims

    # Filter duplicates
    deduplicated: List[Claim] = []
    for i, nc in enumerate(new_claims):
        is_dup = False
        for ev in existing_vecs:
            sim = _cosine_similarity(new_vecs[i], ev)
            if sim > DEDUP_COSINE_THRESHOLD:
                logger.debug("Dedup: claim '%s...' is duplicate (sim=%.3f)", nc.text[:40], sim)
                is_dup = True
                break
        if not is_dup:
            deduplicated.append(nc)

    if len(deduplicated) < len(new_claims):
        logger.info(
            "Dedup removed %d/%d claims (threshold=%.2f)",
            len(new_claims) - len(deduplicated), len(new_claims), DEDUP_COSINE_THRESHOLD,
        )
    return deduplicated
