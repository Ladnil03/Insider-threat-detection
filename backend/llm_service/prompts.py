"""Prompt templates for LLM recommendation generation.

Templates are kept separate from orchestration logic so they can be
iterated without touching code.
"""

ANALYST_PROMPT_TEMPLATE = """You are an insider-risk analyst assistant.
Given the following information, produce a brief plain-English
recommendation for a security analyst.

Risk Score: {risk_score:.2f} / 1.00 (higher = more risky)
Severity Bucket: {severity_bucket}
Top Contributing Factors (SHAP):
{shap_summary}

User History:
{user_history_summary}

Recommendation:
"""
