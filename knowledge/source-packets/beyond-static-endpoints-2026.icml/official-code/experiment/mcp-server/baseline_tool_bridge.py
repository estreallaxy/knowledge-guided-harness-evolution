"""
将 ToolPro / exp2 Baseline 的 ``DirectusToolRunner`` 接到 MCP 子进程。

``run_server.py`` 的 cwd 在 ``experiment/mcp-server``，须把仓库根加入 ``sys.path`` 才能 ``import exp2``。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, FrozenSet

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# 与 exp2/baseline/directus_tools.TOOL_LIST_DOC 工具名一致；由 MCP 子进程转发为真实 HTTP。
BASELINE_TOOL_NAMES: FrozenSet[str] = frozenset(
    {
        "get_items",
        "patch_item",
        "post_items",
        "prepare_bench_seed",
        "minio_upload_object",
        "minio_list_objects",
        "minio_get_object",
        "minio_copy_object",
        "minio_move_object",
        "minio_delete_object",
        "memos_create",
        "memos_list_recent",
        "memos_delete",
    }
)


def _ensure_repo_importable() -> None:
    root = str(_REPO_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def call_baseline_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """进程内调用 ``DirectusToolRunner.call``，返回已解析的 dict/list（与 WASM 宿主解析 JSON 后一致）。"""
    _ensure_repo_importable()
    from exp2.baseline.directus_tools import DirectusToolRunner

    runner = DirectusToolRunner()
    try:
        raw = runner.call(tool_name, arguments or {})
        return json.loads(raw)
    finally:
        runner.close()
