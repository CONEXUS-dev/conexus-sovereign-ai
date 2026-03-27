"""
SovereignNEXT — Become Expander (Phase 3a)
Per-claim expansion: takes each high-confidence claim and generates 2–4
genuinely distinct alternatives (counter-framing, deeper-why, domain-shift,
limit-case). Single pass only. No routing, no resolution, no loop.

This is the first operator introduced into SovereignNEXT.
It introduces controlled divergence without commitment.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple

from SovereignNEXT.state.claim import Claim
from SovereignNEXT.state.emoji_vector import EmojiVector
from SovereignNEXT.state.paradox import Paradox
from SovereignNEXT.state.system_state import SystemState
from SovereignNEXT.operators.tension_detector import detect_tensions
from SovereignNEXT.operators.emoji_mutator import mutate_become, mutate_paradox_hold

logger = logging.getLogger(__name__)

# Max claims to expand per pass (prevents runaway expansion)
MAX_CLAIMS_TO_EXPAND = 6

# Max expansions per claim
MAX_EXPANSIONS_PER_CLAIM = 4


# ---------------------------------------------------------------------------
# Expansion prompt — Anti-paraphrase rubric
# ---------------------------------------------------------------------------

EXPANSION_SYSTEM_PROMPT = (
    "You are a divergent thinker. Given a claim, generate genuinely distinct alternatives.\n"
    "Each alternative must:\n"
    "- Introduce a concept NOT present in the original claim.\n"
    "- Change the evaluative direction (if original affirms, challenge it; if original is certain, question it).\n"
    "- Be independently falsifiable.\n"
    "- NOT be a paraphrase, restatement, or minor variation of the original.\n"
    "\n"
    "Generate exactly 4 alternatives in these categories:\n"
    "1. COUNTER_FRAMING — An opposing or complicating perspective\n"
    "2. DEEPER_WHY — What hidden assumption does the original claim rest on?\n"
    "3. DOMAIN_SHIFT — What would this claim mean in a completely different context?\n"
    "4. LIMIT_CASE — Where or when does this claim break down?\n"
    "\n"
    "Return ONLY a valid JSON array. No commentary, no markdown.\n"
    "Each element: {\"text\": \"...\", \"confidence\": 0.0-1.0, \"type\": \"counter_framing|deeper_why|domain_shift|limit_case\"}\n"
    "Assign confidence based on how defensible each alternative is, not how creative."
)

EXPANSION_USER_TEMPLATE = (
    'Original claim: "{claim_text}"\n\n'
    "Generate 4 genuinely distinct alternatives as JSON:"
)

# Emoji-vector divergence thresholds
DIVERGENCE_BALANCE_THRESHOLD = 0.35  # pole_balance in [0.35, 0.65] = balanced
DIVERGENCE_STABILITY_THRESHOLD = 0.5  # stability_index > 0.5 = over-stable

BALANCED_SPLIT_INSTRUCTION = (
    "\n[DIVERGENCE FIELD: The system currently holds balanced opposition on this topic. "
    "Generate alternatives that DEEPEN the split rather than reconcile it. "
    "Avoid synthesizing or bridging the two sides. Push each alternative further "
    "from the center.]"
)

OVERSTABLE_INSTRUCTION = (
    "\n[INSTABILITY REQUIRED: The current contradiction field is over-stable. "
    "Prioritize LIMIT_CASE and COUNTER_FRAMING categories. Generate alternatives "
    "that destabilize settled assumptions. Avoid reinforcing the existing consensus.]"
)


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


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------

def _parse_expansion_json(response: str) -> Optional[List[Dict[str, Any]]]:
    """Try to parse LLM response as JSON array of expansions."""
    cleaned = response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r'\[.*\]', cleaned, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    return None


# ---------------------------------------------------------------------------
# Per-claim expansion
# ---------------------------------------------------------------------------

VALID_EXPANSION_TYPES = {"counter_framing", "deeper_why", "domain_shift", "limit_case"}


def _build_expansion_prompt(
    claim: Claim,
    emoji_field: Optional[EmojiVector] = None,
) -> str:
    """Build expansion user prompt with optional emoji-vector divergence bias."""
    prompt = EXPANSION_USER_TEMPLATE.format(claim_text=claim.text)

    if emoji_field is not None:
        balance = emoji_field.pole_balance
        stability = emoji_field.stability_index

        # Balanced opposition: deepen the split
        if DIVERGENCE_BALANCE_THRESHOLD <= balance <= (1.0 - DIVERGENCE_BALANCE_THRESHOLD):
            prompt += BALANCED_SPLIT_INSTRUCTION
            logger.debug(
                "Balanced-split bias applied (pole_balance=%.3f in [%.2f, %.2f])",
                balance, DIVERGENCE_BALANCE_THRESHOLD, 1.0 - DIVERGENCE_BALANCE_THRESHOLD,
            )

        # Over-stable field: destabilize
        if stability > DIVERGENCE_STABILITY_THRESHOLD:
            prompt += OVERSTABLE_INSTRUCTION
            logger.debug(
                "Overstable bias applied (stability_index=%.3f > %.3f)",
                stability, DIVERGENCE_STABILITY_THRESHOLD,
            )

    return prompt


def expand_claim(
    claim: Claim,
    llm: LLMInterface,
    model: str,
    emoji_field: Optional[EmojiVector] = None,
) -> List[Claim]:
    """Expand a single claim into 2–4 genuinely distinct alternatives.

    Uses LLM with anti-paraphrase rubric. Each expansion is tagged with
    its type and linked back to the parent claim via parent_id.

    When emoji_field is provided, divergence-pressure instructions are appended
    to the expansion prompt based on pole_balance and stability_index.
    None = no bias (v1 behavior).

    Returns new Claim objects (not added to state — caller does that).
    """
    user_prompt = _build_expansion_prompt(claim, emoji_field)

    try:
        response = llm.generate(
            model=model,
            system_prompt=EXPANSION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temp=0.65,
            max_tokens=1024,
        )
        raw_expansions = _parse_expansion_json(response)
    except Exception as e:
        logger.warning("LLM expansion failed for claim '%s...': %s", claim.text[:40], e)
        return []

    if raw_expansions is None:
        logger.warning("JSON parse failed for expansion of claim '%s...'", claim.text[:40])
        return []

    # Convert to Claim objects
    new_claims: List[Claim] = []
    for exp in raw_expansions[:MAX_EXPANSIONS_PER_CLAIM]:
        if not isinstance(exp, dict) or "text" not in exp:
            continue
        exp_text = str(exp["text"]).strip()
        if not exp_text:
            continue

        # Validate expansion type
        exp_type = str(exp.get("type", "unknown")).strip().lower()
        if exp_type not in VALID_EXPANSION_TYPES:
            exp_type = "unknown"

        confidence = float(exp.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))

        tags = [exp_type, "expansion", "become"]

        new_claims.append(Claim(
            text=exp_text,
            confidence=confidence,
            source="become_expand",
            tags=tags,
            mission_id=claim.mission_id,
            operator="become",
            parent_id=claim.id,
        ))

    logger.info(
        "Expanded claim '%s...' → %d alternatives",
        claim.text[:40], len(new_claims),
    )
    return new_claims


# ---------------------------------------------------------------------------
# Single-pass Become over SystemState
# ---------------------------------------------------------------------------

def become_pass(
    state: SystemState,
    llm: LLMInterface,
    model: str,
    judge_model: str,
    confidence_threshold: float = 0.0,
    max_claims: int = MAX_CLAIMS_TO_EXPAND,
    embedding_cache: Optional[Dict[str, List[float]]] = None,
) -> SystemState:
    """Run a single Become expansion pass over the highest-confidence claims.

    1. Select up to `max_claims` claims with confidence >= threshold, sorted desc.
    2. Expand each claim into 2–4 distinct alternatives.
    3. Add expansion claims to state.
    4. Re-run tension detection between expansion claims and all pre-existing claims.
    5. Add new tensions to state.
    6. Return updated state.

    Single pass only. No loop. No routing. No resolution.

    Args:
        state: Current SystemState.
        llm: LLM client.
        model: Model for Become generation (e.g. Opie model, temp=0.65).
        judge_model: Model for tension detection judging (e.g. Sway model, temp=0.0).
        confidence_threshold: Minimum confidence to select claims for expansion.
        max_claims: Maximum number of claims to expand.
        embedding_cache: Shared embedding cache.

    Returns:
        Updated SystemState with expansion claims and new tensions.
    """
    embedding_cache = embedding_cache if embedding_cache is not None else {}

    # Step 1: Select claims to expand (highest confidence first, skip expansions)
    eligible = [
        c for c in state.claims
        if c.confidence >= confidence_threshold and c.parent_id is None
    ]
    eligible.sort(key=lambda c: c.confidence, reverse=True)
    selected = eligible[:max_claims]

    logger.info(
        "Become pass: %d eligible claims, selected %d (threshold=%.2f, cap=%d)",
        len(eligible), len(selected), confidence_threshold, max_claims,
    )

    if not selected:
        logger.info("Become pass: no claims to expand — skipping")
        return state

    # Snapshot pre-existing claims for tension detection
    pre_existing_claims = list(state.claims)

    # Step 2: Expand each selected claim
    all_expansions: List[Claim] = []
    for claim in selected:
        expansions = expand_claim(claim, llm, model)
        all_expansions.extend(expansions)

    # Step 3: Add expansion claims to state
    for exp_claim in all_expansions:
        state.add_claim(exp_claim)

    logger.info(
        "Become pass: expanded %d claims → %d new claims (total: %d)",
        len(selected), len(all_expansions), len(state.claims),
    )

    # Step 4: Re-run tension detection (expansion claims vs all pre-existing)
    if all_expansions and pre_existing_claims:
        new_tensions = detect_tensions(
            new_claims=all_expansions,
            existing_claims=pre_existing_claims,
            llm=llm,
            model=judge_model,
            embedding_cache=embedding_cache,
        )

        # Step 5: Add tensions to state
        for tension in new_tensions:
            state.add_tension(tension)

        logger.info(
            "Become pass: detected %d new tensions (total: %d)",
            len(new_tensions), len(state.tensions),
        )

    state.iteration += 1
    logger.info("Become pass complete — %s", state.summary())
    return state


# ---------------------------------------------------------------------------
# Targeted claim selection for Become pass #2+
# ---------------------------------------------------------------------------

# Max claims to expand in a targeted pass
MAX_TARGETED_CLAIMS = 8

# Max expansions per claim in a targeted pass (tighter than pass 1)
MAX_TARGETED_EXPANSIONS = 3


def _tension_density(claim: Claim, state: SystemState) -> int:
    """Count how many tensions reference this claim (via source_claims)."""
    count = 0
    for t in state.tensions:
        if claim.id in t.source_claims:
            count += 1
    return count


def _cross_claim_tension_score(claim: Claim, state: SystemState) -> int:
    """Count distinct *other* claims this claim shares tensions with.

    A claim that generated tensions with 3 different original claims
    scores higher than one that only conflicts with 1.
    """
    partners: set = set()
    for t in state.tensions:
        if claim.id in t.source_claims:
            for cid in t.source_claims:
                if cid != claim.id:
                    partners.add(cid)
    return len(partners)


def _confidence_band_score(confidence: float) -> float:
    """Score mid-range confidence [0.60, 0.85] higher than extremes.

    Peak score of 1.0 at confidence=0.725 (center of band).
    Claims outside [0.60, 0.85] get 0.0.
    """
    if confidence < 0.60 or confidence > 0.85:
        return 0.0
    center = 0.725
    half_width = 0.125
    return 1.0 - abs(confidence - center) / half_width


def select_targeted_claims(
    state: SystemState,
    max_claims: int = MAX_TARGETED_CLAIMS,
) -> List[Claim]:
    """Score and select claims for targeted Become pass #2.

    Scoring criteria (additive):
      - Tension density: how many tensions reference this claim
      - Mid-range confidence: claims in [0.60, 0.85] score higher
      - Cross-claim tension: claims whose expansions conflict with multiple originals

    Exclusions (score forced to 0):
      - Claims with zero tensions
      - Claims with confidence=1.0 that produced zero tensions
      - Claims tagged as 'limit_case' (already at conceptual edges)

    Returns:
        Up to max_claims claims, sorted by composite score descending.
    """
    scored: List[Tuple[Claim, float]] = []

    for claim in state.claims:
        # --- Exclusions ---
        td = _tension_density(claim, state)

        # Exclude claims with zero tensions
        if td == 0:
            continue

        # Exclude limit_case claims (already at conceptual edges)
        if "limit_case" in claim.tags:
            continue

        # Exclude confidence=1.0 claims with zero tensions (already caught above,
        # but explicit for clarity)
        if claim.confidence >= 1.0 and td == 0:
            continue

        # --- Scoring ---
        score = 0.0

        # Tension density (weighted highest — these are the "hot spots")
        score += td * 3.0

        # Mid-range confidence bonus
        score += _confidence_band_score(claim.confidence) * 2.0

        # Cross-claim tension score
        cross = _cross_claim_tension_score(claim, state)
        score += cross * 1.5

        scored.append((claim, score))

    # Sort by score descending, break ties by confidence ascending (prefer uncertain)
    scored.sort(key=lambda x: (-x[1], x[0].confidence))

    selected = [claim for claim, _score in scored[:max_claims]]

    logger.info(
        "Targeted selection: %d candidates scored, selected %d (cap=%d)",
        len(scored), len(selected), max_claims,
    )
    for claim, score in scored[:max_claims]:
        logger.info(
            "  [%.1f] %s (conf=%.2f, td=%d, cross=%d): %s...",
            score, claim.id, claim.confidence,
            _tension_density(claim, state),
            _cross_claim_tension_score(claim, state),
            claim.text[:50],
        )

    return selected


# ---------------------------------------------------------------------------
# Targeted Become pass #2+
# ---------------------------------------------------------------------------

def become_pass_targeted(
    state: SystemState,
    llm: LLMInterface,
    model: str,
    judge_model: str,
    max_claims: int = MAX_TARGETED_CLAIMS,
    max_expansions: int = MAX_TARGETED_EXPANSIONS,
    embedding_cache: Optional[Dict[str, List[float]]] = None,
) -> SystemState:
    """Run a targeted Become expansion pass over high-tension-density claims.

    Unlike become_pass() which expands highest-confidence originals,
    this targets claims selected by select_targeted_claims() — focusing
    on tension hot spots, mid-confidence uncertainty, and cross-claim conflicts.

    1. Select up to `max_claims` claims via targeted scoring.
    2. Expand each into up to `max_expansions` distinct alternatives.
    3. Add expansion claims to state with correct parent_id lineage.
    4. Re-run tension detection between new expansions and ALL pre-existing claims.
    5. Add new tensions to state.
    6. Return updated state.

    Single pass only. No loop. No routing. No resolution.
    """
    embedding_cache = embedding_cache if embedding_cache is not None else {}

    # Step 1: Select claims via targeted scoring
    selected = select_targeted_claims(state, max_claims=max_claims)

    if not selected:
        logger.info("Targeted Become pass: no claims selected — skipping")
        return state

    # Snapshot pre-existing claims for tension detection
    pre_existing_claims = list(state.claims)

    # Step 2: Expand each selected claim
    all_expansions: List[Claim] = []
    for claim in selected:
        expansions = expand_claim(claim, llm, model)
        # Cap expansions per claim for targeted pass
        expansions = expansions[:max_expansions]
        all_expansions.extend(expansions)

    # Step 3: Add expansion claims to state
    for exp_claim in all_expansions:
        state.add_claim(exp_claim)

    logger.info(
        "Targeted Become pass: expanded %d claims → %d new claims (total: %d)",
        len(selected), len(all_expansions), len(state.claims),
    )

    # Step 4: Re-run tension detection (new expansions vs ALL pre-existing)
    if all_expansions and pre_existing_claims:
        new_tensions = detect_tensions(
            new_claims=all_expansions,
            existing_claims=pre_existing_claims,
            llm=llm,
            model=judge_model,
            embedding_cache=embedding_cache,
        )

        # Step 5: Add tensions to state
        for tension in new_tensions:
            state.add_tension(tension)

        logger.info(
            "Targeted Become pass: detected %d new tensions (total: %d)",
            len(new_tensions), len(state.tensions),
        )

    state.iteration += 1
    logger.info("Targeted Become pass complete — %s", state.summary())
    return state


# ---------------------------------------------------------------------------
# Pass 3 — Adaptive strategy analysis
# ---------------------------------------------------------------------------

# Budget constants for adaptive pass
MAX_BROAD_CLAIMS = 6
MAX_BROAD_EXPANSIONS = 3
HYBRID_TARGETED_BUDGET = 4
HYBRID_BROAD_BUDGET = 4


def _tension_cluster_ratio(state: SystemState) -> float:
    """Fraction of tensions concentrated on the top-3 most-referenced claims."""
    if not state.tensions:
        return 0.0

    # Count tension references per claim
    ref_counts: Dict[str, int] = {}
    for t in state.tensions:
        for cid in t.source_claims:
            ref_counts[cid] = ref_counts.get(cid, 0) + 1

    if not ref_counts:
        return 0.0

    sorted_counts = sorted(ref_counts.values(), reverse=True)
    top3_total = sum(sorted_counts[:3])
    total_refs = sum(sorted_counts)
    return top3_total / total_refs if total_refs > 0 else 0.0


def _count_zero_tension_claims(state: SystemState) -> int:
    """Count claims that appear in zero tensions."""
    claims_in_tensions: set = set()
    for t in state.tensions:
        for cid in t.source_claims:
            claims_in_tensions.add(cid)
    return sum(1 for c in state.claims if c.id not in claims_in_tensions)


def _count_polarity_axes(state: SystemState) -> int:
    """Count tensions of type 'polarity'."""
    return sum(1 for t in state.tensions if t.relation_type == "polarity")


def _confidence_stratification(state: SystemState) -> Dict[str, int]:
    """Bucket claims by confidence tier."""
    tiers = {"low_0_60": 0, "mid_60_85": 0, "high_85_100": 0}
    for c in state.claims:
        if c.confidence < 0.60:
            tiers["low_0_60"] += 1
        elif c.confidence <= 0.85:
            tiers["mid_60_85"] += 1
        else:
            tiers["high_85_100"] += 1
    return tiers


def analyze_pass3_strategy(state: SystemState) -> Dict[str, Any]:
    """Analyze the post-pass-2 state geometry and recommend a pass-3 strategy.

    Returns a dict with:
      - strategy: "targeted" | "broad" | "hybrid"
      - rationale: human-readable explanation
      - metrics: supporting data (cluster_ratio, zero_tension_count, etc.)
    """
    cluster_ratio = _tension_cluster_ratio(state)
    zero_tension_count = _count_zero_tension_claims(state)
    polarity_count = _count_polarity_axes(state)
    conf_tiers = _confidence_stratification(state)
    total_claims = len(state.claims)

    metrics = {
        "cluster_ratio": round(cluster_ratio, 3),
        "zero_tension_claims": zero_tension_count,
        "polarity_axes": polarity_count,
        "confidence_tiers": conf_tiers,
        "total_claims": total_claims,
        "total_tensions": len(state.tensions),
    }

    # Decision logic
    # Priority: broad check first — if most claims are untouched, widen the field
    # regardless of how clustered the existing tensions are.
    zero_ratio = zero_tension_count / total_claims if total_claims > 0 else 0.0

    if zero_ratio > 0.40:
        strategy = "broad"
        rationale = (
            f"{zero_tension_count}/{total_claims} claims ({zero_ratio:.0%}) have "
            f"zero tensions. Broadening the field by expanding untouched claims "
            f"will discover new tension axes."
        )
    elif cluster_ratio > 0.60:
        strategy = "targeted"
        rationale = (
            f"Tensions are highly clustered (top-3 claims hold {cluster_ratio:.0%} "
            f"of tension references). Deepening hot spots will produce the most "
            f"informative divergence."
        )
    else:
        strategy = "hybrid"
        rationale = (
            f"Mixed geometry: cluster_ratio={cluster_ratio:.2f}, "
            f"zero_tension_ratio={zero_ratio:.2f}. "
            f"Splitting budget between hot-spot deepening and field broadening."
        )

    logger.info(
        "Pass-3 strategy analysis: %s (cluster=%.2f, zero_tension=%d/%d, polarity=%d)",
        strategy, cluster_ratio, zero_tension_count, total_claims, polarity_count,
    )
    logger.info("  Rationale: %s", rationale)
    logger.info("  Confidence tiers: %s", conf_tiers)

    return {"strategy": strategy, "rationale": rationale, "metrics": metrics}


# ---------------------------------------------------------------------------
# Broad claim selection (zero/low tension claims)
# ---------------------------------------------------------------------------

def _select_broad_claims(
    state: SystemState,
    max_claims: int = MAX_BROAD_CLAIMS,
) -> List[Claim]:
    """Select claims with zero or minimal tension involvement for broad expansion.

    Prioritizes:
      1. Claims with zero tensions (completely unexplored)
      2. Among those, prefer mid-range confidence (0.60-0.85)
      3. Then lower-tension claims (td=1)

    Excludes limit_case claims.
    """
    claims_in_tensions: set = set()
    for t in state.tensions:
        for cid in t.source_claims:
            claims_in_tensions.add(cid)

    scored: List[Tuple[Claim, float]] = []
    for c in state.claims:
        if "limit_case" in c.tags:
            continue

        td = _tension_density(c, state)
        if td > 1:
            continue  # broad mode only picks zero/low-tension claims

        score = 0.0

        # Zero-tension claims get highest priority
        if td == 0:
            score += 10.0
        else:
            score += 2.0  # td=1 gets a small base

        # Mid-range confidence bonus
        score += _confidence_band_score(c.confidence) * 3.0

        # Prefer gen-1/gen-2 over originals (already expanded originals less interesting)
        if c.parent_id is not None:
            score += 1.0

        scored.append((c, score))

    scored.sort(key=lambda x: (-x[1], x[0].confidence))
    selected = [claim for claim, _score in scored[:max_claims]]

    logger.info(
        "Broad selection: %d candidates scored, selected %d (cap=%d)",
        len(scored), len(selected), max_claims,
    )
    for claim, score in scored[:max_claims]:
        logger.info(
            "  [%.1f] %s (conf=%.2f, td=%d): %s...",
            score, claim.id, claim.confidence,
            _tension_density(claim, state),
            claim.text[:50],
        )

    return selected


# ---------------------------------------------------------------------------
# Adaptive Become pass #3
# ---------------------------------------------------------------------------

def become_pass_adaptive(
    state: SystemState,
    llm: LLMInterface,
    model: str,
    judge_model: str,
    max_targeted: int = MAX_TARGETED_CLAIMS,
    max_broad: int = MAX_BROAD_CLAIMS,
    max_expansions: int = MAX_TARGETED_EXPANSIONS,
    embedding_cache: Optional[Dict[str, List[float]]] = None,
) -> SystemState:
    """Run an adaptive Become pass that chooses targeted, broad, or hybrid strategy.

    1. Analyze post-pass-2 geometry to pick strategy.
    2. Select claims according to strategy.
    3. Expand each into up to `max_expansions` distinct alternatives.
    4. Add expansion claims to state with correct parent_id lineage.
    5. Re-run tension detection between new expansions and ALL pre-existing claims.
    6. Add new tensions to state.
    7. Return updated state.

    Single pass only. No loop. No routing. No resolution. No Collapse.
    No ParadoxHold. No emojis. No memory feedback.
    """
    embedding_cache = embedding_cache if embedding_cache is not None else {}

    # Step 1: Analyze and choose strategy
    analysis = analyze_pass3_strategy(state)
    strategy = analysis["strategy"]

    logger.info("Adaptive Become pass: strategy=%s", strategy)

    # Step 2: Select claims based on strategy
    if strategy == "targeted":
        selected = select_targeted_claims(state, max_claims=max_targeted)
    elif strategy == "broad":
        selected = _select_broad_claims(state, max_claims=max_broad)
    else:  # hybrid
        targeted_picks = select_targeted_claims(state, max_claims=HYBRID_TARGETED_BUDGET)
        broad_picks = _select_broad_claims(state, max_claims=HYBRID_BROAD_BUDGET)
        # Deduplicate (a claim could appear in both lists)
        seen_ids: set = set()
        selected = []
        for c in targeted_picks + broad_picks:
            if c.id not in seen_ids:
                selected.append(c)
                seen_ids.add(c.id)
        logger.info(
            "Hybrid selection: %d targeted + %d broad → %d unique",
            len(targeted_picks), len(broad_picks), len(selected),
        )

    if not selected:
        logger.info("Adaptive Become pass: no claims selected — skipping")
        return state

    # Snapshot pre-existing claims for tension detection
    pre_existing_claims = list(state.claims)

    # Step 3: Expand each selected claim
    all_expansions: List[Claim] = []
    for claim in selected:
        expansions = expand_claim(claim, llm, model)
        expansions = expansions[:max_expansions]
        all_expansions.extend(expansions)

    # Step 4: Add expansion claims to state
    for exp_claim in all_expansions:
        state.add_claim(exp_claim)

    logger.info(
        "Adaptive Become pass (%s): expanded %d claims → %d new claims (total: %d)",
        strategy, len(selected), len(all_expansions), len(state.claims),
    )

    # Step 5: Re-run tension detection (new expansions vs ALL pre-existing)
    if all_expansions and pre_existing_claims:
        new_tensions = detect_tensions(
            new_claims=all_expansions,
            existing_claims=pre_existing_claims,
            llm=llm,
            model=judge_model,
            embedding_cache=embedding_cache,
        )

        # Step 6: Add tensions to state
        for tension in new_tensions:
            state.add_tension(tension)

        logger.info(
            "Adaptive Become pass: detected %d new tensions (total: %d)",
            len(new_tensions), len(state.tensions),
        )

    state.iteration += 1
    logger.info("Adaptive Become pass complete — %s", state.summary())
    logger.info("Strategy used: %s — %s", strategy, analysis["rationale"])
    return state


# ---------------------------------------------------------------------------
# Phase 5: Pure state Become (no LLM)
# ---------------------------------------------------------------------------

# Default entropy ceiling — system-level safety valve against runaway divergence
BECOME_ENTROPY_CEILING = 0.95

# Default maximum emoji vector sequence length
BECOME_VECTOR_LENGTH_LIMIT = 20


@dataclass
class BecomeAction:
    """Record of the action taken on a single paradox by Become."""
    paradox_id: str
    decision: str           # "expand", "stabilize", "skip"
    entropy_before: float
    entropy_after: float
    vector_length_before: int
    vector_length_after: int
    claims_spawned: int = 0
    child_paradox_id: Optional[str] = None
    skip_reason: Optional[str] = None


@dataclass
class BecomeResult:
    """Full result of a single become_pure() pass."""
    total_eligible: int = 0
    expanded: int = 0
    stabilized: int = 0
    skipped: int = 0
    claims_spawned: int = 0
    paradoxes_spawned: int = 0
    actions: List[BecomeAction] = field(default_factory=list)


def _check_become_eligible(
    paradox: Paradox,
    state: SystemState,
) -> Optional[EmojiVector]:
    """Check if a paradox is eligible for Become action.

    Become may act on a paradox if:
      - Status is 'open' or 'paradox_held' (not collapsed, not integrated)
      - Has a linked emoji vector in state

    Returns the linked EmojiVector if eligible, else None.
    """
    if paradox.status not in ("open", "paradox_held"):
        return None

    if paradox.emoji_vector_id is None:
        return None

    for ev in state.emoji_fields:
        if ev.id == paradox.emoji_vector_id:
            return ev

    return None


def _check_entropy_gate(
    ev: EmojiVector,
    entropy_ceiling: float = BECOME_ENTROPY_CEILING,
) -> str:
    """Determine whether Become should expand or stabilize.

    If entropy < ceiling → 'expand' (increase divergence)
    If entropy >= ceiling → 'stabilize' (prevent runaway divergence)
    """
    if ev.entropy < entropy_ceiling:
        return "expand"
    return "stabilize"


def _apply_become_expand(
    paradox: Paradox,
    ev: EmojiVector,
    state: SystemState,
    vector_length_limit: int = BECOME_VECTOR_LENGTH_LIMIT,
    seed: Optional[int] = None,
) -> BecomeAction:
    """Apply a Become expand action: mutate emoji vector, spawn derivative claims.

    1. Mutate emoji vector with chaos/superposition emojis (respecting length limit)
    2. Generate low-confidence derivative claims from each pole
    3. Record history on paradox
    """
    entropy_before = ev.entropy
    length_before = ev.length

    # Mutate emoji vector (only if under length limit)
    if ev.length < vector_length_limit:
        mutate_become(ev, seed=seed)
    else:
        logger.info(
            "Become expand: vector %s at length limit (%d >= %d), skipping mutation",
            ev.id, ev.length, vector_length_limit,
        )

    entropy_after = ev.entropy
    length_after = ev.length

    # Generate low-confidence derivative claims from each pole
    claims_created = 0
    pole_a_claim_id = paradox.claim_ids[0] if paradox.claim_ids else None
    pole_b_claim_id = paradox.claim_ids[1] if len(paradox.claim_ids) > 1 else pole_a_claim_id

    for pole, parent_cid in [
        (paradox.pole_a, pole_a_claim_id),
        (paradox.pole_b, pole_b_claim_id),
    ]:
        new_claim = Claim(
            text=f"{pole.id} may require reconsideration given expanded context",
            confidence=0.3,
            source="become_pure",
            tags=["expanded_by_become", "proposal"],
            operator="become",
            parent_id=parent_cid,
            mission_id=paradox.mission_ids[0] if paradox.mission_ids else None,
        )
        state.add_claim(new_claim)
        claims_created += 1

    # Record history event on paradox
    paradox.record_event(
        event="become_expand",
        operator="become",
        entropy=entropy_after,
        entropy_before=entropy_before,
        claims_spawned=claims_created,
    )

    action = BecomeAction(
        paradox_id=paradox.id,
        decision="expand",
        entropy_before=entropy_before,
        entropy_after=entropy_after,
        vector_length_before=length_before,
        vector_length_after=length_after,
        claims_spawned=claims_created,
    )

    logger.info(
        "Become expand: %s (entropy %.3f→%.3f, length %d→%d, claims=%d)",
        paradox.id, entropy_before, entropy_after,
        length_before, length_after, claims_created,
    )

    return action


def _apply_become_stabilize(
    paradox: Paradox,
    ev: EmojiVector,
    seed: Optional[int] = None,
) -> BecomeAction:
    """Apply a Become stabilize action when entropy is at/above ceiling.

    Uses mutate_paradox_hold() (superposition emojis) to maintain tension
    without adding chaos. Does NOT spawn new claims.
    """
    entropy_before = ev.entropy
    length_before = ev.length

    # Stabilize: add superposition emojis (not chaos)
    mutate_paradox_hold(ev, seed=seed)

    entropy_after = ev.entropy
    length_after = ev.length

    # Record history event on paradox
    paradox.record_event(
        event="become_stabilize",
        operator="become",
        entropy=entropy_after,
        entropy_before=entropy_before,
    )

    action = BecomeAction(
        paradox_id=paradox.id,
        decision="stabilize",
        entropy_before=entropy_before,
        entropy_after=entropy_after,
        vector_length_before=length_before,
        vector_length_after=length_after,
        claims_spawned=0,
    )

    logger.info(
        "Become stabilize: %s (entropy %.3f→%.3f, length %d→%d)",
        paradox.id, entropy_before, entropy_after,
        length_before, length_after,
    )

    return action


def become_pure(
    state: SystemState,
    entropy_ceiling: float = BECOME_ENTROPY_CEILING,
    vector_length_limit: int = BECOME_VECTOR_LENGTH_LIMIT,
    seed: Optional[int] = None,
) -> BecomeResult:
    """Phase 5 Become: pure state transformer, no LLM calls.

    Iterates all paradox objects in state, checks eligibility and entropy
    gate, then applies expand or stabilize. Generates low-confidence
    derivative claims from pole labels. Mutates emoji vectors mechanically.

    This is the Phase 5 replacement for become_pass(). The Phase 4
    become_pass() family is preserved unchanged for backward compatibility.

    Args:
        state: SystemState to transform (mutated in place).
        entropy_ceiling: Max entropy before Become stabilizes instead of expanding.
        vector_length_limit: Max emoji vector sequence length.
        seed: Optional RNG seed for emoji mutation reproducibility.

    Returns:
        BecomeResult with counts and per-paradox action log.
    """
    result = BecomeResult()

    logger.info(
        "Become-pure pass starting: %d paradoxes to evaluate (ceiling=%.2f, limit=%d)",
        len(state.paradoxes), entropy_ceiling, vector_length_limit,
    )

    for paradox in state.paradoxes:
        # Step 1: Eligibility check
        ev = _check_become_eligible(paradox, state)
        if ev is None:
            skip_reason = (
                f"status={paradox.status}"
                if paradox.status not in ("open", "paradox_held")
                else "no_emoji_vector"
            )
            action = BecomeAction(
                paradox_id=paradox.id,
                decision="skip",
                entropy_before=0.0,
                entropy_after=0.0,
                vector_length_before=0,
                vector_length_after=0,
                skip_reason=skip_reason,
            )
            result.actions.append(action)
            result.skipped += 1
            continue

        result.total_eligible += 1

        # Step 2: Entropy gate
        gate_decision = _check_entropy_gate(ev, entropy_ceiling)

        # Step 3: Apply
        if gate_decision == "expand":
            action = _apply_become_expand(
                paradox, ev, state,
                vector_length_limit=vector_length_limit,
                seed=seed,
            )
            result.expanded += 1
            result.claims_spawned += action.claims_spawned
        else:
            action = _apply_become_stabilize(paradox, ev, seed=seed)
            result.stabilized += 1

        result.actions.append(action)

    logger.info(
        "Become-pure pass complete: %d eligible, %d expanded, %d stabilized, "
        "%d skipped, %d claims spawned",
        result.total_eligible, result.expanded, result.stabilized,
        result.skipped, result.claims_spawned,
    )

    return result
