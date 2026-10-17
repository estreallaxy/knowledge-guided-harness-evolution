#!/usr/bin/env python3
"""
验证 ``SessionManager.call_tool('local_apis', …)`` 与 WasmRuntime 子进程路径一致。

实现见 ``exp2.ToolPro.mcp_local_apis_subprocess_verification``。

用法（仓库根）：
  python scripts/verify_local_apis_mcp_call_tool.py
  python scripts/verify_local_apis_mcp_call_tool.py --strict
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from exp2.ToolPro.mcp_local_apis_subprocess_verification import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
