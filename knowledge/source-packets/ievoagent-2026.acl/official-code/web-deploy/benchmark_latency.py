#!/usr/bin/env python3
"""
按基座模型分类的对话延时测试：从 24 个用户实验结果中，按每个 task 的 assignedModel 分组，
只对「该 task 对应的基座模型」测量该 task 下各轮对话的回复延时。

即：IEvoAgent 只测 assignedModel=IEvoAgent 的 task 的轮次；kto 只测 assignedModel=kto 的 task；以此类推。
"""

import argparse
import asyncio
import json
import os
import statistics
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

# --------------- 配置 ---------------
_SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = os.environ.get("BENCH_RESULTS_DIR", str(_SCRIPT_DIR / "results"))
KTO_VLLM_URL = os.environ.get("KTO_VLLM_API_URL", "http://localhost:8010/v1")
BASE_VLLM_URL = os.environ.get("BASE_VLLM_API_URL", "http://localhost:8009/v1")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
# 第三方 GPT API 时改为对应 base_url，例如 https://api.gptsapi.net/v1
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
BACKEND_URL = os.environ.get("IEVO_BACKEND_URL", "http://localhost:8000")

KTO_MODEL_NAME = "qwen-kto"
BASE_MODEL_NAME = "qwen2.5-7b-inst"
GPT4_MODEL_NAME = "gpt-4o"

# 与 Result.json 中 assignedModel 一致
MODEL_KEYS = ["IEvoAgent", "kto", "GPT-4o", "qwen2.5"]


def load_all_results(results_dir: str) -> List[Dict[str, Any]]:
    """加载 results 目录下所有 IEVO-*_Result.json。"""
    results_dir = Path(results_dir)
    if not results_dir.exists():
        raise FileNotFoundError(f"Results dir not found: {results_dir}")
    out = []
    for p in sorted(results_dir.glob("IEVO-*_Result.json")):
        with open(p, "r", encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def extract_turn_prompts_by_assigned_model(data: List[Dict]) -> Dict[str, List[Dict]]:
    """
    按基座模型分类抽取对话轮次。
    返回: { assigned_model: [ sample1, sample2, ... ] }
    每个 sample: { session_id, task_id, turn_1based, messages, assigned_model }
    只包含「该 task 由该 assigned_model 负责」的轮次。
    """
    by_model: Dict[str, List[Dict]] = {m: [] for m in MODEL_KEYS}
    for user in data:
        session_id = user.get("sessionId", "")
        for task in user.get("tasks", []):
            assigned_model = task.get("assignedModel", "")
            if assigned_model not in by_model:
                by_model[assigned_model] = []
            history = task.get("history", [])
            task_id = task.get("taskId", 0)
            turn_1based = 0
            for i in range(1, len(history), 2):
                if history[i]["role"] != "assistant":
                    continue
                turn_1based += 1
                messages = [{"role": h["role"], "content": h["content"]} for h in history[:i]]
                by_model[assigned_model].append({
                    "session_id": session_id,
                    "task_id": task_id,
                    "turn_1based": turn_1based,
                    "messages": messages,
                    "assigned_model": assigned_model,
                })
    return by_model


async def measure_openai_latency(
    client: AsyncOpenAI,
    model: str,
    messages: List[Dict],
    max_tokens: int = 1024,
) -> Tuple[float, int, str]:
    start = time.perf_counter()
    completion = await client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.7,
    )
    elapsed = time.perf_counter() - start
    content = completion.choices[0].message.content or ""
    usage = getattr(completion, "usage", None)
    if usage and getattr(usage, "completion_tokens", None) is not None:
        out_tokens = usage.completion_tokens
    else:
        out_tokens = max(1, len(content) // 2)
    return elapsed, out_tokens, content


async def measure_ievo_agent_latency(
    backend_url: str,
    session_id: str,
    messages: List[Dict],
) -> Tuple[float, int, str]:
    try:
        import aiohttp
    except ImportError:
        raise RuntimeError("IEvoAgent 需要 aiohttp: pip install aiohttp")
    start = time.perf_counter()
    url = f"{backend_url.rstrip('/')}/chat"
    payload = {"model_name": "IEvoAgent", "session_id": session_id, "messages": messages}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise RuntimeError(f"IEvoAgent backend {resp.status}: {text}")
            data = await resp.json()
    elapsed = time.perf_counter() - start
    content = data.get("response", "") or ""
    return elapsed, max(1, len(content) // 2), content


async def run_one_sample(
    sample: Dict,
    model_key: str,
    clients: Dict,
    backend_url: str,
    max_tokens: int,
) -> Tuple[float, int, str]:
    messages = sample["messages"]
    session_id = sample.get("session_id", "bench-session")

    if model_key == "GPT-4o":
        client = clients.get("gpt")
        if not client:
            raise RuntimeError("OpenAI client 未配置 (OPENAI_API_KEY?)")
        return await measure_openai_latency(client, GPT4_MODEL_NAME, messages, max_tokens)
    if model_key == "qwen2.5":
        client = clients.get("base_vllm")
        if not client:
            raise RuntimeError("Base vLLM 未配置")
        return await measure_openai_latency(client, BASE_MODEL_NAME, messages, max_tokens)
    if model_key == "kto":
        client = clients.get("kto_vllm")
        if not client:
            raise RuntimeError("KTO vLLM 未配置")
        return await measure_openai_latency(client, KTO_MODEL_NAME, messages, max_tokens)
    if model_key == "IEvoAgent":
        return await measure_ievo_agent_latency(backend_url, session_id, messages)
    raise ValueError(f"Unknown model_key: {model_key}")


def build_clients(args) -> Dict:
    clients = {}
    if AsyncOpenAI is None:
        return clients
    api_key = args.openai_api_key or OPENAI_API_KEY
    if "GPT-4o" in args.models and api_key:
        base = args.openai_base_url or OPENAI_BASE_URL
        clients["gpt"] = AsyncOpenAI(api_key=api_key, base_url=base)
    if "qwen2.5" in args.models:
        clients["base_vllm"] = AsyncOpenAI(api_key="EMPTY", base_url=args.base_vllm_url or BASE_VLLM_URL)
    if "kto" in args.models:
        clients["kto_vllm"] = AsyncOpenAI(api_key="EMPTY", base_url=args.kto_vllm_url or KTO_VLLM_URL)
    return clients


def summarize_latencies(latencies: List[float], name: str) -> Dict[str, Any]:
    if not latencies:
        return {"model": name, "mean": 0, "median": 0, "p95": 0, "min": 0, "max": 0, "count": 0}
    lat = sorted(latencies)
    n = len(lat)
    return {
        "model": name,
        "mean": round(statistics.mean(lat), 4),
        "median": round(lat[n // 2], 4),
        "p95": round(lat[int(n * 0.95)] if n >= 20 else lat[-1], 4),
        "min": round(min(lat), 4),
        "max": round(max(lat), 4),
        "count": n,
    }


async def main_async(args):
    results_dir = args.results_dir or RESULTS_DIR
    if not results_dir:
        raise SystemExit("请指定 --results-dir 或设置 BENCH_RESULTS_DIR")
    if not args.models:
        args.models = list(MODEL_KEYS)

    data = load_all_results(results_dir)
    by_model = extract_turn_prompts_by_assigned_model(data)

    # 每个模型只测「分配给该模型的 task」的轮次
    for m in MODEL_KEYS:
        n = len(by_model.get(m, []))
        print(f"  基座模型 {m}: {n} 个对话轮次")

    # 可选限制
    def apply_limits(samples: List[Dict]) -> List[Dict]:
        if args.max_turns:
            samples = [s for s in samples if s["turn_1based"] <= args.max_turns]
        if args.max_samples and len(samples) > args.max_samples:
            samples = samples[: args.max_samples]
        return samples

    if AsyncOpenAI is None:
        need = [m for m in args.models if m in ("kto", "qwen2.5", "GPT-4o")]
        if need:
            raise SystemExit(
                "未安装 openai 库，无法测试 " + ",".join(need) + "。"
                "请用: pip install openai ，或使用 conda 环境 wildbench 运行: "
                "/data2/miniconda3/envs/wildbench/bin/python benchmark_latency.py ..."
            )
    clients = build_clients(args)
    backend_url = args.backend_url or BACKEND_URL
    if "IEvoAgent" in args.models and not backend_url:
        print("警告: 未配置 IEvoAgent 后端，跳过 IEvoAgent")
        args.models = [m for m in args.models if m != "IEvoAgent"]

    all_stats: Dict[str, List[float]] = {m: [] for m in args.models}
    token_counts: Dict[str, List[int]] = {m: [] for m in args.models}
    detail_dir = Path(args.output_dir or ".")
    detail_dir.mkdir(parents=True, exist_ok=True)
    details: Dict[str, List[Dict]] = {m: [] for m in args.models}

    for model_key in args.models:
        samples = by_model.get(model_key, [])
        samples = apply_limits(samples)
        if not samples:
            print(f"  跳过 {model_key}: 无对应样本")
            continue
        print(f"\n测试基座模型 [{model_key}]，共 {len(samples)} 轮...")
        verbose = getattr(args, "verbose", False)
        max_user_len = getattr(args, "verbose_max_user", 120)
        max_reply_len = getattr(args, "verbose_max_reply", 200)
        for i, sample in enumerate(samples):
            if (i + 1) % 30 == 0 or i == 0:
                print(f"    {model_key}: {i+1}/{len(samples)}")
            if verbose:
                last_user = ""
                for m in reversed(sample["messages"]):
                    if m.get("role") == "user":
                        last_user = (m.get("content") or "").strip().replace("\n", " ")
                        break
                last_user_preview = last_user[:max_user_len] + ("..." if len(last_user) > max_user_len else "")
                print(f"  --- [{model_key}] {sample['session_id']} task={sample['task_id']} turn={sample['turn_1based']} ---")
                print(f"  输入(最后一句): {last_user_preview!r}")
            try:
                elapsed, out_tokens, response_content = await run_one_sample(
                    sample, model_key, clients, backend_url, args.max_tokens
                )
                all_stats[model_key].append(elapsed)
                token_counts[model_key].append(out_tokens)
                details[model_key].append({
                    "session_id": sample["session_id"],
                    "task_id": sample["task_id"],
                    "turn": sample["turn_1based"],
                    "latency_sec": round(elapsed, 4),
                    "out_tokens": out_tokens,
                })
                if verbose:
                    reply_preview = (response_content or "").strip().replace("\n", " ")[:max_reply_len]
                    if len((response_content or "").strip()) > max_reply_len:
                        reply_preview += "..."
                    print(f"  回复: {reply_preview!r}")
                    print(f"  延时={elapsed:.3f}s, tokens≈{out_tokens}")
            except Exception as e:
                print(f"    [WARN] {model_key} 第 {i+1} 个样本失败: {e}")
                if args.fail_fast:
                    raise

    summary = []
    for model_key in args.models:
        latencies = all_stats[model_key]
        s = summarize_latencies(latencies, model_key)
        if token_counts.get(model_key):
            s["out_tokens_mean"] = round(statistics.mean(token_counts[model_key]), 2)
        summary.append(s)

    print("\n========== 按基座模型分类的对话延时 (秒) ==========")
    for s in summary:
        print(f"  {s['model']}: mean={s['mean']}s, median={s['median']}s, p95={s['p95']}s, n={s['count']}")

    out_summary = detail_dir / (args.summary_filename or "latency_summary.json")
    with open(out_summary, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n汇总已写入: {out_summary}")

    if args.save_details:
        for model_key in args.models:
            p = detail_dir / f"latency_details_{model_key.replace('-', '_')}.json"
            with open(p, "w", encoding="utf-8") as f:
                json.dump(details[model_key], f, ensure_ascii=False, indent=2)
            print(f"  详情: {p}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="按基座模型分类测试对话延时 (vLLM / GPT-4o / IEvoAgent)")
    parser.add_argument("--results-dir", type=str, default=RESULTS_DIR, help="IEVO-*_Result.json 所在目录")
    parser.add_argument("--models", nargs="+", default=MODEL_KEYS, help="要测试的基座模型")
    parser.add_argument("--max-turns", type=int, default=None, help="每个任务最多取前 N 轮")
    parser.add_argument("--max-samples", type=int, default=None, help="每个模型最多样本数")
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--base-vllm-url", type=str, default=None)
    parser.add_argument("--kto-vllm-url", type=str, default=None)
    parser.add_argument("--openai-api-key", type=str, default=None)
    parser.add_argument("--openai-base-url", type=str, default=None,
                        help="GPT API 的 base_url，第三方如 gptsapi 填 https://api.gptsapi.net/v1")
    parser.add_argument("--backend-url", type=str, default=None)
    parser.add_argument("--output-dir", type=str, default=".")
    parser.add_argument("--summary-filename", type=str, default="latency_summary.json")
    parser.add_argument("--save-details", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--verbose", action="store_true", help="测试时打印每条对话的输入与回复，便于核对正确性")
    parser.add_argument("--verbose-max-user", type=int, default=120, help="--verbose 时用户输入预览最大字符数")
    parser.add_argument("--verbose-max-reply", type=int, default=200, help="--verbose 时模型回复预览最大字符数")
    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
