# 标杆卡 001：任务相关 Skill refinement

> 来源：Liu et al., *How Well Do Agentic Skills Work in the Wild: Benchmarking LLM Skill Usage in Realistic Settings*, arXiv:2604.04323v1，2026-04-06。机制是论文第 4.1 节及附录 C.1 的 **query-specific refinement**，不是整篇论文的所有检索/评测机制。

| 字段 | 核实内容 |
| --- | --- |
| 问题与模块 | 从大规模 Skill 库取出的条目可能只部分相关、内容嘈杂，执行 agent 也可能不读取。作用于 harness 的 **Skill 检索、选择、加载与任务适配**。 |
| 核心机制 | 输入是当前任务说明及检索到的若干 Skill。先让 refinement agent 在**同一任务环境**阅读条目并尝试任务；不提供 ground-truth verifier，让它自评哪些内容有用、误导或缺失；再合并、删减并补充内容，输出任务化的 `SKILL.md`；执行 agent 再使用它完成任务。论文只做一轮 refinement。 |
| 触发与状态 | 在某任务开始执行前、已有候选 Skill 且允许一次额外探索时触发。状态变化是原检索 Skill → 任务化 Skill 文件；原始 Skill 保留，任务化产物仅对当前任务有效，不自动成为全局通用知识。 |
| 适用条件 | 检索结果中**确有相关知识**，任务环境允许探索，预算能承担一次额外 agent rollout，能够把 Skill 提供给执行 agent。初始覆盖差时，refinement 无法凭空补出可靠知识。 |
| 已知不利情况 | 在 SkillsBench 的“检索但无人工精选 Skill”条件下，Claude 为 `38.4% → 37.9%`；在“含精选 Skill”条件下，Kimi 为 `33.5% → 26.7%`。额外探索可能选错知识；没有完整数值化 token/美元成本的统一报告。 |
| 原论文证据 | Terminal-Bench 2.0（全部 89 题，3 次/题）上，Claude Opus 4.6 + Claude Code：无 Skill `57.7%`、只检索 `61.4%`、检索加任务相关 refinement `65.5%`；后两者差 `+4.1` 个百分点。Kimi + Terminus-2 为 `50.6% → 56.2%`，Qwen + Qwen-Code 为 `44.2% → 49.1%`。这是**整个“检索 + refinement + 相应 agent harness”流程**的结果，不能归因于单独的 Skill 文本或我们的方法卡。不同模型搭配不同 harness，不能据此比较模型强弱。 |
| 实现依据 | [论文 §4、附录 B/C](https://arxiv.org/html/2604.04323)；[原仓库](https://github.com/UCSB-NLP-Chang/Skill-Usage/tree/03446d16f7b659ccc93ac5bd512f62e9b7fabb45)；[refinement 脚本](https://github.com/UCSB-NLP-Chang/Skill-Usage/blob/03446d16f7b659ccc93ac5bd512f62e9b7fabb45/scripts/query_specific_refinement.py)。代码把任务复制进临时目录，加入 retrieved skills 和 skill-creator，替换任务说明为 refinement prompt，**禁用真实 verifier**，运行 Harbor 后收集生成的 Skill。 |
| 迁移到共同 H0 | **待测假设**：优化 agent 可在 train 的任务缺口与候选方法卡上借鉴“先试用、再整理适用内容”的策略，选择/组合外部知识来修改 H0 的 Skill 接口或指令。论文原机制是**执行前任务级 Skill 适配**，并非“用外部论文卡优化 harness 代码”；不能宣称已经验证迁移。H0 需新增 Skill 装载接口，且一次探索的成本必须计入预算。 |
| 与其他方法关系 | 与纯关键词/语义检索为“检索后适配”关系；与直接把原论文全文交给优化器是可对照替代；与候选 Skill 质量门槛、渐进披露、H0 的上下文预算存在依赖。组合效果未在共同 H0 中测试。 |
| 本地验证状态 | **只完成论文 PDF 和核心代码静态核对**；未复现实验，未在共同 H0 上测试；人工复核签名：待完成。 |
| 推荐范围 | 当前只推荐为方法卡制作与迁移假设的标杆，**不推荐为已证实能提高 H0 的改动**。 |

## 来源、版本与核对记录

| 类型 | 记录 |
| --- | --- |
| 论文 | [arXiv 摘要](https://arxiv.org/abs/2604.04323)、[HTML](https://arxiv.org/html/2604.04323)、[本仓库 PDF](../sources/papers/2604.04323v1.pdf)；PDF SHA-256 `dd3c1ec25f258e655413751192b2dec9dffec3063c28882748efa86e446e6ad4`。论文页面写明 **Preprint. Under review.** |
| 代码 | `UCSB-NLP-Chang/Skill-Usage` 提交 `03446d16f7b659ccc93ac5bd512f62e9b7fabb45`；核对 `scripts/query_specific_refinement.py` 的 `INSTRUCTION_PROMPT`、`create_temp_task_dir`、`generate_harbor_config` 和结果收集流程。 |
| 原实验设置 | 论文附录 B：TB2 89 题、每题 3 次；Claude Code `v2.1.19`，Kimi 用 Terminus-2，Qwen 用 Qwen-Code。论文未报告与本研究 30/19/40 封存划分同条件的结果。 |
| 选入理由 | 第一方向“指令与 Skill”；问题明确，机制与代码可核查，提供同一 TB2 的原始对照与反例，足以演示“机制—边界—证据—迁移假设”的卡片格式。 |
| 尚未核实 | 核心实验的每次原始 rollout、任务级置信区间、统一货币成本、在 KIRA H0 下的结果，以及与我们外部论文方法卡的直接关系。没有数据时保持“未知”。 |

**重要边界：**论文的任务相关 refinement 在测试题上可以作为**执行 agent 自身的推理步骤**运行，但如果把测试题探索记录回传给优化器改写共享 H0 或全局方法库，就会破坏封存测试。我们第一阶段仅在 train/dev 探索该迁移，最终评测前冻结 H0 候选和方法卡版本。
