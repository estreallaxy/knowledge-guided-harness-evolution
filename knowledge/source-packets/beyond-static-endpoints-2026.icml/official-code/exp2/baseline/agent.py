"""
Baseline Agent：OpenRouter 对话循环 + JSON tool_call/stop，进程内调用 DirectusToolRunner。
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from .case_prompts import get_case_user_prompt
from .directus_tools import TOOL_LIST_DOC, DirectusToolRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_STEPS_DEFAULT = 25

_STEP_SEP = "=" * 60


def _print_step_block(step: int, title: str, body: str, *, verbose: bool) -> None:
    if not verbose:
        return
    print(f"\n{_STEP_SEP}\n[Step {step}] {title}\n{_STEP_SEP}\n{body}\n", flush=True)


SYSTEM_PROMPT_TEMPLATE = """你是一个通过 MCP 暴露的工具操作内容后端数据的 Agent。

输出要求（必须遵守）：
- 每一轮你只输出一个 JSON 对象，且必须是合法 JSON。
- 不要输出 Markdown、不要代码围栏、不要自然语言段落。
- 允许的 action 仅有："tool_call" 和 "stop"。

当 action 为 "tool_call" 时：
- 字段 "tool" 为 MCP 服务器注册的工具名称（须与下方说明书中的工具名完全一致）。
- 字段 "arguments" 为传给该工具的参数对象，键名与说明书中一致。

当 action 为 "stop" 时：
- 必须包含 "reason" 字符串，简要说明为何认为任务已完成。
- 系统会在 stop 之后独立验证数据库状态；stop 不代表一定通过验证。

决策要求：
- 仅根据对话历史与用户任务描述、以及工具返回内容推理；不要编造未在工具返回中出现的 id 或列表。
- 若任务需要多步查询与写入，请分步调用工具。

【MCP 工具说明书】
{TOOL_LIST}

最大步数：本任务最多 {MAX_STEPS} 轮模型决策；请合理安排并在完成时 stop。
"""


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = REPO_ROOT / ".env"
    if env_path.is_file():
        # 默认 load_dotenv 不覆盖已有环境变量；若 shell/User 环境里有旧 key，会盖过根目录 .env 的修改
        load_dotenv(env_path, override=True)


def load_openrouter_config() -> tuple[str, str, str]:
    _load_dotenv()
    api_key = (os.getenv("OPENROUTER_API_KEY") or "").strip().strip('"')
    model = (os.getenv("OPENROUTER_MODEL") or "").strip().strip('"')
    base = (
        os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"
    ).strip().strip('"')
    if not api_key or not model:
        raise RuntimeError(
            "请在项目根 .env 中配置 OPENROUTER_API_KEY 与 OPENROUTER_MODEL"
        )
    return api_key, model, base.rstrip("/")


def extract_json_object(text: str) -> Dict[str, Any]:
    s = text.strip()
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("输出中未找到 JSON 对象")
    return json.loads(s[start : end + 1])


def build_system_prompt(max_steps: int) -> str:
    return SYSTEM_PROMPT_TEMPLATE.replace("{TOOL_LIST}", TOOL_LIST_DOC).replace(
        "{MAX_STEPS}", str(max_steps)
    )


@dataclass
class BaselineAgentResult:
    case_id: int
    steps_used: int
    stop_reason: str
    validation_pending: bool
    transcript: List[Dict[str, Any]] = field(default_factory=list)
    last_parse_error: Optional[str] = None
    last_assistant_raw: str = ""
    llm_bytes_sent: int = 0
    llm_bytes_received: int = 0


def _chat_completion(
    messages: List[Dict[str, str]],
    *,
    api_key: str,
    model: str,
    base_url: str,
    timeout: float = 120.0,
) -> tuple[str, int, int]:
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload_bytes = len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    with httpx.Client(timeout=timeout) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        response_bytes = len(resp.content or b"")
    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    content = msg.get("content")
    if not content:
        raise RuntimeError(f"LLM 返回无 content: {repr(data)[:500]}")
    return content, payload_bytes, response_bytes


def run_baseline_agent(
    case_id: int,
    *,
    max_steps: int = MAX_STEPS_DEFAULT,
    transcript: Optional[List[Dict[str, Any]]] = None,
    verbose: bool = True,
) -> BaselineAgentResult:
    """
    执行 Agent 循环；工具层使用 directus_tools 内写死的 Directus 连接，与验证器所用 .env 连接相互独立。
    transcript 若传入则原地追加逐步记录（便于写日志）。
    verbose 为 True 时，在终端逐步打印模型原始返回与每次工具（Directus）返回全文。
    """
    api_key, model, base_url = load_openrouter_config()
    runner = DirectusToolRunner()
    log = transcript if transcript is not None else []

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": build_system_prompt(max_steps)},
        {"role": "user", "content": get_case_user_prompt(case_id)},
    ]

    result = BaselineAgentResult(
        case_id=case_id,
        steps_used=0,
        stop_reason="",
        validation_pending=True,
        transcript=log,
    )

    try:
        for step in range(1, max_steps + 1):
            result.steps_used = step
            try:
                raw, llm_sent, llm_recv = _chat_completion(
                    messages, api_key=api_key, model=model, base_url=base_url
                )
                result.llm_bytes_sent += llm_sent
                result.llm_bytes_received += llm_recv
            except Exception as e:
                result.stop_reason = "llm_error"
                result.last_parse_error = str(e)
                log.append({"step": step, "type": "llm_error", "error": str(e)})
                _print_step_block(
                    step,
                    "LLM 请求失败（无模型返回正文）",
                    str(e),
                    verbose=verbose,
                )
                return result

            result.last_assistant_raw = raw
            log.append({"step": step, "type": "assistant", "content": raw})
            _print_step_block(step, "Agent（模型）返回", raw, verbose=verbose)

            try:
                action = extract_json_object(raw)
            except Exception as e:
                err = f"JSON 解析失败: {e}"
                result.last_parse_error = err
                messages.append({"role": "assistant", "content": raw})
                messages.append(
                    {
                        "role": "user",
                        "content": f"系统拒绝：{err}。请仅输出单个合法 JSON 对象（action 为 tool_call 或 stop），不要其它文字。",
                    },
                )
                log.append({"step": step, "type": "parse_error", "error": err})
                _print_step_block(step, "JSON 解析失败（本步将重试）", err, verbose=verbose)
                continue

            act = action.get("action")
            if act == "stop":
                result.stop_reason = "stop"
                log.append(
                    {
                        "step": step,
                        "type": "stop",
                        "reason": action.get("reason", ""),
                    }
                )
                reason = action.get("reason", "")
                _print_step_block(
                    step,
                    "Agent 结束（action=stop）",
                    f"reason: {reason!r}",
                    verbose=verbose,
                )
                return result

            if act != "tool_call":
                err = f"非法 action: {act!r}"
                result.last_parse_error = err
                messages.append({"role": "assistant", "content": raw})
                messages.append(
                    {
                        "role": "user",
                        "content": f"系统拒绝：{err}。仅允许 tool_call 或 stop。",
                    },
                )
                log.append({"step": step, "type": "bad_action", "error": err})
                _print_step_block(step, "非法 action（本步将重试）", err, verbose=verbose)
                continue

            tool = action.get("tool")
            arguments = action.get("arguments")
            if not isinstance(arguments, dict):
                arguments = {}

            if verbose:
                call_desc = json.dumps(
                    {"tool": tool, "arguments": arguments},
                    ensure_ascii=False,
                    indent=2,
                )
                _print_step_block(step, "工具调用（入参）", call_desc, verbose=verbose)

            tool_out = runner.call(str(tool), arguments)
            _print_step_block(
                step,
                "接口（Directus / 工具执行）返回",
                tool_out,
                verbose=verbose,
            )
            messages.append({"role": "assistant", "content": raw})
            messages.append(
                {
                    "role": "user",
                    "content": "工具执行结果（JSON 字符串如下，请据此继续决策下一步 JSON）：\n"
                    + tool_out,
                },
            )
            log.append(
                {
                    "step": step,
                    "type": "tool_result",
                    "tool": tool,
                    "arguments": arguments,
                    "api_response": tool_out,
                }
            )

        result.stop_reason = "max_steps"
        log.append({"step": max_steps, "type": "terminated", "reason": "max_steps"})
        _print_step_block(
            max_steps,
            "达到最大步数（max_steps）",
            f"max_steps={max_steps}",
            verbose=verbose,
        )
        return result
    finally:
        runner.close()


def main() -> None:
    """调试：python -m exp2.baseline.agent <case_id>（需已初始化 Directus）"""
    if len(sys.argv) < 2:
        print("用法: python -m exp2.baseline.agent <case_id>", file=sys.stderr)
        sys.exit(2)
    cid = int(sys.argv[1])
    r = run_baseline_agent(cid)
    print(
        json.dumps(
            {"stop_reason": r.stop_reason, "steps": r.steps_used},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
