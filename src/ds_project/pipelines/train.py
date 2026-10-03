"""Pipeline de treino: dados brutos → modelo salvo + métricas.

uv run python -m ds_project.pipelines.train
"""

import json
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split

from ds_project import paths
from ds_project.config import CONFIG
from ds_project.data import clean, load_raw
from ds_project.evaluate import compute_metrics
from ds_project.features import build_features
from ds_project.model import build_model


def run(raw_file: Path = paths.RAW_FILE) -> dict[str, float]:
    df = clean(load_raw(raw_file)).dropna(subset=[CONFIG.target])
    X = build_features(df.drop(columns=[CONFIG.target]))
    y = df[CONFIG.target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=CONFIG.test_size, random_state=CONFIG.seed, stratify=y
    )
    model = build_model(CONFIG.seed).fit(X_train, y_train)
    metrics = compute_metrics(y_test, model.predict(X_test), model.predict_proba(X_test)[:, 1])

    paths.MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    paths.METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, paths.MODEL_FILE)
    paths.METRICS_FILE.write_text(json.dumps(metrics, indent=2) + "\n")
    return metrics


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
    print(f"Modelo salvo em {paths.MODEL_FILE}")
