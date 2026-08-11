"""PRISM (Privilege-based Risk & Insider Scoring Mechanism) Rule Engine.

Implements pure sub-score functions for the paper formula:
R = (Wp*Sp) + (WA*SA) + (WC*SC) + (WIP*SIP) + (WB*SB) + (WD*SD) + (WCA*SCA)
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import pandas as pd
import yaml

from prism.buckets import RiskLevel, classify_risk_score, min_max_normalize

# Path to default weights YAML configuration file
DEFAULT_WEIGHTS_PATH = Path(__file__).resolve().parent / "weights.yaml"

# Default fallback weights matching weights.yaml (summing to 1.00)
DEFAULT_WEIGHTS: Dict[str, float] = {
    "user_privilege": 0.20,
    "activity_type": 0.15,
    "application_context": 0.15,
    "ip_address": 0.15,
    "business_hours": 0.15,
    "device_compliance": 0.10,
    "cumulative_activity": 0.10,
}


def load_prism_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Loads PRISM weights and thresholds from YAML configuration file.

    Args:
        config_path: Path to weights.yaml file. Defaults to module config.

    Returns:
        Dictionary containing 'weights', 'decay_factor', and 'thresholds'.
    """
    target_path = config_path or DEFAULT_WEIGHTS_PATH
    if target_path.exists():
        with open(target_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data and "weights" in data:
                return data

    return {
        "weights": DEFAULT_WEIGHTS,
        "decay_factor": 0.95,
        "thresholds": {"low_max": 0.30, "moderate_max": 0.60, "high_max": 0.80},
    }


def user_privilege_score(user_role: str) -> float:
    """Calculates user privilege risk sub-score (Sp).

    Args:
        user_role: Role name string (e.g. 'domain_admin', 'low_privilege').

    Returns:
        Sub-score between 0.0 and 1.0.
    """
    role_lower = str(user_role).strip().lower()
    if role_lower in ("domain_admin", "system_administrator", "admin"):
        return 1.0
    if role_lower in ("it_admin", "executive"):
        return 0.6
    if role_lower in ("analyst", "engineer", "manager"):
        return 0.3
    if role_lower in ("low_privilege", "employee", "regular", "contractor"):
        return 0.1
    return 0.2


def activity_type_score(activity_type: str) -> float:
    """Calculates activity type risk sub-score (SA).

    Args:
        activity_type: Action type identifier string (e.g. 'usb_exfiltration', 'file_move').

    Returns:
        Sub-score between 0.0 and 1.0.
    """
    act_lower = str(activity_type).strip().lower()
    if act_lower in (
        "exfiltration",
        "usb_exfiltration",
        "privilege_escalation",
        "usb_copy",
    ):
        return 1.0
    if act_lower in ("sensitive_file_access", "job_search"):
        return 0.7
    if act_lower in ("file_move", "file_copy", "file_download"):
        return 0.3
    if act_lower in ("email_sent", "web_visit"):
        return 0.2
    if act_lower in ("logon", "logoff"):
        return 0.1
    return 0.2


def application_context_score(app_name: str) -> float:
    """Calculates application context sensitivity sub-score (SC).

    Args:
        app_name: Target application name or category (e.g. 'sharepoint', 'personal_webmail').

    Returns:
        Sub-score between 0.0 and 1.0.
    """
    app_lower = str(app_name).strip().lower()
    if app_lower in ("personal_webmail", "cloud_exfil", "darkweb"):
        return 1.0
    if app_lower in ("usb_storage", "external_drive"):
        return 0.8
    if app_lower in ("sharepoint", "cloud_storage"):
        return 0.4
    if app_lower in ("internal_crm", "intranet"):
        return 0.2
    return 0.1


def ip_score(
    ip_address: str,
    known_ips_for_user: Optional[Union[List[str], Set[str]]] = None,
) -> float:
    """Calculates IP network origin risk sub-score (SIP).

    Args:
        ip_address: IP address string.
        known_ips_for_user: Collection of known/approved IPs for this user.

    Returns:
        Sub-score between 0.0 and 1.0.
    """
    ip_str = str(ip_address).strip()
    if ip_str.lower() in ("tor_node", "suspicious_vpn"):
        return 1.0

    if known_ips_for_user is not None and len(known_ips_for_user) > 0:
        if ip_str in known_ips_for_user:
            return 0.0
        return 0.5

    return 0.5


def business_hours_score(timestamp: Union[str, datetime, pd.Timestamp]) -> float:
    """Calculates business hours activity risk sub-score (SB).

    Args:
        timestamp: Timestamp representation (ISO string, datetime, or pandas Timestamp).

    Returns:
        Sub-score between 0.0 and 1.0.
    """
    if isinstance(timestamp, str):
        ts_lower = timestamp.strip().lower()
        if ts_lower in ("off_hours", "after_hours", "weekend"):
            return 0.6
        if ts_lower == "business_hours":
            return 0.0
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            return 0.6
    elif isinstance(timestamp, (datetime, pd.Timestamp)):
        dt = timestamp
    else:
        return 0.6

    # Check weekday (0=Mon, 4=Fri, 5=Sat, 6=Sun)
    if dt.weekday() >= 5:
        return 0.6

    hour = dt.hour
    if 8 <= hour < 18:
        return 0.0
    if hour < 5 or hour >= 23:
        return 1.0
    return 0.6


def device_compliance_score(
    device_id: str,
    compliant_device_list: Optional[Union[List[str], Set[str]]] = None,
) -> float:
    """Calculates endpoint device compliance risk sub-score (SD).

    Args:
        device_id: Device identifier string.
        compliant_device_list: Collection of approved compliant device IDs.

    Returns:
        Sub-score between 0.0 and 1.0.
    """
    dev_str = str(device_id).strip()
    if dev_str.lower() in ("compliant", "managed"):
        return 0.0

    if compliant_device_list is not None and len(compliant_device_list) > 0:
        if dev_str in compliant_device_list:
            return 0.0

    return 0.7


def cumulative_activity_score(
    user_activity_window: Union[List[Dict[str, Any]], int, float],
) -> float:
    """Calculates cumulative activity volume sub-score (SCA).

    Args:
        user_activity_window: Count of activities or list of activity objects.

    Returns:
        Sub-score between 0.0 and 1.0 scaled relative to saturation threshold (20 actions).
    """
    if isinstance(user_activity_window, (int, float)):
        count = float(user_activity_window)
    elif isinstance(user_activity_window, list):
        count = float(len(user_activity_window))
    else:
        count = 0.0

    return min(1.0, max(0.0, count / 20.0))


def calculate_prism_score(
    user_role: str = "employee",
    activity_type: str = "logon",
    app_name: str = "intranet",
    ip_address: str = "10.0.0.1",
    known_ips: Optional[Union[List[str], Set[str]]] = None,
    timestamp: Union[str, datetime, pd.Timestamp] = "2026-08-05 10:00:00",
    device_id: str = "DEV-001",
    compliant_devices: Optional[Union[List[str], Set[str]]] = None,
    activity_window: Union[List[Dict[str, Any]], int, float] = 1,
    custom_weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Calculates full weighted PRISM risk score from component sub-scores.

    Paper Formula: R = Wp*Sp + WA*SA + WC*SC + WIP*SIP + WB*SB + WD*SD + WCA*SCA

    Returns:
        Dictionary containing 'raw_score', 'prism_score', 'risk_level', and 'sub_scores'.
    """
    cfg = load_prism_config()
    weights = custom_weights or cfg.get("weights", DEFAULT_WEIGHTS)
    thresholds = cfg.get("thresholds", {})

    sp = user_privilege_score(user_role)
    sa = activity_type_score(activity_type)
    sc = application_context_score(app_name)
    sip = ip_score(ip_address, known_ips)
    sb = business_hours_score(timestamp)
    sd = device_compliance_score(device_id, compliant_devices)
    sca = cumulative_activity_score(activity_window)

    raw_score = (
        weights.get("user_privilege", 0.20) * sp
        + weights.get("activity_type", 0.15) * sa
        + weights.get("application_context", 0.15) * sc
        + weights.get("ip_address", 0.15) * sip
        + weights.get("business_hours", 0.15) * sb
        + weights.get("device_compliance", 0.10) * sd
        + weights.get("cumulative_activity", 0.10) * sca
    )

    normalized_score = min_max_normalize(raw_score, min_val=0.0, max_val=1.0)
    risk_level: RiskLevel = classify_risk_score(normalized_score, thresholds)

    return {
        "raw_score": round(raw_score, 4),
        "prism_score": round(normalized_score, 4),
        "risk_level": risk_level,
        "sub_scores": {
            "Sp_user_privilege": sp,
            "SA_activity_type": sa,
            "SC_app_context": sc,
            "SIP_ip_address": sip,
            "SB_business_hours": sb,
            "SD_device_compliance": sd,
            "SCA_cumulative_activity": sca,
        },
    }


def score_activity_row(
    row: pd.Series, custom_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Adapts a preprocessed daily user activity feature row to PRISM scoring.

    Args:
        row: pandas Series representing a daily user-activity record from activity_features.parquet.
        custom_weights: Optional weight dictionary override.

    Returns:
        Dictionary containing raw score, normalized prism score, and risk level.
    """
    user_role = str(row.get("role", "employee"))

    # Activity type severity
    file_copy_usb = float(row.get("file_copy_usb", 0.0))
    file_sensitive = float(row.get("file_sensitive_access", 0.0))
    email_ext = float(row.get("email_external_count", 0.0))
    web_job = float(row.get("web_job_search_count", 0.0))
    logon_after = float(row.get("logon_after_hours", 0.0))
    device_conn = float(row.get("device_connect_count", 0.0))

    if file_copy_usb > 0:
        sa = 1.0
        sc = 0.8
    elif file_sensitive > 0:
        sa = 0.8
        sc = 0.5
    elif email_ext > 0 or float(row.get("email_large_attachment_count", 0.0)) > 0:
        sa = 0.7
        sc = 0.6
    elif web_job > 0:
        sa = 0.7
        sc = 0.7
    elif float(row.get("file_count", 0.0)) > 0:
        sa = 0.3
        sc = 0.2
    else:
        sa = 0.1
        sc = 0.1

    sp = user_privilege_score(user_role)
    sip = 0.5 if logon_after > 0 else 0.0
    sb = 1.0 if logon_after > 0 else 0.0
    sd = 0.7 if device_conn > 0 else 0.0

    high_risk_vol = (
        (file_copy_usb * 4.0)
        + (file_sensitive * 2.0)
        + (web_job * 2.0)
        + (email_ext * 1.5)
    )
    sca = min(1.0, max(0.0, high_risk_vol / 10.0))

    cfg = load_prism_config()
    w = custom_weights or cfg.get("weights", DEFAULT_WEIGHTS)

    raw_score = (
        w.get("user_privilege", 0.20) * sp
        + w.get("activity_type", 0.15) * sa
        + w.get("application_context", 0.15) * sc
        + w.get("ip_address", 0.15) * sip
        + w.get("business_hours", 0.15) * sb
        + w.get("device_compliance", 0.10) * sd
        + w.get("cumulative_activity", 0.10) * sca
    )

    normalized_score = min_max_normalize(raw_score, min_val=0.0, max_val=1.0)
    risk_level = classify_risk_score(normalized_score, cfg.get("thresholds"))

    return {
        "raw_score": round(raw_score, 4),
        "prism_score": round(normalized_score, 4),
        "risk_level": risk_level,
    }
