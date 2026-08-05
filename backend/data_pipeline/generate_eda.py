"""Script to perform exploratory data analysis and export figures and eda.ipynb notebook."""

import json
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from data_pipeline.config import (
    BASE_BACKEND_DIR,
    PROCESSED_PARQUET_PATH,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DOCS_DIR = BASE_BACKEND_DIR.parent / "docs"


def generate_eda_figures(df: pd.DataFrame, docs_dir: Path = DOCS_DIR) -> None:
    """Generates and saves key EDA visualization PNG plots.

    Args:
        df: Preprocessed daily activity feature DataFrame.
        docs_dir: Destination directory for PNG artifacts.
    """
    docs_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="muted")

    # 1. Class Balance Plot
    fig, ax = plt.subplots(figsize=(7, 5))
    counts = df["is_malicious"].value_counts()
    labels = ["Benign (0)", "Malicious (1)"]
    sns.barplot(
        x=labels,
        y=[counts.get(0, 0), counts.get(1, 0)],
        hue=labels,
        legend=False,
        ax=ax,
        palette=["#2ecc71", "#e74c3c"],
    )
    ax.set_title(
        "OpenIRM Class Balance: Daily Activity Records", fontsize=14, fontweight="bold"
    )
    ax.set_ylabel("Count of User-Days", fontsize=12)
    for p in ax.patches:
        ax.annotate(
            f"{int(p.get_height()):,}",
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="center",
            xytext=(0, 8),
            textcoords="offset points",
            fontsize=11,
            fontweight="bold",
        )
    plt.tight_layout()
    plot1_path = docs_dir / "eda_class_balance.png"
    plt.savefig(plot1_path, dpi=300)
    plt.close()
    logger.info(f"Saved figure: {plot1_path}")

    # 2. Activity Volume Distribution per User
    fig, ax = plt.subplots(figsize=(10, 6))
    user_volumes = df.groupby("user")[
        ["logon_count", "file_count", "email_count", "web_visit_count"]
    ].sum()
    user_volumes_melted = user_volumes.melt(
        var_name="Activity Metric", value_name="Total Events"
    )
    sns.boxplot(
        data=user_volumes_melted,
        x="Activity Metric",
        y="Total Events",
        hue="Activity Metric",
        legend=False,
        ax=ax,
        palette="Blues_d",
    )
    ax.set_yscale("log")
    ax.set_title(
        "User Activity Volume Distribution (Log Scale)", fontsize=14, fontweight="bold"
    )
    ax.set_ylabel("Total Event Count (Log Scale)", fontsize=12)
    plt.tight_layout()
    plot2_path = docs_dir / "eda_activity_volume.png"
    plt.savefig(plot2_path, dpi=300)
    plt.close()
    logger.info(f"Saved figure: {plot2_path}")

    # 3. Off-Hours Activity Distribution
    fig, ax = plt.subplots(figsize=(9, 5))
    df["logon_normal"] = df["logon_count"] - df["logon_after_hours"]
    time_df = pd.DataFrame(
        {
            "Normal Business Hours": [df["logon_normal"].sum()],
            "After Hours / Weekend": [df["logon_after_hours"].sum()],
        }
    )
    time_df_melted = time_df.melt(var_name="Time Period", value_name="Total Logons")
    sns.barplot(
        data=time_df_melted,
        x="Time Period",
        y="Total Logons",
        hue="Time Period",
        legend=False,
        ax=ax,
        palette=["#3498db", "#9b59b6"],
    )
    ax.set_title(
        "Logon Distribution: Business Hours vs After-Hours",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_ylabel("Total Logon Events", fontsize=12)
    for p in ax.patches:
        ax.annotate(
            f"{int(p.get_height()):,}",
            (p.get_x() + p.get_width() / 2.0, p.get_height()),
            ha="center",
            va="center",
            xytext=(0, 8),
            textcoords="offset points",
            fontsize=11,
            fontweight="bold",
        )
    plt.tight_layout()
    plot3_path = docs_dir / "eda_time_distribution.png"
    plt.savefig(plot3_path, dpi=300)
    plt.close()
    logger.info(f"Saved figure: {plot3_path}")

    # 4. Malicious Scenario Timeline & Date Window Sanity Check
    fig, ax = plt.subplots(figsize=(10, 5))
    df_malicious = df[df["is_malicious"] == 1]
    if not df_malicious.empty:
        daily_malicious = (
            df_malicious.groupby("date_day")["user"].nunique().reset_index()
        )
        daily_malicious["date_dt"] = pd.to_datetime(daily_malicious["date_day"])
        daily_malicious = daily_malicious.sort_values("date_dt")
        ax.plot(
            daily_malicious["date_dt"],
            daily_malicious["user"],
            color="#e74c3c",
            linewidth=2,
            label="Active Malicious Insiders",
        )
        ax.set_title(
            "Active Malicious User Timeline (Sanity Check: No Truncation)",
            fontsize=14,
            fontweight="bold",
        )
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Count of Active Malicious Users", fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(loc="upper left")
    plt.tight_layout()
    plot4_path = docs_dir / "eda_scenario_timeline.png"
    plt.savefig(plot4_path, dpi=300)
    plt.close()
    logger.info(f"Saved figure: {plot4_path}")


def generate_eda_notebook(docs_dir: Path = DOCS_DIR) -> None:
    """Creates docs/eda.ipynb containing structured markdown and code cells.

    Args:
        docs_dir: Target directory for eda.ipynb notebook file.
    """
    docs_dir.mkdir(parents=True, exist_ok=True)
    notebook_path = docs_dir / "eda.ipynb"

    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# OpenIRM — Exploratory Data Analysis (EDA)\n",
                "\n",
                "This notebook performs exploratory analysis on the preprocessed CERT Insider Threat Dataset r4.2 daily feature matrix (`activity_features.parquet`).\n",
                "\n",
                "### Objectives:\n",
                "1. **Class Balance**: Evaluate the proportion of benign vs malicious user-day records.\n",
                "2. **Activity Volume**: Inspect distribution of logon, file, email, and web activity across users.\n",
                "3. **Time Distribution**: Compare normal business hours vs after-hours / weekend activity.\n",
                "4. **Scenario Window Sanity Check**: Confirm zero truncation of malicious scenario timelines.",
            ],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "from pathlib import Path\n",
                "\n",
                "parquet_path = Path('../backend/data/filtered/processed/activity_features.parquet')\n",
                "df = pd.read_parquet(parquet_path)\n",
                "print(f'Dataset Shape: {df.shape}')\n",
                "df.head()",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 1. Class Balance Analysis"],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "counts = df['is_malicious'].value_counts()\n",
                "print(counts)\n",
                "print(f'Malicious Percentage: {df[\"is_malicious\"].mean() * 100:.2f}%')\n",
                "\n",
                "fig, ax = plt.subplots(figsize=(7, 5))\n",
                "sns.barplot(x=['Benign (0)', 'Malicious (1)'], y=[counts[0], counts[1]], palette=['#2ecc71', '#e74c3c'], ax=ax)\n",
                "ax.set_title('Class Balance: Daily User Activity Records')\n",
                "plt.show()",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 2. Activity Volume per User"],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "user_totals = df.groupby('user')[['logon_count', 'file_count', 'email_count', 'web_visit_count']].sum()\n",
                "user_totals.describe()",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 3. Time Distribution: Business Hours vs Off-Hours"],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "total_logons = df['logon_count'].sum()\n",
                "after_hours_logons = df['logon_after_hours'].sum()\n",
                "print(f'Total Logons: {int(total_logons):,}')\n",
                "print(f'After Hours / Weekend Logons: {int(after_hours_logons):,} ({after_hours_logons / total_logons * 100:.2f}%)')",
            ],
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 4. Malicious Scenario Window Sanity Check"],
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "df_mal = df[df['is_malicious'] == 1]\n",
                "print(f'Unique Malicious Users: {df_mal[\"user\"].nunique()}')\n",
                "print(f'Observation Start Date: {df[\"date_day\"].min()}')\n",
                "print(f'Observation End Date: {df[\"date_day\"].max()}')",
            ],
        },
    ]

    nb = {
        "cells": cells,
        "metadata": {"language_info": {"name": "python"}, "orig_nbformat": 4},
        "nbformat": 4,
        "nbformat_minor": 2,
    }

    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)

    logger.info(f"Saved EDA Jupyter Notebook: {notebook_path}")


def main() -> None:
    """Script entrypoint to load preprocessed parquet and export figures + eda.ipynb."""
    if not PROCESSED_PARQUET_PATH.exists():
        logger.error(f"Processed parquet file not found: {PROCESSED_PARQUET_PATH}")
        return

    logger.info(f"Loading parquet dataset for EDA: {PROCESSED_PARQUET_PATH}")
    df = pd.read_parquet(PROCESSED_PARQUET_PATH)
    generate_eda_figures(df)
    generate_eda_notebook()
    print("\n--- EDA Generation Complete ---")
    print(f"Figures and notebook generated in {DOCS_DIR}")


if __name__ == "__main__":
    main()
