"""
VARGAS V4 Discord UI — Forensic Dashboard

Transforms the structured JSON output from the SovereignPerceptionLoop into
high-fidelity Discord Embeds — Derek's cockpit view of the runtime's internal
state. Every turn renders the full data surface: E-Vector posture, contradiction
ledger, trust spine result, and provenance integrity.

Voice constraint: direct, calm, structurally clear. No pastoral, therapeutic,
or motivational cliché language. No sentience theater.

Color Priority (highest wins):
    1. RESOLUTION_GATE active    → Warning Yellow (0xFFD700)
    2. entropy > 0.7             → Deep Purple    (0x7B2D8E)
    3. challenge_threshold > 0.7 → Sharp Crimson  (0xDC143C)
    4. directness_index > 0.7    → Electric Blue  (0x00BFFF)
    5. Default                   → Sovereign Grey  (0x2F3136)
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import discord

logger = logging.getLogger(__name__)

# ── Color Constants ──────────────────────────────────────────────────────────
COLOR_RESOLUTION_GATE = 0xFFD700   # Warning Yellow
COLOR_HIGH_ENTROPY    = 0x7B2D8E   # Deep Purple
COLOR_HIGH_CHALLENGE  = 0xDC143C   # Sharp Crimson
COLOR_HIGH_DIRECTNESS = 0x00BFFF   # Electric Blue
COLOR_DEFAULT         = 0x2F3136   # Sovereign Grey
COLOR_INTEGRITY_FAIL  = 0xFF0000   # Red — chain broken
COLOR_INTEGRITY_OK    = 0x2ECC71   # Green — chain valid

# ── Dimension Emojis (user-specified) ────────────────────────────────────────
EMOJI_ENTROPY    = "🌀"
EMOJI_CHALLENGE  = "⚖️"
EMOJI_INITIATIVE = "⚡"
EMOJI_DIRECTNESS = "🎯"

# ── System Mode Icons ────────────────────────────────────────────────────────
ICON_WITNESS     = "👁️"
ICON_RESOLUTION  = "🔥"

# ── Bar rendering constants ──────────────────────────────────────────────────
BAR_FILLED = "█"
BAR_EMPTY  = "░"
BAR_LENGTH = 10

# ── State constants ──────────────────────────────────────────────────────────
RESOLUTION_GATE = "RESOLUTION_GATE"
WITNESS_MODE    = "WITNESS_MODE"


class DiscordUI:
    """Forensic dashboard renderer for the VARGAS V4 sovereign runtime.

    Converts SovereignPerceptionLoop output into Discord Embeds without
    simplifying or narrativizing the data. Every field is rendered raw.

    Usage:
        ui = DiscordUI()
        embed = ui.build_state_embed(loop_result)
        await channel.send(embed=embed)
    """

    def __init__(self):
        """Initialize the Discord UI renderer."""
        logger.info("[DISCORD_UI] Initialized")

    # ═══════════════════════════════════════════════════════════════════════
    # PUBLIC: State Embed — one per turn
    # ═══════════════════════════════════════════════════════════════════════

    def build_state_embed(self, loop_result: Dict[str, Any]) -> discord.Embed:
        """Build the full-turn State Embed from a perception loop result.

        Args:
            loop_result: The dict returned by
                SovereignPerceptionLoop.process_message().

        Returns:
            discord.Embed — the forensic dashboard for this turn.
        """
        system_state = loop_result.get("system_state", {})
        e_vector = system_state.get("e_vector", {})
        contradiction_info = loop_result.get("contradiction_info", {})
        action_result = loop_result.get("action_result")
        response_text = loop_result.get("response_text", "")

        is_resolution_gate = contradiction_info.get("state") == RESOLUTION_GATE

        # ── 1. Color ────────────────────────────────────────────────────
        color = self._resolve_color(e_vector, is_resolution_gate)

        # ── 2. Title + description ──────────────────────────────────────
        mode_icon = ICON_RESOLUTION if is_resolution_gate else ICON_WITNESS
        mode_label = RESOLUTION_GATE if is_resolution_gate else WITNESS_MODE
        title = f"{mode_icon}  VARGAS V4 — {mode_label}"

        embed = discord.Embed(
            title=title,
            description=response_text or "_No output this turn._",
            color=color,
            timestamp=datetime.now(timezone.utc),
        )

        # ── 3. E-Vector Posture ─────────────────────────────────────────
        embed.add_field(
            name="E-Vector Posture",
            value=self._render_posture(e_vector),
            inline=False,
        )

        # ── 4. Contradiction Ledger ─────────────────────────────────────
        if is_resolution_gate:
            embed.add_field(
                name="🔥 Held Contradiction",
                value=self._render_contradiction_ledger(contradiction_info),
                inline=False,
            )

        # ── 5. Contradiction Metrics (always shown) ─────────────────────
        embed.add_field(
            name="Contradiction Metrics",
            value=self._render_contradiction_metrics(contradiction_info),
            inline=True,
        )

        # ── 6. Trust Spine ──────────────────────────────────────────────
        embed.add_field(
            name="Trust Spine",
            value=self._render_action(action_result),
            inline=True,
        )

        # ── 7. Posture Shift (if delta applied) ────────────────────────
        e_vector_delta = contradiction_info.get("e_vector_delta")
        if e_vector_delta and is_resolution_gate:
            embed.add_field(
                name="Posture Shift",
                value=self._render_delta(e_vector_delta),
                inline=False,
            )

        # ── 8. Footer ──────────────────────────────────────────────────
        session_id = loop_result.get("session_id", "unknown")
        processing_ms = loop_result.get("processing_time_ms", 0)
        embed.set_footer(
            text=f"Session {session_id[:8]}  •  {processing_ms}ms"
        )

        return embed

    # ═══════════════════════════════════════════════════════════════════════
    # PUBLIC: Integrity Embed — boot protocol / on-demand chain check
    # ═══════════════════════════════════════════════════════════════════════

    def build_integrity_embed(
        self, verification: Dict[str, Any], session_id: str = "unknown"
    ) -> discord.Embed:
        """Build an Integrity Report embed from a provenance chain verification.

        Displays raw hash mismatch data when chain integrity fails.
        No narrative. No interpretation. Data only.

        Args:
            verification: The dict returned by ProvenanceLogger.verify_chain().
                Expected keys: valid (bool), entries_checked (int),
                break_at (int|None), error (str|None).
            session_id: Current session ID for context.

        Returns:
            discord.Embed — green if valid, red if broken.
        """
        valid = verification.get("valid", False)
        entries_checked = verification.get("entries_checked", 0)
        break_at = verification.get("break_at")
        error = verification.get("error")

        if valid:
            embed = discord.Embed(
                title="🔒 Provenance Chain — Integrity OK",
                description=f"Chain verified. {entries_checked} entries checked. No hash mismatches.",
                color=COLOR_INTEGRITY_OK,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="Status",
                value=f"Valid: **True**\nEntries: **{entries_checked}**\nBreaks: **0**",
                inline=True,
            )
        else:
            embed = discord.Embed(
                title="🚨 Provenance Chain — INTEGRITY FAILURE",
                description="Hash chain verification failed. Raw mismatch data below.",
                color=COLOR_INTEGRITY_FAIL,
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                name="Failure Data",
                value=(
                    f"Valid: **False**\n"
                    f"Entries checked: **{entries_checked}**\n"
                    f"Break at entry: **{break_at}**"
                ),
                inline=True,
            )
            embed.add_field(
                name="Error",
                value=f"```\n{error or 'No error detail available'}\n```",
                inline=False,
            )

        embed.set_footer(text=f"Session {session_id[:8]}")
        return embed

    # ═══════════════════════════════════════════════════════════════════════
    # PRIVATE: Color Resolution
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _resolve_color(
        e_vector: Dict[str, float], is_resolution_gate: bool
    ) -> int:
        """Determine embed sidebar color by priority.

        Priority: RESOLUTION_GATE > entropy > challenge > directness > default.
        """
        if is_resolution_gate:
            return COLOR_RESOLUTION_GATE

        entropy = e_vector.get("entropy", 0.5)
        challenge = e_vector.get("challenge_threshold", 0.5)
        directness = e_vector.get("directness_index", 0.5)

        if entropy > 0.7:
            return COLOR_HIGH_ENTROPY
        if challenge > 0.7:
            return COLOR_HIGH_CHALLENGE
        if directness > 0.7:
            return COLOR_HIGH_DIRECTNESS

        return COLOR_DEFAULT

    # ═══════════════════════════════════════════════════════════════════════
    # PRIVATE: E-Vector Posture
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _render_bar(value: float) -> str:
        """Render a visual bar for a dimension value in [0.0, 1.0]."""
        clamped = max(0.0, min(1.0, value))
        filled = round(clamped * BAR_LENGTH)
        empty = BAR_LENGTH - filled
        return f"`{BAR_FILLED * filled}{BAR_EMPTY * empty}` **{clamped:.2f}**"

    @classmethod
    def _render_posture(cls, e_vector: Dict[str, float]) -> str:
        """Render the 4D E-Vector posture with emoji labels and bars."""
        entropy = e_vector.get("entropy", 0.5)
        challenge = e_vector.get("challenge_threshold", 0.5)
        initiative = e_vector.get("initiative_threshold", 0.5)
        directness = e_vector.get("directness_index", 0.5)

        lines = [
            f"{EMOJI_ENTROPY}  Entropy:    {cls._render_bar(entropy)}",
            f"{EMOJI_CHALLENGE}  Challenge:  {cls._render_bar(challenge)}",
            f"{EMOJI_INITIATIVE}  Initiative: {cls._render_bar(initiative)}",
            f"{EMOJI_DIRECTNESS}  Directness: {cls._render_bar(directness)}",
        ]
        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════════════
    # PRIVATE: Contradiction Ledger
    # ═══════════════════════════════════════════════════════════════════════

    @classmethod
    def _render_contradiction_ledger(
        cls, contradiction_info: Dict[str, Any]
    ) -> str:
        """Render the held contradiction — raw Statement A vs Statement B.

        Pulls statement_a and statement_b from the contradiction_payload
        field if present (populated from ContradictionStore). Falls back
        to raw similarity data if the store payload is unavailable.

        No pastoral language. No motivational framing. Data only.
        """
        severity = contradiction_info.get("severity", 0.0)
        topic_sim = contradiction_info.get("topic_similarity", 0.0)
        impl_sim = contradiction_info.get("implication_similarity", 0.0)

        # Severity bar
        sev_filled = round(max(0.0, min(1.0, severity)) * BAR_LENGTH)
        sev_empty = BAR_LENGTH - sev_filled
        sev_bar = f"`{BAR_FILLED * sev_filled}{BAR_EMPTY * sev_empty}`"

        # Attempt to extract structured contradiction from payload
        statement_a, statement_b = cls._extract_statements(contradiction_info)

        lines = [
            f"**Severity**: {sev_bar} **{severity:.3f}**",
            "",
            f"**Statement A** — topic sim: `{topic_sim:.3f}`",
            f"> {statement_a}",
            "",
            f"**Statement B** — impl sim: `{impl_sim:.3f}`",
            f"> {statement_b}",
            "",
            "Status: **held** — not resolved",
        ]
        return "\n".join(lines)

    @staticmethod
    def _extract_statements(
        contradiction_info: Dict[str, Any],
    ) -> tuple:
        """Extract statement_a and statement_b from contradiction data.

        Checks contradiction_payload (JSON string from ContradictionStore),
        then falls back to raw fields, then to numeric-only fallback.

        Returns:
            Tuple of (statement_a: str, statement_b: str).
        """
        # Source 1: structured payload from ContradictionStore
        payload = contradiction_info.get("contradiction_payload")
        if payload:
            parsed = payload if isinstance(payload, dict) else None
            if parsed is None and isinstance(payload, str):
                try:
                    parsed = json.loads(payload)
                except (json.JSONDecodeError, TypeError):
                    parsed = None
            if parsed:
                a = parsed.get("statement_a", "")
                b = parsed.get("statement_b", "")
                if a and b:
                    return (a, b)

        # Source 2: direct fields on contradiction_info
        a = contradiction_info.get("statement_a", "")
        b = contradiction_info.get("statement_b", "")
        if a and b:
            return (a, b)

        # Source 3: numeric fallback — no narrative, just raw data
        topic_sim = contradiction_info.get("topic_similarity", 0.0)
        impl_sim = contradiction_info.get("implication_similarity", 0.0)
        return (
            f"[Topic vector match: {topic_sim:.4f}]",
            f"[Implication vector divergence: {impl_sim:.4f}]",
        )

    # ═══════════════════════════════════════════════════════════════════════
    # PRIVATE: Contradiction Metrics
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _render_contradiction_metrics(
        contradiction_info: Dict[str, Any],
    ) -> str:
        """Render contradiction metrics as a compact inline field."""
        detected = contradiction_info.get("detected", False)
        state = contradiction_info.get("state", WITNESS_MODE)
        severity = contradiction_info.get("severity", 0.0)
        topic_sim = contradiction_info.get("topic_similarity", 0.0)
        impl_sim = contradiction_info.get("implication_similarity", 0.0)

        state_icon = ICON_RESOLUTION if state == RESOLUTION_GATE else ICON_WITNESS

        lines = [
            f"State: {state_icon} {state}",
            f"Detected: {'Yes' if detected else 'No'}",
            f"Severity: **{severity:.3f}**",
            f"Topic Sim: {topic_sim:.3f}",
            f"Impl Sim: {impl_sim:.3f}",
        ]
        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════════════
    # PRIVATE: Trust Spine
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _render_action(action_result: Optional[Dict[str, Any]]) -> str:
        """Render action routing result as a compact inline field."""
        if not action_result:
            return "No action routed\nTier: —\nStatus: —"

        tier = action_result.get("trust_tier", "—")
        status = action_result.get("status", "—")
        snapshot = action_result.get("snapshot_id")

        lines = [
            f"Tier: **{tier}**",
            f"Status: **{status}**",
        ]
        if snapshot:
            lines.append(f"Snapshot: `{snapshot[:12]}…`")

        return "\n".join(lines)

    # ═══════════════════════════════════════════════════════════════════════
    # PRIVATE: E-Vector Delta
    # ═══════════════════════════════════════════════════════════════════════

    @staticmethod
    def _render_delta(delta: Dict[str, float]) -> str:
        """Render E-Vector delta from a contradiction event."""
        dim_emojis = {
            "entropy": EMOJI_ENTROPY,
            "challenge_threshold": EMOJI_CHALLENGE,
            "initiative_threshold": EMOJI_INITIATIVE,
            "directness_index": EMOJI_DIRECTNESS,
        }

        lines = []
        for dim, emoji in dim_emojis.items():
            val = delta.get(dim, 0.0)
            sign = "+" if val >= 0 else ""
            lines.append(f"{emoji}  {dim}: **{sign}{val:.4f}**")

        return "\n".join(lines)
