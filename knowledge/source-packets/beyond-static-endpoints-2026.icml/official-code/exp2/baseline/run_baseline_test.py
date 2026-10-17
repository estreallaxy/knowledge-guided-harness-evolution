"""
Baseline 主流程：初始化 → Agent → 验证器。

无命令行参数时进入**交互式**配置（批次数、Case 选择）。
有参数时使用 argparse（便于脚本/CI）。

结果目录：exp2/baseline/results/baseline/
  - {时间戳}_baseline.json  单次会话唯一结果文件：每批次耗时与是否成功、
    全部 run 的 meta + 每步 transcript（含完整 api_response）、末尾 aggregate
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_DIR = Path(__file__).resolve().parent
DEFAULT_RESULTS_DIR = BASELINE_DIR / "results" / "baseline"
# 兼容 --log-dir：仍可用；默认与 results/baseline 一致
DEFAULT_LOG_DIR = DEFAULT_RESULTS_DIR


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


def _interactive_config() -> SimpleNamespace:
    print("=== Baseline 交互式配置 ===\n")

    raw_b = input("请输入批次数 [1]: ").strip() or "1"
    try:
        batches = int(raw_b)
    except ValueError:
        batches = 1
    if batches < 1:
        print("批次数无效，已改为 1。")
        batches = 1

    print("\n【Case 选择】")
    print("  [1] 全部 Case（1、2、3、4）")
    print("  [2] 自定义：逗号分隔编号，例如 1,3")
    print("  [3] 逐项勾选")
    choice = (input("\n请选择 [1]: ").strip() or "1")

    if choice == "2":
        s = input("请输入 Case 编号（1–4，逗号分隔）: ").strip()
        if not s:
            cases = [1, 2, 3, 4]
            print("输入为空，已选全部 Case。")
        else:
            cases = _parse_cases(s)
    elif choice == "3":
        cases = []
        for cid in (1, 2, 3, 4):
            yn = input(f"  是否运行 Case {cid}? [y/N]: ").strip().lower()
            if yn in ("y", "yes", "是", "1"):
                cases.append(cid)
        if not cases:
            print("未勾选任何 Case，已默认全部运行。")
            cases = [1, 2, 3, 4]
    else:
        cases = [1, 2, 3, 4]

    print(f"\n当前配置：批次数 = {batches}，每批 Case 顺序 = {cases}，开始运行…\n")

    return SimpleNamespace(
        batches=batches,
        cases=cases,
        max_steps=25,
        no_init=False,
        in_process_init=False,
        quiet_init=False,
        quiet_agent=False,
        log_dir=None,
    )


def _build_per_batch(
    results: List[Dict[str, Any]],
    batches: int,
) -> List[Dict[str, Any]]:
    """每个批次一条：墙钟时间、本批内是否全部验证通过。"""
    out: List[Dict[str, Any]] = []
    for b in range(1, batches + 1):
        sub = [r for r in results if r.get("batch") == b]
        wall = sum(
            float(r.get("init_seconds") or 0)
            + float(r.get("agent_seconds") or 0)
            + float(r.get("validate_seconds") or 0)
            for r in sub
        )
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
    from exp2.baseline.agent import run_baseline_agent
    from exp2.baseline.initializer import (
        InitializerError,
        initialize_directus,
        initialize_directus_in_process,
    )
    from exp2.baseline.validator import validate_case
    from exp2.baseline._directus import connect_directus_from_env

    results: List[Dict[str, Any]] = []
    runs_payload: List[Dict[str, Any]] = []
    run_started = time.perf_counter()

    for batch_idx in range(1, args.batches + 1):
        for case_id in args.cases:
            transcript: List[Dict[str, Any]] = []
            row: Dict[str, Any] = {
                "batch": batch_idx,
                "case_id": case_id,
                "passed": False,
            }
            t0 = time.perf_counter()
            init_seconds = 0.0
            t_after_init = t0

            try:
                if case_id != 4 and not args.no_init:
                    if args.in_process_init:
                        initialize_directus_in_process()
                    else:
                        initialize_directus(capture_output=args.quiet_init)
                    init_seconds = time.perf_counter() - t0
                t_after_init = time.perf_counter()

                if case_id == 4:
                    print(f"[Case4] batch={batch_idx} 开始 Agent 执行", flush=True)
                    ar = run_baseline_agent(
                        case_id,
                        max_steps=args.max_steps,
                        transcript=transcript,
                        verbose=True,
                    )
                    t_after_agent = time.perf_counter()
                    print(f"[Case4] batch={batch_idx} 开始验证与清理", flush=True)
                    vr = validate_case(case_id, client=None)
                    t_end = time.perf_counter()
                else:
                    client = connect_directus_from_env()
                    try:
                        ar = run_baseline_agent(
                            case_id,
                            max_steps=args.max_steps,
                            transcript=transcript,
                            verbose=not getattr(args, "quiet_agent", False),
                        )
                        t_after_agent = time.perf_counter()
                        vr = validate_case(case_id, client=client)
                        t_end = time.perf_counter()
                    finally:
                        client.close()

                row["init_seconds"] = round(init_seconds, 4)
                row["agent_seconds"] = round(t_after_agent - t_after_init, 4)
                row["validate_seconds"] = round(t_end - t_after_agent, 4)
                row["eval_window_seconds"] = round(t_end - t_after_init, 4)
                row["passed"] = vr.passed
                row["agent_stop_reason"] = ar.stop_reason
                row["agent_steps"] = ar.steps_used
                row["validation_errors"] = vr.errors
                row["llm_bytes_sent"] = ar.llm_bytes_sent
                row["llm_bytes_received"] = ar.llm_bytes_received
                row["llm_bytes_total"] = ar.llm_bytes_sent + ar.llm_bytes_received

                if case_id == 4:
                    case4_metrics = {
                        "average_latency_s": row["eval_window_seconds"],
                        "client_traffic_bytes": float(row["llm_bytes_total"]),
                        "success_rate": 1.0 if row["passed"] else 0.0,
                        "fallback_rate": 0.0,
                        "validator_state": vr.metrics.get("validator_state", {}),
                        "validator_checks": vr.metrics.get("validator_checks", []),
                        "validator_passed_before_cleanup": vr.metrics.get(
                            "validator_passed_before_cleanup"
                        ),
                        "cleanup_extra_errors": vr.metrics.get("cleanup_extra_errors", []),
                    }
                    row["case4_metrics"] = case4_metrics
            except InitializerError as e:
                row["error"] = f"init: {e}"
                row["init_seconds"] = round(time.perf_counter() - t0, 4)
                row["agent_seconds"] = 0.0
                row["validate_seconds"] = 0.0
                row["eval_window_seconds"] = 0.0
            except Exception as e:
                row["error"] = str(e)
                row["traceback"] = traceback.format_exc()
                row["init_seconds"] = round(init_seconds, 4)
                t_err = time.perf_counter()
                row["agent_seconds"] = round(max(0.0, t_err - t_after_init), 4)
                row["validate_seconds"] = 0.0
                row["eval_window_seconds"] = row["agent_seconds"]

            wall_one = (
                float(row.get("init_seconds") or 0)
                + float(row.get("agent_seconds") or 0)
                + float(row.get("validate_seconds") or 0)
            )
            row["wall_seconds"] = round(wall_one, 4)

            results.append(row)

            run_entry: Dict[str, Any] = {
                "batch": batch_idx,
                "case_id": case_id,
                "passed": bool(row.get("passed")),
                "wall_seconds": row["wall_seconds"],
                "init_seconds": row.get("init_seconds"),
                "agent_seconds": row.get("agent_seconds"),
                "validate_seconds": row.get("validate_seconds"),
                "eval_window_seconds": row.get("eval_window_seconds"),
                "agent_steps": row.get("agent_steps"),
                "agent_stop_reason": row.get("agent_stop_reason"),
                "validation_errors": row.get("validation_errors"),
                "llm_bytes_sent": row.get("llm_bytes_sent"),
                "llm_bytes_received": row.get("llm_bytes_received"),
                "llm_bytes_total": row.get("llm_bytes_total"),
                "case4_metrics": row.get("case4_metrics"),
                "error": row.get("error"),
                "traceback": row.get("traceback"),
                "transcript": transcript,
            }
            runs_payload.append(run_entry)

            status = "PASS" if row.get("passed") else "FAIL"
            print(
                f"[{status}] batch={batch_idx} case={case_id} "
                f"steps={row.get('agent_steps')} stop={row.get('agent_stop_reason')} "
                f"wall_s={row['wall_seconds']:.2f}"
            )
            if row.get("validation_errors"):
                for err in row["validation_errors"][:5]:
                    print(f"    ! {err}")
                if len(row["validation_errors"]) > 5:
                    print(f"    ! ... 共 {len(row['validation_errors'])} 条")
            if row.get("error"):
                print(f"    E {row['error']}")

    run_elapsed = time.perf_counter() - run_started
    per_batch = _build_per_batch(results, args.batches)
    aggregate = _build_aggregate(
        results, args.batches, list(args.cases), run_elapsed
    )

    result_name = f"{session_ts}_baseline.json"
    result_path = out_dir / result_name
    # 顺序：per_batch、runs 在前，aggregate 置底便于阅读「先明细后汇总」
    session_payload: Dict[str, Any] = {
        "session_timestamp": session_ts,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "config": {
            "batches": args.batches,
            "cases_order": list(args.cases),
            "max_steps": args.max_steps,
            "no_init": args.no_init,
            "in_process_init": args.in_process_init,
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
    print("=== Baseline 汇总 ===")
    print(f"总运行次数: {aggregate['total_runs']}")
    print(f"验证通过: {aggregate['passed_runs']} / {aggregate['total_runs']}")
    print(f"正确率: {aggregate['accuracy'] * 100:.2f}%")
    print(f"全会话总时间: {aggregate['total_wall_seconds']:.2f}s")
    print(f"平均每批次时间: {aggregate['average_seconds_per_batch']:.2f}s")
    print(f"平均每 run 时间: {aggregate['average_seconds_per_run']:.2f}s")
    print("各批次（与 JSON 中 per_batch 一致）:")
    for bb in per_batch:
        ok = "成功" if bb["success"] else "未全过"
        print(
            f"  Batch {bb['batch']}: {bb['wall_seconds']:.2f}s, {ok}, "
            f"通过 {bb['passed_count']}/{bb['run_count']}"
        )
    print("各 Case（若曾运行）:")
    for cid, info in sorted(aggregate.get("by_case", {}).items()):
        print(
            f"  Case {cid}: 正确率 {info['accuracy'] * 100:.1f}% "
            f"({info['passed']}/{info['runs']})"
        )
    print(f"\n结果目录: {out_dir}")
    print(f"结果 JSON（单文件）: {result_path.name}")


def main(argv: Optional[List[str]] = None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        args = _interactive_config()
    else:
        parser = argparse.ArgumentParser(
            description="Baseline：初始化 → Agent → 验证（无参数时进入交互式配置）"
        )
        parser.add_argument(
            "--batches",
            type=int,
            default=1,
            help="批次数",
        )
        parser.add_argument(
            "--cases",
            type=str,
            default="all",
            help='Case：逗号分隔或 all',
        )
        parser.add_argument("--max-steps", type=int, default=25)
        parser.add_argument("--no-init", action="store_true")
        parser.add_argument("--in-process-init", action="store_true")
        parser.add_argument("--quiet-init", action="store_true")
        parser.add_argument(
            "--quiet-agent",
            action="store_true",
            help="不打印 Agent 每步模型返回与工具（Directus）返回",
        )
        parser.add_argument(
            "--log-dir",
            type=Path,
            default=None,
            help="输出目录（默认 exp2/baseline/results/baseline）",
        )

        args_ns = parser.parse_args(argv)
        if args_ns.batches < 1:
            parser.error("--batches 须 >= 1")
        cases = _parse_cases(args_ns.cases)
        args = SimpleNamespace(
            batches=args_ns.batches,
            cases=cases,
            max_steps=args_ns.max_steps,
            no_init=args_ns.no_init,
            in_process_init=args_ns.in_process_init,
            quiet_init=args_ns.quiet_init,
            quiet_agent=args_ns.quiet_agent,
            log_dir=args_ns.log_dir,
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


if __name__ == "__main__":
    if __package__ is None:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
    main(sys.argv[1:])
