"""Leakage-safe feature engineering for the fraud model.

The same function is used in training and serving, so the inference path can
accept raw transactions and engineer features identically (no train/serve skew).
"""

from __future__ import annotations

import pandas as pd

LABEL = "is_fraud"
NUMERIC = [
    "amount",
    "hour",
    "day_of_week",
    "customer_age",
    "account_age_days",
    "n_tx_24h",
    "avg_amount_30d",
    "distance_from_home",
    "is_foreign",
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return the model feature matrix (numeric + derived + one-hot category).

    Never reads the label, so it is safe to call on raw inference payloads.
    """
    out = df[NUMERIC].copy()
    out["amount_to_avg_ratio"] = df["amount"] / df["avg_amount_30d"].clip(lower=1.0)
    out["is_night"] = ((df["hour"] < 5) | (df["hour"] >= 23)).astype(int)
    cats = pd.get_dummies(df["merchant_category"], prefix="mcat")
    return pd.concat([out, cats], axis=1)


def split_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Return (features, label) for a labelled frame."""
    return build_features(df), df[LABEL].astype(int)
