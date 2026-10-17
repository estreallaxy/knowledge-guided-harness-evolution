"""
ToolPro 主入口：交互式或 argparse 配置 → 代码生成 → 第一层（读写标记 + WASM 编译）。

结果目录：exp2/ToolPro/results/
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLPRO_DIR = Path(__file__).resolve().parent
DEFAULT_RESULTS_DIR = TOOLPRO_DIR / "results"

_VERBOSE_RAW_MAX = 14_000
_VERBOSE_CODE_MAX = 20_000
_VERBOSE_ERR_MAX = 8_000


def _try_reconfigure_stdio_utf8(stream: io.TextIOBase) -> None:
    """Windows 等环境下尽量用 UTF-8 解释控制台输出，减轻中文乱码。"""
    fn = getattr(stream, "reconfigure", None)
    if not callable(fn):
        return
    try:
        fn(encoding="utf-8", errors="replace")
    except (OSError, ValueError, AttributeError, TypeError):
        return


def _toolpro_session_env_flag(name: str) -> bool:
    v = (os.environ.get(name) or "").strip().lower()
    return v in ("1", "true", "yes", "on", "y")


class _TeeTextIO:
    """同时写入真实 stdout 与内存缓冲，用于保存完整终端打印日志。"""

    def __init__(self, *streams: io.TextIOBase) -> None:
        self._streams = streams

    def write(self, s: str) -> int:
        for f in self._streams:
            f.write(s)
            f.flush()
        return len(s)

    def flush(self) -> None:
        for f in self._streams:
            f.flush()

    # 部分环境会检查 isatty
    def isatty(self) -> bool:
        return any(getattr(f, "isatty", lambda: False)() for f in self._streams)


def _parse_cases(s: str) -> List[int]:
    t = s.strip().lower()
    if t in ("all", "*"):
        return [1, 2, 3, 4]
    out: List[int] = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        n = int(part)
        if n not in (1, 2, 3, 4):
            raise ValueError(f"非法 case id: {n}（仅支持 1–4）")
        out.append(n)
    if not out:
        raise ValueError("未指定任何 case")
    return out


def _trunc_for_terminal(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len] + f"\n... [已截断，全文共 {len(text)} 字符；完整内容见结果 JSON]"


def _compact_exec_audit_for_toolpro(exec_res: Dict[str, Any]) -> Dict[str, Any]:
    """从引擎返回中抽取小体积字段，便于对照「执行成功 vs Directus 实况」。"""
    if not isinstance(exec_res, dict):
        return {}
    out: Dict[str, Any] = {}
    for k in (
        "strategy",
        "execution_mode",
        "final_mode",
        "fallback_triggered",
        "fallback_reason",
        "error",
        "go_execution_backend",
    ):
        if exec_res.get(k) is not None:
            out[k] = exec_res.get(k)
    di = exec_res.get("debug_info")
    if isinstance(di, dict) and di.get("q_history_status") is not None:
        out["q_history_status"] = di.get("q_history_status")
    return out


def _attach_toolpro_post_validation_fields(
    row: Dict[str, Any],
    exec_res: Dict[str, Any],
    vr: Any,
) -> None:
    row["execution_vs_validation_mismatch"] = bool(exec_res.get("success")) and (
        not bool(vr.passed)
    )
    m = getattr(vr, "metrics", None)
    row["validation_db_snapshot"] = dict(m) if isinstance(m, dict) and m else None
    row["execution_audit_compact"] = _compact_exec_audit_for_toolpro(exec_res)


def _print_toolpro_validation_diag_if_verbose(
    *,
    verbose: bool,
    batch_idx: int,
    case_id: int,
    row: Dict[str, Any],
    vr: Any,
) -> None:
    if not verbose or not row.get("validation_ran") or vr.passed:
        return
    exec_ok = bool(row.get("execution_success"))
    print(
        f"[ToolPro][DIAG] batch={batch_idx} case={case_id} 校验未通过 "
        f"(execution_success={exec_ok})。errors 前几条: {list(vr.errors)[:5]!r}",
        flush=True,
    )
    snap = row.get("validation_db_snapshot")
    if isinstance(snap, dict):
        print(
            f"[ToolPro][DIAG] Directus 实况 orders id=1: {snap.get('live_orders_id_1')!r}",
            flush=True,
        )
    if row.get("execution_vs_validation_mismatch"):
        print(
            "[ToolPro][DIAG] execution_success=True 但库未达期望：请核对 Guest 是否调用写工具、"
            "write_mode 是否命中 Q_history 缓存而复用旧响应、以及 MCP/Directus 与校验器是否同一实例。",
            flush=True,
        )
        print(
            f"[ToolPro][DIAG] execution_audit_compact={row.get('execution_audit_compact')!r}",
            flush=True,
        )


def _print_verbose_block(title: str, body: str, max_len: int = _VERBOSE_RAW_MAX) -> None:
    sep = "─" * 60
    print(f"\n{sep}\n{title}\n{sep}")
    print(_trunc_for_terminal(body, max_len))


def _system_message_for_language(lang: str) -> str:
    lang = lang.lower()
    if lang == "rust":
        return "你是一个专家级Rust程序员，专门编写能够编译为纯WebAssembly的代码。"
    if lang == "go":
        return "你是一个专家级Go程序员，根据工具说明编写可审查的 HTTP 客户端代码。"
    if lang == "lua":
        return "你是一个专家级Lua程序员，根据工具说明编写数据访问脚本。"
    return "你是一个专业程序员。"


def _interactive_config() -> SimpleNamespace:
    from exp2.baseline.agent import load_openrouter_config
    from exp2.ToolPro.wasm_compilers.model_presets import (
        GENERATOR_MODEL_MENU_ORDER,
        GENERATOR_MODEL_PRESETS,
    )

    _api, env_model, _base = load_openrouter_config()

    print("=== ToolPro 交互式配置 ===\n")

    print("【生成目标语言】")
    print("  [1] Rust（默认，可走 core WASM 编译校验）")
    print("  [2] Golang")
    print("  [3] Lua")
    lc = (input("\n请选择 [1]: ").strip() or "1")
    lang_map = {"1": "rust", "2": "go", "3": "lua"}
    target_language = lang_map.get(lc, "rust")

    go_execution_backend = "wasip1_wasmtime"
    if target_language == "go":
        print("\n【Go 第二层执行后端】")
        print("  [1] wasip1_wasmtime（默认：Go → WASI wasm，Wasmtime _start）")
        print("  [2] rust_wasm_core（与 Rust 相同 core 引擎；源码需含 TOOLPRO_RUST_GUEST_* 块）")
        gb = (input("\n请选择 [1]: ").strip() or "1")
        if gb == "2":
            go_execution_backend = "rust_wasm_core"

    print("\n【代码生成模型】")
    print(f"  [1] 使用 .env 默认 OPENROUTER_MODEL（当前: {env_model}）")
    for i, key in enumerate(GENERATOR_MODEL_MENU_ORDER, start=2):
        print(f"  [{i}] {key}")
    mc = (input("\n请选择 [1]: ").strip() or "1")
    if mc == "1":
        generator_model = env_model
    else:
        try:
            choice = int(mc)
        except ValueError:
            choice = 1
        off = choice - 2
        if 0 <= off < len(GENERATOR_MODEL_MENU_ORDER):
            k = GENERATOR_MODEL_MENU_ORDER[off]
            generator_model = GENERATOR_MODEL_PRESETS[k]
        else:
            generator_model = env_model

    raw_b = input("\n请输入批次数 [1]: ").strip() or "1"
    try:
        batches = int(raw_b)
    except ValueError:
        batches = 1
    if batches < 1:
        batches = 1

    print("\n【Case 选择】")
    print("  [1] 全部 Case（1、2、3、4）")
    print("  [2] 自定义：逗号分隔编号")
    choice = (input("\n请选择 [1]: ").strip() or "1")
    if choice == "2":
        s = input("请输入 Case 编号（1–4，逗号分隔）: ").strip()
        cases = _parse_cases(s) if s else [1, 2, 3, 4]
    else:
        cases = [1, 2, 3, 4]

    v_yn = input(
        "\n是否在终端详细打印每步（模型原始回复、抽取源码、读写标记、WASM 编译）？[y/N]: "
    ).strip().lower()
    verbose = v_yn in ("y", "yes", "是", "1")

    sk = input(
        "\n是否跳过进程内执行与验证（仅第一层编译门闩）？[y/N]: "
    ).strip().lower()
    skip_execute = sk in ("y", "yes", "是", "1")

    print("\n【Replay】")
    print("  [1] on（默认，Q_history 写路径可复用）")
    print("  [2] off（关闭 Q_history 命中，每次真实写）")
    rpl = (input("\n请选择 [1]: ").strip() or "1")
    replay = "off" if rpl == "2" else "on"

    go_be_note = (
        f"，go_execution_backend={go_execution_backend}"
        if target_language == "go"
        else ""
    )
    print(
        f"\n当前配置：语言={target_language}，生成模型={generator_model}，"
        f"批次数={batches}，Case 顺序={cases}，详细输出={'开' if verbose else '关'}，"
        f"跳过执行={'是' if skip_execute else '否'}，replay={replay}{go_be_note}，"
        f"extra_rtt_ms=0，route_selection=dynamic_select\n"
    )

    return SimpleNamespace(
        target_language=target_language,
        generator_model=generator_model,
        batches=batches,
        cases=cases,
        log_dir=None,
        verbose=verbose,
        skip_execute=skip_execute,
        replay=replay,
        fallback_policy="safe_stepwise",
        replay_conflict_policy="strict_prefix",
        repair_attempt_budget=None,
        executor_model=None,
        extra_rtt_ms=0,
        route_selection="dynamic_select",
        client_precheck="strict",
        replay_allow_nondeterministic_writes=False,
        go_execution_backend=go_execution_backend,
        layer1_compile_repair_budget=3,
        cargo_stream=False,
        cargo_verbose=False,
    )


def _build_per_batch(
    results: List[Dict[str, Any]],
    batches: int,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for b in range(1, batches + 1):
        sub = [r for r in results if r.get("batch") == b]
        wall = sum(float(r.get("wall_seconds") or 0) for r in sub)
        pcount = sum(1 for r in sub if r.get("passed"))
        n = len(sub)
        out.append(
            {
                "batch": b,
                "wall_seconds": round(wall, 4),
                "run_count": n,
                "passed_count": pcount,
                "success": n > 0 and pcount == n,
            }
        )
    return out


def _build_aggregate(
    results: List[Dict[str, Any]],
    batches: int,
    cases: List[int],
    run_elapsed: float,
) -> Dict[str, Any]:
    total_runs = len(results)
    passed_runs = sum(1 for r in results if r.get("passed"))
    acc = (passed_runs / total_runs) if total_runs else 0.0

    by_case: Dict[int, Dict[str, Any]] = {}
    for cid in (1, 2, 3, 4):
        sub = [r for r in results if r.get("case_id") == cid]
        if not sub:
            continue
        c_pass = sum(1 for r in sub if r.get("passed"))
        by_case[cid] = {
            "runs": len(sub),
            "passed": c_pass,
            "accuracy": c_pass / len(sub),
            "avg_eval_seconds": sum(
                float(r.get("eval_window_seconds") or 0) for r in sub
            )
            / len(sub),
        }

    avg_per_run = (run_elapsed / total_runs) if total_runs else 0.0
    avg_per_batch = (run_elapsed / batches) if batches else 0.0

    return {
        "batches_configured": batches,
        "cases_per_batch_order": cases,
        "total_runs": total_runs,
        "passed_runs": passed_runs,
        "accuracy": round(acc, 6),
        "total_wall_seconds": round(run_elapsed, 4),
        "average_seconds_per_batch": round(avg_per_batch, 4),
        "average_seconds_per_run": round(avg_per_run, 4),
        "by_case": by_case,
    }


def run_suite(
    args: SimpleNamespace,
    *,
    session_ts: str,
    out_dir: Path,
) -> None:
    from exp2.baseline.agent import load_openrouter_config
    from exp2.baseline.case_prompts import get_case_user_prompt
    from exp2.ToolPro.code_extract import extract_code_from_response
    from exp2.ToolPro.llm_client import chat_completion_with_stats
    from exp2.ToolPro.prompts import (
        build_layer1_compile_repair_prompt,
        build_prompt,
        layer1_repair_system_message,
    )
    from exp2.ToolPro.wasm_compile_check import compile_first_layer_to_wasm
    from exp2.ToolPro.wasm_compilers.tool_markers import validate_layer1_tool_markers

    api_key, _env_model, base_url = load_openrouter_config()
    gen_model = args.generator_model
    verbose = bool(getattr(args, "verbose", False))

    results: List[Dict[str, Any]] = []
    runs_payload: List[Dict[str, Any]] = []
    run_started = time.perf_counter()
    lang = args.target_language.lower()

    replay_arg = str(getattr(args, "replay", "on")).strip().lower()
    if replay_arg in ("1", "true", "yes"):
        replay_arg = "on"
    if replay_arg in ("0", "false", "no"):
        replay_arg = "off"
    replay_engine_on = replay_arg == "on"
    fallback_pol = getattr(args, "fallback_policy", "safe_stepwise") or "safe_stepwise"
    replay_cpol = getattr(args, "replay_conflict_policy", "strict_prefix") or "strict_prefix"
    repair_budget = getattr(args, "repair_attempt_budget", None)
    executor_model = getattr(args, "executor_model", None)
    replay_allow_nd = bool(
        getattr(args, "replay_allow_nondeterministic_writes", False)
    )
    go_exec_be = str(
        getattr(args, "go_execution_backend", "wasip1_wasmtime") or "wasip1_wasmtime"
    ).strip().lower()
    if go_exec_be not in ("wasip1_wasmtime", "rust_wasm_core"):
        go_exec_be = "wasip1_wasmtime"

    if getattr(args, "cargo_stream", False):
        os.environ["TOOLPRO_CARGO_STREAM_OUTPUT"] = "1"
    if getattr(args, "cargo_verbose", False):
        os.environ["TOOLPRO_CARGO_BUILD_VERBOSE"] = "1"

    for batch_idx in range(1, args.batches + 1):
        for case_id in args.cases:
            row: Dict[str, Any] = {
                "batch": batch_idx,
                "case_id": case_id,
                "passed": False,
                "target_language": lang,
                "generator_model": gen_model,
                "replay": replay_arg,
                "replay_enabled_engine": replay_engine_on,
                "fallback_policy": fallback_pol,
                "replay_conflict_policy": replay_cpol,
                "repair_attempt_budget": repair_budget,
                "executor_model": executor_model,
                "replay_allow_nondeterministic_writes": replay_allow_nd,
                "go_execution_backend": go_exec_be,
                "intent_instance_id": str(uuid.uuid4()),
            }
            t0 = time.perf_counter()
            raw_response = ""
            source_code = ""
            compile_passed: Optional[bool] = None
            compile_error: Optional[str] = None
            llm_bytes_sent = 0
            llm_bytes_received = 0
            task_text = get_case_user_prompt(case_id)

            if case_id in (1, 2, 3, 4):
                try:
                    from exp2.baseline.initializer import (
                        InitializerError,
                        initialize_directus_in_process,
                    )

                    print(
                        f"[ToolPro] batch={batch_idx} case={case_id} "
                        "Directus 基准数据重置（与 expectations 对齐）…",
                        flush=True,
                    )
                    initialize_directus_in_process()
                except InitializerError as ie:
                    print(
                        f"[ToolPro][WARN] batch={batch_idx} case={case_id} "
                        f"Directus 初始化失败: {ie}",
                        flush=True,
                    )
                except Exception as ex:
                    print(
                        f"[ToolPro][WARN] batch={batch_idx} case={case_id} "
                        f"Directus 初始化异常: {ex}",
                        flush=True,
                    )

            try:
                if case_id == 4:
                    print(f"[Case4][ToolPro] batch={batch_idx} step=1 构建提示词", flush=True)
                prompt = build_prompt(task_text, lang)
                t_gen0 = time.perf_counter()
                if case_id == 4:
                    print(f"[Case4][ToolPro] batch={batch_idx} step=2 调用LLM生成代码", flush=True)
                print(
                    f"[ToolPro] batch={batch_idx} case={case_id} "
                    "等待 LLM 生成响应（首包可能较慢，请稍候）…",
                    flush=True,
                )
                llm_resp = chat_completion_with_stats(
                    [
                        {
                            "role": "system",
                            "content": _system_message_for_language(lang),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    api_key=api_key,
                    model=gen_model,
                    base_url=base_url,
                    temperature=0.1,
                    max_tokens=4096,
                    timeout=180.0,
                )
                raw_response = str(llm_resp["content"])
                llm_bytes_sent = int(llm_resp.get("request_bytes") or 0)
                llm_bytes_received = int(llm_resp.get("response_bytes") or 0)
                if not (raw_response or "").strip():
                    print(
                        f"[ToolPro] batch={batch_idx} case={case_id} "
                        "LLM 首次返回空内容，重试一次生成…",
                        flush=True,
                    )
                    llm_retry = chat_completion_with_stats(
                        [
                            {
                                "role": "system",
                                "content": _system_message_for_language(lang),
                            },
                            {
                                "role": "user",
                                "content": prompt
                                + "\n\n【补发】上一条回复正文为空；请输出**非空**的一个 ```"
                                + ("rust" if lang == "rust" else lang)
                                + " 围栏，内含完整业务代码。",
                            },
                        ],
                        api_key=api_key,
                        model=gen_model,
                        base_url=base_url,
                        temperature=0.2,
                        max_tokens=4096,
                        timeout=180.0,
                    )
                    raw_response = str(llm_retry.get("content") or "")
                    llm_bytes_sent += int(llm_retry.get("request_bytes") or 0)
                    llm_bytes_received += int(llm_retry.get("response_bytes") or 0)
                row["generate_seconds"] = round(time.perf_counter() - t_gen0, 4)
                if case_id == 4:
                    print(f"[Case4][ToolPro] batch={batch_idx} step=3 抽取源码", flush=True)
                source_code = extract_code_from_response(raw_response, lang)
                row["source_code_length"] = len(source_code)

                pc_mode = str(getattr(args, "client_precheck", "strict") or "strict").strip().lower()
                skip_client_precheck = False
                pr_failures: List[str] = []
                if pc_mode == "off":
                    row["client_precheck_passed"] = None
                    row["client_precheck_failures"] = None
                else:
                    from exp2.ToolPro.client_interface_precheck import run_client_precheck

                    pr = run_client_precheck(
                        source_code, case_id=case_id, language=lang
                    )
                    row["client_precheck_passed"] = pr.passed
                    row["client_precheck_failures"] = list(pr.failures)
                    pr_failures = list(pr.failures)
                    if pc_mode == "strict" and not pr.passed:
                        skip_client_precheck = True
                    if pc_mode == "warn" and not pr.passed and verbose:
                        print(f"\n[轻检 warn] failures={pr.failures}")

                if verbose:
                    print(
                        f"\n{'=' * 60}\n"
                        f"[详细] batch={batch_idx} case={case_id} lang={lang}\n"
                        f"{'=' * 60}"
                    )
                    _print_verbose_block(
                        "① 生成模型原始回复",
                        raw_response,
                        _VERBOSE_RAW_MAX,
                    )
                    _print_verbose_block(
                        "② 围栏抽取后源码",
                        source_code,
                        _VERBOSE_CODE_MAX,
                    )
                    mk_err = validate_layer1_tool_markers(lang, source_code)
                    if mk_err:
                        print(f"\n[③ 第一层 · 读写标记] 未通过\n{mk_err}")
                    else:
                        print("\n[③ 第一层 · 读写标记] 通过")

                t_comp0 = time.perf_counter()
                if case_id == 4:
                    print(f"[Case4][ToolPro] batch={batch_idx} step=4 编译检测", flush=True)
                else:
                    print(
                        f"[ToolPro] batch={batch_idx} case={case_id} 第一层 cargo 编译开始…",
                        flush=True,
                    )
                if skip_client_precheck:
                    if pr_failures and any(
                        x.startswith("generation_empty:") for x in pr_failures
                    ):
                        gen_e = ";".join(pr_failures)
                    else:
                        gen_e = "client_precheck_failed: " + ";".join(pr_failures)
                    cr = {
                        "success": False,
                        "error": gen_e,
                        "wasm_bytes": None,
                        "backend": None,
                    }
                else:
                    cr = compile_first_layer_to_wasm(lang, source_code)
                compile_passed = bool(cr.get("success"))
                if not compile_passed:
                    compile_error = str(cr.get("error", "未知编译错误"))
                else:
                    compile_error = None
                row["compile_backend"] = cr.get("backend")
                row["wasm_bytes_length"] = (
                    len(cr["wasm_bytes"]) if cr.get("wasm_bytes") else 0
                )
                row["compile_seconds"] = round(time.perf_counter() - t_comp0, 4)

                row["layer1_compile_repair_attempts"] = 0
                row["layer1_compile_repair_generate_seconds"] = 0.0
                row["compile_error_first"] = None
                raw_response_last_repair = ""

                if verbose:
                    wb = len(cr.get("wasm_bytes") or b"")
                    print(
                        f"\n[④ 第一层 · WASM 编译] backend={cr.get('backend')} "
                        f"success={bool(cr.get('success'))} "
                        f"wasm_bytes={wb} "
                        f"time_s={row['compile_seconds']}"
                    )
                    if not cr.get("success"):
                        err = str(cr.get("error", ""))
                        print(_trunc_for_terminal(err, _VERBOSE_ERR_MAX))

                # 第一层编译/校验失败：就地纠错（任务 + 源码 + 报错 → 仅返回纠错后围栏代码）
                if (not compile_passed) and (not skip_client_precheck):
                    err0 = str(compile_error or "")
                    l1_budget = int(
                        getattr(args, "layer1_compile_repair_budget", 3) or 0
                    )
                    _non_repairable = (
                        err0.startswith("client_precheck_failed")
                        or err0.startswith("generation_empty")
                    )
                    if l1_budget > 0 and not _non_repairable:
                        row["compile_error_first"] = err0
                        err_for_repair = err0
                        repair_gen_acc = 0.0
                        repair_calls = 0
                        for r_idx in range(l1_budget):
                            if case_id == 4:
                                print(
                                    f"[Case4][ToolPro] batch={batch_idx} "
                                    f"第一层纠错 attempt={r_idx + 1}/{l1_budget}",
                                    flush=True,
                                )
                            else:
                                print(
                                    f"[ToolPro] batch={batch_idx} case={case_id} "
                                    f"第一层纠错 LLM 第 {r_idx + 1}/{l1_budget} 轮…",
                                    flush=True,
                                )
                            print(
                                f"[ToolPro] batch={batch_idx} case={case_id} "
                                f"纠错：等待 LLM 响应（可能较久）…",
                                flush=True,
                            )
                            if verbose:
                                print(
                                    f"\n[④-b 第一层纠错 LLM] attempt {r_idx + 1}/{l1_budget}"
                                )
                            repair_user = build_layer1_compile_repair_prompt(
                                task_text, lang, source_code, err_for_repair
                            )
                            t_rep0 = time.perf_counter()
                            rep_resp = chat_completion_with_stats(
                                [
                                    {
                                        "role": "system",
                                        "content": layer1_repair_system_message(lang),
                                    },
                                    {"role": "user", "content": repair_user},
                                ],
                                api_key=api_key,
                                model=gen_model,
                                base_url=base_url,
                                temperature=0.1,
                                max_tokens=4096,
                                timeout=180.0,
                            )
                            repair_gen_acc += time.perf_counter() - t_rep0
                            rs = int(rep_resp.get("request_bytes") or 0)
                            rr = int(rep_resp.get("response_bytes") or 0)
                            llm_bytes_sent += rs
                            llm_bytes_received += rr
                            raw_rr = str(rep_resp.get("content") or "")
                            raw_response_last_repair = raw_rr
                            repair_calls += 1
                            new_src = extract_code_from_response(raw_rr, lang).strip()
                            if not new_src:
                                err_for_repair = (
                                    f"layer1_repair_empty_extract:attempt_{r_idx + 1}"
                                )
                                if verbose:
                                    print("[④-b] 纠错回复未抽取到围栏代码，继续下一轮")
                                continue
                            source_code = new_src
                            row["source_code_length"] = len(source_code)
                            print(
                                f"[ToolPro] batch={batch_idx} case={case_id} "
                                f"第一层纠错后重新 cargo 编译…",
                                flush=True,
                            )
                            t_rec = time.perf_counter()
                            cr = compile_first_layer_to_wasm(lang, source_code)
                            row["compile_seconds"] = round(
                                float(row["compile_seconds"] or 0)
                                + time.perf_counter()
                                - t_rec,
                                4,
                            )
                            compile_passed = bool(cr.get("success"))
                            row["compile_backend"] = cr.get("backend")
                            row["wasm_bytes_length"] = (
                                len(cr["wasm_bytes"]) if cr.get("wasm_bytes") else 0
                            )
                            if compile_passed:
                                compile_error = None
                                if verbose:
                                    wb2 = len(cr.get("wasm_bytes") or b"")
                                    print(
                                        f"\n[④-b 第一层纠错后编译] success=True "
                                        f"wasm_bytes={wb2} (attempt {r_idx + 1})"
                                    )
                                break
                            compile_error = str(cr.get("error", "未知编译错误"))
                            err_for_repair = compile_error
                            if verbose:
                                print(
                                    f"\n[④-b 第一层纠错后编译] success=False "
                                    f"(attempt {r_idx + 1})"
                                )
                                print(
                                    _trunc_for_terminal(
                                        str(compile_error), _VERBOSE_ERR_MAX
                                    )
                                )

                        row["layer1_compile_repair_attempts"] = repair_calls
                        row["layer1_compile_repair_generate_seconds"] = round(
                            repair_gen_acc, 4
                        )

                row["execution_ran"] = False
                row["validation_ran"] = False
                row["compile_passed"] = compile_passed
                row["compile_error"] = compile_error
                row["llm_bytes_sent"] = llm_bytes_sent
                row["llm_bytes_received"] = llm_bytes_received
                row["llm_bytes_total"] = llm_bytes_sent + llm_bytes_received
                if raw_response_last_repair:
                    row["raw_llm_response_last_repair"] = raw_response_last_repair[
                        :200000
                    ]

                print(
                    f"[ToolPro] batch={batch_idx} case={case_id} "
                    f"第一层结束 compile_passed={compile_passed} "
                    f"compile_s={row.get('compile_seconds')} "
                    f"repair_llm_calls={row.get('layer1_compile_repair_attempts', 0)}",
                    flush=True,
                )

                skip_execute = bool(getattr(args, "skip_execute", False))

                if not compile_passed:
                    row["passed"] = False
                elif lang == "rust" and not skip_execute:
                    row["execution_backend"] = "rust_wasm_core"
                    row["execution_ran"] = True
                    t_exec0 = time.perf_counter()
                    exec_replay_allow_nd = bool(
                        replay_allow_nd or case_id in (3, 4)
                    )
                    try:
                        from exp2.ToolPro.program_execution import (
                            run_rust_program_execution_sync,
                        )

                        exec_res = run_rust_program_execution_sync(
                            source_code,
                            module_id=(
                                f"toolpro_b{batch_idx}_c{case_id}_"
                                f"{uuid.uuid4().hex[:12]}"
                            ),
                            user_query=task_text,
                            input_data=json.dumps(
                                {"case_id": case_id}, ensure_ascii=False
                            ),
                            timeout=120,
                            force_read_mode=False,
                            replay_enabled=replay_engine_on,
                            fallback_policy=fallback_pol,
                            replay_conflict_policy=replay_cpol,
                            repair_attempt_budget=repair_budget,
                            intent_instance_id=row.get("intent_instance_id"),
                            replay_allow_nondeterministic_writes=exec_replay_allow_nd,
                        )
                    except Exception as exec_exc:
                        exec_res = {
                            "success": False,
                            "error": str(exec_exc),
                            "strategy": "toolpro_execution_exception",
                            "execution_mode": "unknown",
                        }
                    row["execution_seconds"] = round(
                        time.perf_counter() - t_exec0, 4
                    )
                    row["execution_success"] = bool(exec_res.get("success"))
                    row["execution_error"] = exec_res.get("error")
                    row["execution_strategy"] = exec_res.get("strategy")
                    row["execution_mode_detected"] = exec_res.get(
                        "execution_mode"
                    )
                    row["engine_replay_enabled"] = exec_res.get("replay_enabled")
                    row["engine_fallback_policy"] = exec_res.get("fallback_policy")
                    row["engine_replay_conflict_policy"] = exec_res.get(
                        "replay_conflict_policy"
                    )
                    if exec_res.get("repair_attempt_budget") is not None:
                        row["engine_repair_attempt_budget"] = exec_res.get(
                            "repair_attempt_budget"
                        )
                    row["replay_allow_nondeterministic_writes_engine"] = (
                        exec_res.get("replay_allow_nondeterministic_writes")
                    )
                    if exec_res.get("intent_instance_id"):
                        row["intent_instance_id"] = exec_res.get(
                            "intent_instance_id"
                        )
                    t_val0 = time.perf_counter()
                    from exp2.baseline.validator import validate_case

                    vr = validate_case(case_id)
                    row["validation_seconds"] = round(
                        time.perf_counter() - t_val0, 4
                    )
                    row["validation_passed"] = vr.passed
                    row["validation_errors"] = list(vr.errors)
                    row["validation_ran"] = True
                    row["passed"] = bool(vr.passed)
                    _attach_toolpro_post_validation_fields(row, exec_res, vr)
                    _print_toolpro_validation_diag_if_verbose(
                        verbose=verbose,
                        batch_idx=batch_idx,
                        case_id=case_id,
                        row=row,
                        vr=vr,
                    )
                elif lang == "go" and not skip_execute:
                    row["execution_backend"] = (
                        "go_rust_wasm_core"
                        if go_exec_be == "rust_wasm_core"
                        else "go_wasip1_wasmtime"
                    )
                    row["execution_ran"] = True
                    t_exec0 = time.perf_counter()
                    exec_replay_allow_nd = bool(
                        replay_allow_nd or case_id in (3, 4)
                    )
                    try:
                        from exp2.ToolPro.program_execution import (
                            run_go_program_execution_sync,
                        )

                        exec_res = run_go_program_execution_sync(
                            source_code,
                            module_id=(
                                f"toolpro_go_b{batch_idx}_c{case_id}_"
                                f"{uuid.uuid4().hex[:12]}"
                            ),
                            user_query=task_text,
                            input_data=json.dumps(
                                {"case_id": case_id}, ensure_ascii=False
                            ),
                            timeout=120,
                            go_execution_backend=go_exec_be,
                            force_read_mode=False,
                            replay_enabled=replay_engine_on,
                            fallback_policy=fallback_pol,
                            replay_conflict_policy=replay_cpol,
                            repair_attempt_budget=repair_budget,
                            intent_instance_id=row.get("intent_instance_id"),
                            replay_allow_nondeterministic_writes=exec_replay_allow_nd,
                        )
                    except Exception as exec_exc:
                        exec_res = {
                            "success": False,
                            "error": str(exec_exc),
                            "strategy": "toolpro_go_wasip1_exception",
                            "execution_mode": "wasip1",
                        }
                    row["execution_seconds"] = round(
                        time.perf_counter() - t_exec0, 4
                    )
                    row["execution_success"] = bool(exec_res.get("success"))
                    row["execution_error"] = exec_res.get("error")
                    row["execution_strategy"] = exec_res.get("strategy")
                    row["execution_mode_detected"] = exec_res.get(
                        "execution_mode"
                    )
                    row["engine_replay_enabled"] = exec_res.get("replay_enabled")
                    row["engine_fallback_policy"] = exec_res.get("fallback_policy")
                    row["engine_replay_conflict_policy"] = exec_res.get(
                        "replay_conflict_policy"
                    )
                    if exec_res.get("repair_attempt_budget") is not None:
                        row["engine_repair_attempt_budget"] = exec_res.get(
                            "repair_attempt_budget"
                        )
                    row["replay_allow_nondeterministic_writes_engine"] = (
                        exec_res.get("replay_allow_nondeterministic_writes")
                    )
                    if exec_res.get("intent_instance_id"):
                        row["intent_instance_id"] = exec_res.get(
                            "intent_instance_id"
                        )
                    t_val0 = time.perf_counter()
                    from exp2.baseline.validator import validate_case

                    vr = validate_case(case_id)
                    row["validation_seconds"] = round(
                        time.perf_counter() - t_val0, 4
                    )
                    row["validation_passed"] = vr.passed
                    row["validation_errors"] = list(vr.errors)
                    row["validation_ran"] = True
                    row["passed"] = bool(vr.passed)
                    _attach_toolpro_post_validation_fields(row, exec_res, vr)
                    _print_toolpro_validation_diag_if_verbose(
                        verbose=verbose,
                        batch_idx=batch_idx,
                        case_id=case_id,
                        row=row,
                        vr=vr,
                    )
                elif lang == "rust" and skip_execute:
                    row["passed"] = True
                    row["execution_skipped"] = True
                    row["execution_skip_reason"] = "skip_execute_flag"
                elif lang == "go" and skip_execute:
                    row["passed"] = True
                    row["execution_skipped"] = True
                    row["execution_skip_reason"] = "skip_execute_flag"
                elif compile_passed:
                    row["passed"] = True
                    row["execution_skipped"] = True
                    row["execution_skip_reason"] = (
                        f"language_{lang}_no_inprocess_engine"
                    )

            except Exception as e:
                row["passed"] = False
                row["error"] = str(e)
                row["traceback"] = traceback.format_exc()
                row["compile_passed"] = compile_passed
                row["compile_error"] = compile_error
                for k in (
                    "generate_seconds",
                    "compile_seconds",
                ):
                    if k not in row:
                        row[k] = 0.0
                row["llm_bytes_sent"] = llm_bytes_sent
                row["llm_bytes_received"] = llm_bytes_received
                row["llm_bytes_total"] = llm_bytes_sent + llm_bytes_received
                if verbose:
                    print(f"\n[异常] {e}")
                    print(_trunc_for_terminal(row.get("traceback", ""), _VERBOSE_ERR_MAX))

            t_end = time.perf_counter()
            row["eval_window_seconds"] = round(t_end - t0, 4)
            row["wall_seconds"] = row["eval_window_seconds"]
            if case_id == 4:
                if row.get("validation_ran"):
                    v_reason = "toolpro_program_execution_and_validate"
                elif row.get("execution_skipped"):
                    v_reason = row.get("execution_skip_reason") or "skipped"
                else:
                    v_reason = "toolpro_no_validation"
                case4_metrics = {
                    "average_latency_s": row["eval_window_seconds"],
                    "client_traffic_bytes": float(row.get("llm_bytes_total") or 0),
                    "success_rate": 1.0 if row.get("passed") else 0.0,
                    "fallback_rate": 0.0,
                    "validator_stage": {
                        "executed": bool(row.get("validation_ran")),
                        "reason": v_reason,
                    },
                }
                row["case4_metrics"] = case4_metrics

            results.append(row)

            run_entry: Dict[str, Any] = {
                "batch": batch_idx,
                "case_id": case_id,
                "passed": bool(row.get("passed")),
                "target_language": lang,
                "generator_model": gen_model,
                "wall_seconds": row["wall_seconds"],
                "eval_window_seconds": row.get("eval_window_seconds"),
                "generate_seconds": row.get("generate_seconds"),
                "compile_seconds": row.get("compile_seconds"),
                "compile_passed": row.get("compile_passed"),
                "compile_backend": row.get("compile_backend"),
                "wasm_bytes_length": row.get("wasm_bytes_length"),
                "compile_error": row.get("compile_error"),
                "compile_error_first": row.get("compile_error_first"),
                "layer1_compile_repair_attempts": row.get(
                    "layer1_compile_repair_attempts"
                ),
                "layer1_compile_repair_generate_seconds": row.get(
                    "layer1_compile_repair_generate_seconds"
                ),
                "raw_llm_response_last_repair": (
                    (row.get("raw_llm_response_last_repair") or "")[:200000]
                    + (
                        "\n... [truncated]"
                        if len(row.get("raw_llm_response_last_repair") or "") > 200000
                        else ""
                    )
                    if row.get("raw_llm_response_last_repair")
                    else None
                ),
                "llm_bytes_sent": row.get("llm_bytes_sent"),
                "llm_bytes_received": row.get("llm_bytes_received"),
                "llm_bytes_total": row.get("llm_bytes_total"),
                "error": row.get("error"),
                "traceback": row.get("traceback"),
                "task_user_prompt": task_text,
                "raw_llm_response": raw_response[:200000]
                if len(raw_response) <= 200000
                else raw_response[:200000] + "\n... [truncated]",
                "extracted_source_code": source_code[:200000]
                if len(source_code) <= 200000
                else source_code[:200000] + "\n... [truncated]",
                "case4_metrics": row.get("case4_metrics"),
                "intent_instance_id": row.get("intent_instance_id"),
                "client_precheck_passed": row.get("client_precheck_passed"),
                "client_precheck_failures": row.get("client_precheck_failures"),
                "execution_ran": row.get("execution_ran"),
                "execution_backend": row.get("execution_backend"),
                "execution_seconds": row.get("execution_seconds"),
                "execution_success": row.get("execution_success"),
                "execution_error": row.get("execution_error"),
                "execution_strategy": row.get("execution_strategy"),
                "execution_mode_detected": row.get("execution_mode_detected"),
                "replay": row.get("replay"),
                "replay_enabled_engine": row.get("replay_enabled_engine"),
                "fallback_policy": row.get("fallback_policy"),
                "replay_conflict_policy": row.get("replay_conflict_policy"),
                "repair_attempt_budget": row.get("repair_attempt_budget"),
                "replay_allow_nondeterministic_writes": row.get(
                    "replay_allow_nondeterministic_writes"
                ),
                "go_execution_backend": row.get("go_execution_backend"),
                "executor_model": row.get("executor_model"),
                "engine_replay_enabled": row.get("engine_replay_enabled"),
                "engine_fallback_policy": row.get("engine_fallback_policy"),
                "engine_replay_conflict_policy": row.get(
                    "engine_replay_conflict_policy"
                ),
                "engine_repair_attempt_budget": row.get(
                    "engine_repair_attempt_budget"
                ),
                "replay_allow_nondeterministic_writes_engine": row.get(
                    "replay_allow_nondeterministic_writes_engine"
                ),
                "validation_ran": row.get("validation_ran"),
                "validation_seconds": row.get("validation_seconds"),
                "validation_passed": row.get("validation_passed"),
                "validation_errors": row.get("validation_errors"),
                "execution_vs_validation_mismatch": row.get(
                    "execution_vs_validation_mismatch"
                ),
                "validation_db_snapshot": row.get("validation_db_snapshot"),
                "execution_audit_compact": row.get("execution_audit_compact"),
                "execution_skipped": row.get("execution_skipped"),
                "execution_skip_reason": row.get("execution_skip_reason"),
            }
            runs_payload.append(run_entry)

            status = "PASS" if row.get("passed") else "FAIL"
            cp = row.get("compile_passed")
            cp_s = "skip" if cp is None else ("ok" if cp else "fail")
            ex_s = (
                "ok"
                if row.get("execution_success") is True
                else (
                    "fail"
                    if row.get("execution_success") is False
                    else "n/a"
                )
            )
            val_s = (
                "ok"
                if row.get("validation_passed") is True
                else (
                    "fail"
                    if row.get("validation_passed") is False
                    else "n/a"
                )
            )
            print(
                f"[{status}] batch={batch_idx} case={case_id} lang={lang} "
                f"compile={cp_s} exec={ex_s} validate={val_s} "
                f"wall_s={row['wall_seconds']:.2f}"
            )
            if row.get("compile_error"):
                print(f"    compile: {row['compile_error'][:300]}")
            if row.get("execution_error"):
                print(f"    exec: {str(row['execution_error'])[:300]}")
            if row.get("validation_errors"):
                print(
                    f"    validate: {len(row['validation_errors'])} error(s); "
                    f"first: {row['validation_errors'][0][:200]}"
                )
            if row.get("error"):
                print(f"    E {row['error']}")

    run_elapsed = time.perf_counter() - run_started
    per_batch = _build_per_batch(results, args.batches)
    aggregate = _build_aggregate(
        results, args.batches, list(args.cases), run_elapsed
    )
    aggregate["target_language"] = lang
    aggregate["generator_model"] = gen_model

    result_name = f"{session_ts}_toolpro.json"
    result_path = out_dir / result_name
    session_payload: Dict[str, Any] = {
        "session_timestamp": session_ts,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "config": {
            "target_language": lang,
            "generator_model": gen_model,
            "batches": args.batches,
            "cases_order": list(args.cases),
            "verbose_terminal": verbose,
            "skip_execute": bool(getattr(args, "skip_execute", False)),
            "replay": getattr(args, "replay", "on"),
            "fallback_policy": getattr(args, "fallback_policy", "safe_stepwise"),
            "replay_conflict_policy": getattr(
                args, "replay_conflict_policy", "strict_prefix"
            ),
            "repair_attempt_budget": getattr(args, "repair_attempt_budget", None),
            "layer1_compile_repair_budget": int(
                getattr(args, "layer1_compile_repair_budget", 3) or 0
            ),
            "executor_model": getattr(args, "executor_model", None),
            "extra_rtt_ms": int(getattr(args, "extra_rtt_ms", 0) or 0),
            "route_selection": str(getattr(args, "route_selection", "dynamic_select") or "dynamic_select"),
            "client_precheck": getattr(args, "client_precheck", "strict"),
            "replay_allow_nondeterministic_writes": bool(
                getattr(args, "replay_allow_nondeterministic_writes", False)
            ),
            "go_execution_backend": str(
                getattr(args, "go_execution_backend", "wasip1_wasmtime")
                or "wasip1_wasmtime"
            ).strip().lower(),
            "cargo_stream_cli": bool(getattr(args, "cargo_stream", False)),
            "cargo_verbose_cli": bool(getattr(args, "cargo_verbose", False)),
            "cargo_stream_output_effective": _toolpro_session_env_flag(
                "TOOLPRO_CARGO_STREAM_OUTPUT"
            ),
            "cargo_build_verbose_effective": _toolpro_session_env_flag(
                "TOOLPRO_CARGO_BUILD_VERBOSE"
            ),
            "terminal_log_file": f"{session_ts}_toolpro_terminal.txt",
        },
        "per_batch": per_batch,
        "runs": runs_payload,
        "aggregate": aggregate,
    }
    result_path.write_text(
        json.dumps(session_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print()
    print("=== ToolPro 汇总 ===")
    print(f"总运行次数: {aggregate['total_runs']}")
    print(f"通过（含 Rust 执行+校验 或 非 Rust 仅编译门闩）: {aggregate['passed_runs']} / {aggregate['total_runs']}")
    print(f"正确率: {aggregate['accuracy'] * 100:.2f}%")
    print(f"全会话总时间: {aggregate['total_wall_seconds']:.2f}s")
    print(f"平均每批次时间: {aggregate['average_seconds_per_batch']:.2f}s")
    print(f"平均每 run 时间: {aggregate['average_seconds_per_run']:.2f}s")
    for bb in per_batch:
        ok = "成功" if bb["success"] else "未全过"
        print(
            f"  Batch {bb['batch']}: {bb['wall_seconds']:.2f}s, {ok}, "
            f"通过 {bb['passed_count']}/{bb['run_count']}"
        )
    for cid, info in sorted(aggregate.get("by_case", {}).items()):
        print(
            f"  Case {cid}: 正确率 {info['accuracy'] * 100:.1f}% "
            f"({info['passed']}/{info['runs']})"
        )
    print(f"\n结果目录: {out_dir}")
    print(f"结果 JSON: {result_path.name}")
    print(f"终端日志 TXT: {session_ts}_toolpro_terminal.txt")


def main(argv: Optional[List[str]] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    real_stdout = sys.stdout
    _try_reconfigure_stdio_utf8(real_stdout)
    _try_reconfigure_stdio_utf8(sys.stderr)
    log_buffer = io.StringIO()
    tee = _TeeTextIO(real_stdout, log_buffer)
    out_dir: Optional[Path] = None
    session_ts: Optional[str] = None

    try:
        sys.stdout = tee

        if not argv:
            args = _interactive_config()
        else:
            parser = argparse.ArgumentParser(
                description="ToolPro：代码生成 + 第一层编译；Rust 默认再经 core 执行并 baseline 校验"
            )
            parser.add_argument(
                "--language",
                choices=("rust", "go", "lua"),
                default="rust",
                help="生成语言",
            )
            parser.add_argument(
                "--model",
                type=str,
                default="env",
                help='生成模型：env=使用 OPENROUTER_MODEL，或指定完整模型 id（如 openai/gpt-5.1）',
            )
            parser.add_argument("--batches", type=int, default=1)
            parser.add_argument("--cases", type=str, default="all")
            parser.add_argument(
                "--log-dir",
                type=Path,
                default=None,
                help="结果目录（默认 exp2/ToolPro/results）",
            )
            parser.add_argument(
                "-v",
                "--verbose",
                action="store_true",
                help="在终端打印每步详情：原始回复、抽取源码、读写标记、WASM 编译",
            )
            parser.add_argument(
                "--skip-execute",
                action="store_true",
                help="跳过进程内执行与 validate_case（仅保留第一层编译门闩；Rust 亦如此）",
            )
            parser.add_argument(
                "--replay",
                choices=("on", "off"),
                default="on",
                help="Q_history 写路径复用：on=开启，off=禁用命中（每次真实 MCP 写）",
            )
            parser.add_argument(
                "--fallback-policy",
                choices=("safe_stepwise", "fail_fast"),
                default="safe_stepwise",
                help="降级策略名（当前写入结果 JSON；stepwise 接入后生效）",
            )
            parser.add_argument(
                "--replay-conflict-policy",
                choices=("strict_prefix", "off"),
                default="strict_prefix",
                help="前缀冲突策略名（ReplayGuard 全量接入后生效）",
            )
            parser.add_argument(
                "--replay-allow-nondeterministic-writes",
                action="store_true",
                help="§3.2.7 消融：放宽 nondeterministic WRITE 的 replay 策略（默认关闭）",
            )
            parser.add_argument(
                "--repair-attempt-budget",
                type=int,
                default=None,
                help="覆盖 core ErrorHandler 默认 repair 上限；不设则 3",
            )
            parser.add_argument(
                "--executor-model",
                type=str,
                default=None,
                help="执行/修复阶段模型 id（当前仅写入结果 JSON）",
            )
            parser.add_argument(
                "--extra-rtt-ms",
                type=int,
                default=0,
                help="附加 RTT（毫秒）；与 client/scheduler 对齐时写入会话配置（默认 0）",
            )
            parser.add_argument(
                "--route-selection",
                type=str,
                default="dynamic_select",
                choices=(
                    "dynamic_select",
                    "direct",
                    "wasm",
                    "program",
                    "program_mode",
                    "stepwise",
                ),
                help="invocation 路线：program/program_mode→wasm，stepwise→direct",
            )
            parser.add_argument(
                "--client-precheck",
                type=str,
                default="strict",
                choices=("strict", "warn", "off"),
                help="客户端 Step1 轻检：strict=不通过则跳过编译；warn=记录仍编译；off=跳过",
            )
            parser.add_argument(
                "--generator-model",
                type=str,
                default=None,
                help="代码生成模型；指定则优先于 --model=env",
            )
            parser.add_argument(
                "--go-execution-backend",
                type=str,
                default="wasip1_wasmtime",
                choices=("wasip1_wasmtime", "rust_wasm_core"),
                help="Go 第二层：wasip1_wasmtime=WASI _start；rust_wasm_core=从 Go 注释抽取 TOOLPRO_RUST_GUEST 走 SeparatedExecutionEngine（与 Rust 共用宿主 MCP）",
            )
            parser.add_argument(
                "--layer1-compile-repair-budget",
                type=int,
                default=3,
                help="第一层编译/标记校验失败后，就地 LLM 纠错的最大轮数（与 --model 同一生成模型）；0=关闭",
            )
            parser.add_argument(
                "--cargo-stream",
                action="store_true",
                help="Rust 第一层：cargo 合并输出流式刷到 stderr（仍可用环境变量 TOOLPRO_CARGO_STREAM_OUTPUT=1）",
            )
            parser.add_argument(
                "--cargo-verbose",
                action="store_true",
                help="Rust 第一层：cargo build 追加 -v（更啰嗦；可与 --cargo-stream 同开）",
            )
            ns = parser.parse_args(argv)
            if ns.batches < 1:
                parser.error("--batches 须 >= 1")
            cases = _parse_cases(ns.cases)
            from exp2.baseline.agent import load_openrouter_config

            _k, env_model, _b = load_openrouter_config()
            if getattr(ns, "generator_model", None):
                generator_model = str(ns.generator_model).strip()
            elif ns.model == "env":
                generator_model = env_model
            else:
                generator_model = ns.model.strip()
            if getattr(ns, "extra_rtt_ms", 0) < 0:
                parser.error("--extra-rtt-ms 须 >= 0")
            if getattr(ns, "layer1_compile_repair_budget", 3) < 0:
                parser.error("--layer1-compile-repair-budget 须 >= 0")
            args = SimpleNamespace(
                target_language=ns.language,
                generator_model=generator_model,
                batches=ns.batches,
                cases=cases,
                log_dir=ns.log_dir,
                verbose=ns.verbose,
                skip_execute=bool(ns.skip_execute),
                replay=ns.replay,
                fallback_policy=ns.fallback_policy,
                replay_conflict_policy=ns.replay_conflict_policy,
                repair_attempt_budget=ns.repair_attempt_budget,
                replay_allow_nondeterministic_writes=bool(
                    getattr(ns, "replay_allow_nondeterministic_writes", False)
                ),
                go_execution_backend=str(
                    getattr(ns, "go_execution_backend", "wasip1_wasmtime")
                    or "wasip1_wasmtime"
                ).strip().lower(),
                executor_model=ns.executor_model,
                extra_rtt_ms=int(ns.extra_rtt_ms or 0),
                route_selection=str(ns.route_selection or "dynamic_select").strip(),
                client_precheck=str(ns.client_precheck or "strict").strip().lower(),
                layer1_compile_repair_budget=int(ns.layer1_compile_repair_budget),
                cargo_stream=bool(ns.cargo_stream),
                cargo_verbose=bool(ns.cargo_verbose),
            )

        case4_results_dir = REPO_ROOT / "exp2" / "exp_case4" / "results"
        if args.log_dir:
            out_dir = Path(args.log_dir)
        elif list(args.cases) == [4]:
            out_dir = case4_results_dir
        else:
            out_dir = DEFAULT_RESULTS_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        session_ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_suite(args, session_ts=session_ts, out_dir=out_dir)
    finally:
        sys.stdout = real_stdout
        save_dir = out_dir if out_dir is not None else DEFAULT_RESULTS_DIR
        save_dir.mkdir(parents=True, exist_ok=True)
        ts = session_ts if session_ts else datetime.now().strftime("%Y%m%d-%H%M%S")
        log_name = f"{ts}_toolpro_terminal.txt"
        log_path = save_dir / log_name
        try:
            log_path.write_text(log_buffer.getvalue(), encoding="utf-8")
            print(f"终端完整日志已保存: {log_path}", file=real_stdout)
        except OSError as e:
            print(f"警告: 无法写入终端日志 {log_path}: {e}", file=real_stdout)


if __name__ == "__main__":
    if __package__ is None:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
    main(sys.argv[1:])
