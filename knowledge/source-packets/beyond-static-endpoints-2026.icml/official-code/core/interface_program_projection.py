"""
论文 Step 2：服务端 interface-program projection（Π）的最小实现。

将候选 Rust tool program 收敛到可编译、可静态分析、与运行时 replay 约定一致的形式：
先做结构校验（见 ``tool_program_validator``），再做轻量规范化（换行/BOM），
不修改业务语义。完整 AST→IR  lowering 可作为后续工作。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .tool_program_validator import collect_structural_violations

logger = logging.getLogger(__name__)


@dataclass
class ProjectionResult:
    ok: bool
    projected_source: str
    errors: List[str] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)


def project_tool_program(
    source_code: str,
    semantic_info: Optional[Dict[str, Any]] = None,
) -> ProjectionResult:
    """
    Π：候选程序 → 受限接口程序面（此处为「校验 + 规范化后的同源 Rust」）。

    semantic_info 预留与任务/API 规格交叉检查（当前最小实现仅记录 module_id）。
    """
    _ = semantic_info or {}
    diagnostics: List[str] = ["projection:structural_validate"]

    errors = collect_structural_violations(source_code)
    if errors:
        logger.warning("Π projection rejected: %s", errors[:5])
        return ProjectionResult(
            ok=False,
            projected_source="",
            errors=errors,
            diagnostics=diagnostics + ["projection:rejected"],
        )

    projected = source_code.replace("\r\n", "\n").lstrip("\ufeff")
    if projected != source_code:
        diagnostics.append("projection:normalized_crlf_or_bom")

    diagnostics.append("projection:accepted")
    return ProjectionResult(
        ok=True,
        projected_source=projected,
        errors=[],
        diagnostics=diagnostics,
    )
