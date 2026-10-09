# 实现依据

核对代码来源：[`microsoft/autogen`](https://github.com/microsoft/autogen)（论文对应 0.2.x 时代实现；v0.4 起重构为 event-driven actor 架构）。

| 环节 | 论文/上游行为 | 关键位置 |
| --- | --- | --- |
| 对话驱动控制流 | `ConversableAgent` 收到消息即调用 auto-reply，无需外部控制平面 | `autogen/agentchat/conversable_agent.py` |
| 协调者发言选择 | `GroupChatManager` 在群聊中动态选择下一位发言者 | `autogen/agentchat/groupchat.py` |
| 子任务递归委派 | nested chat 允许 agent 在处理子任务时开启嵌套会话并回收结果 | `autogen/agentchat/conversable_agent.py`（register_nested_chats） |
| 人机回退 | 支持人工输入介入的对话模式 | `autogen/agentchat/` |

## 输入输出约定

```text
task + agent 角色定义 + model_call 回调
                    ↓
       主编排循环（选择发言者 → auto-reply）
                    ↓
   子任务出现 → nested chat（可递归，摘要或全量回传）
                    ↓
TERMINATE / 预算耗尽 → 结果摘要 + 完整消息历史
```

## 本仓库代码

[`../code/delegation_orchestrator.py`](../code/delegation_orchestrator.py) 按上述三个原语重新实现为与 harness 无关的骨架，而非复制上游代码。差异：发言者选择默认为可注入回调（规则或模型选择由调用方决定）；子会话支持全量历史与摘要回传两种模式；不包含上游的缓存、错误处理与人机交互组件。接入 Terminus-KIRA 时需显式实现模型回调与工具绑定，不能只把提示词追加到系统提示中。

上游仓库当前未复制进仓库；其运行依赖和可复现性仍需通过实际复现确认。
