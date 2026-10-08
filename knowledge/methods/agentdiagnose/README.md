# AgentDiagnose

## 方法概要

AgentDiagnose 提供面向 Agent trajectory 的诊断工具思路，围绕任务分解、历史观察、回溯探索和自验证组织分析过程。

## 可迁移机制

- 保存可按步骤展开的完整轨迹。
- 结合任务目标、历史观察和动作结果定位失败点。
- 将回溯和自验证作为诊断步骤，而不是直接修改 Harness。

## 使用边界

依赖结构化 trajectory 和足够的环境观察；当前仅完成论文收集，尚未验证其接口能否接入 Meta-Harness。

## 代码

官方代码已收集到 `code/`，来源为论文作者的 AgentDiagnose 仓库。
代码尚未在当前 Harness 上运行验证。

## 证据

正式论文材料：[AgentDiagnose 来源](../../sources/2025.emnlp-demos.agentdiagnose/README.md)。第一阶段仅完成收集，未做本地验证。
