# OpenIRM: Deep Technical Architecture & Project Explanation (Weeks 1–5)

**Author:** OpenIRM Architecture & Engineering Team  
**Scope:** Inception through Week 5 (Scaffolding, Ingestion, Preprocessing, PRISM Rule Engine, and AIRS Deep Autoencoder)  
**Reference Paper:** *"AI-Driven IRM: Transforming Insider Risk Management with Adaptive Scoring and LLM-Based Threat Detection"* (Koli et al., arXiv:2505.03796, May 2025)

---

## 1. Executive Summary & Problem Context

Insider threats represent one of the most asymmetric and damaging challenges in enterprise cybersecurity. Unlike external adversaries who must breach perimeter defenses (firewalls, WAFs, EDRs), insider threats originate from **authenticated, authorized identities** operating with legitimate privileges. Consequently, perimeter security mechanisms are fundamentally blind to malicious insider actions such as data exfiltration, privilege abuse, and intellectual property theft.

Detecting insider risk in enterprise production environments suffers from three structural data science challenges:

1. **Extreme Class Imbalance**: In real-world enterprise telemetry, benign actions outnumber malicious activities by ratios between $100:1$ and $10,000:1$. Traditional supervised classifiers trained on such distributions suffer from severe false positive fatigue or complete class collapse.
2. **Polymorphic Threat Vectors**: Insider threats do not exhibit uniform signatures. An insider may exfiltrate data via encrypted email, physical USB removable drives, cloud storage, or after-hours print jobs. Supervised models trained on historical patterns fail to detect novel attack variants.
3. **The "Black-Box" SOC Bottleneck**: Machine learning models that produce uncalibrated probability scores without auditable reasoning are rejected by Security Operations Center (SOC) analysts and enterprise compliance teams.

**OpenIRM** solves these challenges by implementing a defense-in-depth, hybrid risk architecture:
- **PRISM (Privilege-based Risk & Insider Scoring Mechanism)**: A deterministic, policy-aligned rule engine that computes baseline behavioral risk across 7 categorical dimensions.
- **AIRS (Adaptive Insider Risk System)**: A deep PyTorch autoencoder trained strictly on benign baseline behaviors to detect subtle statistical anomalies via reconstruction error ($L_{\text{MSE}}$).

This document provides a comprehensive technical walkthrough of the design decisions, mathematical formulations, data engineering pipelines, neural network architectures, and tech stack choices implemented from **Week 1 through Week 5**.

---

## 2. End-to-End System Architecture (Week 1–5 Scope)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 DATA INGESTION & FILTERING                             │
│  CMU CERT r4.2 Multi-Domain Logs (Logon, File, Device, Email, Web, Psychometric, Insiders)   │
│                 │ Chunked Streaming (100k rows) & Seeded Sampling (Seed=42)            │
│                 ▼                                                                      │
│    Filtered Raw Data (30 Known Malicious + 300 Benign Users | Jan 2010 – Sep 2010)     │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                          │
                                          ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        TEMPORAL PREPROCESSING & FEATURE ENGINEERING                     │
│  • Group-by (User, Date_Day) Aggregation                                                │
│  • 12 Base Behavioral Metrics (Logons, USB copies, Sensitive Files, Emails, Job Search) │
│  • 48 Rolling Window Metrics (7-day acute bursts + 30-day behavioral baselines)         │
│  • 12 Standardized Z-Score Deviations (30-day trailing baseline with shift(1))          │
│                 │ 72-Dimensional Daily Activity Feature Matrix                          │
│                 │ Contiguous Chronological Time Split (Train: 70% | Val: 15% | Test: 15%) │
│                 ▼                                                                      │
│        activity_features.parquet (99,987 User-Days) + split_metadata.json              │
└───────────────────────┬────────────────────────────────────────┬───────────────────────┘
                        │                                        │
                        ▼                                        ▼
┌──────────────────────────────────────────────┐ ┌──────────────────────────────────────┐
│             PRISM RULE ENGINE                │ │      AIRS DEEP AUTOENCODER           │
│  7 Pure Sub-Score Functions:                 │ │  PyTorch Symmetric Architecture:     │
│  • S_P (Privilege: 0.05)                     │ │  Input: 72 Features                  │
│  • S_A (Activity Severity: 0.25)             │ │  Encoder: 72 → 48 → 24 → 12 (Latent) │
│  • S_C (Application Context: 0.15)           │ │  Decoder: 12 → 24 → 48 → 72          │
│  • S_IP (Network Origin: 0.10)               │ │  Regularization: LeakyReLU + Dropout │
│  • S_B (Business Hours: 0.10)                │ │                                      │
│  • S_D (Device Compliance: 0.15)             │ │  Training Strategy:                  │
│  • S_CA (Cumulative Volume: 0.20)            │ │  • Strictly Benign Train Set Only    │
│                                              │ │  • All 30 Malicious Users Held Out   │
│  Composite Score R ∈ [0.0, 1.0]              │ │  • StandardScaler Isolated on Train  │
│  Risk Buckets: LOW / MOD / HIGH / CRITICAL   │ │  • Objective: Minimize MSE Loss      │
│                 │                            │ │                 │                    │
│                 ▼                            │ │                 ▼                    │
│  prism_scored_activity.parquet               │ │  airs_autoencoder.pt + scaler.pkl    │
└──────────────────────────────────────────────┘ └──────────────────────────────────────┘
```

---

## 3. Tech Stack Selection & Justification Matrix

Every technology chosen for OpenIRM was evaluated against alternatives based on performance, enterprise maintainability, computational overhead, and ecosystem interoperability:

| Component | Selected Technology | Version | Evaluated Alternatives | Engineering Justification |
| :--- | :--- | :---: | :--- | :--- |
| **Language** | **Python** | `3.11` | Python 3.9/3.10, C++, Go | Python 3.11 provides significant CPython performance improvements (10–60% speedup via adaptive specializing interpreter) while maintaining universal compatibility with PyTorch, SHAP, and scientific data libraries. |
| **Deep Learning** | **PyTorch** | `>=2.2.0` | TensorFlow / Keras, JAX, Scikit-Learn | PyTorch offers dynamic computational graphs, clean object-oriented `nn.Module` subclassing, seamless CUDA/CPU switching, fine-grained gradient hooks for explainability, and superior production serving patterns via TorchScript / state dicts. |
| **Tabular Data** | **Pandas & NumPy** | `>=2.2.0` | Polars, Dask, DuckDB | Pandas 2.2 provides native PyArrow backend integration, high-performance rolling window routines (`rolling(window)`), robust vectorized transformations, and complete compatibility across ML feature engineering ecosystems. |
| **Storage Format** | **Apache Parquet** (`pyarrow` / `fastparquet`) | `>=15.0.0` | CSV, SQLite, HDF5 | Parquet is a columnar binary format with snappy compression. It reduces disk footprint by >85% compared to CSV, preserves strict column datatypes, supports selective column projection, and enables fast vectorized chunk loading. |
| **Data Preprocessing** | **Scikit-Learn** | `>=1.4.0` | Custom NumPy Scalers | Provides robust, battle-tested implementations of `StandardScaler` and `MinMaxScaler` that can be serialized (`joblib`) and safely transferred between training and inference pipelines. |
| **Configuration** | **PyYAML** | `>=6.0.1` | JSON, TOML, Hardcoded constants | Human-readable configuration for risk weights, neural layer dimensions, and training hyperparameters. Allows SOC teams to tune scoring rules without modifying Python code. |
| **Code Hygiene** | **Black & Ruff** | `>=24.1.0` / `>=0.2.0` | Flake8, Pylint, autopep8 | `ruff` (written in Rust) executes static analysis and linting 10–100x faster than Flake8/Pylint. `black` enforces deterministic code formatting (PEP 8, line length 88). |
| **Testing** | **Pytest & Pytest-Asyncio** | `>=8.0.0` | Unittest, Nose2 | Modular fixture management, parameterized test suites, clean CLI reporting, and native support for async API endpoint testing. |

---

## 4. Phase-by-Phase Technical Deep Dive (Weeks 1 to 5)

---

### Week 1: Project Scaffolding, Tooling & Modular Architecture

#### Objective & Design Principles
The foundational week established a production-grade repository architecture adhering to strict separation of concerns, environment isolation, and continuous quality enforcement.

#### Directory Architecture
```
Insider-threat-detection/
├── backend/                  # Core Python backend services & pipelines
│   ├── airs/                 # Adaptive Insider Risk System (Autoencoder)
│   ├── api/                  # FastAPI web service & endpoint routes
│   ├── data/                 # Raw, filtered, and processed data artifacts
│   ├── data_pipeline/        # CERT dataset streaming, filtering & feature extraction
│   ├── explainability/       # SHAP feature attribution & visualization
│   ├── llm_service/          # LLM threat reasoning & prompt engine
│   ├── policy_engine/        # Automated policy triggers & action simulator
│   ├── prism/                # Privilege-based deterministic rule engine
│   ├── tests/                # Comprehensive Pytest test suite
│   ├── pyproject.toml        # Ruff and Black tool configurations
│   └── requirements.txt      # Pinned dependency manifest
├── docs/                     # Visualizations, EDA notebooks, and weekly logs
│   ├── phase_reports/        # Formal milestone validation reports
│   └── weekly_logs/          # Week-by-week engineering logs
├── docker/                   # Dockerfile and Docker Compose manifests
└── README.md                 # System overview and setup instructions
```

#### Engineering Decisions:
1. **Virtual Environment Isolation (`backend/venv/`)**: Enforced dedicated virtual environment execution to prevent dependency contamination across development hosts.
2. **Self-Documenting Modules**: Placed dedicated `README.md` files in every submodule detailing functional inputs, outputs, and usage guidelines.
3. **No Magic Numbers Rule**: All thresholds, window sizes, and file paths were strictly consolidated into configuration modules (`config.py`, `config.yaml`, `weights.yaml`).

---

### Week 2: Dataset Selection, Filtering & Memory-Efficient Chunked Ingestion

#### 1. Why CMU CERT Insider Threat Dataset r4.2?
Evaluating insider risk algorithms requires ground-truth labeled scenarios reflecting realistic enterprise telemetry. Real-world corporate logs cannot be published due to privacy and regulatory constraints (GDPR, HIPAA). The **CMU CERT v4.2 dataset** is the recognized academic and industry benchmark:
- **Comprehensive Activity Coverage**: Contains billions of timestamped events across 5 core enterprise domains:
  - `logon.csv`: Workstation logon/logoff events, timestamps, hostnames.
  - `file.csv`: File operations (open, copy, delete), removable drive destinations, file extensions.
  - `device.csv`: USB mass storage connection/disconnection events.
  - `email.csv`: Internal and external communications, recipient counts, byte sizes, attachment flags.
  - `web.csv`: URL visits across external internet domains.
- **Realistic Synthesized Scenarios**: Includes 30 known malicious insiders executing diverse attack patterns:
  - *Scenario 1*: Off-hours data exfiltration via removable USB drive by a departing employee.
  - *Scenario 2*: Systematic unauthorized access and collection of sensitive corporate intellectual property.
  - *Scenario 3*: IT administrator privilege abuse and tool staging.
- **Scale**: Over 20 GB of raw uncompressed CSV records spanning 18+ months of enterprise activity.

#### 2. The Memory Bottleneck & Chunked Streaming Solution
Loading 20+ GB of raw CSVs simultaneously exceeds commodity development RAM (16–32 GB) and causes out-of-memory (OOM) crashes during data exploration.

**Implementation**: `backend/data_pipeline/filter_cert.py`
- Implemented streaming chunk processing using `pandas.read_csv(chunksize=100_000, usecols=...)`.
- Leveraged explicit column projection (`LOGON_USECOLS`, `FILE_USECOLS`, etc.) to discard unneeded string payloads before memory allocation.
- **Processing Flow**:
  1. Parse `answers/insiders.csv` to isolate the 30 ground-truth malicious user IDs and extract their active threat timeline bounds (min/max timestamps).
  2. Define the target observation window: **2010-01-01 to 2010-09-30** (9 months of continuous telemetry capturing all active threat phases).
  3. Sample **300 benign users** deterministically using a fixed random seed (`seed=42`) from `psychometric.csv`, strictly excluding all 30 malicious users.
  4. Stream all raw logs in 100,000-row chunks, filtering in-flight to keep only records belonging to the 330 target users within the 9-month window.
  5. Write the filtered records to `backend/data/filtered/`.

```python
# Chunked streaming snippet from filter_cert.py
def filter_csv_file(raw_path: Path, filtered_path: Path, target_users: Set[str], 
                    start_date: str, end_date: str, usecols: List[str]) -> int:
    filtered_chunks = []
    for chunk in pd.read_csv(raw_path, usecols=usecols, chunksize=CHUNK_SIZE):
        chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce")
        mask = (
            chunk["user"].isin(target_users) &
            (chunk["date"] >= start_date) &
            (chunk["date"] <= end_date)
        )
        filtered_chunks.append(chunk[mask])
    df_filtered = pd.concat(filtered_chunks, ignore_index=True)
    df_filtered.to_csv(filtered_path, index=False)
    return len(df_filtered)
```

---

### Week 3 & Week 3b: Advanced Feature Engineering & Contiguous Temporal Split

#### 1. Daily User-Level Aggregation `(user, date_day)`
Insider risk indicators rarely manifest in a single isolated log entry (e.g., sending an email is normal; sending 50 emails with 10MB archives to an external domain at 2:00 AM on Sunday is high risk). Therefore, events must be aggregated into structured **daily behavioral vectors** $x_{u,t}$.

#### 2. The 12 Base Behavioral Features
`backend/data_pipeline/preprocess.py` extracts 12 domain indicators per `(user, date_day)`:

| Feature Name | Telemetry Source | Behavioral & Threat Rationale |
| :--- | :--- | :--- |
| `logon_count` | `logon.csv` | Baseline user workstation presence. |
| `logon_after_hours` | `logon.csv` | Off-hours (outside 08:00–18:00) or weekend logons. Reconnaissance indicator. |
| `file_count` | `file.csv` | Raw file system operation volume. |
| `file_copy_usb` | `file.csv` | File transfer operations to removable storage. Primary data exfiltration vector. |
| `file_sensitive_access` | `file.csv` | Access to sensitive extensions (`.exe`, `.zip`, `.tar`, `.iso`, `.sh`, `.bat`). Staging indicator. |
| `device_connect_count` | `device.csv` | USB drive insertion events. Physical hardware interaction. |
| `device_disconnect_count` | `device.csv` | USB drive removal events. |
| `email_count` | `email.csv` | Total outbound/inbound email communication volume. |
| `email_external_count` | `email.csv` | Emails sent to non-corporate external domains. External leak vector. |
| `email_large_attachment_count` | `email.csv` | Emails with attachments exceeding 5 MB (`LARGE_ATTACHMENT_BYTES`). Mass exfiltration. |
| `web_visit_count` | `web.csv` | General HTTP web browsing volume. |
| `web_job_search_count` | `web.csv` | Visits to job search keywords (`indeed`, `glassdoor`, `monster`, `resume`, `hiring`). Flight risk indicator. |

---

#### 3. Advanced Feature Engineering Retrofit (Week 3b: 72-Feature Architecture)
Static daily counts fail to capture temporal velocity. A user who downloads 10 files daily has a normal baseline; a user who normally downloads 0 files and suddenly downloads 10 exhibits an anomaly.

OpenIRM expands the 12 base counts into a **72-dimensional feature space**:
- **48 Rolling Window Statistics**:
  - **7-day Rolling Mean & Standard Deviation** ($\mu_{7d}, \sigma_{7d}$): Captures acute behavioral bursts and short-term volatility.
  - **30-day Rolling Mean & Standard Deviation** ($\mu_{30d}, \sigma_{30d}$): Establishes the user's stable medium-term baseline.
- **12 Standardized Baseline Deviation Features ($Z$-scores)**:
  Measures the statistical distance between today's activity count and the user's trailing 30-day history:
  $$Z_{u,t} = \frac{x_{u,t} - \mu_{30d}(t-1)}{\sigma_{30d}(t-1) + \epsilon}$$

#### 4. Critical Engineering Protections in Baseline Deviations:
1. **Target Leakage Prevention (`shift(1)`)**: The rolling window must strictly be calculated on $t-1$ history (`df.groupby('user')[col].shift(1).rolling(30)`). If today's value $x_{u,t}$ were included in the baseline mean, the anomaly would partially dilute itself.
2. **Cold-Start Handling**: For a new employee or the first 30 days of telemetry, trailing history is insufficient. OpenIRM explicitly assigns $Z_{u,t} = 0.0$ (neutral baseline) rather than generating `NaN` or ungrounded spikes.
3. **Zero-Variance Baseline Protection**: If an employee has zero USB copies for 30 consecutive days, $\sigma_{30d} = 0$. A standard division would cause a division-by-zero error. OpenIRM implements unit-scaling fallback ($\sigma_{\text{eff}} = 1.0$), ensuring that a sudden spike from a constant zero baseline is preserved cleanly as $Z = x_{u,t}$.

---

#### 5. Dataset Splitting: Why Random Split is Invalid for Security Telemetry
In standard tabular ML benchmarks, researchers often use `train_test_split(shuffle=True)` or random $k$-fold cross-validation. **In temporal security telemetry, this is a critical methodological flaw**:
- Random shuffling distributes records from the same user across train and test sets on adjacent days.
- Future temporal patterns leak into the training set (lookahead bias).
- The model memorizes user-specific dates rather than learning generalizable benign behavior manifolds.

**OpenIRM Solution**: Contiguous Chronological Time Split (`split_by_time`):
- Sorts the entire 99,987 user-day dataset strictly by `date_day`.
- Partitions the timeline into 3 non-overlapping contiguous temporal windows:
  - **Train Split (70%)**: `2010-01-01` to `2010-07-11` (69,991 user-days)
  - **Validation Split (15%)**: `2010-07-12` to `2010-08-20` (14,998 user-days)
  - **Test Split (15%)**: `2010-08-21` to `2010-09-30` (14,998 user-days)
- Guarantees zero date overlap and zero temporal leakage.

---

### Week 4: PRISM (Privilege-based Risk & Insider Scoring Mechanism) Rule Engine

#### 1. Why Implement a Rule-Based Engine First?
Machine learning alone is insufficient in regulated enterprise security environments. SOC analysts require deterministic baseline scoring that can immediately flag known policy violations (e.g., unmanaged USB connections during off-hours by high-privilege accounts).

**PRISM** acts as the deterministic anchor in OpenIRM's hybrid architecture, reproducing and extending *Koli et al. (arXiv:2505.03796)*.

#### 2. Mathematical Formulation
PRISM evaluates each user-day record across 7 orthogonal security categories:
$$R_{\text{raw}} = \sum_{i=1}^{7} W_i \cdot S_i = (W_P \cdot S_P) + (W_A \cdot S_A) + (W_C \cdot S_C) + (W_{IP} \cdot S_{IP}) + (W_B \cdot S_B) + (W_D \cdot S_D) + (W_{CA} \cdot S_{CA})$$
where $\sum W_i = 1.00$.

#### 3. Category Weights & Sub-Score Calculations (`backend/prism/scorer.py`):

| Sub-Score | Category Parameter | Weight ($W_i$) | Formulation & Evaluation Logic |
| :--- | :--- | :---: | :--- |
| **$S_P$** | `user_privilege` | `0.05` | Role-based privilege tier: Domain Admin (`1.0`), Executive (`0.7`), IT/Dev (`0.5`), General Employee (`0.1`). |
| **$S_A$** | `activity_type` | `0.25` | Highest-severity daily action: USB file transfer (`1.0`), Sensitive file access (`0.8`), Job search browsing (`0.7`), Standard file edit (`0.3`), Logon (`0.1`). |
| **$S_C$** | `application_context` | `0.15` | Sensitivity of destination asset: Removable Media / External Webmail (`0.8`), SharePoint / Cloud Storage (`0.4`), Internal Corporate Portal (`0.2`). |
| **$S_{IP}$** | `ip_address` | `0.10` | Network origin risk: Unknown / Off-subnet IP (`0.5`), Known corporate intranet IP (`0.0`). |
| **$S_B$** | `business_hours` | `0.10` | Temporal penalty: Activity occurring outside 08:00–18:00 or during weekends (`1.0`), standard business hours (`0.0`). |
| **$S_D$** | `device_compliance` | `0.15` | Endpoint hardware posture: Unmanaged external USB peripheral (`0.7`), Compliant managed corporate laptop (`0.0`). |
| **$S_{CA}$** | `cumulative_activity` | `0.20` | Daily action volume saturation: $S_{CA} = \min(1.0, \frac{\text{High-Risk Event Count}}{10.0})$. |

All weights are configured via `backend/prism/weights.yaml` and loaded dynamically.

#### 4. Normalization and Risk Bucketing (`backend/prism/buckets.py`)
Raw scores $R_{\text{raw}}$ are clipped to $[0.0, 1.0]$ and mapped into actionable operational risk tiers:
- **LOW** ($[0.00, 0.30)$): Routine background enterprise activity. No analyst intervention.
- **MODERATE** ($[0.30, 0.60)$): Elevated activity or minor anomaly. Queued for standard monitoring.
- **HIGH** ($[0.60, 0.80)$): Severe policy violation or multiple concurrent threat indicators. Generates high-priority SOC alert.
- **CRITICAL** ($[0.80, 1.00]$): Immediate automated isolation trigger.

#### 5. Empirical Batch Scoring Results
Batch scoring the 99,987 user-day records produced `prism_scored_activity.parquet`:
- **Mean Benign User-Day Score**: `0.5730`
- **Mean Malicious User-Day Score**: `0.6761`
- **Score Separation Delta**: `+0.1031` (PRISM demonstrates statistically significant positive separation for malicious behavior)
- **Detection Rate**: **82.84%** of malicious user-days (1,072 / 1,294) scored in the `HIGH` risk bucket ($\ge 0.60$). Zero malicious user-days scored in `LOW`.

---

### Week 5: AIRS (Adaptive Insider Risk System) Deep Autoencoder Architecture

#### 1. Why Semi-Supervised Autoencoders Over Alternative ML Paradigms?
A core architectural decision in OpenIRM is the selection of a **deep symmetric autoencoder neural network** for anomaly detection.

```
                         AIRS AUTOENCODER LATENT BOTTLENECK
                             
   72 Input Features                                              72 Reconstructed
   ┌───────────────┐                                              ┌───────────────┐
   │ x1, x2, ...x72│                                              │x̂1, x̂2, ... x̂72│
   └───────┬───────┘                                              └───────▲───────┘
           │ Linear(72, 48) + LeakyReLU(0.1) + Dropout(0.1)               │ Linear(48, 72)
           ▼                                                              │
   ┌───────────────┐                                              ┌───────┴───────┐
   │ Hidden Dim 48 │                                              │ Hidden Dim 48 │
   └───────┬───────┘                                              └───────▲───────┘
           │ Linear(48, 24) + LeakyReLU(0.1) + Dropout(0.1)               │ Linear(24, 48) + LeakyReLU
           ▼                                                              │
   ┌───────────────┐                                              ┌───────┴───────┐
   │ Hidden Dim 24 │                                              │ Hidden Dim 24 │
   └───────┬───────┘                                              └───────▲───────┘
           │ Linear(24, 12) + LeakyReLU(0.1)                              │ Linear(12, 24) + LeakyReLU
           ▼                                                              │
   ┌───────────────────────────────┐                                      │
   │  BOTTLENECK LATENT SPACE (12) ├──────────────────────────────────────┘
   │  Learned Benign Manifold      │
   └───────────────────────────────┘
```

#### Detailed Model Comparison:

| Anomaly Detection Approach | Strengths | Critical Failure Mode in Insider Threat Detection |
| :--- | :--- | :--- |
| **Supervised Classifiers**<br>*(XGBoost, Random Forest, MLP)* | High precision on known training attack distributions. | **Complete failure on zero-day / novel attacks.** Overfits to synthetic scenario artifacts; unusable in real SOCs where ground truth attacks are rarely labeled. |
| **Isolation Forest** | Fast training, tree-based isolation of outliers. | Computes random axis-aligned splits. **Fails to capture non-linear correlation structures** across rolling temporal deviations (e.g., joint correlation between off-hours logon and USB file transfer spikes). |
| **One-Class SVM** | Kernelized boundary around normal data. | $O(N^2)$ to $O(N^3)$ computational scaling complexity. Infeasible for millions of daily enterprise log vectors; hypersensitive to kernel bandwidth parameter. |
| **PyTorch Autoencoder (AIRS)**<br>*(Selected Approach)* | • Learns non-linear manifold of benign enterprise behavior.<br>• Constant-time $O(1)$ forward-pass inference.<br>• Continuously differentiable loss suitable for gradient-based explainability (SHAP/Integrated Gradients).<br>• Supports online fine-tuning and feedback adaptation. | Requires careful bottleneck dimension tuning to prevent identity mapping. (Solved via 6:1 compression ratio). |

---

#### 2. AIRS Neural Network Architecture (`backend/airs/model.py`)
The `AIRSAutoencoder` class implements a symmetric encoder-decoder pipeline:

1. **Input Layer ($D_{\text{in}} = 72$)**: Receives the standardized daily feature vector.
2. **Encoder Compression**:
   - $72 \to 48$: First dimensionality reduction (1.5x compression). Filters redundant cross-feature correlations.
   - $48 \to 24$: Second compression step (2.0x compression). Condenses temporal dynamics into high-level behavioral motifs.
   - $24 \to 12$: Bottleneck compression (2.0x compression).
3. **Bottleneck Latent Space ($D_{\text{latent}} = 12$)**:
   - Total compression ratio of **6:1** ($72 \to 12$).
   - Forces the neural network to discard individual sample noise and learn the compact, fundamental manifold of normal user behavior.
4. **Symmetric Decoder**:
   - Mirrors the encoder: $12 \to 24 \to 48 \to 72$.
   - Reconstructs the 72-dimensional input vector ($\hat{x}$).
5. **Activation & Regularization Choices**:
   - **`LeakyReLU(negative_slope=0.1)`**: Selected over standard ReLU to eliminate the "dying ReLU" problem where negative feature standardized deviations ($Z < 0$) permanently deactivate neurons.
   - **`Dropout(p=0.1)`**: Regularizes intermediate layers, preventing the autoencoder from memorizing identity connections.
   - **Linear Output Activation**: The final decoder layer uses a pure linear identity activation, allowing the network to reconstruct unbounded standardized $Z$-scores.

```python
# Symmetric Autoencoder definition from model.py
class AIRSAutoencoder(nn.Module):
    def __init__(self, input_dim: int = 72, hidden_dims: List[int] = [48, 24], 
                 latent_dim: int = 12, dropout_rate: float = 0.1):
        super().__init__()
        # Encoder: 72 -> 48 -> 24 -> 12
        encoder_layers = []
        prev_dim = input_dim
        for h_dim in hidden_dims:
            encoder_layers.append(nn.Linear(prev_dim, h_dim))
            encoder_layers.append(nn.LeakyReLU(negative_slope=0.1))
            if dropout_rate > 0.0:
                encoder_layers.append(nn.Dropout(p=dropout_rate))
            prev_dim = h_dim
        encoder_layers.append(nn.Linear(prev_dim, latent_dim))
        encoder_layers.append(nn.LeakyReLU(negative_slope=0.1))
        self.encoder = nn.Sequential(*encoder_layers)

        # Decoder: 12 -> 24 -> 48 -> 72
        decoder_layers = []
        prev_dim = latent_dim
        for h_dim in reversed(hidden_dims):
            decoder_layers.append(nn.Linear(prev_dim, h_dim))
            decoder_layers.append(nn.LeakyReLU(negative_slope=0.1))
            if dropout_rate > 0.0:
                decoder_layers.append(nn.Dropout(p=dropout_rate))
            prev_dim = h_dim
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.encoder(x))
```

---

#### 3. Semi-Supervised Benign Training Strategy (`backend/airs/train.py`)
The training pipeline enforces strict statistical hygiene:
1. **Benign-Only Training Set**: The training dataset is filtered strictly to benign user-days (`is_malicious == 0`).
2. **Complete Malicious User Holdout**: All 30 ground-truth malicious users are completely excluded from training and validation sets.
3. **StandardScaler Isolation**: A `StandardScaler` is fitted **strictly on the benign `train` split**. The validation and test sets are transformed using the saved parameters ($\mu_{\text{train}}, \sigma_{\text{train}}$) to prevent distribution leakage.
4. **Optimization Routine**:
   - Loss Function: Mean Squared Error (MSE) reconstruction loss:
     $$L_{\text{MSE}}(x, \hat{x}) = \frac{1}{72} \sum_{j=1}^{72} (x_j - \hat{x}_j)^2$$
   - Optimizer: `Adam` with initial learning rate $\eta = 0.001$ and $L_2$ weight decay $\lambda = 10^{-5}$.
   - Batch Size: 128.
   - Epochs: 30.

#### 4. Training Results & Checkpoint Deliverables:
- **Training Loss**: MSE loss decreased steadily from `0.4213` (Epoch 1) to `0.1642` (Epoch 30).
- **Validation Loss**: Validation MSE decreased from `0.3230` to `0.1080`.
- **Model Footprint**: 10,020 parameters (~40 KB memory footprint), enabling ultra-low-latency real-time inference ($<1\text{ ms}$ per sample on CPU).
- **Artifacts Saved**:
  - `backend/checkpoints/airs_autoencoder.pt`: PyTorch model weights and training metadata.
  - `backend/checkpoints/airs_scaler.pkl`: Serialized `StandardScaler`.
  - `docs/train_colab.ipynb`: Fallback training notebook for Google Colab GPU execution.

---

## 5. Summary of Deliverables & Test Metrics (Weeks 1 to 5)

Across the first 5 weeks of development, OpenIRM achieved 100% test coverage across all pipeline stages:

| Phase / Week | Milestone Description | Primary Artifacts Generated | Verification Criteria & Metrics |
| :--- | :--- | :--- | :--- |
| **Week 1** | Scaffolding, Tooling & Virtual Environment | `requirements.txt`, `pyproject.toml`, directory structure | 8/8 unit tests passing; 100% Black & Ruff compliance across 47 source files. |
| **Week 2** | CERT Dataset Filtering & Chunked Ingestion | `filter_cert.py`, `config.py` | 12/12 unit tests passing; filtered 20GB+ raw logs to 330 target users without OOM. |
| **Week 3** | Daily Feature Matrix & Initial EDA | `preprocess.py`, `generate_eda.py`, `activity_features.parquet` | 19/19 unit tests passing; 99,987 user-day records generated; 4 EDA plots. |
| **Week 3b** | 72-Feature Engineering & Contiguous Time Split | `compute_rolling_features()`, `compute_baseline_deviation_features()`, `split_metadata.json` | 22/22 unit tests passing; zero date overlap across 70/15/15 chronological splits. |
| **Week 4** | PRISM Rule Engine Implementation | `weights.yaml`, `scorer.py`, `batch_scorer.py`, `prism_scored_activity.parquet` | 31/31 unit tests passing; Paper worked example validated ($R=0.3850$); +0.1031 separation delta; 82.84% malicious in HIGH. |
| **Week 5** | AIRS Autoencoder Architecture & Benign Training | `airs/model.py`, `airs/train.py`, `airs/inference.py`, `airs_autoencoder.pt`, `train_colab.ipynb` | **38/38 unit tests passing**; Train MSE converged to 0.1642; Val MSE converged to 0.1080. |

---

## 6. Architectural Transition: Beyond Week 5

With the completion of Week 5, the core scoring engines (PRISM deterministic rule engine and AIRS deep autoencoder) are fully constructed and validated. The remaining architecture bridges these models into operational SOC intelligence:

- **Week 6**: Evaluation on held-out test split, threshold sweeping (Precision-Recall curve optimization), and hybrid ensemble blending ($S_{\text{ensemble}} = \beta S_{\text{PRISM}} + (1-\beta)S_{\text{AI}}$).
- **Week 7**: Novel Game-Theoretic Explainability layer using **SHAP (SHapley Additive exPlanations)** to compute quantitative feature attributions for anomalous reconstruction loss.
- **Week 8**: Natural Language Threat Reasoning service powered by open-weight LLMs (Llama 3 / DeepSeek via Groq API and Ollama).
- **Weeks 9–12**: Automated Policy Mitigation Engine, FastAPI REST endpoints, and interactive React + TypeScript Analyst Dashboard.

---

## 7. How to Verify and Run Weeks 1–5 Pipelines

All pipelines can be verified inside the virtual environment (`backend/venv/`):

```bash
# 1. Activate Virtual Environment (PowerShell)
backend\venv\Scripts\Activate.ps1

# 2. Run Complete Backend Test Suite (38 Tests)
python -m pytest backend/tests/ -v

# 3. Verify Code Formatting and Linting
python -m black --check backend/
python -m ruff check backend/

# 4. Re-run Preprocessing Pipeline (Generates 72-feature dataset)
python -m data_pipeline.preprocess

# 5. Re-run PRISM Batch Scoring
python -m prism.batch_scorer

# 6. Re-run AIRS Autoencoder Training Loop
python -m airs.train --config airs/config.yaml
```
