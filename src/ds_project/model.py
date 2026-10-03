"""Definição do modelo.  ✏️ ADAPTE (algoritmo, pré-processamento, hiperparâmetros)."""

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC = ["age", "income", "tenure_months", "income_per_age", "is_new_customer"]
CATEGORICAL = ["plan"]


def build_model(seed: int) -> Pipeline:
    preprocess = ColumnTransformer(
        [
            ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ]
    )
    return Pipeline(
        [
            ("preprocess", preprocess),
            ("clf", RandomForestClassifier(n_estimators=100, random_state=seed)),
        ]
    )
