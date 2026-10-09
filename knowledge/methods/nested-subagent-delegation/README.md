# Nested Subagent Delegation

## 什么时候使用

| 判断 | 内容 |
| --- | --- |
| 要解决的问题 | 复杂任务难以用单 agent 顺序处理，需要分解给多个专职子 agent、协调执行顺序并回收结果。 |
| 使用前提 | 任务可分解为边界清晰的子任务；各子任务有可描述的职责；执行模型可调用；每轮委派有预算上限。 |
| 输入 | 任务描述、agent 角色定义（名称 + 系统提示）、模型调用回调、最大步数与子会话深度。 |
| 输出 | 每个子任务的结果摘要与完整消息历史（谁在何时对谁说了什么）。 |
| 不使用 | 任务高度耦合无法分解、上下文预算不足以承载多 agent 历史、子 agent 职责重叠造成推诿，或单 agent 循环已足够时（多 agent 开销不值得）。 |
| 主要风险 | 委派链过深导致 token 成本与墙钟时间线性增长；协调者选错执行者；子会话摘要丢失关键细节造成错误回收。 |

## 怎么工作

1. 协调者持有共享消息历史，按 `select_next_speaker` 选择下一位执行者（可规则或模型选择）。
2. 被选 agent 收到消息后触发 auto-reply：以「角色系统提示 + 共享历史」调用执行模型，生成回复或动作。
3. 遇到可分解子任务时，协调者发起嵌套子会话（nested chat）：子编排循环独立推进，完成后把结果或摘要回收到主会话。
4. 协调者判断终止（输出终止标记或 step 预算耗尽），输出任务结果与完整历史。

本方法改造的是 harness 的编排层与子 agent 委派模块，不修改执行模型与工具层。子会话默认回传摘要而非全量历史，以控制上下文成本；摘要模式要求子任务的关键结果被显式保留。

方法关系：依赖可注入的模型调用回调。可与 Lifecycle Kernel Services（其他方向，未在本分支登记）组合（以生命周期服务管理 agent 池与调度）；可与 [Evaluation Archive Guided Search](../evaluation-archive-guided-search/README.md) 组合（用评分存档挑选委派方案）。与单 agent 顺序循环是替代关系。以上组合均为待实验验证的假设，尚无本地证据。

## 直接运行

```bash
python code/delegation_orchestrator.py demo
```

| 文件 | 用途 |
| --- | --- |
| [`code/delegation_orchestrator.py`](code/delegation_orchestrator.py) | 协调者循环、agent 注册、嵌套子会话与消息历史的机制骨架；模型调用以回调注入，不绑定 provider。 |
| [`code/orchestrator_prompt.md`](code/orchestrator_prompt.md) | 协调者选择发言者、发起子会话与输出终止标记的提示模板。 |
| [`code/requirements.txt`](code/requirements.txt) | Python 依赖清单；当前实现仅使用标准库。 |

论文结果、固定版本映射和核验状态保存在 [`evidence/`](evidence/)，仅在审计方法来源或研究结论时读取。
