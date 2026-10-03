"""Carga e limpeza dos dados brutos.  ✏️ ADAPTE ao seu dataset."""

from pathlib import Path

import pandas as pd


def load_raw(path: Path) -> pd.DataFrame:
    """Lê os dados brutos. Troque por parquet, SQL, API... conforme a fonte."""
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Limpeza usada no TREINO e na INFERÊNCIA — não pode depender da coluna target."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df.drop_duplicates()
