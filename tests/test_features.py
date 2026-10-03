import pandas as pd

from ds_project.features import build_features


def test_build_features():
    df = pd.DataFrame({"age": [20, 0], "income": [4000.0, 1000.0], "tenure_months": [2, 12]})
    out = build_features(df)
    assert out["income_per_age"].tolist() == [200.0, 1000.0]
    assert out["is_new_customer"].tolist() == [1, 0]


def test_build_features_does_not_mutate_input():
    df = pd.DataFrame({"age": [20], "income": [4000.0], "tenure_months": [2]})
    build_features(df)
    assert list(df.columns) == ["age", "income", "tenure_months"]
