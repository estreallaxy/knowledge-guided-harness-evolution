"""
对 ToolPro 实验涉及的 OpenRouter 模型做一次最小对话烟测。

烟测模型与 wasm_compilers.model_presets.GENERATOR_MODEL_MENU_ORDER 一致。

在仓库根目录执行：
    python -m exp2.ToolPro.test_tools.test_models_chat
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    p = REPO_ROOT / ".env"
    if p.is_file():
        # 默认 load_dotenv 不覆盖已有环境变量；本机若曾 export 过旧 key，会盖过 .env 修改
        load_dotenv(p, override=True)


def _label_for_model(mid: str) -> str:
    if mid.startswith("google/"):
        return f"Gemini ({mid})"
    if mid.startswith("openai/"):
        return f"OpenAI ({mid})"
    if mid.startswith("qwen/"):
        return f"Qwen ({mid})"
    return mid


def _collect_models_to_test() -> list[tuple[str, str]]:
    """(展示用标签, OpenRouter model id)"""
    from exp2.ToolPro.wasm_compilers.model_presets import GENERATOR_MODEL_MENU_ORDER

    _load_dotenv()
    out: list[tuple[str, str]] = []
    for m in GENERATOR_MODEL_MENU_ORDER:
        mid = m.strip()
        if not mid:
            continue
        out.append((_label_for_model(mid), mid))
    return out


def main() -> int:
    _load_dotenv()
    api_key = (os.getenv("OPENROUTER_API_KEY") or "").strip().strip('"')
    base_url = (
        os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"
    ).strip().strip('"').rstrip("/")

    if not api_key:
        print("错误: 未设置 OPENROUTER_API_KEY（请在仓库根目录 .env 中配置）", file=sys.stderr)
        return 1

    print(f"OPENROUTER_API_KEY (repo .env 优先)={api_key}")

    models = _collect_models_to_test()
    if not models:
        print("错误: 没有可测模型。请检查 model_presets.GENERATOR_MODEL_MENU_ORDER。", file=sys.stderr)
        return 1

    from exp2.ToolPro.llm_client import chat_completion

    user_msg = (
        "请用一句话回答：数字 42 加 1 等于多少？只输出阿拉伯数字，不要其它文字。"
    )
    print(f"base_url={base_url}")
    print(f"待测模型数: {len(models)}\n")

    ok_count = 0
    for label, model_id in models:
        print(f"── {label}")
        print(f"   model={model_id}")
        try:
            reply = chat_completion(
                [{"role": "user", "content": user_msg}],
                api_key=api_key,
                model=model_id,
                base_url=base_url,
                temperature=0.0,
                max_tokens=64,
                timeout=120.0,
            )
            preview = (reply or "").replace("\n", " ").strip()
            if len(preview) > 120:
                preview = preview[:120] + "…"
            print(f"   [OK] 回复摘录: {preview}")
            ok_count += 1
        except httpx.HTTPStatusError as e:
            body = ""
            try:
                body = (e.response.text or "")[:400]
            except Exception:
                pass
            print(f"   [FAIL] HTTP {e.response.status_code}: {body or e!s}")
        except Exception as e:
            print(f"   [FAIL] {type(e).__name__}: {e}")

    print(f"\n通过: {ok_count} / {len(models)}")
    return 0 if ok_count == len(models) else 2


if __name__ == "__main__":
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    raise SystemExit(main())
