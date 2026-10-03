from ds_project.evaluate import compute_metrics


def test_perfect_predictions():
    metrics = compute_metrics([0, 1, 1], [0, 1, 1], [0.1, 0.9, 0.8])
    assert metrics == {"accuracy": 1.0, "f1": 1.0, "roc_auc": 1.0}
