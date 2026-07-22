"""Configuration constants for the data pipeline.

Column names, file paths, and data-type mappings used across
filter_cert.py and preprocess.py. Centralised here to avoid
hardcoded values.
"""

from pathlib import Path

# --- Project paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "backend" / "data" / "raw"
FILTERED_DATA_DIR = PROJECT_ROOT / "backend" / "data" / "filtered"

# --- CERT column names ---
# ponytail: these are the r4.2 column names from the CERT spec;
#   adjust if the user's filtered CSVs differ.
COL_USER_ID = "user_id"
COL_DATE = "date"
COL_ACTIVITY = "activity"
COL_ROLE = "role"
COL_DEPT = "department"

# --- Feature columns for PRISM / AIRS (populated in Week 2) ---
PRISM_FEATURE_COLS: list[str] = []
AIRS_FEATURE_COLS: list[str] = []

# --- Subsampling defaults ---
DEFAULT_BENIGN_COUNT = 300
DEFAULT_WINDOW_MONTHS = 6
