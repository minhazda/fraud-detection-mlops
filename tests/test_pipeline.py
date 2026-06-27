"""Unit tests for the data generator, feature builder, and metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd

from fraud_detection.data.generate import generate
from fraud_detection.features import LABEL, split_xy
from fraud_detection.metrics import best_threshold, evaluate


def test_generate_is_deterministic_and_imbalanced() -> None:
    a = generate(2000, seed=1)
    b = generate(2000, seed=1)
    pd.testing.assert_frame_equal(a, b)
    assert 0.003 < a[LABEL].mean() < 0.10
    assert {"amount", "merchant_category", LABEL} <= set(a.columns)


def test_features_drop_label_and_engineer() -> None:
    df = generate(500, seed=2)
    features, labels = split_xy(df)
    assert LABEL not in features.columns
    assert "amount_to_avg_ratio" in features.columns
    assert any(c.startswith("mcat_") for c in features.columns)
    assert len(features) == len(labels)


def test_evaluate_perfect_separation() -> None:
    m = evaluate([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9], 0.5)
    assert m.roc_auc == 1.0
    assert m.tp == 2 and m.fp == 0


def test_best_threshold_in_unit_interval() -> None:
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 200)
    p = rng.random(200)
    assert 0.0 <= best_threshold(y, p) <= 1.0
