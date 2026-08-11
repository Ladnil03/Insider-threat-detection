# AIRS (Adaptive Insider Risk System) Autoencoder Module

AIRS is a PyTorch-based neural autoencoder model trained strictly on benign baseline user activity profiles to detect statistical behavioral anomalies.

---

## 1. Network Architecture

The model uses a symmetric encoder/decoder structure:

```
[ Input: 72 Features ]
          │  Linear(72 -> 48) + LeakyReLU(0.1) + Dropout(0.1)
          ▼
    [ Hidden 1: 48 ]
          │  Linear(48 -> 24) + LeakyReLU(0.1) + Dropout(0.1)
          ▼
    [ Hidden 2: 24 ]
          │  Linear(24 -> 12) + LeakyReLU(0.1)
          ▼
[ Latent Bottleneck: 12 ]
          │  Linear(12 -> 24) + LeakyReLU(0.1) + Dropout(0.1)
          ▼
    [ Hidden 2: 24 ]
          │  Linear(24 -> 48) + LeakyReLU(0.1) + Dropout(0.1)
          ▼
    [ Hidden 1: 48 ]
          │  Linear(48 -> 72)
          ▼
[ Reconstructed Output: 72 ]
```

- **Reconstruction Error Metric**: Mean Squared Error (MSE)
  $$\mathcal{L}_{\text{MSE}}(x, \hat{x}) = \frac{1}{D} \sum_{i=1}^{D} (x_i - \hat{x}_i)^2$$

---

## 2. Configuration (`config.yaml`)

```yaml
model:
  input_dim: 72
  hidden_dims: [48, 24]
  latent_dim: 12
  dropout_rate: 0.1

training:
  epochs: 30
  batch_size: 128
  learning_rate: 0.001
  weight_decay: 1e-5
  alpha: 0.7
  retrain_threshold_count: 50

storage:
  checkpoint_dir: "checkpoints"
  model_save_name: "airs_autoencoder.pt"
  scaler_save_name: "airs_scaler.pkl"
```

---

## 3. Usage & CLI Commands

### Train AIRS Model on Benign Baseline
```bash
# Ensure venv is active in backend/
python -m airs.train --config airs/config.yaml
```

### Run Unit Tests
```bash
python -m pytest tests/test_airs.py -v
```
