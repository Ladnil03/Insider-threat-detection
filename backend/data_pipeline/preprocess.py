"""Preprocess filtered CERT data: cleaning, joins, normalization.

Takes filtered CSVs and produces normalized feature vectors ready for
PRISM scoring and AIRS autoencoder training.
"""

from pathlib import Path


def preprocess_activity_data(input_dir: Path, output_path: Path) -> None:
    """Load filtered CSVs, clean, join, normalize, write parquet/CSV.

    Args:
        input_dir: Directory with filtered CERT CSVs.
        output_path: Path to write preprocessed output.

    Todo:
        Implement preprocessing logic in Week 2.

    """
    raise NotImplementedError("Week 2 — implement preprocessing logic.")
