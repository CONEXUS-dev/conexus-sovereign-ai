"""
Redaction utility for sanitizing logs before sharing.
Strips API keys and other sensitive patterns.
"""

import re


# Patterns that match common API key formats
_REDACT_PATTERNS = [
    (re.compile(r'sk-ant-api\S+'), 'sk-ant-[REDACTED]'),
    (re.compile(r'sk-proj-\S+'), 'sk-proj-[REDACTED]'),
    (re.compile(r'sk-[A-Za-z0-9_-]{20,}'), 'sk-[REDACTED]'),
    (re.compile(r'ANTHROPIC_API_KEY\s*=\s*\S+'), 'ANTHROPIC_API_KEY=[REDACTED]'),
    (re.compile(r'OPENAI_API_KEY\s*=\s*\S+'), 'OPENAI_API_KEY=[REDACTED]'),
]


def redact_text(text: str) -> str:
    """Replace any API key patterns in text with [REDACTED] placeholders."""
    for pattern, replacement in _REDACT_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def redact_file(input_path: str, output_path: str = None) -> str:
    """Read a file, redact secrets, write to output_path (or overwrite in place).
    Returns the redacted text."""
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    redacted = redact_text(text)
    out = output_path or input_path
    with open(out, 'w', encoding='utf-8') as f:
        f.write(redacted)
    return redacted
