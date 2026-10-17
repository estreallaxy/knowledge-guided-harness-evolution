import os
from typing import Any, Dict, Optional


# Public-safe model registry.
#
# All configs keep their historical registry names so existing CLI commands remain valid,
# but credentials/endpoints are now loaded from environment variables or passed via CLI
# overrides at runtime. Nothing in this file should contain private URLs, IPs, or keys.


def _optional_env(name: str) -> Optional[str]:
    value = os.environ.get(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _openai_compatible_config(
    model: str,
    *,
    api_type: str = "3rd_openai",
    base_url_env: str = "OPENAI_BASE_URL",
    api_key_env: str = "OPENAI_API_KEY",
    base_url_default: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    config: Dict[str, Any] = {
        "api_type": api_type,
        "model": model,
    }

    base_url = _optional_env(base_url_env) or base_url_default
    api_key = _optional_env(api_key_env)

    if base_url:
        config["base_url"] = base_url
    if api_key:
        config["api_key"] = api_key

    config.update(kwargs)
    return config


claude4_5_config = _openai_compatible_config(
    "claude-sonnet-4-5-20250929",
)

qwen3vl235b_thinking_tione_config = _openai_compatible_config(
    "Qwen3-VL-235B-A22B-Thinking-FP8",
    temperature=0.6,
)

qwen3vl32b_thinking_tione_config = _openai_compatible_config(
    "Qwen3-VL-32B-Thinking",
    temperature=0.6,
    repetition_penalty=1.05,
    max_tokens=16384,
    timeout=600,
)

kimi_k25_tione_config = _openai_compatible_config(
    "Kimi-K2.5",
    temperature=0.6,
    repetition_penalty=1.05,
    max_tokens=16384,
    timeout=600,
)

qwen35_tione_config = _openai_compatible_config(
    "Qwen3.5-397B-A17B-FP8",
    temperature=0.6,
    repetition_penalty=1.05,
    max_tokens=16384,
    timeout=600,
)

glm_4_5_V_tione_config = _openai_compatible_config(
    "glm-4.5v",
)

gpt_4o_config = _openai_compatible_config(
    "gpt-4o",
)


guiowl_7b_tione_config = _openai_compatible_config(
    "GUI-Owl-7B",
)

guiowl_32b_tione_config = _openai_compatible_config(
    "GUI-Owl-32B",
)

cuawsm_7b_tione_config = _openai_compatible_config(
    "CUA_World_State_Model",
)

seagent_7b_tione_config = _openai_compatible_config(
    "SEAgent-1.0-7B",
)

step3_siliconflow_config = _openai_compatible_config(
    "stepfun-ai/step3",
    base_url_env="SILICONFLOW_BASE_URL",
    api_key_env="SILICONFLOW_API_KEY",
    base_url_default="https://api.siliconflow.cn/v1",
)

minicpm_v_4_5_config = _openai_compatible_config(
    "MiniCPM-V-4_5",
    api_type="openai",
)

glm_siliconflow_config = _openai_compatible_config(
    "Pro/THUDM/GLM-4.1V-9B-Thinking",
    api_type="3rd_openai_glm",
    base_url_env="SILICONFLOW_BASE_URL",
    api_key_env="SILICONFLOW_API_KEY",
    base_url_default="https://api.siliconflow.cn/v1",
)

qwen2p5vl_7b_tione_config = _openai_compatible_config(
    "Qwen2.5-VL-7B-Instruct",
)

qwen2p5vl_32b_tione_config = _openai_compatible_config(
    "Qwen2.5-VL-32B-Instruct",
)

qwen2p5vl_72b_tione_config = _openai_compatible_config(
    "Qwen2.5-VL-72B-Instruct",
)

qvq_72b_tione_config = _openai_compatible_config(
    "QVQ-72B-Preview",
)

siliconflow_config = _openai_compatible_config(
    "Pro/Qwen/Qwen2.5-VL-7B-Instruct",
    base_url_env="SILICONFLOW_BASE_URL",
    api_key_env="SILICONFLOW_API_KEY",
    base_url_default="https://api.siliconflow.cn/v1",
)
