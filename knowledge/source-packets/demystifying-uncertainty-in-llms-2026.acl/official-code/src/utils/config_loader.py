from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import yaml


@dataclass
class LLMConfig:

    model_path: str

    num_gpus: int = None
    tensor_parallel_size: int = None

    dtype: str = "float16"
    max_model_len: int = None
    gpu_memory_utilization: float = None
    trust_remote_code: bool = True

    verbose: bool = True


def load_llm_config(config_path: str) -> LLMConfig:
    """
    Load LLMConfig from a YAML configuration file.
    Expected YAML structure:
      model: { path, dtype, max_model_len, trust_remote_code }
      resource: { num_gpus, tensor_parallel_size }
      runtime: { gpu_memory_utilization, verbose }
    """
    with open(config_path, "r", encoding="utf-8") as f:
        raw: Dict[str, Any] = yaml.safe_load(f)

    model_cfg = raw.get("model", {})
    res_cfg = raw.get("resource", {})
    run_cfg = raw.get("runtime", {})

    cfg = LLMConfig(
        model_path=model_cfg.get("path", ""),
        dtype=model_cfg.get("dtype", "float16"),
        max_model_len=int(model_cfg.get("max_model_len", 4096)),
        trust_remote_code=bool(model_cfg.get("trust_remote_code", True)),

        num_gpus=int(res_cfg.get("num_gpus", 1)),
        tensor_parallel_size=int(res_cfg.get("tensor_parallel_size", 1)),

        gpu_memory_utilization=float(run_cfg.get("gpu_memory_utilization", 0.9)),
        verbose=bool(run_cfg.get("verbose", True)),
    )

    if not cfg.model_path:
        raise ValueError(
            "PolicyLLMConfig: model_path is empty. Please set model.path in the YAML config file."
        )

    if cfg.tensor_parallel_size > cfg.num_gpus:
        raise ValueError(
            f"Invalid config: tensor_parallel_size={cfg.tensor_parallel_size} "
            f"cannot be greater than num_gpus={cfg.num_gpus}."
        )

    return cfg