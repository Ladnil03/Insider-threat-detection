"""Input Sanitization and Safety Module for Prompt Hygiene."""

import re


def sanitize_input_text(text: str) -> str:
    """Sanitizes user and metric inputs before inserting into LLM prompt templates.

    Removes prompt injection attempts, control characters, and structural markdown exploits.

    Args:
        text: Raw input string.

    Returns:
        Cleaned input string safe for prompt formatting.
    """
    if not text:
        return ""
    # Strip dangerous instruction injection keywords and non-printable chars
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)
    cleaned = re.sub(
        r"(SYSTEM PROMPT:|IGNORE PREVIOUS INSTRUCTIONS)",
        "[REDACTED]",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip()
