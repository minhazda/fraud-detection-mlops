"""Typed, YAML-driven configuration with environment overrides for paths."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Settings:
    seed: int = 7
    n_samples: int = 50_000
    test_size: float = 0.4
    model_path: str = "models/fraud_model.joblib"


def load(path: str | Path | None = None) -> Settings:
    """Load settings from YAML (FD_CONFIG), with FD_MODEL_PATH override."""
    if path is None:
        path = os.environ.get("FD_CONFIG", "configs/config.yaml")
    cfg_path = Path(path)
    data: dict[str, Any] = {}
    if cfg_path.is_file():
        data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    model_path = os.environ.get(
        "FD_MODEL_PATH", str(data.get("model_path", "models/fraud_model.joblib"))
    )
    return Settings(
        seed=int(data.get("seed", 7)),
        n_samples=int(data.get("n_samples", 50_000)),
        test_size=float(data.get("test_size", 0.4)),
        model_path=model_path,
    )
