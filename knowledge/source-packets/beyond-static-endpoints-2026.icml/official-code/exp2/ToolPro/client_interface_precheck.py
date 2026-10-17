"""
ToolPro 客户端 Step 1 轻检（与 Docs/toolpro_mainflow_integration_plan §3.2.9 对齐，最小可用实现）。

在 ``compile_first_layer_to_wasm`` 之前调用；失败码写入 ``client_precheck_failures``。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Sequence, Tuple


@dataclass
class PrecheckResult:
    passed: bool
    failures: List[str] = field(default_factory=list)


_MCP_TOOL_RE = re.compile(
    r'call_mcp_tool\s*\(\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def _rust_tool_calls(source: str) -> List[str]:
    return [m.group(1).lower() for m in _MCP_TOOL_RE.finditer(source)]


def _go_mentions_tool(source: str, tool_lc: str) -> bool:
    s = source.lower()
    t = tool_lc.replace("_", "")
    if tool_lc in s:
        return True
    if t in s.replace("_", ""):
        return True
    # HTTP 路径常含 collection 名
    if "get_items" in tool_lc and "/items/" in s:
        return True
    if "patch_item" in tool_lc and "patch" in s and "/items/" in s:
        return True
    if "post_items" in tool_lc and "post" in s and "/items/" in s:
        return True
    return False


# Case → 最小 MCP 工具名集合（Rust call_mcp_tool 或 Go 等价 HTTP/命名）
_REQUIRED_TOOLS: dict[int, Tuple[str, ...]] = {
    1: ("get_items", "patch_item"),
    # Case2 常出现非常规字面量/封装；编译与 baseline 校验仍是硬门闩，此处避免误杀整轮。
    2: (),
    3: ("get_items", "patch_item", "post_items"),
    4: (),  # MinIO/Memos：轻检不强制 MCP 名
}


def run_client_precheck(
    source: str,
    *,
    case_id: int,
    language: str,
) -> PrecheckResult:
    failures: List[str] = []
    lang = (language or "rust").strip().lower()
    src = source or ""

    required = _REQUIRED_TOOLS.get(case_id, ())
    if required and not src.strip():
        return PrecheckResult(
            False, ["generation_empty:no_extractable_source"]
        )
    if required:
        if lang in ("rust", "rs"):
            have = set(_rust_tool_calls(src))
            for tool in required:
                if tool.lower() not in have:
                    failures.append(f"missing_endpoint:{tool}")
        elif lang == "go":
            for tool in required:
                if not _go_mentions_tool(src, tool.lower()):
                    failures.append(f"missing_endpoint:{tool}")
        else:
            # Lua 等：暂不强制端点名
            pass

    # 骨架：Case 2 期望循环、分支或常见批量迭代写法（避免仅接受 for/while 误伤迭代器风格）
    if case_id == 2:
        has_loopish = bool(
            re.search(r"\b(for|while)\s+", src, re.IGNORECASE)
            or re.search(r"\.for_each\s*\(", src)
            or re.search(r"\.iter\s*\(\s*\)", src)
            or re.search(r"\.into_iter\s*\(\s*\)", src)
            or (
                re.search(r"\bif\s+", src, re.IGNORECASE)
                and "pending" in src.lower()
            )
        )
        if not has_loopish:
            failures.append("skeleton_mismatch:expect_loop_or_branch")

    # value-flow：Case 2 要求先读后写（READ 注释行在首个 WRITE 之前）
    if case_id == 2 and "@WRITE_OPERATION" in src.upper():
        lines = src.splitlines()
        read_i = write_i = None
        for i, line in enumerate(lines):
            u = line.upper()
            if read_i is None and "@READ_OPERATION" in u:
                read_i = i
            if write_i is None and "@WRITE_OPERATION" in u:
                write_i = i
        if write_i is not None and read_i is None:
            failures.append("value_flow_invalid:no_read_before_write")
        elif write_i is not None and read_i is not None and read_i > write_i:
            failures.append("value_flow_invalid:read_after_write_marker_order")

    # Case 4：常见 LLM 误解析 —— list 的 body 是对象含 objects，get 的正文在 body.content
    if case_id == 4 and lang in ("rust", "rs") and src:
        if "minio_list_objects" in src and re.search(
            r'get\s*\(\s*["\']body["\']\s*\)\s*\.\s*and_then\s*\(\s*\|\s*b\s*\|\s*b\.as_array\s*\(\s*\)',
            src,
        ):
            failures.append("case4_json_shape:list_body_use_objects_array_not_as_array")
        if "minio_get_object" in src and re.search(
            r'get\s*\(\s*["\']body["\']\s*\)\s*\.\s*and_then\s*\(\s*\|\s*b\s*\|\s*b\.as_str\s*\(\s*\)',
            src,
        ):
            failures.append("case4_json_shape:get_body_use_content_field_not_as_str")

    return PrecheckResult(passed=len(failures) == 0, failures=failures)
