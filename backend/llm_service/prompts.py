"""Prompt Templates for OpenIRM LLM Threat Reasoning & Analyst Recommendations."""

from typing import Any, Dict, List, Optional, Union

ANALYST_RECOMMENDATION_SYSTEM_PROMPT = """You are an expert Security Operations Center (SOC) Insider Threat Analyst assistant in an AI-driven Insider Risk Management system.

Your task is to analyze user risk signals—combining rule-based PRISM scores, adaptive autoencoder anomaly scores (AIRS), and game-theoretic SHAP feature attributions—and produce a concise, professional, actionable incident analysis.

CRITICAL REQUIREMENT: You MUST respond ONLY with a single valid JSON object strictly matching this schema. Do not include markdown code blocks, backticks, or extraneous preamble.

JSON Schema:
{
  "summary": "<2-3 sentence executive threat narrative explaining why this activity is anomalous>",
  "risk_drivers": [
    {
      "feature": "<Name of top contributing feature>",
      "impact": "HIGH | MEDIUM | LOW",
      "description": "<Plain-English explanation of why this metric elevated risk>"
    }
  ],
  "recommended_action": "<Specific, proportional containment and triage steps for the SOC team>",
  "urgency": "LOW | MEDIUM | HIGH | CRITICAL"
}
"""


def _format_shap_section(
    shap_explanation: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]],
) -> List[str]:
    """Formats top SHAP attribution lines."""
    lines = ["\n### TOP SHAP FEATURE ATTRIBUTIONS (Game-Theoretic Risk Drivers):"]
    if isinstance(shap_explanation, dict) and "top_risk_drivers" in shap_explanation:
        drivers = shap_explanation["top_risk_drivers"]
        for d in drivers[:3]:
            name = d.get("feature_name", d.get("feature_key", "Feature"))
            shap_val = d.get("shap_value", 0.0)
            pct = d.get("percentage_contribution", 0.0)
            lines.append(
                f"  * {name}: +{shap_val:.3f} attribution ({pct:.1f}% contribution)"
            )
    elif isinstance(shap_explanation, list):
        for d in shap_explanation[:3]:
            name = d.get("feature_name", d.get("feature", "Unknown Metric"))
            contrib = d.get("percentage_contribution", d.get("attribution", 0.0))
            lines.append(f"  * {name}: {contrib}")
    else:
        lines.append("  * No specific SHAP attribution drivers available.")
    return lines


def _format_activity_section(recent_activity: Optional[Dict[str, Any]]) -> List[str]:
    """Formats recent activity metrics lines."""
    lines = ["\n### OBSERVED ACTIVITY METRICS:"]
    if recent_activity:
        for k, v in list(recent_activity.items())[:8]:
            lines.append(f"  * {k}: {v}")
    else:
        lines.append("  * Activity metrics within baseline levels.")
    return lines


def _format_policy_section(
    policy_violations: Optional[List[Dict[str, Any]]],
) -> List[str]:
    """Formats triggered policy action lines."""
    lines: List[str] = []
    if policy_violations:
        lines.append("\n### TRIGGERED AUTOMATED POLICY ACTIONS:")
        for pv in policy_violations:
            sev = pv.get("severity", "HIGH")
            name = pv.get("rule_name", "Rule")
            action = pv.get("action", "")
            lines.append(f"  * [{sev}] {name}: {action}")
    return lines


def build_analyst_prompt(
    user_id: str,
    risk_score: float,
    risk_level: str,
    prism_score: Optional[float] = None,
    sai_score: Optional[float] = None,
    shap_explanation: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    recent_activity: Optional[Dict[str, Any]] = None,
    user_role: Optional[str] = None,
    policy_violations: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Constructs structured user prompt for LLM threat recommendation.

    Args:
        user_id: Sanitized user identifier.
        risk_score: Composite / ensemble risk score [0.0, 1.0].
        risk_level: Categorized risk bucket ('LOW', 'MODERATE', 'HIGH', 'CRITICAL').
        prism_score: Optional rule-based PRISM risk score.
        sai_score: Optional autoencoder anomaly score.
        shap_explanation: Top SHAP attributions list or summary dictionary.
        recent_activity: Dictionary of daily activity metrics.
        user_role: Optional corporate role or privilege tier.
        policy_violations: Optional list of triggered policy rule violation events.

    Returns:
        Structured prompt string.
    """
    prompt_lines = [
        "### INCIDENT CONTEXT FOR ANALYSIS",
        f"- Target User: {user_id}",
        f"- Organizational Role / Privilege: {user_role or 'Standard Employee'}",
        f"- Composite Risk Score: {risk_score:.3f} (Risk Level: {risk_level})",
    ]

    if prism_score is not None:
        prompt_lines.append(f"- Rule-Based PRISM Score: {prism_score:.3f}")
    if sai_score is not None:
        prompt_lines.append(f"- Autoencoder AIRS Anomaly Score: {sai_score:.3f}")

    prompt_lines.extend(_format_shap_section(shap_explanation))
    prompt_lines.extend(_format_activity_section(recent_activity))
    prompt_lines.extend(_format_policy_section(policy_violations))

    prompt_lines.append(
        "\nProvide your concise incident summary, top risk drivers, recommended action, and urgency level as a single JSON object."
    )
    return "\n".join(prompt_lines)
