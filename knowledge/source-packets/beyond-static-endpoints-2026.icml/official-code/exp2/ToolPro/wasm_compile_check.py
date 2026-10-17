"""第一层编译：Rust 走 core.CompilationEngine；Go/Lua 走 WASI 临时工程（与「临时目录 + 子进程」模型一致）。"""

from __future__ import annotations

import asyncio
from typing import Any, Dict


async def _compile_async(source_code: str) -> Dict[str, Any]:
    from core.compilation_engine import CompilationEngine

    engine = CompilationEngine()
    semantic_info = {
        "module_id": "toolpro_eval",
        "source_type": "rust",
        "compilation_target": "wasm",
        "features": ["std", "serde", "serde_json"],
    }
    return await engine.compile_rust_to_wasm(source_code, semantic_info)


def compile_rust_snippet_to_wasm(source_code: str) -> Dict[str, Any]:
    """同步包装。success 时含 wasm_bytes（bytes）。"""
    return asyncio.run(_compile_async(source_code))


def compile_first_layer_to_wasm(language: str, source_code: str) -> Dict[str, Any]:
    """
    ToolPro 第一层统一入口。返回结构与 compile_rust_to_wasm 对齐，并附带 backend 字段：
    rust_compilation_engine | go_wasip1 | lua_gopher_wasip1
    """
    from exp2.ToolPro.wasm_compilers.tool_markers import validate_layer1_tool_markers

    lang = (language or "").strip().lower()
    backend_by_lang = {
        "rust": "rust_compilation_engine",
        "go": "go_wasip1",
        "lua": "lua_gopher_wasip1",
    }
    backend = backend_by_lang.get(lang, "none")

    marker_err = validate_layer1_tool_markers(lang, source_code)
    if marker_err:
        return {
            "success": False,
            "error": marker_err,
            "wasm_bytes": None,
            "cached": False,
            "template_hit": False,
            "backend": backend,
        }

    if lang == "rust":
        out = dict(compile_rust_snippet_to_wasm(source_code))
        out.setdefault("backend", "rust_compilation_engine")
        return out
    if lang == "go":
        from core.go_wasip1_compiler import compile_go_to_wasip1_wasm

        return compile_go_to_wasip1_wasm(source_code)
    if lang == "lua":
        from exp2.ToolPro.wasm_compilers.lua_gopher_wasip1 import (
            compile_lua_via_gopher_wasip1,
        )

        return compile_lua_via_gopher_wasip1(source_code)
    return {
        "success": False,
        "error": f"不支持的第一层语言: {language}",
        "wasm_bytes": None,
        "cached": False,
        "template_hit": False,
        "backend": "none",
    }
