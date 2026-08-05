"""Data Pipeline Configuration Constants and Column Schemas."""

from pathlib import Path
from typing import Final, List

# Base data paths
BASE_BACKEND_DIR: Final[Path] = Path(__file__).resolve().parent.parent
DATA_DIR: Final[Path] = BASE_BACKEND_DIR / "data"
RAW_DATA_DIR: Final[Path] = DATA_DIR / "raw"
FILTERED_DATA_DIR: Final[Path] = DATA_DIR / "filtered"
ANSWERS_DATA_DIR: Final[Path] = RAW_DATA_DIR / "answers"
PROCESSED_DATA_DIR: Final[Path] = FILTERED_DATA_DIR / "processed"
PROCESSED_PARQUET_PATH: Final[Path] = PROCESSED_DATA_DIR / "activity_features.parquet"
ENCODING_CONFIG_PATH: Final[Path] = PROCESSED_DATA_DIR / "encoding_config.json"
SPLIT_METADATA_PATH: Final[Path] = PROCESSED_DATA_DIR / "split_metadata.json"

# Business Hours & Feature Threshold Constants
WORK_HOURS_START: Final[int] = 8
WORK_HOURS_END: Final[int] = 18
LARGE_ATTACHMENT_BYTES: Final[int] = 5 * 1024 * 1024  # 5 MB
SENSITIVE_EXTENSIONS: Final[List[str]] = [
    ".exe",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
    ".iso",
    ".dll",
    ".sh",
    ".bat",
]
JOB_SEARCH_KEYWORDS: Final[List[str]] = [
    "job",
    "career",
    "indeed",
    "glassdoor",
    "linkedin",
    "monster",
    "resume",
    "hiring",
]

# Base Activity Count Features (12)
BASE_FEATURE_COLS: Final[List[str]] = [
    "logon_count",  # Daily total logon events - establishes baseline user presence
    "logon_after_hours",  # Daily logons outside 08:00-18:00 or weekends - indicates off-hours reconnaissance
    "file_count",  # Daily file system operations - measures raw file interaction volume
    "file_copy_usb",  # Daily file transfers to removable media - key exfiltration vector
    "file_sensitive_access",  # Daily access to archive/executables - indicates staging or tool deployment
    "device_connect_count",  # Daily USB connect events - physical hardware tampering or exfiltration prep
    "device_disconnect_count",  # Daily USB disconnect events - hardware removal tracking
    "email_count",  # Daily email volume - baseline communication activity
    "email_external_count",  # Daily emails sent to non-corporate domains - external communication / exfiltration
    "email_large_attachment_count",  # Daily emails exceeding 5MB - mass data exfiltration via email
    "web_visit_count",  # Daily HTTP browsing events - general web activity baseline
    "web_job_search_count",  # Daily job board visits - indicator of flight risk / insider dissatisfaction
]

# Rolling Window Features (7-day and 30-day mean & std for each base feature - 48 features)
# Rationale: Captures short-term activity spikes (7d) and medium-term behavioral baselines (30d)
ROLLING_WINDOWS: Final[List[int]] = [7, 30]

# Baseline Deviation Features (30-day standardized deviation for each base feature - 12 features)
# Rationale: Standardized z-score distance ((today - mean_30d) / std_30d) isolates user-specific statistical anomalies
BASELINE_DEVIATION_WINDOW: Final[int] = 30

# Complete combined feature column set (72 total features)
ALL_FEATURE_COLS: Final[List[str]] = (
    BASE_FEATURE_COLS
    + [f"{col}_7d_mean" for col in BASE_FEATURE_COLS]
    + [f"{col}_7d_std" for col in BASE_FEATURE_COLS]
    + [f"{col}_30d_mean" for col in BASE_FEATURE_COLS]
    + [f"{col}_30d_std" for col in BASE_FEATURE_COLS]
    + [f"{col}_baseline_dev" for col in BASE_FEATURE_COLS]
)

# CERT Dataset Parameters
DEFAULT_BENIGN_USER_COUNT: Final[int] = 300
KNOWN_MALICIOUS_USER_COUNT: Final[int] = 30
DEFAULT_RANDOM_SEED: Final[int] = 42
CHUNK_SIZE: Final[int] = 100_000

# Target observation window fallback defaults (6-9 months if raw answers absent)
DEFAULT_START_DATE: Final[str] = "2010-01-01"
DEFAULT_END_DATE: Final[str] = "2010-09-30"

# Column selections for chunked reads (memory optimization)
LOGON_USECOLS: Final[List[str]] = ["id", "date", "user", "pc", "activity"]
FILE_USECOLS: Final[List[str]] = [
    "id",
    "date",
    "user",
    "pc",
    "filename",
    "content",
]
DEVICE_USECOLS: Final[List[str]] = ["id", "date", "user", "pc", "activity"]
EMAIL_USECOLS: Final[List[str]] = [
    "id",
    "date",
    "user",
    "pc",
    "to",
    "from",
    "size",
    "attachments",
]
WEB_USECOLS: Final[List[str]] = ["id", "date", "user", "pc", "url"]
USER_USECOLS: Final[List[str]] = [
    "user_name",
    "user_id",
    "domain",
    "email",
    "role",
]

# Raw CSV File Names
LOGON_CSV: Final[str] = "logon.csv"
FILE_CSV: Final[str] = "file.csv"
DEVICE_CSV: Final[str] = "device.csv"
EMAIL_CSV: Final[str] = "email.csv"
WEB_CSV: Final[str] = "web.csv"
USER_CSV: Final[str] = "psychometric.csv"
INSIDERS_CSV: Final[str] = "insiders.csv"
