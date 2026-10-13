# 实验依据

下表来自论文 Table 2。`Retrieved` 是先检索 Skill 后直接执行，`+ refinement` 是增加一次 query-specific refinement 后再执行；Pass 和 Load 均为百分比。

## Terminal-Bench 2.0

89 个任务，每题运行 3 次。不同模型使用不同执行 harness，因此只能比较同一行组内的前后变化。

| 模型 / Harness | 无 Skill Pass | Retrieved Pass | Retrieved Load | + refinement Pass | + refinement Load | Pass 变化 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.6 / Claude Code | 57.7 | 61.4 | 40.8 | 65.5 | 74.9 | +4.1 |
| Kimi K2.5 / Terminus-2 | 46.6 | 50.6 | 79.0 | 56.2 | 93.6 | +5.6 |
| Qwen3.5-397B-A17B / Qwen-Code | 44.7 | 44.2 | 31.1 | 49.1 | 42.3 | +4.9 |

## SkillsBench

84 个有效任务，每个条件运行 3 次。这里展示 initial Skill 覆盖较高和较低时的相反结果。

| 检索条件 | 模型 | Retrieved Pass | + refinement Pass | 变化 |
| --- | --- | ---: | ---: | ---: |
| curated Skill 仍在检索池 | Claude Opus 4.6 | 40.1 | 48.2 | +8.1 |
| curated Skill 仍在检索池 | Kimi K2.5 | 33.5 | 26.7 | -6.8 |
| curated Skill 仍在检索池 | Qwen3.5-397B-A17B | 26.7 | 30.8 | +4.1 |
| curated Skill 已移出检索池 | Claude Opus 4.6 | 38.4 | 37.9 | -0.5 |
| curated Skill 已移出检索池 | Kimi K2.5 | 19.8 | 23.1 | +3.3 |
| curated Skill 已移出检索池 | Qwen3.5-397B-A17B | 19.7 | 21.5 | +1.8 |

论文用 GPT-5.4 对初始 Skill 集合做 1–5 分覆盖度判断：有效条件的平均覆盖度至少为 `3.83`，低收益条件不高于 `3.49`。这支持作者关于“refinement 放大已有知识，而不是凭空生成知识”的解释，但该阈值来自事后分析，不能直接当作新任务的固定准入门槛。

## 证据限制

- TB2 的结果属于完整流程，无法从表中分离“内容变好”和“更愿意加载 Skill”各自贡献。
- 论文没有提供与本研究 30/19/40 划分相同的结果，也没有在 Terminus-KIRA H0 上运行。
- 未统一报告 refinement 的 token、美元费用和墙钟开销；只能确定每个任务增加一次探索 rollout。
- 当前仓库没有原始逐次 rollout，无法独立计算方差、置信区间或逐题配对显著性。
