from pathlib import Path

import pandas as pd
import pytest

SAMPLE = Path(__file__).parent / "fixtures" / "sample_raw.csv"


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """Amostra pequena e versionada dos dados brutos (também usada pelo ds-check)."""
    return pd.read_csv(SAMPLE)
