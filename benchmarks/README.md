# Benchmark 协议

第一组组合为 Meta-Harness + Terminal-Bench 2.0。[Terminal-Bench 2.0 的固定清单与划分](terminal-bench-2.0/README.md)已经入库；模型、环境、评分器、可编辑边界和试点预算见[第一阶段协议](../docs/phase1-decisions.md)。服务器环境 smoke 与实际分数尚未完成。

训练集供优化器查看，开发集供候选选择，测试集封存至最终评估。论文报告分数不能与新划分或新底座的结果直接混算。具体适配器与配置通过复现后补充。
