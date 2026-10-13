# 核验记录

| 项目 | 状态 | 结论 |
| --- | --- | --- |
| 论文与发表 | 已核对 | arXiv:2305.05176；TMLR 2024。 |
| 核心机制 | 已核对 | prompt adaptation、近似和多模型 cascade。 |
| 上游代码 | 已定位 | Stanford FutureData 仓库提交已固定。 |
| 当前 H0 迁移 | 不适用 | 当前协议固定模型，不允许 cascade。 |
| 本地代码最小测试 | 已完成 | `python3 code/cascade_router.py demo` 通过（2026-10-12）：always-small 质量 0.350/成本 0.0020，always-large 质量 0.950/成本 0.2240；校准 target=0.90 得到 tau=0.58，质量 0.900、成本 0.0849（约为 always-large 的 38%）；误设 tau=1.00 时成本回到 0.2240。未联网、未调用模型。 |
| demo 覆盖边界 | 部分 | 三个合成模型 + 100 条确定性查询；未覆盖真实打分器训练、真实价格表与论文的成本节省数值。 |
