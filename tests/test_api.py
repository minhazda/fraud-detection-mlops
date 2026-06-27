"""API tests using an injected dummy model (no artifact, no training)."""

from __future__ import annotations

import numpy as np
from fastapi.testclient import TestClient

from fraud_detection.api import main as api


class _DummyModel:
    """Returns a fixed high fraud probability for every row."""

    def predict_proba(self, matrix: object) -> np.ndarray:
        n = len(matrix)  # type: ignore[arg-type]
        return np.column_stack([np.full(n, 0.2), np.full(n, 0.8)])


def _client() -> TestClient:
    api._STATE.update(
        model=_DummyModel(),
        features=["amount", "hour", "is_night"],
        threshold=0.5,
    )
    return TestClient(api.app)


_ROW = {
    "amount": 500,
    "hour": 2,
    "day_of_week": 5,
    "merchant_category": "online",
    "customer_age": 30,
    "account_age_days": 10,
    "n_tx_24h": 9,
    "avg_amount_30d": 20,
    "distance_from_home": 300,
    "is_foreign": 1,
}


def test_health_ok() -> None:
    resp = _client().get("/health")
    assert resp.status_code == 200
    assert resp.json()["model_loaded"] is True


def test_predict_flags_high_probability() -> None:
    resp = _client().post("/predict", json={"rows": [_ROW]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["fraud_probability"] == [0.8]
    assert body["is_fraud"] == [True]


def test_metrics_endpoint_served() -> None:
    assert _client().get("/metrics").status_code == 200
