"""Ensemble Risk Scoring Module.

Combines rule-based PRISM score (S_PRISM) and autoencoder reconstruction score (SAI)
into a unified composite ensemble risk score:
S_ensemble = beta * S_PRISM + (1 - beta) * SAI
"""

from typing import Union

import numpy as np
import pandas as pd


def compute_ensemble_score(
    prism_score: Union[float, np.ndarray, pd.Series],
    sai_score: Union[float, np.ndarray, pd.Series],
    beta: float = 0.5,
) -> Union[float, np.ndarray, pd.Series]:
    """Computes weighted ensemble risk score combining PRISM and AIRS SAI scores.

    Formula: S_ensemble = beta * S_PRISM + (1 - beta) * SAI

    Args:
        prism_score: Normalized PRISM risk score(s) in [0.0, 1.0].
        sai_score: Normalized AIRS SAI anomaly score(s) in [0.0, 1.0].
        beta: Weight given to PRISM rule engine (0.0 to 1.0). Default is 0.5.

    Returns:
        Ensemble composite risk score(s) strictly bounded in [0.0, 1.0].
    """
    beta = float(np.clip(beta, 0.0, 1.0))
    ensemble = beta * prism_score + (1.0 - beta) * sai_score
    if isinstance(ensemble, (np.ndarray, pd.Series)):
        return np.clip(ensemble, 0.0, 1.0)
    return float(np.clip(ensemble, 0.0, 1.0))
