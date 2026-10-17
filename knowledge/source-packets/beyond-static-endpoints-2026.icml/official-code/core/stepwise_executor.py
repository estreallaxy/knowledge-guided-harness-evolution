"""
逐步 MCP 调用执行器（Program-mode 失败后的 safe_stepwise 降级路径）。

不依赖 ``exp2/baseline``：通过既有 ``WasmRuntime._perform_actual_mcp_call`` 与宿主 SessionManager 发工具调用。
可选 ``input_data`` JSON 字段 ``stepwise_plan`` 描述显式步骤；无计划时由上层 handler 或返回 ``stepwise_no_plan``。
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

ToolStep = Tuple[str, Dict[str, Any]]


@dataclass
class StepwiseRunResult:
    success: bool
    trace: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


class StepwiseExecutor:
    """在 Wasm 宿主上按序执行 MCP 工具（同步 MCP 路径，异步包装）。"""

    def __init__(self, wasm_runtime: Any):
        self._wasm = wasm_runtime

    async def invoke_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._wasm._perform_actual_mcp_call(tool_name, parameters),
        )

    async def run_sequence(self, steps: List[ToolStep]) -> StepwiseRunResult:
        trace: List[Dict[str, Any]] = []
        for tool_name, params in steps:
            logger.info("StepwiseExecutor step: %s", tool_name)
            resp = await self.invoke_tool(tool_name, params)
            trace.append({"tool": tool_name, "response": resp})
            if resp is None or (isinstance(resp, dict) and not resp.get("success", True)):
                err = None
                if isinstance(resp, dict):
                    err = resp.get("error") or resp.get("message")
                return StepwiseRunResult(False, trace=trace, error=err or "tool_failed")
        return StepwiseRunResult(True, trace=trace, error=None)


def parse_stepwise_plan_from_input(input_data: str) -> List[ToolStep]:
    """
    从 ``input_data`` JSON 解析 ``stepwise_plan``::

        {"stepwise_plan": [{"tool": "x", "arguments": {...}}, ...]}
    """
    try:
        payload = json.loads(input_data)
    except (json.JSONDecodeError, TypeError):
        return []
    if not isinstance(payload, dict):
        return []
    raw = payload.get("stepwise_plan")
    if not isinstance(raw, list):
        return []
    out: List[ToolStep] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        tool = item.get("tool")
        if not tool:
            continue
        args = item.get("arguments") or item.get("parameters") or {}
        if not isinstance(args, dict):
            args = {}
        out.append((str(tool), dict(args)))
    return out
