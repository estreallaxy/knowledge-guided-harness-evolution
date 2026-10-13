# 实现依据

`code/preference_router.py` 把论文的「请求级路由 + 阈值校准」做成可运行实现：

| 论文环节 | 本仓库实现 | 说明 |
| --- | --- | --- |
| 请求级路由 | `PreferenceRouter.route(request)` | 用难度分与阈值在弱/强模型间选择，返回可审计决策。 |
| 难度/偏好评分器 | `Scorer` 可调用对象，默认 `KeywordDifficultyScorer` | 论文用偏好数据训练的分类器；本地用确定性占位，接口不变。 |
| 阈值校准 | `calibrate(records, quality_target=... / cost_budget=...)` | 在质量下限或成本上限下取最优阈值；平局取更低阈值。 |
| 策略评估 | `evaluate_threshold` | 报告平均质量、平均成本、升级率、达标率，能看出「升错」的浪费。 |
| 应用校准结果 | `apply_calibration` | 返回带新阈值的路由副本，不改调用方。 |

评分器**训练**与 provider 调用留在 harness 层（`route` 子命令演示），避免把未经数据支持的
默认路由写进知识层。
