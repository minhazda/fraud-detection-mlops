"""Metrics for imbalanced binary classification.

For rare-event fraud, accuracy is useless; we report ROC-AUC, PR-AUC (average
precision), and precision/recall/F1 at an operating threshold, plus the
confusion matrix. ``best_threshold`` picks the F-beta-optimal threshold from the
precision-recall curve (tune on validation, never on test).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    precision_recall_fscore_support,
    roc_auc_score,
)


@dataclass(frozen=True)
class ClassMetrics:
    roc_auc: float
    pr_auc: float
    precision: float
    recall: float
    f1: float
    threshold: float
    tn: int
    fp: int
    fn: int
    tp: int


def evaluate(y_true: Sequence[int], y_prob: Sequence[float], threshold: float) -> ClassMetrics:
    """Compute ranking + threshold metrics for predicted probabilities."""
    y_true_arr = np.asarray(y_true)
    y_prob_arr = np.asarray(y_prob, dtype=float)
    y_pred = (y_prob_arr >= threshold).astype(int)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true_arr, y_pred, average="binary", zero_division=0
    )
    tn, fp, fn, tp = confusion_matrix(y_true_arr, y_pred, labels=[0, 1]).ravel()
    return ClassMetrics(
        roc_auc=float(roc_auc_score(y_true_arr, y_prob_arr)),
        pr_auc=float(average_precision_score(y_true_arr, y_prob_arr)),
        precision=float(precision),
        recall=float(recall),
        f1=float(f1),
        threshold=float(threshold),
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
    )


def best_threshold(y_true: Sequence[int], y_prob: Sequence[float], beta: float = 1.0) -> float:
    """Return the threshold maximising F-beta over the precision-recall curve."""
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)
    if len(thresholds) == 0:
        return 0.5
    b2 = beta * beta
    p, r = precision[:-1], recall[:-1]
    fbeta = (1 + b2) * p * r / np.maximum(b2 * p + r, 1e-12)
    return float(thresholds[int(np.argmax(fbeta))])
