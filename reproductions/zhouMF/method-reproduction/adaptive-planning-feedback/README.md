# Adaptive Planning from Feedback

## 什么时候使用

任务会在执行中暴露新约束或发生偏离，静态计划已不足以保持进度时使用。

## 机制

把环境反馈写入当前计划状态，并区分计划内局部修订和计划外重规划；成功计划可以作为后续任务的少样本示例。

## 本项目边界

必须记录触发重规划的反馈、原计划与新计划，并在开发任务验证收益。成功计划不能直接当作跨任务通用知识，除非另有迁移证据。

## 直接运行

代码与依赖已保存在 [`code/`](code/)，运行时不需要再查论文或 GitHub。`demo` 在确定性的最小家务环境里
对比「不自适应」与「自适应」，并分别触发 in-plan 与 out-of-plan 两类反馈，全程不联网、不需要模型：

```bash
cd reproductions/zhouMF/method-reproduction/adaptive-planning-feedback/code
python3 adaptive_plan.py demo           # 离线自测，输出轨迹、修订记录与成败
```

真实模型生成重规划（要走 OpenAI 兼容端点，`openai` 已列在 `requirements.txt`）：

```bash
export OPENAI_API_KEY=...
python3 adaptive_plan.py replan-live --observation "the door to the study is locked"
```

| 文件 | 用途 |
| --- | --- |
| [`code/adaptive_plan.py`](code/adaptive_plan.py) | 计划状态、两类修订、最小环境、反馈识别、离线 demo、live 入口。 |
| [`code/requirements.txt`](code/requirements.txt) | 依赖清单；核心与自测仅用标准库，live 模式需要 `openai`。 |
| [`code/UPSTREAM.md`](code/UPSTREAM.md) | 上游仓库与固定 revision（面向 ALFWorld/MiniWoB++，未导入）。 |

## 来源与边界

固定论文与来源见 [arXiv:2305.16653](https://arxiv.org/abs/2305.16653)（该论文不在本人负责的来源包范围内）；
上游代码版本与获取命令见
[code/UPSTREAM.md](code/UPSTREAM.md)。本地 demo 验证的是**反馈分类与计划修订语义**，
不是论文在 ALFWorld/MiniWoB++ 上的成功率；反馈解析在真实系统里应由模型完成，本地用正则占位。
