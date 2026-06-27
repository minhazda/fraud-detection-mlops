# fraud-detection-mlops

Real-time **card-fraud detection** — an imbalanced binary-classification MLOps
pipeline, built to the same typed / tested / CI / containerised / cloud-deployed
bar as my [retail-forecasting pipeline](https://github.com/minhazda/synthetic-retail-mlops-pipeline),
but on a deliberately different problem type (rare-event classification, not
forecasting) to show breadth.

> **Author:** Md Minhazur Rahman · MSc Data Science, University of Greenwich

## Why this project

Fraud is the canonical **imbalanced** problem: positives are ~1–4% of traffic, so
accuracy is meaningless and the real work is ranking quality, threshold choice,
and the precision/recall trade-off. This repo demonstrates that end to end:

- **Deterministic synthetic generator** (`data/generate.py`) where fraud is a
  logistic function of genuine risk signals (night-time, risky merchant
  category, amount vs the customer's own average, foreign / far-from-home, new
  account, transaction velocity) plus noise — real signal, not trivially
  separable.
- **Leakage-safe features** (`features.py`) shared by training and serving, so
  the API engineers features from **raw transactions** with no train/serve skew.
- **Imbalance-aware training** (`train.py`): LightGBM with `scale_pos_weight`, a
  three-way stratified split (train / validation / test) so the operating
  **threshold is tuned on validation, never on test**.
- **Honest metrics** (`metrics.py`): ROC-AUC, **PR-AUC**, precision/recall/F1 at
  the chosen threshold, and the confusion matrix.

## Live API (GCP Cloud Run)

Deployed from the Terraform IaC in [`terraform/`](terraform/) (Cloud Run that
scales to zero, Artifact Registry, keyless GitHub→GCP Workload Identity
Federation). Endpoints: `/health`, `/metadata`, `/predict`, `/metrics`.

```bash
curl -X POST "$SERVICE_URL/predict" -H 'Content-Type: application/json' -d '{
  "rows": [{
    "amount": 920.0, "hour": 2, "day_of_week": 6, "merchant_category": "online",
    "customer_age": 31, "account_age_days": 12, "n_tx_24h": 9,
    "avg_amount_30d": 40.0, "distance_from_home": 480.0, "is_foreign": 1
  }]
}'
# -> {"fraud_probability":[..],"is_fraud":[true],"threshold":..}
```

## Results

Produced by `python -m fraud_detection.train` on the synthetic dataset
(see [`models/metrics.json`](models/metrics.json), regenerated on every build).
Metrics below are from a real run on the held-out test split:

<!-- METRICS:START -->
_Run `python -m fraud_detection.train` to populate; latest values in `models/metrics.json`._
<!-- METRICS:END -->

## Engineering

| Area | Detail |
|------|--------|
| Quality | ruff · black · mypy · pytest — enforced in CI |
| Container | multi-stage, non-root, healthcheck; model trained at build so cold start is just load |
| Observability | Prometheus `/metrics` (HTTP + `fd_transactions_scored_total`, `fd_transactions_flagged_total`, `fd_fraud_probability`) |
| IaC / deploy | Terraform → Cloud Run; keyless CD via Workload Identity Federation |

## Quickstart

```bash
python -m venv .venv && . .venv/Scripts/activate   # or source .venv/bin/activate
pip install -r requirements-dev.txt && pip install -e .

python -m fraud_detection.train                    # train + write models/
uvicorn fraud_detection.api.main:app --reload      # serve on :8000
ruff check src tests && black --check src tests && mypy src && pytest
```

Or with Docker: `docker build -t fraud-detection . && docker run --rm -p 8000:8000 fraud-detection`.

Deployment details: [`terraform/`](terraform/) + the `deploy.yml` workflow.

## License

MIT © Md Minhazur Rahman
