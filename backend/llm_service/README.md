# OpenIRM LLM Recommendation Service (`backend/llm_service/`)

## 1. Overview & Purpose

The LLM Service bridges deep quantitative anomaly detection and human Security Operations Center (SOC) workflows. It ingests composite risk scores (PRISM + AIRS + Ensemble) and game-theoretic SHAP feature attributions, transforming multi-dimensional telemetry into **plain-English, executive threat narratives and proportional mitigation recommendations**.

---

## 2. Model Evaluation & Selection Rationale

OpenIRM evaluated three candidate open-weight models available on the free-tier Groq Cloud API:

| Model Tag | Parameter Size | Reasoning Quality | JSON Mode Reliability | Inference Speed (Tokens/s) | Groq Free Rate Limits | Selected Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`llama-3.3-70b-versatile`** | **70B** | **Exceptional** | **100% (Native Object)** | **~280 T/s** | **1,000 req/day (6,000 TPM)** | **Default Production Model** |
| `llama-3.1-8b-instant` | 8B | Good | High (Prompt-guided) | ~800 T/s | 14,400 req/day (30,000 TPM) | High-throughput fallback |
| `deepseek-r1-distill-llama-70b` | 70B | High (CoT) | Moderate (Thinking tags) | ~220 T/s | 1,000 req/day (6,000 TPM) | Deep reasoning alternative |

### Selection Rationale:
- **`llama-3.3-70b-versatile`** was selected as the **primary default**. It combines frontier-class cyber-threat reasoning with native Groq JSON Mode schema enforcement, ensuring zero formatting hallucinations while operating safely within standard SOC alert volumes.
- For high-volume automated testing or rate-limited environments, users can toggle `LLM_MODEL=llama-3.1-8b-instant` for 5x rate-limit headroom.

---

## 3. Provider Abstraction Architecture

To maintain complete provider independence and preserve on-prem data sovereignty options, the service implements a decoupled provider interface:

```
backend/llm_service/
├── config.yaml               # Model parameters, timeouts, retry backoff
├── prompts.py                # System personas and structured prompt templates
├── safety.py                 # Multi-stage prompt injection sanitization
├── recommend.py              # Orchestrator with JSON parsing & error fallback
├── live_test.py              # Interactive CLI live verification utility
├── providers/
│   ├── base.py               # Abstract BaseLLMProvider interface
│   ├── groq_provider.py      # Official Groq API client with JSON mode & 429 retry
│   ├── ollama_provider.py    # Local Ollama client (HTTP /api/generate)
│   └── factory.py            # Dynamic get_llm_provider() resolver
```

### Swapping Providers:
Contributors can switch between cloud and on-prem providers simply by setting the environment variable in `.env`:
```env
# Default Cloud (Groq)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_groq_key_here

# Local On-Prem (Ollama)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 4. Prompt Injection Defense (`safety.py`)

Because log fields and usernames may contain malicious payloads in real-world attacks, all inputs pass through `sanitize_input_text()` and `sanitize_activity_metadata()` before prompt interpolation:
- **Control Character Stripping**: Removes non-printable characters (`\x00-\x1f`).
- **Instruction Override Neutralization**: Regex patterns redact phrases like `IGNORE PREVIOUS INSTRUCTIONS`, `SYSTEM PROMPT:`, and `DEVELOPER MODE`.
- **Structural Delimiter Escaping**: Strips markdown header tags (`###`) and code fences (` ``` ` $\to$ ` ''' `) to prevent prompt boundary hijacking.

---

## 5. Usage Example

```python
from llm_service.recommend import get_threat_recommendation

rec = get_threat_recommendation(
    user_id="ACM2278",
    risk_score=0.895,
    risk_level="CRITICAL",
    prism_score=0.780,
    sai_score=0.912,
    shap_explanation={
        "top_risk_drivers": [
            {"feature_name": "Mass USB File Exfiltration", "shap_value": 0.48, "percentage_contribution": 52.4},
            {"feature_name": "Off-Hours Logons", "shap_value": 0.26, "percentage_contribution": 28.4}
        ]
    },
    recent_activity={"file_copy_usb": 142, "logon_after_hours": 8}
)

print(rec["summary"])
print(rec["recommended_action"])
```

---

## 6. Testing & Verification

Run unit tests covering mocked providers, safety sanitization, and fallback recovery:
```bash
python -m pytest tests/test_llm_service.py -v
```

Execute live test script against Groq API:
```bash
python backend/llm_service/live_test.py
```
