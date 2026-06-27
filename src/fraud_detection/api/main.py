"""FastAPI real-time fraud-scoring service.

Loads the persisted ``{model, features, threshold}`` bundle on startup and
exposes:

* ``GET  /health``   -- liveness/readiness probe;
* ``GET  /metadata`` -- feature schema + operating threshold;
* ``POST /predict``  -- score raw transactions (features engineered server-side);
* ``GET  /metrics``  -- Prometheus metrics (HTTP + custom fraud metrics).
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field

MODEL_PATH = Path(os.environ.get("FD_MODEL_PATH", "models/fraud_model.joblib"))
_STATE: dict[str, Any] = {"model": None, "features": [], "threshold": 0.5}

SCORED = Counter("fd_transactions_scored_total", "Transactions scored.")
FLAGGED = Counter("fd_transactions_flagged_total", "Transactions flagged as fraud.")
FRAUD_PROB = Histogram(
    "fd_fraud_probability",
    "Predicted fraud probability distribution.",
    buckets=(0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0),
)


def _load_model(path: Path | None = None) -> None:
    path = path or MODEL_PATH
    if not path.is_file():
        raise FileNotFoundError(f"Model artifact not found at {path}")
    bundle = joblib.load(path)
    _STATE.update(
        model=bundle["model"],
        features=list(bundle["features"]),
        threshold=float(bundle["threshold"]),
    )


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        _load_model()
    except FileNotFoundError:
        pass  # /health reports model_loaded=false until an artifact is present
    yield


app = FastAPI(title="Fraud Detection API", version="0.1.0", lifespan=lifespan)


class ScoreRequest(BaseModel):
    rows: list[dict[str, Any]] = Field(..., min_length=1, description="Raw transactions.")


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "model_loaded": _STATE["model"] is not None}


@app.get("/metadata")
def metadata() -> dict[str, Any]:
    if _STATE["model"] is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Model not loaded.")
    return {
        "n_features": len(_STATE["features"]),
        "features": _STATE["features"],
        "threshold": _STATE["threshold"],
    }


@app.post("/predict")
def predict(req: ScoreRequest) -> dict[str, Any]:
    model = _STATE["model"]
    features: list[str] = _STATE["features"]
    threshold: float = _STATE["threshold"]
    if model is None:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Model not loaded.")

    from ..features import build_features

    try:
        engineered = build_features(pd.DataFrame(req.rows))
    except KeyError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, f"Missing field: {exc}"
        ) from exc
    matrix = engineered.reindex(columns=features, fill_value=0)

    probabilities = model.predict_proba(matrix)[:, 1]
    SCORED.inc(len(probabilities))
    fraud_probability: list[float] = []
    is_fraud: list[bool] = []
    flagged = 0
    for p in probabilities:
        fraud_probability.append(float(p))
        FRAUD_PROB.observe(float(p))
        decision = bool(p >= threshold)
        is_fraud.append(decision)
        flagged += int(decision)
    FLAGGED.inc(flagged)
    return {
        "fraud_probability": fraud_probability,
        "is_fraud": is_fraud,
        "threshold": threshold,
    }


Instrumentator(excluded_handlers=["/metrics", "/health"]).instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)
