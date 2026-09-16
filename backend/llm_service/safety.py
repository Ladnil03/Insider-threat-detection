"""Input Sanitization and Safety Module for Prompt Injection Prevention."""

import re
from typing import Any, Dict

# Dangerous prompt injection attack patterns to redact
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|all)?\s*(instructions|rules|guidelines|directives|policies)",
    r"disregard\s+(all\s+)?(rules|guidelines|policies|instructions)",
    r"system\s*prompt\s*:",
    r"you\s+are\s+now\s+(in\s+)?(developer\s+mode|dan|an\s+unrestricted)",
    r"new\s+system\s+(directive|instruction|prompt)",
    r"<\s*\|?\s*im_(start|end)\s*\|?\s*>",
    r"```\s*(system|assistant|user)",
]

COMPILED_INJECTION_RE = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)


def sanitize_input_text(text: Any, max_length: int = 500) -> str:
    """Sanitizes user and metric inputs before inserting into LLM prompt templates.

    Removes prompt injection attempts, non-printable control characters, and structural delimiter exploits.

    Args:
        text: Raw input string or value.
        max_length: Maximum permitted character length.

    Returns:
        Cleaned input string safe for prompt formatting.
    """
    if text is None:
        return ""

    s = str(text)

    # 1. Strip non-printable and invisible control characters (preserve standard spaces and tabs)
    s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", s)

    # 2. Redact prompt injection attack payloads
    s = COMPILED_INJECTION_RE.sub("[REDACTED_INJECTION_ATTEMPT]", s)

    # 3. Escape markdown structural header / fence delimiters that could alter prompt parsing
    s = re.sub(r"^\s*###\s*", "", s, flags=re.MULTILINE)
    s = s.replace("```", "'''")

    # 4. Enforce strict character limit
    s = s.strip()[:max_length]
    return s


def sanitize_activity_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively cleans and sanitizes dictionary keys and values for prompt insertion.

    Args:
        data: Dictionary of activity metrics or user metadata.

    Returns:
        Cleaned dictionary with sanitized strings and safe numeric types.
    """
    if not isinstance(data, dict):
        return {}

    sanitized: Dict[str, Any] = {}
    for k, v in data.items():
        clean_key = sanitize_input_text(k, max_length=64)
        if isinstance(v, str):
            sanitized[clean_key] = sanitize_input_text(v, max_length=200)
        elif isinstance(v, (int, float, bool)):
            sanitized[clean_key] = v
        elif isinstance(v, dict):
            sanitized[clean_key] = sanitize_activity_metadata(v)
        elif isinstance(v, list):
            sanitized[clean_key] = [
                sanitize_input_text(x, max_length=200) if isinstance(x, str) else x
                for x in v[:10]
            ]
        else:
            sanitized[clean_key] = str(v)[:100]

    return sanitized
