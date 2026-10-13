# 实现依据

`code/cascade_router.py` 把论文的「质量门 + 级联」做成可运行、可校准的实现：

| 论文环节 | 本仓库实现 | 说明 |
| --- | --- | --- |
| 由廉到贵的级联 | `run_cascade(task, stages, tau, gate_cost)` | 顺序调用，置信度达门槛即采纳，否则升级。 |
| 打分/验证函数 | `StageResponse.confidence` + `tau` | 论文用训练出的打分器；本地用可替换的置信度占位。 |
| 门槛必须在开发集校准 | `calibrate_cascade` | 在网格上取「满足质量目标且成本最小」的门槛。 |
| 质量/成本评估 | `evaluate_cascade` | 报告质量、平均成本、至少升级一次的查询比例。 |
| 打分本身有成本 | `gate_cost` | 每次升级前扣除一次打分开销，避免把门当免费。 |

代码不嵌入任何模型价格表或 provider，因此不会把过期价格写进 harness；`_stages()` 里的
成本与置信度只是 demo 用的合成值。
