"""Input sanitisation before prompting the LLM.

Ensures no PII, free-form user text, or unexpected content reaches
the prompt. All fields are validated against expected types and
lengths.
"""


def sanitise_for_llm(context: dict) -> dict:
    """Strip or redact fields that should not reach the LLM.

    Args:
        context: Raw context dict (score, SHAP, user info).

    Returns:
        Sanitised copy safe for prompt construction.

    Todo:
        Implement redaction rules in Week 7.

    """
    raise NotImplementedError("Week 7 — implement sanitisation.")
