"""
Project Vargas — OpenClaw Bridge

Wraps the existing SemanticSkillMatcher from openclaw/skills/ to provide
transparent skill invocation. When Vargas detects a skill_invoke intent,
this bridge matches the message to the best OpenClaw skill and returns
the skill body for prompt injection.

Skill execution is invisible to the user.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Resolve paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # CONEXUS_REPO/
OPENCLAW_SKILLS_DIR = PROJECT_ROOT / "openclaw" / "skills"
SEMANTIC_MATCHER_PATH = OPENCLAW_SKILLS_DIR / "semantic_matcher.py"


class OpenClawBridge:
    """Bridge between Vargas and OpenClaw's semantic skill matcher."""

    def __init__(self):
        self._matcher = None
        self._available = False
        self._initialize()

    def _initialize(self):
        """Load the semantic matcher from openclaw/skills/."""
        if not SEMANTIC_MATCHER_PATH.exists():
            logger.warning("[OPENCLAW] semantic_matcher.py not found at %s", SEMANTIC_MATCHER_PATH)
            return

        try:
            # Add openclaw/skills to path so the matcher can find its dependencies
            skills_dir = str(OPENCLAW_SKILLS_DIR)
            if skills_dir not in sys.path:
                sys.path.insert(0, skills_dir)

            from semantic_matcher import SemanticSkillMatcher
            self._matcher = SemanticSkillMatcher()
            self._matcher.initialize()
            self._available = True
            logger.info("[OPENCLAW] SemanticSkillMatcher initialized with %d skills", len(self._matcher.skills))
        except ImportError as e:
            logger.warning("[OPENCLAW] Failed to import SemanticSkillMatcher: %s", e)
            logger.warning("[OPENCLAW] You may need: pip install sentence-transformers numpy")
        except Exception as e:
            logger.warning("[OPENCLAW] Initialization failed: %s", e)

    @property
    def available(self) -> bool:
        return self._available

    def match_skill(self, request_text: str) -> Dict[str, Any]:
        """Match a natural language request to the best OpenClaw skill.

        Returns:
            {
                "skill_name": str | None,
                "skill_path": str | None,
                "confidence": float,
                "body": str | None,  # Full skill markdown if matched
            }
        """
        if not self._available or self._matcher is None:
            return {
                "skill_name": None,
                "skill_path": None,
                "confidence": 0.0,
                "body": None,
            }

        try:
            result = self._matcher.match_skill(request_text)
            skill_name = result.get("skill_name")
            body = None

            if skill_name:
                body = self._matcher.get_skill_body(skill_name)
                logger.info(
                    "[OPENCLAW] Matched skill: %s (confidence: %.4f)",
                    skill_name, result["confidence"],
                )
            else:
                logger.info(
                    "[OPENCLAW] No skill matched (best confidence: %.4f)",
                    result["confidence"],
                )

            return {
                "skill_name": skill_name,
                "skill_path": result.get("skill_path"),
                "confidence": result["confidence"],
                "body": body,
            }
        except Exception as e:
            logger.error("[OPENCLAW] Skill matching failed: %s", e)
            return {
                "skill_name": None,
                "skill_path": None,
                "confidence": 0.0,
                "body": None,
            }

    def list_skill_names(self) -> list[str]:
        """Return sorted list of all active skill names."""
        if not self._available or self._matcher is None:
            return []
        try:
            return sorted([s.name for s in self._matcher.skills])
        except Exception:
            return []

    def format_skill_context(self, match_result: Dict[str, Any]) -> Optional[str]:
        """Format a matched skill into context for prompt injection.

        Returns None if no skill was matched.
        """
        if not match_result.get("skill_name") or not match_result.get("body"):
            return None

        return (
            f"[SKILL CONTEXT — {match_result['skill_name']}]\n"
            f"The following skill guidance is available and relevant to this request:\n\n"
            f"{match_result['body'][:2000]}\n\n"
            f"[END SKILL CONTEXT]\n"
            f"Use this guidance to inform your response, but do not mention "
            f"the skill by name or reveal that you are using a skill system."
        )
