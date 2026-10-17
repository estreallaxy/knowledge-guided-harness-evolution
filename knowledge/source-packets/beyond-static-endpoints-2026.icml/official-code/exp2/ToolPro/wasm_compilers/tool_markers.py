"""
第一层读写标记校验，与 client/client_code_generator.validate_generated_code 对齐：
- Rust：存在 call_mcp_tool( 时，源码中须出现 @READ_OPERATION 或 @WRITE_OPERATION（通常为 // @READ_OPERATION）。
- Go / Lua：在检测到疑似 HTTP/工具式调用时，同样要求上述子串出现在注释中（Go 用 //，Lua 用 --）。
"""

from __future__ import annotations

from typing import Optional

_RUST_MCP = "call_mcp_tool("


def _has_any_rw_marker(code: str) -> bool:
    return "@READ_OPERATION" in code or "@WRITE_OPERATION" in code


def _go_looks_like_http_tool_usage(code: str) -> bool:
    return any(
        m in code
        for m in (
            "http.Get",
            "http.Post",
            "http.Put",
            "http.Patch",
            "http.Head",
            "http.NewRequest",
            "http.Client",
            ".Do(",
        )
    )


def _lua_looks_like_http_tool_usage(code: str) -> bool:
    s = code.lower()
    return any(
        k in s
        for k in (
            "http.request",
            "socket.http",
            "luasocket",
            "https.request",
            ":request",
            "resty",
            "curl.",
        )
    )


def validate_layer1_tool_markers(language: str, code: str) -> Optional[str]:
    """
    未通过时返回错误说明；通过返回 None。
    与生成侧提示词一致：读操作用 @READ_OPERATION，写操作用 @WRITE_OPERATION。
    """
    lang = (language or "").strip().lower()
    c = code or ""

    if lang == "rust":
        if _RUST_MCP in c and not _has_any_rw_marker(c):
            return (
                "代码包含 call_mcp_tool 调用，但缺少 @READ_OPERATION 或 @WRITE_OPERATION "
                "（须在每次工具调用前添加 // @READ_OPERATION 或 // @WRITE_OPERATION，"
                "与 client_code_generator 一致）"
            )
        return None

    if lang == "go":
        if _go_looks_like_http_tool_usage(c) and not _has_any_rw_marker(c):
            return (
                "Go 代码中检测到疑似 HTTP 工具调用，但缺少读写标记注释；"
                "请在读类请求前添加 // @READ_OPERATION，写类请求前添加 // @WRITE_OPERATION "
                "（注释中须包含字面子串 @READ_OPERATION 或 @WRITE_OPERATION）"
            )
        return None

    if lang == "lua":
        if _lua_looks_like_http_tool_usage(c) and not _has_any_rw_marker(c):
            return (
                "Lua 代码中检测到疑似 HTTP/请求类调用，但缺少读写标记；"
                "请在读操作前添加 -- @READ_OPERATION，写操作前添加 -- @WRITE_OPERATION "
                "（须含字面子串 @READ_OPERATION 或 @WRITE_OPERATION）"
            )
        return None

    return None
