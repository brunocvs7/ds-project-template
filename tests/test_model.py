from ds_project.data import clean
from ds_project.features import build_features
from ds_project.model import build_model


def test_model_fits_and_predicts_probabilities(raw_df):
    df = clean(raw_df)
    X, y = build_features(df.drop(columns=["target"])), df["target"]
    proba = build_model(seed=0).fit(X, y).predict_proba(X)
    assert proba.shape == (len(df), 2)


def test_model_handles_unknown_category(raw_df):
    df = clean(raw_df)
    X, y = build_features(df.drop(columns=["target"])), df["target"]
    model = build_model(seed=0).fit(X, y)
    X.loc[X.index[0], "plan"] = "plano-novo"
    assert len(model.predict(X)) == len(X)
