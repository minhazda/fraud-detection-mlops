"""Train the fraud classifier and persist {model, features, threshold}.

Uses a three-way stratified split: train (fit), validation (threshold tuning),
test (final metrics) -- so the operating threshold is never selected on the data
it is reported against. Class imbalance is handled with ``scale_pos_weight``.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split

from .config import load
from .data.generate import generate
from .features import split_xy
from .metrics import best_threshold, evaluate


def main() -> dict[str, object]:
    """Train, evaluate, persist the model bundle, and return the metrics report."""
    settings = load()
    df = generate(settings.n_samples, seed=settings.seed)
    features, labels = split_xy(df)

    x_train, x_tmp, y_train, y_tmp = train_test_split(
        features, labels, test_size=settings.test_size, stratify=labels, random_state=settings.seed
    )
    x_val, x_test, y_val, y_test = train_test_split(
        x_tmp, y_tmp, test_size=0.5, stratify=y_tmp, random_state=settings.seed
    )

    pos = int(y_train.sum())
    neg = int(len(y_train) - pos)
    model = LGBMClassifier(
        n_estimators=400,
        learning_rate=0.05,
        num_leaves=31,
        scale_pos_weight=max(neg / max(pos, 1), 1.0),
        random_state=settings.seed,
        n_jobs=-1,
        verbosity=-1,
    )
    model.fit(x_train, y_train)

    threshold = best_threshold(y_val, model.predict_proba(x_val)[:, 1])
    test_prob = model.predict_proba(x_test)[:, 1]
    m = evaluate(y_test, test_prob, threshold)

    model_path = Path(settings.model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": model, "features": list(features.columns), "threshold": threshold},
        model_path,
    )

    report: dict[str, object] = {
        "roc_auc": round(m.roc_auc, 4),
        "pr_auc": round(m.pr_auc, 4),
        "precision": round(m.precision, 4),
        "recall": round(m.recall, 4),
        "f1": round(m.f1, 4),
        "threshold": round(threshold, 4),
        "confusion": {"tn": m.tn, "fp": m.fp, "fn": m.fn, "tp": m.tp},
        "fraud_rate": round(float(labels.mean()), 4),
        "n_samples": int(len(df)),
    }
    (model_path.parent / "metrics.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    main()
