import importlib

from ds_project import paths


def test_defaults_inside_project():
    assert paths.RAW_DIR == paths.ROOT / "data" / "raw"
    assert paths.MODEL_FILE.parent == paths.MODELS_DIR


def test_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("MODELS_DIR", str(tmp_path))
    reloaded = importlib.reload(paths)
    assert tmp_path / "model.joblib" == reloaded.MODEL_FILE
    monkeypatch.delenv("MODELS_DIR")
    importlib.reload(paths)
