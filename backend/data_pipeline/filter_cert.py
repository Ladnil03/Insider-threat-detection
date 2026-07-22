"""Filter the CERT Insider Threat Dataset r4.2 to a manageable subset.

Subsamples 250-350 benign users + all 30 malicious users over a 6-9 month
window. Outputs filtered CSVs to backend/data/filtered/.
"""

from pathlib import Path


def filter_cert_dataset(
    raw_dir: Path,
    output_dir: Path,
    benign_count: int = 300,
    window_months: int = 6,
) -> None:
    """Filter CERT CSVs to a smaller subset for development.

    Args:
        raw_dir: Path to raw CERT CSV files.
        output_dir: Path to write filtered CSVs.
        benign_count: Number of benign users to include.
        window_months: Time window in months to keep.

    Todo:
        Implement actual filtering logic in Week 2.

    """
    raise NotImplementedError("Week 2 — implement CERT filtering logic.")
