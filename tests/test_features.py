from ds_project.features import normalize


def test_normalize_range():
    assert normalize([1.0, 2.0, 3.0]) == [0.0, 0.5, 1.0]


def test_normalize_constant():
    assert normalize([5.0, 5.0]) == [0.0, 0.0]


def test_normalize_empty():
    assert normalize([]) == []
