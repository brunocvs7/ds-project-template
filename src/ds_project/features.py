"""Feature engineering sem estado (linha a linha).  ✏️ ADAPTE ao seu problema.

Transformações que APRENDEM com os dados (scaler, encoder, imputer) não ficam aqui:
vão no `model.py`, dentro do Pipeline do sklearn, para não vazar informação do teste.
"""

import pandas as pd


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["income_per_age"] = df["income"] / df["age"].clip(lower=1)
    df["is_new_customer"] = (df["tenure_months"] < 6).astype(int)
    return df
