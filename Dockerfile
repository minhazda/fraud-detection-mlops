# syntax=docker/dockerfile:1.7
# Multi-stage build: one image, three roles (generate | train | serve).
FROM python:3.11-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
ENV PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 VIRTUAL_ENV=/opt/venv PATH="/opt/venv/bin:$PATH"
RUN python -m venv "$VIRTUAL_ENV"
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

FROM python:3.11-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 curl \
    && rm -rf /var/lib/apt/lists/*
ENV VIRTUAL_ENV=/opt/venv PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src FD_CONFIG=/app/configs/config.yaml FD_MODEL_PATH=/app/models/fraud_model.joblib FD_PORT=8000
COPY --from=builder /opt/venv /opt/venv
RUN useradd --create-home --uid 10001 appuser && mkdir -p /app/models /app/data && chown -R appuser:appuser /app
WORKDIR /app
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser configs/ ./configs/
COPY --chown=appuser:appuser docker/entrypoint.sh ./docker/entrypoint.sh
COPY --chown=appuser:appuser pyproject.toml README.md ./
RUN sed -i 's/\r$//' ./docker/entrypoint.sh && chmod +x ./docker/entrypoint.sh
USER appuser
# Train at build time so the artifact is baked into the image (fast cold start).
RUN python -m fraud_detection.train
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS "http://localhost:${FD_PORT}/health" || exit 1
ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["serve"]
