"""Visualisation helpers for SHAP explanations.

Provides functions to generate summary bar plots, waterfall plots,
and force plots for the frontend or notebook display.
"""


def generate_waterfall_plot(shap_values: dict, output_path: str) -> str:
    """Generate and save a waterfall SHAP plot.

    Args:
        shap_values: Dict mapping feature → SHAP value.
        output_path: Where to save the plot image.

    Returns:
        Path to the saved image.

    Todo:
        Implement plot generation in Week 6.

    """
    raise NotImplementedError("Week 6 — implement visualisation.")
