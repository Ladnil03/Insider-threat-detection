# Data Pipeline

Filters the CERT Insider Threat Dataset r4.2 to a manageable subset, then preprocesses (cleaning, joins, normalization) for downstream scoring.

**Inputs:** Raw CERT CSVs from `backend/data/raw/`
**Outputs:** Filtered + normalized CSVs in `backend/data/filtered/`
