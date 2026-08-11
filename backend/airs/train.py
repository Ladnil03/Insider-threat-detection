"""AIRS Autoencoder Training Pipeline.

Trains PyTorch AIRSAutoencoder strictly on benign user activity profiles.
All malicious user records (and test split records) are held out for evaluation in Week 6.
"""

import argparse
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import joblib
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import yaml
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

from airs.model import AIRSAutoencoder
from data_pipeline.config import (
    ALL_FEATURE_COLS,
    BASE_BACKEND_DIR,
    PROCESSED_DATA_DIR,
)

# Paths for input parquet dataset and output checkpoints
SCORED_PARQUET_PATH = PROCESSED_DATA_DIR / "prism_scored_activity.parquet"
FALLBACK_PARQUET_PATH = PROCESSED_DATA_DIR / "activity_features.parquet"
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


def load_airs_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Loads AIRS model and training hyperparameters from YAML config file.

    Args:
        config_path: Path to config.yaml file.

    Returns:
        Configuration dictionary.
    """
    target = config_path or DEFAULT_CONFIG_PATH
    if target.exists():
        with open(target, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # Fallback configuration dictionary
    return {
        "model": {
            "input_dim": 72,
            "hidden_dims": [48, 24],
            "latent_dim": 12,
            "dropout_rate": 0.1,
        },
        "training": {
            "epochs": 30,
            "batch_size": 128,
            "learning_rate": 0.001,
            "weight_decay": 1e-5,
        },
        "storage": {
            "checkpoint_dir": "checkpoints",
            "model_save_name": "airs_autoencoder.pt",
            "scaler_save_name": "airs_scaler.pkl",
        },
    }


def prepare_benign_dataloaders(
    dataset_path: Path,
    batch_size: int = 128,
) -> Tuple[DataLoader, DataLoader, StandardScaler]:
    """Prepares PyTorch DataLoaders strictly from benign user activity records.

    Filters dataset to benign activity (`is_malicious == 0`), fits StandardScaler
    on the `train` split, and returns train/val DataLoaders.

    Args:
        dataset_path: Path to input Parquet feature dataset.
        batch_size: DataLoader mini-batch size.

    Returns:
        Tuple of (train_loader, val_loader, fitted_scaler).
    """
    if not dataset_path.exists():
        if FALLBACK_PARQUET_PATH.exists():
            dataset_path = FALLBACK_PARQUET_PATH
        else:
            raise FileNotFoundError(
                f"Processed feature dataset not found at {dataset_path}"
            )

    df = pd.read_parquet(dataset_path)

    # Strict Benign Filter: Train ONLY on benign activity profiles
    benign_df = (
        df[df["is_malicious"] == 0].copy()
        if "is_malicious" in df.columns
        else df.copy()
    )

    # Split into train and validation sets based on pre-computed time split tags
    if "split" in benign_df.columns:
        train_df = benign_df[benign_df["split"] == "train"]
        val_df = benign_df[benign_df["split"] == "val"]
    else:
        # Fallback 80/20 time split if split tag absent
        split_idx = int(len(benign_df) * 0.8)
        train_df = benign_df.iloc[:split_idx]
        val_df = benign_df.iloc[split_idx:]

    # Select existing feature columns matching ALL_FEATURE_COLS
    feature_cols = [c for c in ALL_FEATURE_COLS if c in train_df.columns]
    if not feature_cols:
        raise ValueError("No matching feature columns found in dataset")

    # Fit StandardScaler strictly on benign training set
    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(
        train_df[feature_cols].values.astype("float32")
    )
    x_val_scaled = scaler.transform(val_df[feature_cols].values.astype("float32"))

    # Convert to PyTorch Tensors and DataLoaders
    t_train = torch.tensor(x_train_scaled, dtype=torch.float32)
    t_val = torch.tensor(x_val_scaled, dtype=torch.float32)

    train_loader = DataLoader(
        TensorDataset(t_train), batch_size=batch_size, shuffle=True
    )
    val_loader = DataLoader(TensorDataset(t_val), batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, scaler


def train_airs_model(
    config_path: Optional[Path] = None,
    dataset_path: Optional[Path] = None,
    verbose: bool = True,
) -> Dict[str, Any]:
    """Executes end-to-end AIRS autoencoder training loop.

    Args:
        config_path: Optional path to YAML config file.
        dataset_path: Optional path to input Parquet dataset.
        verbose: If True, prints epoch progress.

    Returns:
        Dictionary containing training history, final loss, model, and artifact paths.
    """
    cfg = load_airs_config(config_path)
    m_cfg = cfg.get("model", {})
    t_cfg = cfg.get("training", {})
    s_cfg = cfg.get("storage", {})

    target_data_path = dataset_path or SCORED_PARQUET_PATH
    batch_size = t_cfg.get("batch_size", 128)
    epochs = t_cfg.get("epochs", 30)
    lr = t_cfg.get("learning_rate", 0.001)
    weight_decay = t_cfg.get("weight_decay", 1e-5)

    # 1. Prepare Benign DataLoaders
    train_loader, val_loader, scaler = prepare_benign_dataloaders(
        target_data_path, batch_size
    )

    # Detect device (CUDA GPU or CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 2. Instantiate Model
    input_dim = m_cfg.get("input_dim", 72)
    hidden_dims = m_cfg.get("hidden_dims", [48, 24])
    latent_dim = m_cfg.get("latent_dim", 12)
    dropout_rate = m_cfg.get("dropout_rate", 0.1)

    model = AIRSAutoencoder(
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        latent_dim=latent_dim,
        dropout_rate=dropout_rate,
    ).to(device)

    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.MSELoss()

    train_loss_history = []
    val_loss_history = []

    if verbose:
        print(f"Starting AIRS Training on device: {device}")
        print(
            f"Benign Training Batches: {len(train_loader)}, Validation Batches: {len(val_loader)}"
        )

    # 3. Training Epoch Loop
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss_sum = 0.0
        for (batch_x,) in train_loader:
            batch_x = batch_x.to(device)
            optimizer.zero_grad()
            reconstructed = model(batch_x)
            loss = criterion(reconstructed, batch_x)
            loss.backward()
            optimizer.step()
            train_loss_sum += loss.item() * len(batch_x)

        epoch_train_loss = train_loss_sum / len(train_loader.dataset)
        train_loss_history.append(epoch_train_loss)

        # Validation phase
        model.eval()
        val_loss_sum = 0.0
        with torch.no_grad():
            for (batch_x,) in val_loader:
                batch_x = batch_x.to(device)
                reconstructed = model(batch_x)
                loss = criterion(reconstructed, batch_x)
                val_loss_sum += loss.item() * len(batch_x)

        epoch_val_loss = val_loss_sum / len(val_loader.dataset)
        val_loss_history.append(epoch_val_loss)

        if verbose and (epoch == 1 or epoch % 5 == 0 or epoch == epochs):
            print(
                f"Epoch {epoch:02d}/{epochs:02d} | Train MSE: {epoch_train_loss:.6f} | Val MSE: {epoch_val_loss:.6f}"
            )

    # 4. Save Checkpoint Artifacts
    ckpt_dir = BASE_BACKEND_DIR / s_cfg.get("checkpoint_dir", "checkpoints")
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    model_path = ckpt_dir / s_cfg.get("model_save_name", "airs_autoencoder.pt")
    scaler_path = ckpt_dir / s_cfg.get("scaler_save_name", "airs_scaler.pkl")

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": cfg,
            "final_val_loss": val_loss_history[-1],
        },
        model_path,
    )
    joblib.dump(scaler, scaler_path)

    if verbose:
        print("\nTraining Complete!")
        print(f"Saved Trained Model Checkpoint To: {model_path}")
        print(f"Saved Fitted StandardScaler Artifact To: {scaler_path}")

    return {
        "train_loss_history": train_loss_history,
        "val_loss_history": val_loss_history,
        "final_train_loss": train_loss_history[-1],
        "final_val_loss": val_loss_history[-1],
        "model_path": str(model_path),
        "scaler_path": str(scaler_path),
        "model": model,
    }


def main() -> None:
    """CLI entrypoint for AIRS training."""
    parser = argparse.ArgumentParser(
        description="Train AIRS Autoencoder on Benign Activity Baseline"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to config.yaml",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=str(SCORED_PARQUET_PATH),
        help="Path to input Parquet file",
    )
    args = parser.parse_args()

    train_airs_model(
        config_path=Path(args.config), dataset_path=Path(args.dataset), verbose=True
    )


if __name__ == "__main__":
    main()
