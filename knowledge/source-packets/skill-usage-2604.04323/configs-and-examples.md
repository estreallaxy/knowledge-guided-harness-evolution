# Configs and examples

## 官方实验配置

| 设置 | 配置目录 | 主要差异 |
| --- | --- | --- |
| SkillsBench | `official-code/experiments/configs/skillsbench/` | Claude、Kimi、Qwen 三套运行配置。 |
| Terminal-Bench 2.0 | `official-code/experiments/configs/terminalbench/` | Claude、Kimi、Qwen 三套运行配置。 |

配置只能和对应论文版本、代码 revision、任务数据与模型环境一起解释。论文中的运行结果不能由单个 YAML 独立复现。

## 官方流程入口

官方仓库把过程分为四步：

1. `scripts/prepare_experiment.py`：下载或组织实验材料，生成任务目录与 Harbor 配置。
2. `scripts/retrieve_skills.py`：针对任务检索候选技能。
3. `scripts/query_specific_refinement.py`：在任务环境中探索、判断并生成任务条件技能。
4. `scripts/check_skill_usage.py` 与 `scripts/calculate_results.py`：检查轨迹中的技能使用并汇总结果。

Query-specific refinement 的代码入口：

```bash
python scripts/query_specific_refinement.py prepare \
  --tasks-dir <tasks-with-retrieved-skills> \
  --workspace <isolated-workspace> \
  --agent <agent> \
  --model <model>

harbor run -c <generated-config>

python scripts/query_specific_refinement.py collect \
  --tasks-dir <tasks-with-retrieved-skills> \
  --workspace <isolated-workspace>
```

运行前必须另外取得论文使用的数据与外部依赖。仓库根 README 指向 Hugging Face 数据集 `Shiyu-Lab/Skill-Usage`；大型数据没有放入本来源包。

## 本地保存范围

`official-code/` 保存与论文方法直接相关的核心脚本、检索服务、六套实验配置、任务查询元数据、三种检索 Skill，以及 refinement 使用的 skill-creator。任务全集、Terminal-Bench 2.0 副本、运行缓存和下载数据不在本目录中。
