"""Human Analyst Feedback Blending and Online Adaptation."""


def blend_analyst_feedback(
    model_score: float, analyst_score: float, alpha: float = 0.7
) -> float:
    """Blends model reconstruction score with analyst manual rating using parameter alpha.

    Args:
        model_score: Score computed by AIRS model.
        analyst_score: Analyst adjusted score from UI.
        alpha: Weight given to analyst feedback (0.0 to 1.0).

    Returns:
        Blended composite score.
    """
    return (1.0 - alpha) * model_score + alpha * analyst_score
