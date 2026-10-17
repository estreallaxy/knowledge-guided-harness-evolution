"""
Go 文件内嵌 Rust 业务片段（与 ``CompilationEngine`` 模板中 ``execute_internal`` 体一致），
供 ``go_execution_backend=rust_wasm_core`` 时走 ``SeparatedExecutionEngine``（M4 与 Rust 共用宿主 MCP）。
"""

from __future__ import annotations

import re
from typing import Optional

_RUST_GUEST_RE = re.compile(
    r"TOOLPRO_RUST_GUEST_BEGIN\s*(.*?)\s*TOOLPRO_RUST_GUEST_END",
    re.DOTALL | re.IGNORECASE,
)


def extract_rust_guest_from_go(go_source: str) -> Optional[str]:
    """
    从 Go 源码块注释中抽取 Rust 片段（须为可嵌入 ``execute_internal`` 的语句序列，通常以 ``Ok(result)`` 结束）。

    示例（放在 ``package main`` 之前）::

        /* TOOLPRO_RUST_GUEST_BEGIN
        result.insert("k".to_string(), serde_json::json!(1));
        Ok(result)
        TOOLPRO_RUST_GUEST_END */
        package main
    """
    if not go_source or not go_source.strip():
        return None
    m = _RUST_GUEST_RE.search(go_source)
    if not m:
        return None
    frag = (m.group(1) or "").strip()
    return frag or None
