# Action-Observation Event Stream

## 什么时候使用

| 判断 | 内容 |
| --- | --- |
| 要解决的问题 | 执行轨迹散落在各处日志与调用里，无法结构化回放、诊断、评估与审计。 |
| 使用前提 | harness 的所有交互（agent 动作、环境反馈、系统消息）可改造为统一事件流；记录粒度可按预算配置。 |
| 输入 | 统一事件流：每个事件带类型、时间戳、来源、载荷与父事件引用。 |
| 输出 | 可过滤、可逐步回放、可导出 JSONL 的结构化轨迹，以及事件统计摘要。 |
| 不使用 | 只关心最终结果且不需要诊断；事件量远超存储与预算；或 harness 交互无法全部收敛到事件流（观测将不完整）。 |
| 主要风险 | 记录粒度与 token/存储成本需权衡；事件模式一旦对外承诺，改动会影响下游诊断与评估工具。 |

## 怎么工作

1. agent 与环境的一切交互统一为 Action/Observation 事件：Action 是 agent 发起的动作（代码执行、命令、浏览、编辑等），Observation 是环境的反馈（输出、状态、错误）。
2. 每个事件带时间戳、来源、目标、动作类型、载荷与父事件引用，嵌套动作形成事件树。
3. 事件流是通信媒介与轨迹来源合二为一：支持按类型/来源过滤、从任意位置逐步回放、导出 JSONL 供离线分析。
4. 轨迹分析工具（诊断、评估、重放）只依赖事件流，不依赖具体 harness 实现。

本方法改造的是 harness 的观测层与集成接口，不改变执行逻辑本身。论文（OpenHands）的动作分类（IPython 代码、命令、浏览、编辑）可直接作为通用动作类型的起点。

方法关系：事件流输出可作为 [Evaluation Archive Guided Search](../evaluation-archive-guided-search/README.md) 的评估信号来源（组合关系）；观测器也可作为服务接入 Lifecycle Kernel Services（其他方向，未在本分支登记）。与散落在日志与调用中的非结构化采集是替代关系。以上组合均为待实验验证的假设，尚无本地证据。

## 直接运行

```bash
python code/event_stream.py demo
```

| 文件 | 用途 |
| --- | --- |
| [`code/event_stream.py`](code/event_stream.py) | Event 与 EventStream 的机制骨架：追加、过滤、回放、JSONL 导入导出与统计。 |
| [`code/trace_schema.md`](code/trace_schema.md) | 事件字段规范与记录粒度建议，供接入具体 harness 时作为契约。 |
| [`code/requirements.txt`](code/requirements.txt) | Python 依赖清单；当前实现仅使用标准库。 |

论文结果、固定版本映射和核验状态保存在 [`evidence/`](evidence/)，仅在审计方法来源或研究结论时读取。
