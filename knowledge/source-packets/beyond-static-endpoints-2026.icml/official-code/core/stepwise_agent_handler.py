"""
LLM-driven stepwise fallback handler.

This module implements a minimal multi-turn loop:
1) provide initial task + tool list + prior trace
2) model returns one structured action each turn
3) execute one MCP tool call
4) repeat until stop/final_answer or max_steps
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from config import Config
from .stepwise_executor import StepwiseExecutor

logger = logging.getLogger(__name__)

_MAX_INPUT_CONTEXT_CHARS = 12000


def _compose_task_description(user_query: str, input_data: str) -> str:
    """
    合并 user_query 与 input_data JSON 中的常见任务字段；避免把整段 stepwise_plan 塞进 prompt。
    """
    q = (user_query or "").strip()
    payload: Any = None
    raw = (input_data or "").strip()
    if raw:
        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            payload = None
    hints: List[str] = []
    if isinstance(payload, dict):
        for key in ("task", "user_query", "goal", "instruction", "initial_task"):
            v = payload.get(key)
            if isinstance(v, str) and v.strip():
                t = v.strip()
                if t != q:
                    hints.append(t)
        if not q:
            for key in ("task", "user_query", "goal", "instruction", "initial_task"):
                v = payload.get(key)
                if isinstance(v, str) and v.strip():
                    q = v.strip()
                    break
    if q and hints:
        extra = "\n".join(h for h in hints if h and h != q)
        if extra:
            q = f"{q}\n---\n{extra}"
    if not q and raw:
        if isinstance(payload, dict):
            slim = {k: v for k, v in payload.items() if k != "stepwise_plan"}
            try:
                q = json.dumps(slim, ensure_ascii=False)[:_MAX_INPUT_CONTEXT_CHARS]
            except (TypeError, ValueError):
                q = raw[:_MAX_INPUT_CONTEXT_CHARS]
        else:
            q = raw[:_MAX_INPUT_CONTEXT_CHARS]
    return q or "(no task description)"


def _compact_tool_spec(tool: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(tool, dict):
        return {}
    return {
        "name": tool.get("name"),
        "description": tool.get("description", ""),
        "inputSchema": tool.get("inputSchema", {}),
    }


def _load_available_tools(wasm_runtime: Any) -> List[Dict[str, Any]]:
    sm = getattr(wasm_runtime, "session_manager", None)
    if sm is None:
        return []
    try:
        if hasattr(sm, "get_tools"):
            tools = sm.get_tools("local_apis")
            if isinstance(tools, list) and tools:
                return [_compact_tool_spec(t) for t in tools]
            all_tools = sm.get_tools()
            if isinstance(all_tools, list):
                return [_compact_tool_spec(t) for t in all_tools]
        if hasattr(sm, "get_all_tools_by_server"):
            merged: List[Dict[str, Any]] = []
            by_server = sm.get_all_tools_by_server()
            if isinstance(by_server, dict):
                for _, tool_list in by_server.items():
                    if isinstance(tool_list, list):
                        merged.extend(_compact_tool_spec(t) for t in tool_list)
            return merged
    except Exception as e:
        logger.warning("load tools for stepwise handler failed: %s", e)
    return []


def _build_messages(
    *,
    task: str,
    tools: List[Dict[str, Any]],
    trace: List[Dict[str, Any]],
    turn: int,
    max_steps: int,
) -> List[Dict[str, str]]:
    system_prompt = (
        "You are a stepwise tool-calling planner. "
        "On each turn, output JSON only with exactly one action.\n"
        "Schema:\n"
        "{"
        '"tool_name": string,'
        '"arguments": object,'
        '"stop": boolean,'
        '"final_answer": string'
        "}\n"
        "Rules:\n"
        "- If more tool calls are needed, set stop=false and provide tool_name+arguments.\n"
        "- If task is complete, set stop=true and provide final_answer.\n"
        "- Never output text outside JSON."
    )
    user_payload = {
        "task": task,
        "turn": turn,
        "max_steps": max_steps,
        "tools": tools,
        "trace": trace,
    }
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
    ]


async def _call_llm_for_step(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    llm = Config.get_llm_config()
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
        resp = await client.post(
            f"{llm['base_url']}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {llm['api_key']}",
            },
            json={
                "model": llm["model"],
                "temperature": 0,
                "max_tokens": 800,
                "messages": messages,
            },
        )
        resp.raise_for_status()
        data = resp.json()
    content = (
        ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    ).strip()
    if content.startswith("```"):
        lines = [ln for ln in content.splitlines() if not ln.strip().startswith("```")]
        content = "\n".join(lines).strip()
    parsed = json.loads(content)
    if not isinstance(parsed, dict):
        raise ValueError("stepwise llm action must be a JSON object")
    return parsed


def build_llm_stepwise_handler(max_steps: int = 8):
    async def _handler(
        *,
        wasm_runtime: Any,
        user_query: str,
        input_data: str,
        module_id: str,
        fallback_reason: str,
        prior_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        _ = (module_id, fallback_reason, prior_result)
        try:
            if hasattr(wasm_runtime, "initialize_session_manager_if_needed"):
                wasm_runtime.initialize_session_manager_if_needed()
        except Exception as e:
            logger.warning("stepwise agent initialize_session_manager_if_needed: %s", e)

        tools = _load_available_tools(wasm_runtime)
        if len(tools) == 0:
            return {
                "success": False,
                "strategy": "stepwise_agent_no_tools",
                "error": "no_mcp_tools_available_for_stepwise_agent",
                "data": {"stepwise_trace": []},
            }

        task = _compose_task_description(user_query, input_data)
        executor = StepwiseExecutor(wasm_runtime)
        trace: List[Dict[str, Any]] = []
        final_answer = ""

        for turn in range(1, max_steps + 1):
            messages = _build_messages(
                task=task,
                tools=tools,
                trace=trace,
                turn=turn,
                max_steps=max_steps,
            )
            try:
                action = await _call_llm_for_step(messages)
            except Exception as e:
                return {
                    "success": False,
                    "strategy": "stepwise_agent_llm_error",
                    "error": str(e),
                    "data": {"stepwise_trace": trace},
                }

            stop = bool(action.get("stop", False))
            if stop:
                final_answer = str(action.get("final_answer", "") or "")
                return {
                    "success": True,
                    "strategy": "stepwise_agent_complete",
                    "error": None,
                    "data": {
                        "stepwise_trace": trace,
                        "final_answer": final_answer,
                        "turns": turn,
                    },
                }

            tool_name = str(action.get("tool_name") or "").strip()
            arguments = action.get("arguments") or {}
            if not tool_name or not isinstance(arguments, dict):
                return {
                    "success": False,
                    "strategy": "stepwise_agent_invalid_action",
                    "error": "invalid stepwise action: require tool_name and object arguments",
                    "data": {"stepwise_trace": trace, "action": action},
                }

            tool_resp = await executor.invoke_tool(tool_name, arguments)
            trace.append(
                {
                    "turn": turn,
                    "tool": tool_name,
                    "arguments": arguments,
                    "response": tool_resp,
                }
            )
            if tool_resp is None or (
                isinstance(tool_resp, dict) and not tool_resp.get("success", True)
            ):
                err = None
                if isinstance(tool_resp, dict):
                    err = tool_resp.get("error") or tool_resp.get("message")
                return {
                    "success": False,
                    "strategy": "stepwise_agent_tool_failed",
                    "error": err or "tool_failed",
                    "data": {"stepwise_trace": trace},
                }

        return {
            "success": False,
            "strategy": "stepwise_agent_max_steps_reached",
            "error": f"max_steps_reached:{max_steps}",
            "data": {"stepwise_trace": trace, "final_answer": final_answer},
        }

    return _handler

