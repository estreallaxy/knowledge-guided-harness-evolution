# method-reproduction（周梦凡 / zhouMF）

本人负责的方法知识的**离线可运行 demo**：把每篇论文的机制落成不联网、不依赖模型的
最小实现，用来验证「机制是否讲得通、实现是否与论文一致」，再判断能否迁移到 harness。
论文、官方代码与来源锚点在 `knowledge/source-packets/`，本目录只放复现产物。

> 这些 demo 验证的是**机制语义**，不是论文数值。每个目录的 `evidence/` 记录已核对项、
> 未运行项与主张边界；不得把 demo 输出写成论文的分数或成本曲线。

## 目录

| 方法 | 方向 | 来源包 | 离线自测命令 |
| --- | --- | --- | --- |
| Query-specific Skill Refinement | 指令与 Skill | [skill-usage-2604.04323](../../../knowledge/source-packets/skill-usage-2604.04323/) | `python3 code/refine_skills.py demo` |
| Agent Skill Induction | 指令与 Skill | [agent-skill-induction-2504.06821](../../../knowledge/source-packets/agent-skill-induction-2504.06821/) | `python3 code/skill_induction.py demo` |
| Failure-guided Context Compression | 上下文管理与压缩 | [acon-2510.00615](../../../knowledge/source-packets/acon-2510.00615/) | `python3 code/context_compression.py demo` |
| Proactive Context Folding | 上下文管理与压缩 | [agentfold-2510.24699](../../../knowledge/source-packets/agentfold-2510.24699/) | `python3 code/context_folding.py demo` |
| Frugal LLM Cascade | 模型选择与资源分配 | [frugalgpt-2305.05176](../../../knowledge/source-packets/frugalgpt-2305.05176/) | `python3 code/cascade_router.py demo` |
| Preference-based LLM Routing | 模型选择与资源分配 | [routellm-2406.18665](../../../knowledge/source-packets/routellm-2406.18665/) | `python3 code/preference_router.py demo` |
| Plan-and-Solve Prompting | 规划与任务进度管理（非本人来源包） | arXiv:2305.04091 | `python3 code/plan_and_solve.py demo` |
| Adaptive Planning from Feedback | 规划与任务进度管理（非本人来源包） | arXiv:2305.16653 | `python3 code/adaptive_plan.py demo` |

每个目录的结构一致：

```text
<method>/
├── README.md      # 什么时候用、机制、本项目边界、直接运行
├── code/          # 可运行实现（核心与自测仅用标准库，不联网）
└── evidence/      # implementation / verification / experiments 三条证据
```

## 怎么跑

每个 demo 都是纯标准库、无网络、无模型调用，输出机制级自测结论：

```bash
cd reproductions/zhouMF/method-reproduction/<method>
python3 code/<file>.py demo
```

需要真实模型的 `run-live` / `solve-live` 入口只在显式提供 OpenAI 兼容端点与凭据时使用
（依赖列在各目录 `code/requirements.txt`，凭据不入库）。

## 核验状态

- 2026-10-13：8 个 demo 全部在当前仓库重跑通过（退出码 0），路径已按 `main` 的新目录结构修正。
- 上游仓库与固定 revision 记在各目录 `code/UPSTREAM.md`；未在本项目运行论文的原始实验。
- 规划方向的两个方法（Plan-and-Solve、AdaPlanner）不在本人负责的来源包范围内，
  仅保留离线 demo，论文与官方代码见对应 arXiv 页面。
