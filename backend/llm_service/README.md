# LLM Threat Service Module

This module orchestrates prompt construction, safety sanitization, and LLM provider invocation to convert numerical scores + SHAP attributions into natural language threat analyst recommendations.

## Provider Architecture
OpenIRM uses a decoupled provider interface (`providers/base.py`):
- **Groq API Provider (`groq_provider.py`)**: Default hosted free-tier provider serving open-weight models (`Llama 3.3 70B`, `DeepSeek-R1 distills`).
- **Ollama Provider (`ollama_provider.py`)**: Secondary local provider for offline/on-prem air-gapped deployments.

## Trade-off Notice
Using Groq trades off strict on-prem data sovereignty for cloud inference speed and zero-cost infrastructure. The provider pattern allows swapping in local Ollama without modifying business logic.
