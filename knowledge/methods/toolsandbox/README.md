# ToolSandbox

## 方法概要

ToolSandbox 将工具使用建模为有状态、可多轮交互的环境，而不是独立函数调用。核心关注工具调用之间的隐式状态依赖，并同时评价中间里程碑和最终状态。

## 可迁移机制

- 为工具调用记录输入、输出和环境状态变化。
- 将多轮调用中的状态依赖作为诊断信号。
- 同时保留 intermediate milestone 和 final outcome，避免只看最终答案。

## 使用边界

适合工具会改变共享环境状态、后续调用依赖前序结果的任务。论文基准本身的评价效果不能直接等同于当前 Harness 的迁移效果。

## 代码

官方代码已保存到 [`code/`](code/)，来源为 [apple/ToolSandbox](https://github.com/apple/ToolSandbox)。

## 证据

正式论文材料：[ToolSandbox 来源](../../sources/2025.findings-naacl.65/README.md)。第一阶段仅完成收集，未做本地验证。
