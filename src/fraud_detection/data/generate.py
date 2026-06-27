"""Deterministic synthetic card-transaction generator with labelled fraud.

Produces an imbalanced dataset (~1-4% fraud) whose fraud probability is a
logistic function of real risk signals (night-time, risky merchant category,
high amount vs the customer's personal average, foreign/far-from-home, new
account, transaction velocity) plus noise -- so a model has genuine signal to
learn without the labels being trivially separable.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

MERCHANT_CATEGORIES = (
    "grocery",
    "restaurant",
    "travel",
    "electronics",
    "gambling",
    "fuel",
    "online",
)


def _category_probs() -> np.ndarray:
    p = np.array([0.30, 0.22, 0.08, 0.10, 0.03, 0.15, 0.12])
    return p / p.sum()


def generate(n: int = 50_000, *, seed: int = 7) -> pd.DataFrame:
    """Return a reproducible DataFrame of transactions with an ``is_fraud`` label."""
    rng = np.random.default_rng(seed)
    amount = np.round(rng.lognormal(mean=3.2, sigma=1.1, size=n), 2)
    hour = rng.integers(0, 24, n)
    day_of_week = rng.integers(0, 7, n)
    merchant = rng.choice(MERCHANT_CATEGORIES, size=n, p=_category_probs())
    customer_age = rng.integers(18, 85, n)
    account_age_days = rng.integers(1, 3650, n)
    n_tx_24h = rng.poisson(3, n)
    avg_amount_30d = np.round(rng.lognormal(3.0, 0.8, n), 2)
    distance_from_home = np.round(rng.exponential(20, n), 1)
    is_foreign = rng.binomial(1, 0.08, n)

    amount_ratio = amount / np.maximum(avg_amount_30d, 1.0)
    night = ((hour < 5) | (hour >= 23)).astype(float)
    risky_cat = np.isin(merchant, ("gambling", "online")).astype(float)
    z = (
        -5.2
        + 0.9 * night
        + 1.1 * risky_cat
        + 0.6 * np.log1p(amount_ratio)
        + 1.4 * is_foreign
        + 0.015 * distance_from_home
        + 0.5 * (account_age_days < 60).astype(float)
        + 0.08 * np.maximum(n_tx_24h - 6, 0)
    )
    prob = 1.0 / (1.0 + np.exp(-z))
    is_fraud = rng.binomial(1, np.clip(prob, 0.0, 0.95))

    return pd.DataFrame(
        {
            "amount": amount,
            "hour": hour,
            "day_of_week": day_of_week,
            "merchant_category": merchant,
            "customer_age": customer_age,
            "account_age_days": account_age_days,
            "n_tx_24h": n_tx_24h,
            "avg_amount_30d": avg_amount_30d,
            "distance_from_home": distance_from_home,
            "is_foreign": is_foreign,
            "is_fraud": is_fraud.astype(int),
        }
    )


if __name__ == "__main__":
    df = generate()
    print(f"rows={len(df)} fraud_rate={df['is_fraud'].mean():.4f}")
