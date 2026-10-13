"""Validated experiment settings; credentials never belong in configuration files."""

from dataclasses import asdict, dataclass, fields, replace
import json
from pathlib import Path

from .openrouter import ModelConfig
from .prompts import agent_name
from .types import DiscussionConfig


@dataclass(frozen=True)
class RunConfig:
    discussion: DiscussionConfig
    model: ModelConfig | None
    agent_models: dict[str, ModelConfig]
    secretary_model: ModelConfig | None


def _object(value, allowed, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    unknown = set(value) - set(allowed)
    if unknown:
        raise ValueError(f"Unknown {label} fields: {', '.join(sorted(unknown))}")
    return value


def _profile(value, base=None):
    values = asdict(base) if base is not None else {}
    values.update(_object(value, (f.name for f in fields(ModelConfig)), "model"))
    if "model" not in values:
        raise ValueError("model configuration requires a model identifier")
    return ModelConfig(**values)


def load_config(path: Path | None = None, *, model: str | None = None,
                discussion_overrides: dict | None = None) -> RunConfig:
    raw = json.loads(Path(path).read_text(encoding="utf-8")) if path else {}
    _object(raw, ("discussion", "model", "agent_models", "secretary_model"), "configuration")
    discussion = dict(_object(raw.get("discussion", {}),
                              (f.name for f in fields(DiscussionConfig)), "discussion"))
    discussion.update(discussion_overrides or {})
    settings = DiscussionConfig(**discussion)
    default = dict(_object(raw.get("model", {}), (f.name for f in fields(ModelConfig)), "model"))
    if model is not None:
        default["model"] = model
    default_model = _profile(default) if default or "model" in raw else None
    allowed_agents = {agent_name(i) for i in range(settings.agents)}
    overrides = _object(raw.get("agent_models", {}), allowed_agents, "agent_models")
    if default_model is None and (overrides or "secretary_model" in raw):
        raise ValueError("agent_models and secretary_model require a default model")
    profiles = {agent: _profile(profile, default_model) for agent, profile in overrides.items()}
    secretary = (_profile(raw["secretary_model"], default_model)
                 if "secretary_model" in raw else default_model)
    return RunConfig(settings, default_model, profiles, secretary)


def load_suite(path: Path) -> dict[str, RunConfig]:
    """Compare each model alone, homogeneous CMD, and a balanced mixed CMD."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    _object(raw, ("discussion", "models", "secretary"), "suite")
    settings = DiscussionConfig(**_object(raw.get("discussion", {}),
        (f.name for f in fields(DiscussionConfig)), "discussion"))
    profiles = raw.get("models")
    if not isinstance(profiles, list) or len(profiles) < 2:
        raise ValueError("suite requires at least two model profiles")
    profiles = [_profile(profile) for profile in profiles]
    if len({p.model for p in profiles}) != len(profiles):
        raise ValueError("suite model identifiers must be distinct")
    if settings.group_size % len(profiles):
        raise ValueError("suite group_size must be divisible by the number of models")
    secretary = raw.get("secretary", 0)
    if type(secretary) is not int or not 0 <= secretary < len(profiles):
        raise ValueError("secretary must be an index into models")
    experiments = {}
    for i, profile in enumerate(profiles, 1):
        single = replace(settings, agents=1, group_size=1, rounds=1)
        experiments[f"single-{i}"] = RunConfig(single, profile, {}, profile)
        experiments[f"cmd-{i}"] = RunConfig(settings, profile, {}, profile)
    routes = {agent_name(i): profiles[i % len(profiles)] for i in range(settings.agents)}
    experiments["cmd-mixed"] = RunConfig(settings, profiles[0], routes, profiles[secretary])
    return experiments
