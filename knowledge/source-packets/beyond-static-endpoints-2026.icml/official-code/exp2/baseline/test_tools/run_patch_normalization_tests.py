"""
测试 directus_tools 对 patch_item / post_items 的 items 类字段规范化。

前置：Directus 可访问，且与 directus_tools 中写死的 DIRECTUS_* 一致；
      会调用 initialize_directus_in_process 重置数据。

运行（仓库根）：
  python -m exp2.baseline.test_tools.run_patch_normalization_tests
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from exp2.baseline.directus_tools import (  # noqa: E402
    DirectusToolRunner,
    coerce_items_like_field,
    normalize_write_fields,
)
from exp2.baseline.initializer import (  # noqa: E402
    InitializerError,
    initialize_directus_in_process,
)
from exp2.baseline.validator import _str_list_normalized  # noqa: E402


def _assert_coerce(label: str, raw: Any, expected: List[str]) -> None:
    got = coerce_items_like_field(raw)
    if got != expected:
        raise AssertionError(f"[coerce] {label}: 期望 {expected!r} 实际 {got!r}")


def test_coerce_unit() -> None:
    _assert_coerce("list", ["1096508426"], ["1096508426"])
    _assert_coerce("json array str", '["1096508426"]', ["1096508426"])
    _assert_coerce("escaped json str", "[\"1096508426\"]", ["1096508426"])
    _assert_coerce("single sku", "1096508426", ["1096508426"])
    _assert_coerce("empty", "", [])
    _assert_coerce("none", None, [])
    n = normalize_write_fields(
        {"items": "[\"1096508426\"]", "total": "55", "shipping_address": "x"}
    )
    if n["items"] != ["1096508426"]:
        raise AssertionError(f"normalize items: {n!r}")
    if n["total"] != 55.0:
        raise AssertionError(f"normalize total: {n!r}")
    print("[OK] 单元测试 coerce_items_like_field / normalize_write_fields")


def _tool_call(runner: DirectusToolRunner, tool: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    raw = runner.call(tool, arguments)
    return json.loads(raw)


def _get_order1(runner: DirectusToolRunner) -> Dict[str, Any]:
    r = _tool_call(
        runner,
        "get_items",
        {
            "collection": "orders",
            "query": {
                "filter": {"id": {"_eq": 1}},
                "limit": 1,
            },
        },
    )
    if r.get("status_code") != 200:
        raise RuntimeError(f"GET orders 失败: {r!r}")
    body = r.get("body") or {}
    rows = body.get("data") or []
    if not rows:
        raise RuntimeError("orders id=1 不存在，请先初始化")
    return rows[0]


def _assert_order_case1(row: Dict[str, Any]) -> Tuple[str, ...]:
    """Case 1 期望：items 单元素 SKU，total 55"""
    items_t = _str_list_normalized(row.get("items"))
    total = float(row.get("total"))
    if items_t != ("1096508426",):
        raise AssertionError(f"items 期望 ('1096508426',) 实际 {items_t!r}")
    if total != 55.0:
        raise AssertionError(f"total 期望 55.0 实际 {total!r}")
    return items_t


def test_patch_formats_integration(runner: DirectusToolRunner) -> None:
    """多种 Agent 常见写法 PATCH orders/1，应均能落库为期望形态。"""
    variants = [
        ("list", {"items": ["1096508426"], "total": 55.0}),
        ("json str", {"items": '["1096508426"]', "total": 55}),
        (
            "python-escaped str",
            {"items": "[\"1096508426\"]", "total": 55},
        ),
        ("single sku str", {"items": "1096508426", "total": 55.0}),
    ]
    for label, data in variants:
        pr = _tool_call(
            runner,
            "patch_item",
            {"collection": "orders", "item_id": 1, "data": data},
        )
        if pr.get("status_code") not in (200, 204):
            raise AssertionError(f"[{label}] PATCH 状态异常: {pr!r}")
        row = _get_order1(runner)
        try:
            _assert_order_case1(row)
        except AssertionError as e:
            raise AssertionError(f"[{label}] {e}") from e
        print(f"  [OK] PATCH 形态 {label}")


def main() -> int:
    print("=== directus_tools 规范化测试 ===\n")
    test_coerce_unit()

    print("\n=== 集成测试（Directus）===")
    try:
        initialize_directus_in_process()
    except InitializerError as e:
        print(f"[SKIP] 初始化失败，跳过集成测试: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[SKIP] 初始化异常: {e}", file=sys.stderr)
        return 1

    runner = DirectusToolRunner()
    try:
        row0 = _get_order1(runner)
        init_items = _str_list_normalized(row0.get("items"))
        if init_items != ("9779102705",):
            print(
                f"  [WARN] 初始 items 非 ['9779102705'] 而是 {init_items!r}，仍继续 PATCH 测试",
                file=sys.stderr,
            )
        test_patch_formats_integration(runner)
    finally:
        runner.close()

    print("\n[OK] 全部测试通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
