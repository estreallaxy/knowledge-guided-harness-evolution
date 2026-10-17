"""
ToolPro / Baseline 侧 MCP 工具「真实 HTTP」冒烟验证。

与 LLM 提示词中的 ``TOOL_LIST_DOC``（``DirectusToolRunner.call``）对齐，进程内直连 Directus / MinIO / Memos，
等价于 ToolPro 生成代码期望的 ``get_items`` / ``patch_item`` / ``post_items`` 等工具名与参数形态。

**数据安全**：``run_verification`` 与 pytest 模块均在前后调用 ``initialize_directus_in_process()``，
将 customers / orders / exchange_logs 恢复为 ``exp2/init_directus_forms.py`` 的 CSV 初始状态；
涉及 ``post_items`` 的测试写入 ``exchange_logs``，收尾初始化会清空该集合。

运行：
  python -m exp2.ToolPro.mcp_tools_live_verification
  或
  python scripts/verify_toolpro_mcp_tools_live.py

环境：Directus 可访问且与 ``exp2/baseline/directus_tools`` 中 ``DIRECTUS_*`` 一致；
      Case4 扩展工具需 MinIO/Memos 与 ``exp2/exp_case4/config`` 可用（不可用则跳过对应段）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from exp2.baseline.directus_tools import DirectusToolRunner  # noqa: E402
from exp2.baseline.initializer import InitializerError, initialize_directus_in_process  # noqa: E402


def _call(runner: DirectusToolRunner, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    raw = runner.call(tool, arguments)
    return json.loads(raw)


def _require_status(resp: Dict[str, Any], tool: str, min_status: int = 200) -> None:
    sc = resp.get("status_code")
    if sc is None and "error" in resp:
        raise AssertionError(f"{tool}: 无 status_code，响应={resp!r}")
    if not isinstance(sc, int) or sc < min_status or sc >= 300:
        raise AssertionError(f"{tool}: HTTP 状态异常 status_code={sc!r} 响应={resp!r}")


def verify_get_items_customers_mei(runner: DirectusToolRunner) -> None:
    r = _call(
        runner,
        "get_items",
        {
            "collection": "customers",
            "query": {
                "filter": {
                    "first_name": {"_eq": "Mei"},
                    "last_name": {"_eq": "Patel"},
                    "zip_code": {"_eq": "76165"},
                },
                "limit": 5,
            },
        },
    )
    _require_status(r, "get_items(customers)")
    rows = (r.get("body") or {}).get("data") or []
    if len(rows) != 1:
        raise AssertionError(f"get_items customers: 期望 1 条，实际 {len(rows)}")
    if int(rows[0].get("id", -1)) != 6:
        raise AssertionError(f"get_items customers: 期望 id=6，实际 {rows[0]!r}")


def verify_get_items_orders_pending(runner: DirectusToolRunner) -> None:
    r = _call(
        runner,
        "get_items",
        {
            "collection": "orders",
            "query": {
                "filter": {
                    "customer_id": {"_eq": 6},
                    "status": {"_eq": "pending"},
                },
                "sort": "id",
            },
        },
    )
    _require_status(r, "get_items(orders)")
    rows = (r.get("body") or {}).get("data") or []
    if not rows:
        raise AssertionError("get_items orders pending: 无数据（请先跑 init_directus_forms）")
    first = rows[0]
    if first.get("order_number") != "#W4082615":
        raise AssertionError(f"get_items orders: 首条期望 #W4082615，实际 {first!r}")


def verify_patch_item_order1(runner: DirectusToolRunner) -> None:
    """将 orders/1 的 total 改为临时值并读回验证；收尾由全局 init 恢复。"""
    probe = _call(
        runner,
        "get_items",
        {
            "collection": "orders",
            "query": {"filter": {"id": {"_eq": 1}}, "limit": 1},
        },
    )
    _require_status(probe, "get_items(pre-patch)")
    row0 = ((probe.get("body") or {}).get("data") or [None])[0]
    if not row0:
        raise AssertionError("orders id=1 不存在")
    orig_total = float(row0.get("total", 0))
    bump = 0.01 if abs(orig_total - 49.99) > 1e-6 else 0.02
    new_total = round(orig_total + bump, 2)

    p = _call(
        runner,
        "patch_item",
        {
            "collection": "orders",
            "item_id": 1,
            "data": {"total": new_total},
        },
    )
    _require_status(p, "patch_item(orders/1)")

    again = _call(
        runner,
        "get_items",
        {
            "collection": "orders",
            "query": {"filter": {"id": {"_eq": 1}}, "limit": 1},
        },
    )
    _require_status(again, "get_items(post-patch)")
    got = float(((again.get("body") or {}).get("data") or [{}])[0].get("total"))
    if abs(got - new_total) > 1e-6:
        raise AssertionError(f"patch_item 未落库: 期望 total={new_total} 实际 {got}")


def verify_post_items_exchange_logs(runner: DirectusToolRunner) -> None:
    """插入一条交换日志，再 get_items 确认；init 收尾会清空。"""
    marker = "#TOOLPRO_MCP_VERIFY"
    r = _call(
        runner,
        "post_items",
        {
            "collection": "exchange_logs",
            "records": [
                {
                    "order_number": marker,
                    "old_items": ["sku_old_verify"],
                    "new_items": ["sku_new_verify"],
                }
            ],
        },
    )
    _require_status(r, "post_items(exchange_logs)")
    g = _call(
        runner,
        "get_items",
        {
            "collection": "exchange_logs",
            "query": {"filter": {"order_number": {"_eq": marker}}, "limit": 10},
        },
    )
    _require_status(g, "get_items(exchange_logs)")
    rows = (g.get("body") or {}).get("data") or []
    if not rows:
        raise AssertionError("post_items 后未查到 exchange_logs 记录")


def _try_optional(
    label: str,
    fn: Callable[[DirectusToolRunner], None],
    runner: DirectusToolRunner,
    log: List[str],
) -> None:
    try:
        fn(runner)
        log.append(f"[OK] {label}")
    except Exception as e:
        log.append(f"[SKIP] {label}: {e}")


def verify_prepare_bench_seed(runner: DirectusToolRunner) -> None:
    r = _call(runner, "prepare_bench_seed", {})
    _require_status(r, "prepare_bench_seed")
    files = ((r.get("body") or {}).get("files")) or []
    if not files:
        raise AssertionError("prepare_bench_seed 未返回 files")


def verify_minio_roundtrip(runner: DirectusToolRunner) -> None:
    key = "toolpro_mcp_verify/hello.txt"
    _call(runner, "minio_upload_object", {"object_name": key, "content": "toolpro-mcp-verify"})
    lst = _call(runner, "minio_list_objects", {"prefix": "toolpro_mcp_verify/"})
    _require_status(lst, "minio_list_objects")
    got = _call(runner, "minio_get_object", {"object_name": key})
    _require_status(got, "minio_get_object")
    txt = ((got.get("body") or {}).get("content")) or ""
    if "toolpro-mcp-verify" not in txt:
        raise AssertionError(f"minio_get_object 内容异常: {got!r}")
    cp = _call(
        runner,
        "minio_copy_object",
        {"source_key": key, "target_key": "toolpro_mcp_verify/hello_copy.txt"},
    )
    _require_status(cp, "minio_copy_object")
    mv = _call(
        runner,
        "minio_move_object",
        {
            "source_key": "toolpro_mcp_verify/hello_copy.txt",
            "target_key": "toolpro_mcp_verify/hello_moved.txt",
        },
    )
    _require_status(mv, "minio_move_object")
    _call(runner, "minio_delete_object", {"object_name": "toolpro_mcp_verify/hello_moved.txt"})
    _call(runner, "minio_delete_object", {"object_name": key})


def verify_memos_list_create_delete(runner: DirectusToolRunner) -> None:
    title = "TOOLPRO_MCP_VERIFY_DELETE_ME"
    c = _call(
        runner,
        "memos_create",
        {"title": title, "content": "verify", "visibility": "PRIVATE"},
    )
    _require_status(c, "memos_create")
    memo_name = ((c.get("body") or {}).get("memo_name")) or ""
    if not memo_name:
        raise AssertionError(f"memos_create 无 memo_name: {c!r}")
    lst = _call(runner, "memos_list_recent", {"title_contains": "TOOLPRO_MCP_VERIFY", "limit": 20})
    _require_status(lst, "memos_list_recent")
    d = _call(runner, "memos_delete", {"memo_name": memo_name})
    _require_status(d, "memos_delete")


def run_verification(
    *,
    include_optional: bool = True,
    verbose: bool = True,
) -> Tuple[int, List[str]]:
    """
    :return: (exit_code, log_lines)  exit_code 0 表示 Directus 段全部通过；可选段失败仅记 SKIP 不升退出码。
    """
    log: List[str] = []

    def _say(msg: str) -> None:
        log.append(msg)
        if verbose:
            print(msg, flush=True)

    _say("=== [1/3] initialize_directus_in_process（测试前）===")
    try:
        initialize_directus_in_process()
    except InitializerError as e:
        _say(f"[FAIL] Directus 初始化失败: {e}")
        return 2, log
    except Exception as e:
        _say(f"[FAIL] Directus 初始化异常: {e}")
        return 2, log

    runner = DirectusToolRunner()
    try:
        _say("=== [2/3] Directus 工具真实调用 ===")
        verify_get_items_customers_mei(runner)
        _say("[OK] get_items customers (Mei Patel zip)")
        verify_get_items_orders_pending(runner)
        _say("[OK] get_items orders (pending)")
        verify_patch_item_order1(runner)
        _say("[OK] patch_item orders/1 + get_items 读回")
        verify_post_items_exchange_logs(runner)
        _say("[OK] post_items exchange_logs + get_items 确认")

        if include_optional:
            _say("=== Case4 扩展工具（MinIO/Memos/seed），不可用则 SKIP ===")
            _try_optional("prepare_bench_seed", verify_prepare_bench_seed, runner, log)
            _try_optional("minio_*  roundtrip", verify_minio_roundtrip, runner, log)
            _try_optional("memos_*  create/list/delete", verify_memos_list_create_delete, runner, log)
    except AssertionError as e:
        _say(f"[FAIL] {e}")
        return 1, log
    except Exception as e:
        _say(f"[FAIL] 未预期异常: {e}")
        return 1, log
    finally:
        runner.close()

    _say("=== [3/3] initialize_directus_in_process（测试后，恢复数据）===")
    try:
        initialize_directus_in_process()
    except Exception as e:
        _say(f"[WARN] 测试后初始化失败（请手动恢复 Directus）: {e}")
        return 3, log

    _say("=== [DONE] MCP 工具冒烟完成，Directus 已恢复初始 CSV 状态 ===")
    return 0, log


def main(argv: Optional[List[str]] = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="验证 ToolPro MCP 工具真实 HTTP 调用")
    p.add_argument(
        "--no-optional",
        action="store_true",
        help="跳过 MinIO/Memos/prepare_bench_seed 等 Case4 扩展检查",
    )
    p.add_argument("-q", "--quiet", action="store_true", help="少打印，仅退出码")
    args = p.parse_args(argv)
    code, _ = run_verification(
        include_optional=not args.no_optional,
        verbose=not args.quiet,
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
