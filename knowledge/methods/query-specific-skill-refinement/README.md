# Query-specific Skill Refinement

## 什么时候使用

| 判断 | 内容 |
| --- | --- |
| 要解决的问题 | 候选 Skill 已包含有用知识，但内容分散、冗余、冲突，或没有针对当前任务组织。 |
| 使用前提 | 任务具有可探索环境；`environment/skills/` 中已有候选 Skill；允许增加一次 refinement rollout。 |
| 输入 | benchmark 任务目录、任务说明、候选 Skill、refinement agent 与模型配置。 |
| 输出 | 每个任务一组重新组织的任务专用 Skill，先保存到独立目录，不直接覆盖原 Skill。 |
| 不使用 | 候选 Skill 基本不相关、环境不能安全探索、额外 rollout 超出预算，或产物无法再用 benchmark 验证。 |
| 主要风险 | refinement agent 看不到真实 verifier，只能自评，可能把错误判断或任务偶然细节写入新 Skill。 |

## 怎么工作

1. 复制任务环境，将原始 Skill 变成只读候选输入，并移除真实测试反馈。
2. refinement agent 阅读候选 Skill，在目标环境中进行一次受限探索。
3. 根据探索结果保留有效内容、删除噪声、修正错误并合并互补知识。
4. 新 Skill 保存到隔离目录，由独立执行实验验证；通过后才应用。

本方法改造的是执行前的 Skill 准备流程，不直接修改 Terminus-KIRA，也不自动优化 harness 源码。它依赖上游候选知识的覆盖质量，可与 Skill 检索、质量过滤、渐进加载和失败回滚组合。

## 直接运行

代码、提示模板和依赖已经保存在 [`code/`](code/)，运行时不需要再查论文或 GitHub：

```bash
python code/refine_skills.py prepare \
  --tasks-dir /path/to/tasks \
  --workspace /path/to/refinement-workspace \
  --agent claude-code \
  --model claude-opus-4-6

harbor run -c /path/to/refinement-workspace/harbor-refine-skills.yaml

python code/refine_skills.py collect \
  --tasks-dir /path/to/tasks \
  --workspace /path/to/refinement-workspace
```

`collect` 只验证并收集生成结果。完成独立 benchmark 检查后，才执行：

```bash
python code/refine_skills.py apply \
  --tasks-dir /path/to/tasks \
  --workspace /path/to/refinement-workspace
```

| 文件 | 用途 |
| --- | --- |
| [`code/refine_skills.py`](code/refine_skills.py) | 准备隔离任务、生成 Harbor 配置、收集结果并在需要时应用。 |
| [`code/refinement_prompt.md`](code/refinement_prompt.md) | refinement agent 实际收到的完整任务说明。 |
| [`code/requirements.txt`](code/requirements.txt) | Python 依赖清单；当前实现仅使用标准库。Harbor、Docker 和模型凭据属于运行环境依赖。 |

论文结果、固定版本映射和核验状态保存在 [`evidence/`](evidence/)，仅在审计方法来源或研究结论时读取。
