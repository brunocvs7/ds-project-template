import pandas as pd

from ds_project.data import clean, load_raw
from tests.conftest import SAMPLE


def test_load_raw():
    assert len(load_raw(SAMPLE)) > 0


def test_clean_normalizes_columns_and_drops_duplicates():
    df = pd.DataFrame({" Age ": [1, 1], "Plan": ["a", "a"]})
    assert list(clean(df).columns) == ["age", "plan"]
    assert len(clean(df)) == 1


def test_clean_works_without_target(raw_df):
    assert "target" not in clean(raw_df.drop(columns=["target"])).columns
