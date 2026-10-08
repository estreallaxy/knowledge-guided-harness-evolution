# Berkeley Function Calling Leaderboard

## 方法概要

BFCL 提供覆盖单轮、并行、串行和多轮函数调用的标准化评价，用于比较 Agent 选择工具、生成参数和组织调用链的能力。

## 可迁移机制

- 按调用类型拆分工具使用能力。
- 对串行调用和并行调用分别记录结果。
- 将工具调用正确性与多轮 Agent 行为分开统计。

## 使用边界

适合工具调用回归测试和能力对照，不应直接替代 Terminal-Bench 的任务评分器。

## 代码

官方代码已保存到 [`code/`](code/)，来源为 [ShishirPatil/gorilla](https://github.com/ShishirPatil/gorilla)。

## 证据

正式论文材料：[BFCL 来源](../../sources/2025.icml.bfcl/README.md)。第一阶段仅完成收集，未做本地验证。
