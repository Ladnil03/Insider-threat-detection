# OpenIRM Policy Engine Module (`backend/policy_engine/`)

## 1. Overview & Purpose

The Policy Engine acts as an automated incident response and compliance monitor. While statistical and deep learning models (PRISM, AIRS, Ensemble) compute continuous probabilistic risk scores, the Policy Engine evaluates deterministic enterprise security rules against raw counts and standardized behavioral baseline deviations to trigger **simulated automated containment actions**.

---

## 2. Policy Rule Catalogue

| Rule ID | Rule Name | Severity | Trigger Condition | Simulated Response Action |
| :--- | :--- | :---: | :--- | :--- |
| **`RULE-USB-EXFIL`** | Mass USB Exfiltration | `CRITICAL` | `file_copy_usb > 50` or `30d_zscore >= 3.0` | `SIMULATED_REVOKE_USB_PERMISSIONS` |
| **`RULE-CRITICAL-SCORE`** | Critical Risk Score Breach | `CRITICAL` | `risk_score >= 0.85` or `sai_score >= 0.85` | `SIMULATED_MANDATORY_SUPERVISOR_ALERT` |
| **`RULE-AFTER-HOURS-SPIKE`** | Off-Hours Logon Surge | `HIGH` | `logon_after_hours >= 5` or `30d_zscore >= 3.0` | `SIMULATED_PROMPT_MFA_CHALLENGE` |
| **`RULE-MASS-EXTERNAL-ATTACHMENT`** | Large External Attachment Surge | `HIGH` | `email_external >= 10` & `email_large >= 3` | `SIMULATED_QUARANTINE_OUTBOUND_EMAIL` |
| **`RULE-FLIGHT-RISK-JOB-HUNT`** | Flight Risk Job Search Spike | `MEDIUM` | `web_job_search >= 10` or `30d_zscore >= 3.0` | `SIMULATED_ELEVATE_MONITORING_PRIORITY` |

---

## 3. Module Structure

```
backend/policy_engine/
├── __init__.py
├── README.md       # Policy engine architecture and rules documentation
├── rules.py        # Declarative enterprise policy rule definitions
└── engine.py       # Deterministic evaluation and action dispatch engine
```

---

## 4. Usage Example

```python
from policy_engine.engine import evaluate_policy_rules

metrics = {
    "user": "ACM2278",
    "file_copy_usb": 85,
    "risk_score": 0.91,
    "logon_after_hours": 7,
}

triggered_actions = evaluate_policy_rules(metrics)
for action in triggered_actions:
    print(f"[{action['severity']}] {action['rule_name']} -> {action['action']}")

# Output:
# [CRITICAL] Mass USB Removable Media Exfiltration -> SIMULATED_REVOKE_USB_PERMISSIONS
# [CRITICAL] Critical Risk Score Threshold Breach -> SIMULATED_MANDATORY_SUPERVISOR_ALERT
# [HIGH] Abnormal Off-Hours Logon Surge -> SIMULATED_PROMPT_MFA_CHALLENGE
```

---

## 5. Verification & Testing

Run policy engine unit and integration tests:
```bash
python -m pytest tests/test_policy_engine.py -v
```
