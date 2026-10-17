import json
import os
import sys
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    p = REPO_ROOT / ".env"
    if p.is_file():
        load_dotenv(p)


def main() -> int:
    _load_dotenv()
    api_key = (os.getenv("OPENROUTER_API_KEY") or "").strip().strip('"')
    if not api_key:
        print(
            "错误: 未设置 OPENROUTER_API_KEY（可在仓库根目录 .env 中配置）",
            file=sys.stderr,
        )
        return 1

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ToolPro",
            "X-OpenRouter-Title": "ToolPro",
        },
        data=json.dumps(
            {
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": "hello",
                    }
                ],
            }
        ),
        timeout=120,
    )
    print(f"HTTP {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(response.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
