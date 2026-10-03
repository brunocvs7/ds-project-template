"""Caminhos padrão do projeto. Qualquer um pode ser sobrescrito por variável de ambiente (.env)."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _path(env_var: str, default: Path) -> Path:
    return Path(os.getenv(env_var, default))


DATA_DIR = _path("DATA_DIR", ROOT / "data")
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
PREDICTIONS_DIR = DATA_DIR / "predictions"
MODELS_DIR = _path("MODELS_DIR", ROOT / "models")
REPORTS_DIR = _path("REPORTS_DIR", ROOT / "reports")

RAW_FILE = _path("RAW_FILE", RAW_DIR / "dataset.csv")
MODEL_FILE = MODELS_DIR / "model.joblib"
METRICS_FILE = REPORTS_DIR / "metrics.json"
PREDICTIONS_FILE = PREDICTIONS_DIR / "predictions.csv"
