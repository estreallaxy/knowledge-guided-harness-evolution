# 实现依据

核对代码来源：[`UCSB-NLP-Chang/Skill-Usage`](https://github.com/UCSB-NLP-Chang/Skill-Usage)。

| 环节 | 上游代码行为 | 关键位置 |
| --- | --- | --- |
| 输入准备 | 复制完整任务目录；保留原任务说明为 `task_instruction.md`；把原 `environment/skills/` 移到 `retrieved_skills/`；把 `skill-creator` 作为唯一引导 Skill 放回 agent 的 Skill 目录。 | [`create_temp_task_dir`](https://github.com/UCSB-NLP-Chang/Skill-Usage/blob/main/scripts/query_specific_refinement.py) |
| 探索与整理指令 | 要求 agent 阅读全部候选 Skill、尝试目标任务、记录有效/错误/缺失内容，再纠错、删减和跨 Skill 组合；限定只做一轮。 | [`INSTRUCTION_PROMPT`](https://github.com/UCSB-NLP-Chang/Skill-Usage/blob/main/scripts/query_specific_refinement.py) |
| 防止答案反馈 | 删除原测试目录，写入空操作测试，并在 Harbor 配置中禁用 verifier；因此 refinement agent 不获得真实任务得分。 | [`query_specific_refinement.py`](https://github.com/UCSB-NLP-Chang/Skill-Usage/blob/main/scripts/query_specific_refinement.py) |
| 输出收集 | 从 Harbor artifacts 中收集 `refined_skills`；生成成功时替换该任务的 `environment/skills/`，未生成时保留原 Skill。 | [`collect_results`](https://github.com/UCSB-NLP-Chang/Skill-Usage/blob/main/scripts/query_specific_refinement.py) |
| 默认执行配置 | refinement 默认使用 Claude Code `2.1.19` 与 `claude-opus-4-6`，每任务一次尝试，Docker 环境。正式 TB2 执行配置为每题三次。 | [refinement CLI](https://github.com/UCSB-NLP-Chang/Skill-Usage/blob/main/scripts/query_specific_refinement.py)、[TB2 Claude 配置](https://github.com/UCSB-NLP-Chang/Skill-Usage/blob/main/experiments/configs/terminalbench/claude.yaml) |

## 输入输出约定

```text
task instruction + retrieved skills + task environment
                    ↓
       one exploration/refinement rollout
                    ↓
refined_skills/<skill-name>/SKILL.md (+ optional helpers)
                    ↓
          separate task execution rollout
```

论文中的 refinement 产物是**任务专用 Skill**，不是跨任务共享的方法卡，也不是对执行 harness 源码的自动修改。迁移到本研究时必须显式实现 Skill 发现、加载、产物隔离和失败回退，不能只把 refinement 提示词追加到 Terminus-KIRA 的系统提示中。

## 本仓库代码

[`../code/refine_skills.py`](../code/refine_skills.py) 根据上述机制重新实现，而非复制上游脚本。它增加了三项面向本研究的约束：生成结果默认写入隔离目录、收集时检查 Skill 入口文件、显式应用前备份原 Skill。完整提示词随代码保存在 [`../code/refinement_prompt.md`](../code/refinement_prompt.md)，运行时不需要重新检索论文或上游仓库。
