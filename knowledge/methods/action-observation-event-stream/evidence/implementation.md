# 实现依据

核对代码来源：[`All-Hands-AI/OpenHands`](https://github.com/All-Hands-AI/OpenHands)。

| 环节 | 论文/上游行为 | 关键位置 |
| --- | --- | --- |
| 统一事件流 | 以 Action/Observation 事件流统一 agent、环境与 UI 之间的所有通信 | `openhands/events/` |
| 动作抽象 | IPythonRunCellAction、CmdRunAction、BrowserInteractiveAction 等动作类型 | `openhands/events/action/` |
| 观测抽象 | 输出、状态、错误等观测类型 | `openhands/events/observation/` |
| 逐步回放 | 事件流天然支持逐步重放与评估 | `openhands/events/`（session 级事件序列） |
| 沙箱运行时 | Docker sandbox 内执行动作 | `openhands/runtime/` |

## 输入输出约定

```text
所有交互 → Event(kind, source, target, action_type, payload, parent)
                    ↓
      EventStream（追加、过滤、回放、统计）
                    ↓
     JSONL 导出 → 离线诊断 / 评估 / 重放工具
```

## 本仓库代码

[`../code/event_stream.py`](../code/event_stream.py) 按上述机制重新实现为与 harness 无关的骨架，而非复制上游代码。差异：动作类型只保留通用分类（代码/命令/浏览/编辑/回复），载荷不绑定上游的序列化格式；沙箱运行时不在本实现范围内。接入 Terminus-KIRA 时，第一步是把现有日志与工具调用收敛为事件流，第二步才是迁移下游诊断工具；观测粒度（全量/结构化/摘要）见 [`../code/trace_schema.md`](../code/trace_schema.md)。

上游仓库当前未复制进仓库；其运行依赖和可复现性仍需通过实际复现确认。
