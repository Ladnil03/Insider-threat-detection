# PRISM Rule Engine Module

PRISM (Pattern-Based Risk Assessment & Indicator Scoring Matrix) calculates baseline rule-based risk sub-scores reproducing the paper's heuristic layer.

## Purpose
- Evaluates domain-specific indicator categories (after-hours logon, USB usage, sensitive file access, job search activity).
- Computes configurable weighted totals and categorizes risk into bucketing levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

## Inputs
- Daily user activity metric dictionary.

## Outputs
- PRISM risk score dict with score breakdown and risk level.
