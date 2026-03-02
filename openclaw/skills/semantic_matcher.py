"""
Semantic Skill Matcher for OpenClaw / CONEXUS.

Loads active skills from manifest.json, embeds their metadata using
a medium-tier model (all-MiniLM-L6-v2), and exposes match_skill()
which returns the single best-matching skill for a natural-language request.

Architecture decisions (locked):
  1. Agent-requested skill injection
  2. Natural language invocation
  3. Semantic similarity matching
  4. Medium-tier embeddings (CPU-friendly)
  5. One skill per request
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SKILLS_DIR = Path(__file__).resolve().parent          # openclaw/skills/
MANIFEST_PATH = SKILLS_DIR / "manifest.json"
QUARANTINE_PATH = SKILLS_DIR / "quarantine.json"
REPO_ROOT = SKILLS_DIR.parent.parent                  # CONEXUS_REPO/
USAGE_LOG_DIR = REPO_ROOT / "SOVEREIGN_PROOF" / "skills"
USAGE_LOG_PATH = USAGE_LOG_DIR / "usage.log"

CONFIDENCE_THRESHOLD = 0.12   # Below this → "no match"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# Patent 7 — Symbolic Calibration Authority
# ---------------------------------------------------------------------------
# SovereignCalibration is the ROOT symbolic authority.  Its emoji field and
# contradiction vectors (defined in its markdown body, not YAML) are the
# canonical calibration substrate.  All other calibration-bearing skills
# (calibration_type == "patent-7-bearing") must either:
#   • define their own ecp_symbolic_field and ecp_contradiction_pairs, or
#   • explicitly inherit Sovereign’s field.
# Structural skills are exempt — they do not participate in paradox induction.
# Emoji tokens are inward-facing calibration control signals per Patent 7
# (Application #63/891,100) — not decorative.
# ---------------------------------------------------------------------------
CALIBRATION_TYPE_KEY = "patent-7-bearing"

# ---------------------------------------------------------------------------
# Emoji normalization (Patent 7 stability guarantee)
# ---------------------------------------------------------------------------

def _normalize_symbolic_field(raw: str) -> str:
    """Normalize an emoji symbolic field for stable, reproducible embeddings.

    1. Strip Unicode variation selectors (U+FE0E, U+FE0F).
    2. Sort remaining characters by Unicode codepoint for deterministic order.
    3. Return as a space-separated string of emoji tokens.
    """
    # Strip variation selectors
    cleaned = raw.replace("\ufe0e", "").replace("\ufe0f", "")
    # Extract individual characters (each emoji is one codepoint after stripping)
    chars = [ch for ch in cleaned if not ch.isspace()]
    # Sort by codepoint for deterministic ordering
    chars.sort(key=ord)
    return " ".join(chars)


# ---------------------------------------------------------------------------
# YAML frontmatter parser (avoids requiring PyYAML for simple cases)
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str) -> Dict[str, Any]:
    """Extract YAML frontmatter from a SKILL.md file as a dict.

    Handles the subset of YAML used in skill files: scalars, lists, and
    simple nested keys.  Falls back to an empty dict on parse failure.
    """
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    result: Dict[str, Any] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        # Inline list  [a, b, c]
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
            result[key] = [i for i in items if i]
        elif value.startswith('"') and value.endswith('"'):
            result[key] = value.strip('"')
        elif value.startswith("'") and value.endswith("'"):
            result[key] = value.strip("'")
        elif value == "":
            result[key] = ""
        else:
            result[key] = value
    return result


def _read_skill_body(text: str) -> str:
    """Return the markdown body after the YAML frontmatter."""
    match = re.match(r"^---\s*\n.*?\n---\s*\n?", text, re.DOTALL)
    if match:
        return text[match.end():]
    return text

# ---------------------------------------------------------------------------
# Skill loading
# ---------------------------------------------------------------------------

class SkillEntry:
    """In-memory representation of a single active skill."""

    def __init__(self, name: str, path: str, meta: Dict[str, Any], body: str):
        self.name = name
        self.path = path
        self.meta = meta
        self.body = body
        # Build the text blob used for embedding
        label = meta.get("label", "")
        description = meta.get("description", "")
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        # Include first ~200 chars of body for richer semantic signal
        body_snippet = body[:200].replace("\n", " ").strip() if body else ""
        base_parts = [name, label, description, " ".join(tags), body_snippet]

        # Patent 7 / ECP: the Symbol and Contradiction steps of the ECP
        # Micro-Sequence operate on the SAME calibration field.  The emoji
        # tokens (ecp_symbolic_field) are the compressed contradiction vectors;
        # the named pairs (ecp_contradiction_pairs) label what those emoji
        # clusters encode.  Together they form one unified calibration layer.
        # Only the named pairs enter the embedding blob — the text model
        # understands "urgency ↔ calm" but emoji codepoints are noise to it.
        # The full emoji field is preserved in meta for compliance + Sovereign.
        calibration_type = meta.get("calibration_type", "")
        if calibration_type == CALIBRATION_TYPE_KEY:
            ecp_pairs = meta.get("ecp_contradiction_pairs", [])
            if isinstance(ecp_pairs, str):
                ecp_pairs = [ecp_pairs]
            if ecp_pairs:
                base_parts.append(", ".join(ecp_pairs))

        self.text_blob = " ".join(filter(None, base_parts))
        self.embedding: Optional[np.ndarray] = None


def load_active_skills() -> List[SkillEntry]:
    """Load all active skills listed in manifest.json."""
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    skills: List[SkillEntry] = []
    for entry in manifest.get("skills", {}).get("active", []):
        name = entry["name"]
        rel_path = entry["path"]

        # Resolve the file on disk
        full_path = SKILLS_DIR / rel_path
        if full_path.is_dir():
            # agent-browser style: skip directory-only entries without SKILL.md
            candidates = list(full_path.glob("SKILL.md")) + list(full_path.glob("*.md"))
            if not candidates:
                logger.warning("[MATCHER] Skipping %s — no .md file in dir", name)
                continue
            full_path = candidates[0]

        if not full_path.exists():
            logger.warning("[MATCHER] Skipping %s — file not found: %s", name, full_path)
            continue

        text = full_path.read_text(encoding="utf-8")
        meta = _parse_frontmatter(text)
        body = _read_skill_body(text)

        if not meta.get("name") and not meta.get("description"):
            # SovereignCalibration has no YAML name field — use manifest name
            meta["name"] = name

        # Patent 7 enforcement: calibration skills must have a symbolic field
        manifest_cal_type = entry.get("calibration_type", "")
        meta_cal_type = meta.get("calibration_type", "")
        is_calibration = (manifest_cal_type == CALIBRATION_TYPE_KEY
                          or meta_cal_type == CALIBRATION_TYPE_KEY)
        if is_calibration:
            # Propagate calibration_type into meta if only in manifest
            if not meta_cal_type:
                meta["calibration_type"] = CALIBRATION_TYPE_KEY
            sym = meta.get("ecp_symbolic_field", "")
            if not sym and name != "SovereignCalibration":
                logger.warning(
                    "[MATCHER][PATENT7] Calibration skill '%s' missing symbolic_field",
                    name,
                )

        skills.append(SkillEntry(name=name, path=str(rel_path), meta=meta, body=body))

    logger.info("[MATCHER] Loaded %d active skills from manifest", len(skills))
    return skills

# ---------------------------------------------------------------------------
# Embedding engine
# ---------------------------------------------------------------------------

_model = None


def _get_embedding_model():
    """Lazy-load the sentence-transformers model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("[MATCHER] Loading embedding model: %s", EMBEDDING_MODEL_NAME)
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        logger.info("[MATCHER] Embedding model loaded")
    return _model


def _embed_texts(texts: List[str]) -> np.ndarray:
    """Return (N, D) matrix of embeddings."""
    model = _get_embedding_model()
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

# ---------------------------------------------------------------------------
# Semantic Matcher
# ---------------------------------------------------------------------------

class SemanticSkillMatcher:
    """Matches natural-language requests to the single best active skill."""

    def __init__(self):
        self.skills: List[SkillEntry] = []
        self._skill_embeddings: Optional[np.ndarray] = None

    def initialize(self):
        """Load skills and compute embeddings (call once at startup)."""
        self.skills = load_active_skills()
        if not self.skills:
            logger.warning("[MATCHER] No active skills loaded — matching disabled")
            return
        blobs = [s.text_blob for s in self.skills]
        self._skill_embeddings = _embed_texts(blobs)
        for i, skill in enumerate(self.skills):
            skill.embedding = self._skill_embeddings[i]
        logger.info("[MATCHER] Embeddings computed for %d skills", len(self.skills))

    def match_skill(self, request_text: str) -> Dict[str, Any]:
        """Return the single best-matching skill for *request_text*.

        Returns:
            {
                "skill_name": str | None,
                "skill_path": str | None,
                "confidence": float,
            }
        """
        if not self.skills or self._skill_embeddings is None:
            return {"skill_name": None, "skill_path": None, "confidence": 0.0}

        query_emb = _embed_texts([request_text])[0]
        # Cosine similarity (embeddings are already normalized)
        scores = self._skill_embeddings @ query_emb
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])

        if best_score < CONFIDENCE_THRESHOLD:
            return {"skill_name": None, "skill_path": None, "confidence": round(best_score, 4)}

        best = self.skills[best_idx]
        return {
            "skill_name": best.name,
            "skill_path": best.path,
            "confidence": round(best_score, 4),
        }

    def get_skill_body(self, skill_name: str) -> Optional[str]:
        """Return the full markdown body of a skill by name."""
        for s in self.skills:
            if s.name == skill_name:
                return s.body
        return None

# ---------------------------------------------------------------------------
# Usage logging
# ---------------------------------------------------------------------------

def log_skill_usage(
    agent: str,
    request_text: str,
    matched_skill: Optional[str],
    confidence: float,
    mission_id: Optional[str] = None,
):
    """Append a JSONL entry to SOVEREIGN_PROOF/skills/usage.log."""
    USAGE_LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "request_text": request_text,
        "matched_skill": matched_skill,
        "confidence": confidence,
        "mission_id": mission_id,
    }
    try:
        with open(USAGE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        logger.error("[MATCHER] Failed to write usage log: %s", e)


# ---------------------------------------------------------------------------
# Module-level convenience (for quick testing)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    matcher = SemanticSkillMatcher()
    matcher.initialize()

    queries = [
        "I need to hold two opposing truths here.",
        "Help me write a Python function.",
        "I need to check the ethical implications of this action.",
        "Compress this mission into a single directive.",
        "Search the web for recent AI research.",
        "I need to coordinate a handoff between agents.",
    ]

    if len(sys.argv) > 1:
        queries = [" ".join(sys.argv[1:])]

    for q in queries:
        result = matcher.match_skill(q)
        print(f"  Query: {q}")
        print(f"  Match: {result['skill_name']}  (confidence: {result['confidence']:.4f})")
        print()
