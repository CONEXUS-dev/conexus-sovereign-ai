"""
VARGAS V4 Symbolic Module

Contains the native symbolic dialect, posture updater, voice signature,
and lexicon for VARGAS V4's symbolic communication system.

Core components:
- SymbolicLexicon: Core vocabulary and archetypes
- PostureUpdater: Severity-based E-Vector adjustments
- VoiceSignature: Partner Stance voice calibration
"""

from .symbolic_lexicon import SymbolicLexicon, get_lexicon
from .posture_updater import PostureUpdater
from .voice_signature import VoiceSignature

__all__ = [
    "SymbolicLexicon",
    "get_lexicon", 
    "PostureUpdater",
    "VoiceSignature"
]
