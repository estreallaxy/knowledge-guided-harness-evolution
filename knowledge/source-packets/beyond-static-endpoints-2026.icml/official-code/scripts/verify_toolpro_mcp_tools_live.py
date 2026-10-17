#!/usr/bin/env python3
"""
入口脚本：验证 ToolPro 文档中的 MCP 工具（get_items / patch_item / post_items 等）是否可对真实服务发起请求。

实现见 ``exp2.ToolPro.mcp_tools_live_verification``；测试前后会执行 ``initialize_directus_in_process()`` 恢复 Directus 三表数据。

用法（仓库根）：
  python scripts/verify_toolpro_mcp_tools_live.py
  python scripts/verify_toolpro_mcp_tools_live.py --no-optional
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from exp2.ToolPro.mcp_tools_live_verification import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
