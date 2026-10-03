"""Funções de feature engineering."""


def normalize(values: list[float]) -> list[float]:
    """Escala min-max para o intervalo [0, 1]."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]
