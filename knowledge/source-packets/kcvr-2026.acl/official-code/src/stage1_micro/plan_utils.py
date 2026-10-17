from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True)
class PlanSerializeConfig:
    max_tp_anchors: int = 2
    max_kc_concepts: int = 12
    max_deps: int = 5
    include_definitions: bool = False


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_cn(stage: str) -> str:
    """Map canonical stage name to Chinese.

    Args:
        stage: intro/exposition/interaction/conclusion.

    Returns:
        Chinese stage name.
    """
    return {
        "intro": "导入",
        "exposition": "讲授",
        "interaction": "互动",
        "conclusion": "总结",
    }.get(stage, stage)


def _id_to_name(ids: Sequence[str], id2name: Mapping[str, str]) -> List[str]:
    return [id2name.get(i, i) for i in ids]


def serialize_plan(
    plan: Dict[str, Any],
    id2kc: Mapping[str, str],
    id2tp: Mapping[str, str],
    cfg: Optional[PlanSerializeConfig] = None,
) -> str:
    """Serialize a plan.json into a natural language prompt block.

    This follows the design in `第一个模块sg-planner的效果和输出.md`:
    - Concept set (KC names)
    - TP anchors (2-3)
    - Progression path pi (most important)
    - Dependency constraints (optional)

    Args:
        plan: Plan dict.
        id2kc: KC id -> name mapping.
        id2tp: TP id -> name mapping.
        cfg: Optional serialization config.

    Returns:
        Plan prompt text.
    """
    cfg = cfg or PlanSerializeConfig()
    nodes_kc: List[str] = list(plan.get("nodes_kc") or plan.get("kc_nodes") or [])
    nodes_tp: List[str] = list(plan.get("nodes_tp") or plan.get("tp_nodes") or [])
    pi: List[str] = list(plan.get("pi") or plan.get("pi_kc") or [])

    kc_names = _id_to_name(nodes_kc, id2kc)[: cfg.max_kc_concepts]
    tp_names = _id_to_name(nodes_tp, id2tp)[: cfg.max_tp_anchors]
    pi_names = _id_to_name(pi, id2kc)[: cfg.max_kc_concepts]

    concept_text = "知识概念: " + " | ".join(kc_names) if kc_names else "知识概念: (空)"
    anchor_text = "教材锚点: " + " → ".join(tp_names) if tp_names else "教材锚点: (空)"
    path_text = "教学递进: " + " → ".join(pi_names) if pi_names else "教学递进: (空)"

    deps_lines: List[str] = []
    edges_based_on = plan.get("edges_based_on") or (plan.get("edges") or {}).get("BASED_ON") or []
    # edges_based_on items are [post, pre] (post depends on pre)
    for item in edges_based_on[: cfg.max_deps]:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            continue
        post, pre = str(item[0]), str(item[1])
        deps_lines.append(f"- {id2kc.get(post, post)} 依赖 {id2kc.get(pre, pre)}")
    dep_text = "依赖关系:\n" + "\n".join(deps_lines) if deps_lines else ""

    parts = [
        "[知识规划]",
        concept_text,
        anchor_text,
        path_text,
    ]
    if dep_text:
        parts.append(dep_text)
    return "\n".join(parts)


def build_micro_prompt(
    stage: str,
    plan_text: str,
    transcript: str,
    num_images: int,
) -> Tuple[str, List[str]]:
    # Build ShareGPT format prompt for MLLM training
    image_tokens = ["<image>"] * max(0, int(num_images))
    header = f"[视频片段 | {_stage_cn(stage)}]\n"
    # KCVR objective-driven constraints: force plan-following and structured output.
    constraints = (
        "[任务]\n"
        "你将收到：8帧课堂视频截图 + 知识规划(Plan子图与教学递进) + 课堂记录(Transcript)。\n"
        "请输出：先给“学习目标”，再给“结构化摘要”。\n\n"
        "[硬约束]\n"
        "1) 必须围绕[知识规划]中的概念展开，优先覆盖教学递进(pi)上的概念。\n"
        "2) 结构化摘要必须尽量按照“教学递进”顺序组织，避免跳跃。\n"
        "3) 输出必须严格使用如下两段标题：\n"
        "### 学习目标\n"
        "### 结构化摘要\n"
    )
    prompt = (
        "".join(image_tokens)
        + "\n"
        + header
        + "\n"
        + constraints
        + "\n"
        + plan_text
        + "\n\n[课堂记录]\n"
        + transcript
        + "\n"
    )
    return prompt, image_tokens


