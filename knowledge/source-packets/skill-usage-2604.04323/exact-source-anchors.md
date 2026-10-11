# Exact source anchors

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 真实使用中技能检索、加载与执行之间存在缺口 | §3.3，PDF pp.5–7，Table 1 | 比较 curated、retrieved 与 no-skill 设置；不能推出任意外部知识都会提升 agent。 |
| Query-agnostic refinement | §4.1，PDF p.7 | 每个已检索技能在不知道目标任务的情况下独立改写；不能跨技能组合。 |
| Query-specific refinement | §4.1，PDF pp.7–8 | 读取任务和全部已检索技能，先探索并自评，再提取、删除或组合技能内容。 |
| Refinement 的总体结果 | §4.2，PDF pp.8–9，Table 2 | 报告 SkillsBench 与 Terminal-Bench 2.0 上的 pass/load；存在下降或弱收益条件。 |
| 多技能合成案例 | §4.2，PDF p.9，Figure 3 | 展示 tensor-parallel 任务中将两个不完整技能合成一个任务条件技能。 |
| 对初始检索质量的依赖 | §4.2，PDF p.9，Table 3 | refinement 更接近放大已有相关知识，不能在相关知识完全缺失时稳定创造知识。 |
| 实验与提示细节 | Appendix B–C，PDF pp.13–17 | 模型、技能加载、检索和 refinement 提示等复现实验条件。 |

## 官方代码

| 机制或证据 | 文件与行号 | 作用 |
| --- | --- | --- |
| Query-specific refinement 的三阶段提示 | `official-code/scripts/query_specific_refinement.py:53-128` | 明确读取任务和候选技能、实际探索、自评及生成 refined skills。 |
| 将任务、候选技能和 skill-creator 装入隔离任务 | `official-code/scripts/query_specific_refinement.py:175-254` | 构造 Harbor 临时任务，并用无真值 verifier 的探索环境替换原测试。 |
| Refinement 的 Harbor 配置 | `official-code/scripts/query_specific_refinement.py:256-321` | 固定 agent、模型、并发、artifacts 与数据路径。 |
| 收集 refined skills | `official-code/scripts/query_specific_refinement.py:323-401` | 将运行产物写回任务目录并区分 success、missing 与 kept-original。 |
| 任务条件技能检索 | `official-code/scripts/retrieve_skills.py:34-242` | 构造任务环境、加载不同检索 Skill，并保存 found skill IDs。 |
| Hybrid、keyword、semantic 搜索入口 | `official-code/data/find-skills*/SKILL.md` | 给出三种检索接口及调用约定。 |
| 检索后处理与评测 | `official-code/scripts/select_top_k_skills.py`、`eval_retrieval.py`、`check_skill_usage.py`、`calculate_results.py` | 分别处理候选选择、检索评价、轨迹使用检查和结果汇总。 |
| 检索服务 | `official-code/search_server/` | 包含 BM25、semantic、hybrid 服务与索引构建代码。 |

行号以 `source-packet.json` 固定的官方代码 revision 为准。
