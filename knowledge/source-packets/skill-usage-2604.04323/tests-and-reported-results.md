# Tests and reported results

## 论文报告结果

Table 2（PDF p.8）报告如下 pass rate；数值为论文结果，不是本仓库复跑结果。

| Benchmark / 设置 | Claude Opus 4.6 | Kimi K2.5 | Qwen3.5-397B-A17B |
| --- | ---: | ---: | ---: |
| SkillsBench，retrieved w/ curated | 40.1 | 33.5 | 26.7 |
| SkillsBench，retrieved w/ curated + query-specific | 48.2 | 26.7 | 30.8 |
| SkillsBench，retrieved w/o curated | 38.4 | 19.8 | 19.7 |
| SkillsBench，retrieved w/o curated + query-specific | 37.9 | 23.1 | 21.5 |
| Terminal-Bench 2.0，retrieved | 61.4 | 50.6 | 44.2 |
| Terminal-Bench 2.0，retrieved + query-specific | 65.5 | 56.2 | 49.1 |

这些结果同时说明：query-specific refinement 在论文的 9 个比较中改善 7 个，但在 SkillsBench 的部分条件下无增益或退化；方法收益依赖初始检索技能的相关性和覆盖度。

## 官方检查入口

| 检查对象 | 官方代码 |
| --- | --- |
| 检索准确性与覆盖 | `official-code/scripts/eval_retrieval.py`、`judge_skill_coverage.py` |
| Agent 是否实际加载技能 | `official-code/scripts/check_skill_usage.py` |
| 不同条件的任务结果汇总 | `official-code/scripts/calculate_results.py` |
| Query-specific 产物是否生成 | `official-code/scripts/query_specific_refinement.py collect` |

## 当前核验状态

| 项目 | 状态 |
| --- | --- |
| PDF 可解析 | 已通过，19 页。 |
| 论文 §4.1–4.2、Table 2、Table 3 与 Figure 3 | 已与本地全文核对。 |
| 官方代码版本与核心文件 | 已固定并保存。 |
| 大型数据与完整 benchmark 环境 | 未纳入来源包。 |
| 官方端到端实验复跑 | 尚未执行。 |
| 迁移到目标 Harness 的收益 | 尚未验证。 |
