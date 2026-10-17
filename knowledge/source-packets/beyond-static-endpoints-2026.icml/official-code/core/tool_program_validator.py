"""
服务端与客户端共用的 tool program 结构约束校验（论文 Π 的静态子集）。

与 ``call_mcp_tool`` / ``@READ_OPERATION`` / ``@WRITE_OPERATION`` 约定对齐，
供 ``interface_program_projection`` 与 ``ClientCodeGenerator`` 复用。
"""

from __future__ import annotations

import re
from typing import List


def collect_structural_violations(code: str) -> List[str]:
    """返回人类可读的错误列表；空列表表示通过结构校验。"""
    validation_errors: List[str] = []

    forbidden_patterns = [
        "http::client",
        "reqwest::",
        "hyper::",
        "tokio::",
        "result.error =",
        "result.success =",
        "result.done =",
        "return;",
        "use reqwest",
        "use http",
        "use hyper",
        "use tokio",
        'b"{',
        "let response_body = b",
        "serde_json::from_slice(&response_body)",
        "response_body = b",
        "模拟",
        "mock",
        "fake",
        "test_data",
        "hardcoded",
        "static response",
    ]

    for label in forbidden_patterns:
        if label in code:
            validation_errors.append(f"代码包含违禁模式: {label}")

    if "b\"" in code and "response_body" in code:
        validation_errors.append("代码不能使用硬编码的模拟响应（response_body + 字节串）")

    if (
        "result.error =" in code
        or "result.success =" in code
        or "result.done =" in code
    ):
        validation_errors.append("代码不能使用 result 字段赋值语法，必须使用 result.insert()")

    if "return;" in code or re.search(r"\breturn\s+", code):
        validation_errors.append("代码不能直接使用 return 语句，必须使用 result.insert()")

    if "result.insert" not in code:
        validation_errors.append("代码缺少必需模式: result.insert")

    has_read_operation = "@READ_OPERATION" in code
    has_write_operation = "@WRITE_OPERATION" in code
    has_mcp_calls = "call_mcp_tool(" in code

    if has_mcp_calls and not has_read_operation and not has_write_operation:
        validation_errors.append(
            "代码包含 MCP 工具调用但缺少读写标记，必须为每次调用前添加 "
            "// @READ_OPERATION 或 // @WRITE_OPERATION"
        )

    if not has_mcp_calls:
        validation_errors.append("代码必须使用 call_mcp_tool 调用 MCP 工具")

    validation_errors.extend(validate_mcp_calls_have_adjacent_markers(code))

    return validation_errors


def validate_mcp_calls_have_adjacent_markers(source_code: str) -> List[str]:
    """
    每次 ``call_mcp_tool(`` 须在向上若干行内出现显式 ``@READ_OPERATION`` / ``@WRITE_OPERATION``，
    与 ``ExecutionModeDetector`` 的可分析表面一致。
    """
    errors: List[str] = []
    lines = source_code.splitlines()
    # 与 ExecutionModeDetector 的窗口同量级，允许较长业务逻辑夹在标记与调用之间
    max_lookback = 120

    for i, line in enumerate(lines):
        if "call_mcp_tool(" not in line:
            continue
        stripped = line.strip()
        if stripped.startswith("//"):
            continue

        found = False
        for j in range(max(0, i - max_lookback), i):
            prev = lines[j]
            if "@READ_OPERATION" not in prev and "@WRITE_OPERATION" not in prev:
                continue
            if "//" in prev or prev.strip().startswith("//") or "--" in prev:
                found = True
                break

        if not found:
            errors.append(
                f"第 {i + 1} 行 call_mcp_tool 在上方 {max_lookback} 行内缺少 "
                "// @READ_OPERATION 或 // @WRITE_OPERATION 注解"
            )

    return errors
