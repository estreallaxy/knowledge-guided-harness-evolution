"""第一层 WASM 生成链使用的 OpenRouter 模型预设（交互菜单与烟测共用）。"""

from __future__ import annotations

# OpenRouter model id → 同 id（便于日后别名）
GENERATOR_MODEL_PRESETS: dict[str, str] = {
    "openai/gpt-5.1": "openai/gpt-5.1",
    "google/gemini-3-flash-preview": "google/gemini-3-flash-preview",
    "qwen/qwen3-max": "qwen/qwen3-max",
    "qwen/qwen3-coder-flash": "qwen/qwen3-coder-flash",
}

# 交互菜单与 test_models_chat 顺序
GENERATOR_MODEL_MENU_ORDER: tuple[str, ...] = (
    "openai/gpt-5.1",
    "google/gemini-3-flash-preview",
    "qwen/qwen3-max",
    "qwen/qwen3-coder-flash",
)
