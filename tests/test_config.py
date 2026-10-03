from ds_project.config import CONFIG


def test_config_defaults():
    assert CONFIG.target == "target"
    assert 0 < CONFIG.test_size < 1
