"""Pipeline de inferência: dados novos → predições, com a MESMA limpeza e features do treino.

uv run python -m ds_project.pipelines.predict [caminho/do/arquivo.csv]
"""

import sys
from pathlib import Path

import joblib
import pandas as pd

from ds_project import paths
from ds_project.config import CONFIG
from ds_project.data import clean, load_raw
from ds_project.features import build_features


def run(input_file: Path = paths.RAW_FILE) -> pd.DataFrame:
    model = joblib.load(paths.MODEL_FILE)
    df = clean(load_raw(input_file)).drop(columns=[CONFIG.target], errors="ignore")
    X = build_features(df)

    out = df.copy()
    out["prediction"] = model.predict(X)
    out["score"] = model.predict_proba(X)[:, 1]

    paths.PREDICTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(paths.PREDICTIONS_FILE, index=False)
    return out


if __name__ == "__main__":
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else paths.RAW_FILE
    result = run(source)
    print(f"{len(result)} predições salvas em {paths.PREDICTIONS_FILE}")
