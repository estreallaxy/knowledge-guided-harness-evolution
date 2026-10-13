import json

import pytest

from llm_discussion.config import load_config


def write_config(tmp_path, value):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(value))
    return path


def test_model_profiles_inherit_defaults_and_cli_overrides(tmp_path):
    path = write_config(tmp_path, {
        "model": {"model": "vendor/default", "temperature": 0.4, "timeout": 15, "seed": 42},
        "agent_models": {"B": {"model": "vendor/alternate", "temperature": None}},
        "secretary_model": {"model": "vendor/secretary"},
        "discussion": {"concurrency": 2},
    })
    config = load_config(path, model="vendor/new", discussion_overrides={"rounds": 2})
    assert config.model.model == "vendor/new"
    assert config.agent_models["B"].timeout == 15
    assert config.agent_models["B"].seed == 42
    assert config.agent_models["B"].temperature is None
    assert config.secretary_model.temperature == 0.4
    assert config.discussion.rounds == config.discussion.concurrency == 2


@pytest.mark.parametrize("value", [
    {"api_key": "fixture-secret"},
    {"model": {"model": "vendor/default", "api_key": "fixture-secret"}},
    {"model": {"model": "vendor/default"}, "agent_models": {"G": {"model": "vendor/other"}}},
    {"model": {"model": "vendor/default"}, "agent_models": {"nobody": {}}},
    {"discussion": {"round": 3}},
    {"discussion": {"agents": 5}},
    {"agent_models": {"B": {"model": "vendor/other"}}},
    {"secretary_model": {"model": "vendor/other"}},
    {"model": {}},
    {"model": {"model": "vendor/default", "temperature": True}},
    [],
])
def test_invalid_config_rejected_without_printing_secret(tmp_path, value):
    with pytest.raises(ValueError) as error:
        load_config(write_config(tmp_path, value))
    assert "fixture-secret" not in str(error.value)


def test_default_config_is_offline():
    config = load_config()
    assert config.model is None
    assert config.secretary_model is None
    assert config.discussion.agents == 6
