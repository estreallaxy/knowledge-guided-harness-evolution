"""
验证 ``SessionManager.call_tool("local_apis", …)`` 子进程路径：与 ``WasmRuntime._perform_actual_mcp_call`` 一致。

流程：
1. 读取 ``experiment/mcp-client/client_config.toml``，启动 ``local_apis`` MCP 子进程；
2. 列出子进程 ``list_tools`` 得到的工具名；
3. 与 ToolPro / ``TOOL_LIST_DOC`` 期望的工具名集合做差集，打印 **缺失** 与 **已注册且将试调用** 的列表；
4. 对当前 ``experiment/mcp-server`` 里**确实存在**的工具发起真实 ``call_tool``（如 ``get_traffic_stats``、``minio_upload_object`` 等）。

说明：仓库默认 ``mcp-server/server.py`` **未注册** ``get_items`` / ``patch_item`` / ``post_items`` 等 Directus Items 名；
本脚本用于**显式证明**子进程链路与 ToolPro 文档是否对齐；不对齐时缺工具列表非零，但不改退出码（可用 ``--strict`` 使缺工具时返回非 0）。

运行（仓库根）：
  python -m exp2.ToolPro.mcp_local_apis_subprocess_verification
  python scripts/verify_local_apis_mcp_call_tool.py
  python -m exp2.ToolPro.mcp_local_apis_subprocess_verification --strict
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MCP_CLIENT = _REPO_ROOT / "experiment" / "mcp-client"
_CONFIG = _MCP_CLIENT / "client_config.toml"

# 与 exp2/baseline/directus_tools.TOOL_LIST_DOC 中「工具名：」行对齐（ToolPro 生成侧假定可调）
_TOOLPRO_DOC_TOOL_NAMES: Tuple[str, ...] = (
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
)


def _ensure_mcp_client_path() -> None:
    p = str(_MCP_CLIENT)
    if p not in sys.path:
        sys.path.insert(0, p)


async def _async_main(*, strict: bool) -> int:
    if not _CONFIG.is_file():
        print(f"[FAIL] 缺少 MCP 配置: {_CONFIG}", file=sys.stderr)
        return 2

    _ensure_mcp_client_path()
    from session_manager import SessionManager  # noqa: WPS433

    sm = SessionManager(str(_CONFIG))
    try:
        if not await sm.start_all_servers():
            print("[FAIL] start_all_servers 未启动任何服务", file=sys.stderr)
            return 3
        if not await sm.initialize_connections():
            print("[FAIL] initialize_connections 失败", file=sys.stderr)
            return 4

        tools = sm.get_tools("local_apis") or []
        registered: Set[str] = {str(t.get("name", "")) for t in tools if t.get("name")}
        expected = set(_TOOLPRO_DOC_TOOL_NAMES)

        print("=== local_apis 已注册工具名（子进程 list_tools）===")
        for n in sorted(registered):
            print(f"  - {n}")

        missing = sorted(expected - registered)
        overlap = sorted(expected & registered)

        print("\n=== 与 ToolPro TOOL_LIST_DOC 对比 ===")
        if missing:
            print(f"[GAP] 文档期望但子进程未注册（{len(missing)}）:")
            for m in missing:
                print(f"  - {m}")
        else:
            print("[OK] 文档中的工具名在子进程均已注册。")

        if overlap:
            print(f"\n[INFO] 子进程与文档同名工具（{len(overlap)}），将尝试 call_tool：")
            for o in overlap:
                print(f"  - {o}")

        print("\n=== 真实 call_tool 探测 ===")
        # 1) 流量统计：默认 server 必有
        r0 = await sm.call_tool("local_apis", "get_traffic_stats", {})
        if not isinstance(r0, dict):
            print(f"[FAIL] get_traffic_stats 返回非 dict: {r0!r}")
            return 5
        print(f"[OK] get_traffic_stats -> keys={list(r0.keys())[:8]}...")

        # 2) minio_upload_object：若存在则写短文本再删（与 Directus 无关，仅验证子进程→MinIO）
        if "minio_upload_object" in registered:
            key = "toolpro_local_apis_verify/subprocess_probe.txt"
            r1 = await sm.call_tool(
                "local_apis",
                "minio_upload_object",
                {"object_name": key, "content": "subprocess-mcp-probe"},
            )
            print(f"[INFO] minio_upload_object 原始返回片段: {json.dumps(r1, ensure_ascii=False)[:500]}")
            if isinstance(r1, dict) and r1.get("success") is False:
                print(f"[WARN] minio_upload_object 业务失败: {r1.get('error', r1)}")
            elif "minio_get_object" in registered:
                r2 = await sm.call_tool("local_apis", "minio_get_object", {"object_name": key})
                print(f"[INFO] minio_get_object 返回 success={r2.get('success') if isinstance(r2, dict) else r2}")
            # 尽力清理
            if "minio_delete_object" in registered:
                await sm.call_tool("local_apis", "minio_delete_object", {"object_name": key})
                print("[OK] minio_delete_object 已请求清理 probe 对象")
            else:
                print(
                    f"[WARN] 子进程未注册 minio_delete_object，probe 对象可能残留: {key}",
                    file=sys.stderr,
                )

        # 3) get_items：若不存在，SessionManager 会直接返回错误 dict（不启动未知工具）
        if "get_items" not in registered:
            r3 = await sm.call_tool(
                "local_apis",
                "get_items",
                {"collection": "customers", "query": {"limit": 1}},
            )
            print(f"[EXPECTED] get_items 未注册时 call_tool 返回: {r3}")

        if strict and missing:
            print(f"\n[FAIL] --strict：存在 {len(missing)} 个缺工具，见上表 GAP。", file=sys.stderr)
            return 6

        print("\n[DONE] 子进程 MCP 链路探测结束（未改 Directus 数据）。")
        return 0
    finally:
        await sm.shutdown()


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="验证 local_apis MCP 子进程 call_tool 链路")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="若 TOOL_LIST_DOC 中有任一工具名未在子进程注册，则退出码 6",
    )
    args = ap.parse_args(argv)
    return asyncio.run(_async_main(strict=args.strict))


if __name__ == "__main__":
    raise SystemExit(main())
