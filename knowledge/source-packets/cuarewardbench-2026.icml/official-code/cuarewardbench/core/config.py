from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import model_config as _model_config

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROMPT_DIR = REPO_ROOT / "configs" / "prompts"
DEFAULT_ANNOTATION_FILE = REPO_ROOT / "data" / "annotations" / "cuarewardbench-v0.4.json"
DEFAULT_TRAJECTORY_ROOT = REPO_ROOT / "data" / "trajectories" / "osworld_verified"
SUPPORTED_EVAL_MODES = [
    "zerogui",
    "sewsm_thinking",
    "opencua_reflect_thinking",
]


def _discover_model_configs() -> Dict[str, Dict[str, Any]]:
    configs: Dict[str, Dict[str, Any]] = {}
    for name in dir(_model_config):
        value = getattr(_model_config, name)
        if name.endswith("_config") and isinstance(value, dict):
            configs[name] = copy.deepcopy(value)
            configs[name.removesuffix("_config")] = copy.deepcopy(value)
    return configs


MODEL_CONFIGS = _discover_model_configs()

VOTE_CONFIGS: Dict[str, List[str]] = {
    "upe_orm_2_qwen3": [
        "results/detailed_results_evalmode_sewsm_thinking_cuarewardbench-v0.4_Qwen3-VL-32B-Thinking_run1.json",
        "results/detailed_results_evalmode_zerogui_cuarewardbench-v0.4_Qwen3-VL-235B-A22B-Thinking-FP8_run1.json",
    ],
    "upe_orm_3_qwen3": [
        "results/detailed_results_evalmode_sewsm_thinking_cuarewardbench-v0.4_Qwen3-VL-32B-Thinking_run1.json",
        "results/detailed_results_evalmode_zerogui_cuarewardbench-v0.4_Qwen3-VL-32B-Thinking_run1.json",
        "results/detailed_results_evalmode_zerogui_cuarewardbench-v0.4_Qwen3-VL-235B-A22B-Thinking-FP8_run1.json",
    ],
    "upe_prm_2_qwen3": [
        "results/detailed_results_evalmode_sewsm_thinking_cuarewardbench-v0.4_Qwen3-VL-32B-Thinking_run1.json",
        "results/detailed_results_evalmode_opencua_reflect_thinking_cuarewardbench-v0.4_Qwen3-VL-235B-A22B-Thinking_run1.json",
    ],
    "upe_orm_2_kimi_qwen35": [
        "results/crm_results/detailed_results_evalmode_sewsm_thinking_cuarewardbench-v0.4_Kimi-K2.5.json",
        "results/crm_results/detailed_results_evalmode_sewsm_thinking_cuarewardbench-v0.4_Qwen3.5-397B-A17B-FP8_maxS34.json",
    ],
}
VOTE_CONFIGS["majority_orm_2_qwen3"] = VOTE_CONFIGS["upe_orm_2_qwen3"]
VOTE_CONFIGS["majority_orm_3_qwen3"] = VOTE_CONFIGS["upe_orm_3_qwen3"]


def available_eval_modes() -> List[str]:
    return list(SUPPORTED_EVAL_MODES)


def validate_eval_mode(name: str) -> str:
    if name not in SUPPORTED_EVAL_MODES:
        available = ", ".join(SUPPORTED_EVAL_MODES)
        raise ValueError(f"Unsupported eval_mode: {name}. Available modes: {available}")
    return name


def available_model_configs() -> List[str]:
    return sorted(MODEL_CONFIGS)


def get_model_config(name: str) -> Dict[str, Any]:
    if name not in MODEL_CONFIGS:
        available = ", ".join(available_model_configs())
        raise ValueError(f"Unknown model config: {name}. Available configs: {available}")
    return copy.deepcopy(MODEL_CONFIGS[name])


def get_vote_config(name: str) -> List[str]:
    if name not in VOTE_CONFIGS:
        available = ", ".join(sorted(VOTE_CONFIGS))
        raise ValueError(f"Unknown vote config: {name}. Available configs: {available}")
    return list(VOTE_CONFIGS[name])


def apply_model_overrides(config: Dict[str, Any], base_url: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
    updated = copy.deepcopy(config)
    if base_url:
        updated["base_url"] = base_url
        print("[Override] base_url = <set>")
    if api_key:
        updated["api_key"] = api_key
        print("[Override] api_key = <set>")
    return updated


def env_or_default(env_name: str, default: str) -> str:
    return os.environ.get(env_name, default)
