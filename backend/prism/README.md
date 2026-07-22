# PRISM — Peer-Reviewed Insider Scoring Model

Rule-based risk scoring engine. Computes sub-scores (e.g. email sentiment, logon deviation, file access density) and combines them via weighted sum from `weights.yaml`.

**Inputs:** Preprocessed activity records
**Outputs:** Per-activity risk score [0–1] + risk bucket label
