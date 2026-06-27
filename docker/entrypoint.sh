#!/usr/bin/env bash
set -euo pipefail
CMD="${1:-serve}"
shift || true
case "$CMD" in
  generate) exec python -m fraud_detection.data.generate "$@" ;;
  train) exec python -m fraud_detection.train "$@" ;;
  serve) exec uvicorn fraud_detection.api.main:app --host "${FD_HOST:-0.0.0.0}" --port "${FD_PORT:-8000}" "$@" ;;
  *) exec "$CMD" "$@" ;;
esac
