# 实现依据

`code/plan_and_solve.py` 把论文的提示结构与后续解析全部实现，并与模型客户端解耦：

| 论文环节 | 本仓库实现 | 说明 |
| --- | --- | --- |
| 零样本 PS 指令 | `PROMPTS["ps"]` | 逐字取自 `upstream/prompt.py` 的 `prompt_201`。 |
| PS+ 指令（提取变量 + 数值计算） | `PROMPTS["ps+"]` | 逐字取自上游 `prompt_302`。 |
| 对照指令 | `PROMPTS["cot"]` | 上游 `prompt_101`（"Let's think step by step."），用作消融对照。 |
| 提示构建 | `build_prompt(question, variant)` | 只做 `Q:/A:` 组装，不含任何 provider 细节。 |
| 从回复还原计划与执行 | `split_plan_and_execution` | 以提示自身的措辞（"Then, let's carry out the plan"）为切分点，不强制模型输出额外格式。 |
| 答案抽取 | `extract_answer` | 触发串取自上游 `config.py` 的 `direct_answer_trigger_for_direct`。 |
| 模型接入 | `ModelClient` 协议 + `OpenAIClient` | 离线用 `ScriptedClient`，联网用 OpenAI 兼容端点。 |

**与论文的差异**：论文面向静态多步推理数据集；工具型 harness 里计划必须是可修订状态，
不能因为已有初始计划就忽略环境反馈。本模块只负责提示与解析，计划修订留给使用它的 harness。
