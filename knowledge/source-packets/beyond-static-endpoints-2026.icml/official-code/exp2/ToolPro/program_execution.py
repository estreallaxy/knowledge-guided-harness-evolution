"""
ToolPro：Rust 源码经 core SeparatedExecutionEngine 进程内编译并执行（MCP 路径与 server 一致）。

说明：第一层 `compile_first_layer_to_wasm` 已做过一次 Rust→Wasm 校验；此处会再次编译，
与 `server_service` 单进程行为对齐，后续可改为复用 wasm 字节码以省耗时。

Go（M4）：默认仍 wasip1 + ``wasip1_runner``；可选 ``go_execution_backend=rust_wasm_core``，
从 Go 源中 ``TOOLPRO_RUST_GUEST_BEGIN/END`` 抽取 Rust 片段后走与 Rust 相同的 ``execute_rust_with_core_engine``。
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


async def execute_rust_with_core_engine(
    source_code: str,
    *,
    module_id: str,
    user_query: str,
    input_data: Optional[str] = None,
    timeout: int = 120,
    force_read_mode: bool = False,
    replay_enabled: bool = True,
    fallback_policy: str = "safe_stepwise",
    replay_conflict_policy: str = "strict_prefix",
    repair_attempt_budget: Optional[int] = None,
    intent_instance_id: Optional[str] = None,
    replay_allow_nondeterministic_writes: bool = False,
) -> Dict[str, Any]:
    from core.separated_execution_engine import SeparatedExecutionEngine
    from core.stepwise_agent_handler import build_llm_stepwise_handler
    from core.wasm_runtime import WasmRuntime
    from core.compilation_engine import CompilationEngine

    if not (intent_instance_id or "").strip():
        return SeparatedExecutionEngine._attach_reliability_fields(
            {
                "success": False,
                "error": "intent_instance_id_required",
                "strategy": "intent_instance_id_required",
                "execution_mode": "none",
                "data": None,
                "final_mode": "none",
                "fallback_triggered": False,
                "fallback_reason": None,
                "fallback_to_stepwise_success": None,
            },
            intent_instance_id=None,
            replay_enabled=replay_enabled,
            fallback_policy=fallback_policy,
            replay_conflict_policy=replay_conflict_policy,
            repair_attempt_budget=repair_attempt_budget,
            replay_allow_nondeterministic_writes=replay_allow_nondeterministic_writes,
        )

    payload = input_data if input_data is not None else "{}"
    wasm = WasmRuntime()
    engine = SeparatedExecutionEngine(wasm, CompilationEngine())
    engine.register_stepwise_handler(build_llm_stepwise_handler())
    engine.clear_execution_data()
    return await engine.execute_with_mode_detection(
        module_id=module_id,
        source_code=source_code,
        input_data=payload,
        user_query=user_query,
        timeout=timeout,
        force_read_mode=force_read_mode,
        replay_enabled=replay_enabled,
        fallback_policy=fallback_policy,
        replay_conflict_policy=replay_conflict_policy,
        repair_attempt_budget=repair_attempt_budget,
        intent_instance_id=intent_instance_id,
        replay_allow_nondeterministic_writes=replay_allow_nondeterministic_writes,
    )


def _run_go_wasip1_wasmtime_only(
    source_code: str,
    *,
    timeout: int = 120,
) -> Dict[str, Any]:
    """Go wasip1 → Wasmtime ``_start``（与 M4 默认路径一致）。"""
    from core.go_wasip1_compiler import compile_go_to_wasip1_wasm
    from core.wasip1_runner import run_wasip1_wasm_bytes

    _ = timeout
    cr = compile_go_to_wasip1_wasm(source_code)
    if not cr.get("success"):
        return {
            "success": False,
            "error": cr.get("error") or "Go 编译为 wasip1 wasm 失败",
            "strategy": "go_wasip1_compile",
            "execution_mode": "wasip1",
        }
    wb = cr.get("wasm_bytes")
    if not wb:
        return {
            "success": False,
            "error": "编译结果缺少 wasm_bytes",
            "strategy": "go_wasip1_compile",
            "execution_mode": "wasip1",
        }
    out = run_wasip1_wasm_bytes(wb)
    out.setdefault("compile_backend", cr.get("backend"))
    out.setdefault("go_execution_backend", "wasip1_wasmtime")
    return out


def run_go_program_execution_sync(
    source_code: str,
    *,
    module_id: Optional[str] = None,
    user_query: str = "",
    input_data: Optional[str] = None,
    timeout: int = 120,
    go_execution_backend: str = "wasip1_wasmtime",
    force_read_mode: bool = False,
    replay_enabled: bool = True,
    fallback_policy: str = "safe_stepwise",
    replay_conflict_policy: str = "strict_prefix",
    repair_attempt_budget: Optional[int] = None,
    intent_instance_id: Optional[str] = None,
    replay_allow_nondeterministic_writes: bool = False,
) -> Dict[str, Any]:
    """
    Go 第二层执行：默认 wasip1；``rust_wasm_core`` 时从源码抽取 ``TOOLPRO_RUST_GUEST_*`` 内嵌 Rust，
    走 ``execute_rust_with_core_engine``（与 Rust ToolPro 共用 ``SeparatedExecutionEngine`` / 宿主 MCP）。
    """
    be = (go_execution_backend or "wasip1_wasmtime").strip().lower()
    if be == "rust_wasm_core":
        from exp2.ToolPro.go_rust_guest_extract import extract_rust_guest_from_go

        rust_body = extract_rust_guest_from_go(source_code)
        if not rust_body:
            return {
                "success": False,
                "error": "go_execution_backend=rust_wasm_core 但未找到 "
                "TOOLPRO_RUST_GUEST_BEGIN ... TOOLPRO_RUST_GUEST_END 内嵌 Rust 片段",
                "strategy": "go_rust_guest_missing",
                "execution_mode": "go_rust_bridge",
                "go_execution_backend": be,
            }
        mid = module_id or f"go_rust_core_{uuid.uuid4().hex[:12]}"
        iid = (intent_instance_id or "").strip() or str(uuid.uuid4())
        out = asyncio.run(
            execute_rust_with_core_engine(
                rust_body,
                module_id=mid,
                user_query=user_query or "(go rust_wasm_core co-guest)",
                input_data=input_data if input_data is not None else "{}",
                timeout=timeout,
                force_read_mode=force_read_mode,
                replay_enabled=replay_enabled,
                fallback_policy=fallback_policy,
                replay_conflict_policy=replay_conflict_policy,
                repair_attempt_budget=repair_attempt_budget,
                intent_instance_id=iid,
                replay_allow_nondeterministic_writes=replay_allow_nondeterministic_writes,
            )
        )
        out = dict(out)
        out.setdefault("go_execution_backend", be)
        out.setdefault("strategy", out.get("strategy") or "go_rust_wasm_core")
        return out

    if be != "wasip1_wasmtime":
        logger.warning("未知 go_execution_backend=%r，回退 wasip1_wasmtime", be)
    return _run_go_wasip1_wasmtime_only(source_code, timeout=timeout)


def run_go_wasip1_program_execution_sync(
    source_code: str,
    *,
    timeout: int = 120,
) -> Dict[str, Any]:
    """兼容旧入口：等价于 ``go_execution_backend=wasip1_wasmtime``。"""
    return run_go_program_execution_sync(source_code, timeout=timeout)


def run_rust_program_execution_sync(
    source_code: str,
    *,
    module_id: str,
    user_query: str,
    input_data: Optional[str] = None,
    timeout: int = 120,
    force_read_mode: bool = False,
    replay_enabled: bool = True,
    fallback_policy: str = "safe_stepwise",
    replay_conflict_policy: str = "strict_prefix",
    repair_attempt_budget: Optional[int] = None,
    intent_instance_id: Optional[str] = None,
    replay_allow_nondeterministic_writes: bool = False,
) -> Dict[str, Any]:
    iid = (intent_instance_id or "").strip() or str(uuid.uuid4())
    return asyncio.run(
        execute_rust_with_core_engine(
            source_code,
            module_id=module_id,
            user_query=user_query,
            input_data=input_data,
            timeout=timeout,
            force_read_mode=force_read_mode,
            replay_enabled=replay_enabled,
            fallback_policy=fallback_policy,
            replay_conflict_policy=replay_conflict_policy,
            repair_attempt_budget=repair_attempt_budget,
            intent_instance_id=iid,
            replay_allow_nondeterministic_writes=replay_allow_nondeterministic_writes,
        )
    )
