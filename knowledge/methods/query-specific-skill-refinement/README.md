# Query-specific Skill Refinement

在正式执行任务前，让 refinement agent 在目标任务环境中试用全部候选 Skill，根据探索结果删减、纠错和组合内容，生成仅服务当前任务的新 Skill，再交给执行 agent。

| 决策项 | 内容 |
| --- | --- |
| 适合解决 | 候选 Skill 与任务部分相关，但信息分散、含噪声、存在缺口，或原始描述不足以促使执行 agent 加载和使用。 |
| 输入 | 当前任务说明、检索得到的多个 Skill、可探索的目标任务环境、Skill 编写指导。 |
| 干预 | refinement agent 阅读全部 Skill，在目标环境中尝试任务并自评哪些知识有效、错误或缺失；随后保留有效内容、纠错、补充探索所得知识，并跨 Skill 合并为任务专用 Skill。 |
| 输出 | 一个或多个任务专用 Skill；原论文的实现随后用它们替换该任务原有的候选 Skill。 |
| 必要条件 | 初始 Skill 集合已经覆盖任务所需的重要知识；环境允许额外探索；执行 harness 能发现并加载生成的 Skill。 |
| 不宜使用 | 候选 Skill 基本不包含相关知识；任务环境不可安全探索；一次额外 rollout 的成本不可接受；自评错误风险高且缺少后续验证。 |
| 成本与风险 | 每个任务增加一次完整探索和 Skill 生成；refinement agent 看不到真实 verifier，只能自评，可能保留错误结论或把任务偶然细节写入 Skill。 |
| 原始证据 | 在 Terminal-Bench 2.0 上，检索后再做该 refinement 对三个模型/harness 组合均有提升；在 SkillsBench 的低覆盖条件下存在无效或退化。具体数值见[实验依据](evidence/experiments.md)。 |
| 证据边界 | 论文验证的是“检索 + refinement + 相应执行 harness”的完整流程，不能把收益单独归因于 Skill 文本，也没有验证在 Terminus-KIRA H0 上的迁移效果。 |
| 本地状态 | 已静态核对论文和固定版本核心代码；尚未运行原实验，尚未接入共同 H0。 |

## 操作流程

1. 把任务说明、候选 Skill 和 Skill 编写指导放入目标任务环境，但不向 refinement agent 暴露真实 verifier。
2. 让 refinement agent 阅读全部候选 Skill，并在相同环境中尝试任务一次。
3. 根据探索过程识别有效、误导和缺失的知识，合并跨 Skill 的互补内容。
4. 输出任务专用 Skill，随后由独立的执行 agent 使用；保留原始 Skill 和生成过程以便核验。

## 迁移与组合

| 关系 | 判断 |
| --- | --- |
| 上游依赖 | 依赖 Skill 检索或人工候选选择；检索覆盖不足时，refinement 很难产生可靠的新知识。 |
| 可替代方法 | Query-agnostic refinement 可提前离线整理 Skill，推理时成本较低，但不能针对任务探索或跨 Skill 组合。 |
| 可组合模块 | 可与 Skill 质量过滤、渐进加载、执行后验证和失败回滚组合，以降低错误自评带来的风险。 |
| 对共同 H0 的迁移 | Terminus-KIRA 当前没有这套 Skill 准备流程。可借鉴“先试用、再整理”的机制扩展其 Skill 接口，但这是待验证的迁移假设。 |
| 对优化 agent 的借鉴 | 可将同样顺序用于方法知识：先在 train 任务实现候选机制，再根据 trace 修订实现说明。原论文没有验证“用论文方法知识优化 harness”，不能把这种借鉴写成论文结论。 |

真正实现前继续读取：[实现依据](evidence/implementation.md)、[实验依据](evidence/experiments.md)、[核验记录](evidence/verification.md)和[原始材料](../../sources/2604.04323/README.md)。
