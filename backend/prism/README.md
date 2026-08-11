# PRISM (Privilege-based Risk & Insider Scoring Mechanism) Module

PRISM evaluates rule-based risk sub-scores reproducing the paper formula from *Koli et al. (arXiv:2505.03796, May 2025)*:

$$R = (W_P \cdot S_P) + (W_A \cdot S_A) + (W_C \cdot S_C) + (W_{IP} \cdot S_{IP}) + (W_B \cdot S_B) + (W_D \cdot S_D) + (W_{CA} \cdot S_{CA})$$

---

## 1. Sub-Score Components

Each sub-score is implemented as an independently testable pure function in `scorer.py`:

- **$S_P$ (`user_privilege_score`)**: User role privilege baseline (`domain_admin`: 1.0, `employee`: 0.1).
- **$S_A$ (`activity_type_score`)**: Severity of daily actions (`usb_exfiltration`: 1.0, `sensitive_file_access`: 0.8, `job_search`: 0.7, `file_move`: 0.3, `logon`: 0.1).
- **$S_C$ (`application_context_score`)**: Target application context sensitivity (USB media/webmail: 0.8, SharePoint: 0.4, Intranet: 0.2).
- **$S_{IP}$ (`ip_score`)**: IP network origin risk (Known IP: 0.0, Unknown/Off-network: 0.5, Tor node: 1.0).
- **$S_B$ (`business_hours_score`)**: Activity timestamp risk (Business hours 08:00–18:00: 0.0, After-hours/Weekend: 1.0).
- **$S_D$ (`device_compliance_score`)**: Endpoint device compliance status (Compliant: 0.0, Unmanaged USB device: 0.7).
- **$S_{CA}$ (`cumulative_activity_score`)**: Action volume saturation score ($\min(1.0, \text{high\_risk\_vol} / 10.0)$).

---

## 2. Configurable Weights (`weights.yaml`)

Weights and thresholds are dynamically loaded from `weights.yaml`:

```yaml
weights:
  user_privilege: 0.05
  activity_type: 0.25
  application_context: 0.15
  ip_address: 0.10
  business_hours: 0.10
  device_compliance: 0.15
  cumulative_activity: 0.20

thresholds:
  low_max: 0.30        # < 0.30 -> LOW
  moderate_max: 0.60   # 0.30 - 0.60 -> MODERATE
  high_max: 0.80       # 0.60 - 0.80 -> HIGH
                       # >= 0.80 -> CRITICAL
```

---

## 3. Usage & Execution

### Run Batch Scoring Pipeline
Ingests `activity_features.parquet` and exports `prism_scored_activity.parquet`:
```bash
# Ensure venv is active in backend/
python -m prism.batch_scorer
```

### Run Unit & Regression Tests
```bash
python -m pytest tests/test_prism.py -v
```
