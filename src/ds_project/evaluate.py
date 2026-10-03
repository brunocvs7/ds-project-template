"""Métricas de avaliação.  ✏️ ADAPTE às métricas do seu problema."""

from sklearn.metrics import accuracy_score, f1_score, roc_auc_score


def compute_metrics(y_true, y_pred, y_score) -> dict[str, float]:
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "f1": round(float(f1_score(y_true, y_pred)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_score)), 4),
    }
