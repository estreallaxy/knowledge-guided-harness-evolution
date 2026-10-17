"""
Go → WASM（WASI）：实现已迁至 ``core.go_wasip1_compiler``，此处仅作向后兼容重导出。
"""

from __future__ import annotations

from core.go_wasip1_compiler import compile_go_to_wasip1_wasm, prepare_main_go

__all__ = ["compile_go_to_wasip1_wasm", "prepare_main_go"]
