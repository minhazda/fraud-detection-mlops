"""Leakage guards and threshold-sensitivity checks for an imbalanced classifier.

These target the two gaps a hiring-manager review flagged: (1) the README's
"leakage-safe, shared train/serve features" claim wasn't actually regression
tested, and (2) threshold behaviour on the edges (no fraud at all, threshold
sweeps) wasn't covered.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from fraud_detection.data.generate import generate
from fraud_detection.features import LABEL, build_features
from fraud_detection.metrics import best_threshold, evaluate


def test_build_features_identical_with_and_without_label_column() -> None:
    """Training frames carry the label; inference payloads never do. Same rows
    must produce the same feature matrix either way, or serving would skew."""
    labelled = generate(200, seed=3)
    unlabelled = labelled.drop(columns=[LABEL])

    pd.testing.assert_frame_equal(build_features(labelled), build_features(unlabelled))


def test_build_features_ignores_label_values() -> None:
    """Flipping every label must not change a single engineered feature."""
    df = generate(200, seed=4)
    baseline = build_features(df)

    adversarial = df.copy()
    adversarial[LABEL] = 1 - adversarial[LABEL]
    pd.testing.assert_frame_equal(baseline, build_features(adversarial))


def test_amount_to_avg_ratio_guards_against_divide_by_zero() -> None:
    df = generate(5, seed=5)
    df["avg_amount_30d"] = 0.0
    features = build_features(df)
    assert np.isfinite(features["amount_to_avg_ratio"]).all()


def test_evaluate_handles_no_fraud_in_batch_without_crashing() -> None:
    """A quiet day with zero fraud must not raise -- ops will hit this in prod."""
    m = evaluate([0, 0, 0, 0], [0.1, 0.2, 0.3, 0.4], threshold=0.5)
    assert np.isnan(m.roc_auc)
    assert m.precision == 0.0 and m.recall == 0.0 and m.f1 == 0.0
    assert m.tp == 0 and m.fp == 0


def test_best_threshold_handles_no_fraud_without_crashing() -> None:
    t = best_threshold([0, 0, 0, 0], [0.1, 0.2, 0.3, 0.4])
    assert 0.0 <= t <= 1.0


def test_higher_threshold_never_flags_more_transactions() -> None:
    """Raising the decision threshold must monotonically shrink (or hold) the
    flagged set -- a regression here would mean the threshold knob is broken."""
    rng = np.random.default_rng(7)
    y = rng.integers(0, 2, 500)
    p = rng.random(500)

    thresholds = (0.1, 0.3, 0.5, 0.7, 0.9)
    flagged_counts = [evaluate(y, p, t).tp + evaluate(y, p, t).fp for t in thresholds]
    assert flagged_counts == sorted(flagged_counts, reverse=True)


def test_best_threshold_beats_a_naive_midpoint_on_f1() -> None:
    """Sanity-check best_threshold actually optimises something, rather than
    just returning a value in range (already covered elsewhere)."""
    df = generate(4000, seed=8)
    _, y = df.drop(columns=[c for c in df.columns if c != LABEL]), df[LABEL].astype(int)
    rng = np.random.default_rng(9)
    # scores correlated with the label, standing in for a trained model's probabilities
    p = np.clip(y * 0.6 + rng.random(len(y)) * 0.5, 0, 1)

    t = best_threshold(y, p)
    f1_best = evaluate(y, p, t).f1
    f1_midpoint = evaluate(y, p, 0.5).f1
    assert f1_best >= f1_midpoint - 1e-9


@pytest.mark.parametrize("bad_col", ["amount", "hour", "merchant_category"])
def test_build_features_requires_expected_raw_columns(bad_col: str) -> None:
    df = generate(5, seed=6).drop(columns=[bad_col])
    with pytest.raises(KeyError):
        build_features(df)
