# Knowledge-Guided Harness Evolution：前期调研结果

> 调研快照：2026-09-28。本文只汇总已经完成的前期调研及其对当前 Idea 的含义；论文结论与拟迁移设想分开记录。完整 Method 与实验计划见 [research-plan.md](research-plan.md)。

## 1. 当前 Idea 与调研结论

| 问题 | 调研结果 | 对当前 Idea 的含义 |
| --- | --- | --- |
| 自动优化 harness 是否已有直接基础？ | [Meta-Harness](https://arxiv.org/abs/2603.28052) 已展示由外层 coding agent 读取 harness、trace 和得分，并反复修改 harness 代码的基本范式。 | Meta-Harness 适合作为最直接的核心 baseline，当前研究无需重新证明“harness 可以被自动修改”。 |
| 仅靠 trace 和模型内化知识是否足够？ | 现有工作已经探索 trace 诊断、修改历史、多路径候选和模块化搜索，但优化方案仍主要来自优化器自身生成或本轮实验历史。 | 外部方法知识可能扩大候选空间，但这是研究假设，不能预先写成“必然更快、更稳定”。 |
| 是否已有与本方案完全相同的工作？ | 目前找到的近邻工作分别覆盖自主 harness 搜索、经验复用、任务适配、Skill 生成或知识整理；尚未找到同时完成“跨论文与工程实践的离线核验、可执行方法知识、任务导向初始化、trace 驱动持续优化”的同构方案。 | 当前组合具有清晰差异，但“未找到”不等于已经证明首创，仍需继续更新检索并精确界定贡献。 |
| 外部方法库本身是否足以构成贡献？ | 相关研究表明知识或组件可以被整理、检索和复用，但尚不能证明这种知识对 harness 优化一定有效。 | 贡献必须落在知识如何表示、选择、适配、执行和由实验反馈修正，以及它相对无知识优化器的可测收益。 |
| Trace 在方案中是什么角色？ | Trace 既是优化证据，也是 harness 产生、压缩和展示的信息；记录方式会影响诊断质量、token 与时延。 | Trace 采集属于可优化的 harness，但原始运行记录和外部评分必须独立保存，避免优化器改写证据。 |
| 最关键的实证问题是什么？ | 尚未回答结构化方法知识是否优于模型自由探索、原始论文输入或普通检索，也未回答收益能否覆盖整理与适配成本。 | 实验必须区分初始化、知识引导和自主探索的作用，并报告泛化、旧能力退化及总成本。 |

## 2. 近邻工作

### 2.1 Harness 自动优化与经验复用

| 工作 | 已调研的核心定位 | 可借鉴之处 | 与当前 Idea 的边界 |
| --- | --- | --- | --- |
| [Meta-Harness](https://arxiv.org/abs/2603.28052) · [GitHub](https://github.com/stanford-iris-lab/meta-harness) | coding agent 基于 harness 源码、运行 trace 和得分，在外层循环中搜索新 harness。 | 外层优化循环、文件系统式证据组织、候选实现与验证。 | 没有预先整理跨论文和工程实践的外部方法知识，主要依赖优化模型的已有能力与本轮历史。 |
| [AutoSaddler](https://arxiv.org/abs/2608.23041) · [GitHub](https://github.com/microsoft/AutoSaddler) | 强化自动 harness 优化流程，并在多个 benchmark 上重跑 Meta-Harness。 | 强 baseline、经验记录和跨 benchmark 实验协议。 | 不是以经过核验的外部 harness 方法库来增强优化器。 |
| [ModularRSI](https://arxiv.org/abs/2609.14857) · [GitHub](https://github.com/IQuestLab/ModularRSI) | 将自我改进按模块组织，并利用成功与失败轨迹。 | 模块级归因、成败轨迹对照。 | 模块化优化不等同于持续吸收跨来源方法知识。 |
| [HarnessFix](https://arxiv.org/abs/2606.06324) · [GitHub](https://github.com/HarnessFix/HarnessFix) | 依据轨迹诊断问题并定位需要修改的实现。 | 从 trace 到失败定位和代码修复。 | 重点是诊断与修复，没有覆盖任务初始阶段的方法选择和外部知识积累。 |
| [HarnessBank](https://arxiv.org/abs/2607.13683) | 保存和利用 harness 优化过程中产生的候选与经验，支持多路径保留。 | 历史候选复用、避免只保留单一路径。 | 经验主要来自框架自身迭代；当前 Idea 的核心知识来源还包括预先核验的外部论文与工程实践。其具体存储粒度仍需代码复现确认。 |
| [RRSI](https://arxiv.org/abs/2609.24972) | 记录修改历史，并研究 Terminal-Bench 2.1 与跨域泛化。 | 修改谱系、跨域评价和历史经验记录。 | 没有替代外部方法的收集、核验和任务条件建模。 |
| [HarnessCompass](https://arxiv.org/abs/2608.01918) | 利用反馈核对优化方向。 | 在修改后检查反馈是否支持原假设。 | 更接近优化环节的反馈机制，不覆盖完整知识构建流程。 |
| [Adaptive Auto-Harness](https://arxiv.org/abs/2606.01770) | 面向长期任务流的自适应 harness。 | 长期运行中的适应与评价场景。 | 研究场景相邻，知识来源和初始化机制不同。 |

### 2.2 任务适配、方法知识与持续维护

| 工作 | 已调研的核心定位 | 可借鉴之处 | 当前方案需要进一步解决的问题 |
| --- | --- | --- | --- |
| [Task-Aware Harness Provisioning](https://arxiv.org/abs/2608.17433) | 根据任务需求配置 harness。 | 任务和 harness 能力缺口的建模。 | 如何把缺口映射到经过核验、带实现的方法，并支持组合。 |
| [SkVM](https://arxiv.org/abs/2604.03088) | 面向任务选择和组织可用能力。 | 方法发现、适用条件和调用边界。 | 如何把选择结果迁移成可验证的 harness 代码修改。 |
| [SkillWeaver](https://arxiv.org/abs/2606.18051) | 组合和适配多个 Skill。 | 组合兼容性、任务适配。 | Skill 只是 harness 的一个模块，仍需覆盖工具、上下文、记忆、容错、调度和观测等机制。 |
| [Anything2Skill](https://arxiv.org/abs/2606.09316) | 把外部材料转化为可使用的 Skill。 | 从材料到结构化知识的转换流程。 | 需要增加论文主张、代码行为、适用边界与本地迁移证据的分别核验。 |
| [Repo-To-Skill](https://arxiv.org/abs/2609.02749) | 从代码仓库提取可复用 Skill。 | 将实现一并沉淀，减少运行时再次检索。 | 需要处理跨方法依赖、冲突、版本和实验反馈回写。 |
| [How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323) · [GitHub](https://github.com/UCSB-NLP-Chang/Skill-Usage) | 研究 Skill 在真实查询中的使用，并提供 query-specific refinement 机制。 | 已作为第一项“指令与 Skill”方法，验证三层披露和随库代码的组织方式。 | 尚未接入 H0 参考实现并运行 Terminal-Bench 2.0，迁移收益未知。 |
| [Library Drift](https://arxiv.org/abs/2605.19576) | 讨论方法或能力库持续积累后的漂移风险。 | 条目版本、冲突、过时和错误淘汰的管理。 | 需要用本地实验确定推荐范围，不能把一次成功直接推广到新任务。 |

## 3. Baseline 调研结果

| 层级 | 候选 | 选择结论 | 主要用途 |
| --- | --- | --- | --- |
| 共同起点 | 未优化的 `H0` | 必选；它是执行 harness，不是优化方法 baseline。 | 衡量所有优化方法的真实增益、成本和旧能力变化。 |
| 核心 baseline | [Meta-Harness](https://arxiv.org/abs/2603.28052) | 第一阶段优先复现。 | 比较“trace + 自主代码搜索”与“trace + 外部知识 + 自主探索”。 |
| 核心强对照 | [AutoSaddler](https://arxiv.org/abs/2608.23041) | 环境跑通后加入。 | 检验方案能否超过更新、更完整的自动优化流程，并借鉴其实验协议。 |
| 模块化补充 | [ModularRSI](https://arxiv.org/abs/2609.14857) | 按复现成本加入。 | 判断收益是否只来自模块化拆分。 |
| Trace 修复补充 | [HarnessFix](https://arxiv.org/abs/2606.06324) | 按研究问题加入。 | 比较知识引导与专门的 trace 诊断、修复机制。 |
| 无验证标签补充 | [RHO](https://arxiv.org/abs/2606.05922) · [GitHub](https://github.com/wbopan/retro-harness) | 反馈条件匹配时加入。 | 研究缺少直接评分或验证标签时的 harness 优化。 |
| 评测平台 | [HarnessOpt-Bench](https://arxiv.org/abs/2608.06301)、[VeRO](https://arxiv.org/abs/2602.22480) | 不作为方法 baseline。 | 用于评价优化器或提供额外评测视角。 |

## 4. Benchmark 调研结果

| Benchmark | 当前定位 | 选择依据 | 使用边界 |
| --- | --- | --- | --- |
| [Terminal-Bench 2.0](https://arxiv.org/abs/2601.11868) | 主实验 | 被 Meta-Harness、AutoSaddler、ModularRSI 和 HarnessFix 共同使用；仓库已保存数据快照与划分。 | 固定模型、环境、评分器和预算；训练/开发/测试任务隔离，测试反馈不进入优化。 |
| [GAIA2](https://arxiv.org/abs/2602.11964) | 第二环境 | 可参考 AutoSaddler 的跨 Universe 设置检查泛化。 | 需核对 Meta-ARE 版本、场景、模型与评分器。 |
| [SWE-Bench Pro](https://arxiv.org/abs/2509.16941) | 仓库级补充 | AutoSaddler 与 RHO 已用于比较 Meta-Harness。 | 适配成本较高，需固定仓库版本和公开数据划分。 |
| [Terminal-Bench 2.1](https://www.tbench.ai/news/terminal-bench-2-1) | 版本稳健性复查 | RRSI 使用该版本，可检验结论是否依赖 2.0。 | 与 2.0 分开报告，不能混合分数。 |

## 5. 调研形成的研究空缺

| 空缺 | 可以形成的研究问题 | 必须提供的证据 |
| --- | --- | --- |
| 外部方法知识没有系统进入 harness 优化闭环 | 经过核验、带适用条件和代码的方法知识，能否提高有效 harness 修改的产生率？ | 与 Meta-Harness 在相同 H0、模型、任务和预算下对照。 |
| 初始化和运行后优化经常混在一起 | 任务导向的 `H0 → H1` 是否在尚无目标 trace 时带来更好的起点？ | `H0`、无知识初始化、知识初始化的独立比较。 |
| 结构化知识的价值不明确 | 方法目录是否优于直接提供论文、普通检索或只给摘要？ | 结构化方法、原始材料、无外部知识三组消融。 |
| 知识引导可能压制模型自主探索 | 在允许采用、改造、拒绝及提出库外方案时，能否兼顾知识复用与新方案发现？ | 记录优化器查看、采用、拒绝和自主提出的候选及其结果。 |
| 组合方法的收益不能由单项结果推出 | 多个方法怎样判断依赖、冲突和协同？ | 在同条件下比较 `H0`、`H0+A`、`H0+B`、`H0+A+B`。 |
| 局部提升可能伴随旧能力退化 | 多轮优化能否在新任务增益之外保留既有成功能力？ | 每轮重测既有成功任务，报告新增成功和原有成功退化。 |
| 知识整理有显著隐性成本 | 方法库能否在总体上节省搜索、适配和实验成本？ | 同时统计人工整理、人工复核、代码适配、优化 token、执行 token、费用与时延。 |

## 6. 当前可下结论与不可提前下结论的内容

| 类型 | 内容 |
| --- | --- |
| 可以确认 | Meta-Harness 提供了直接可复现的自主 harness 优化起点；外部研究已经覆盖 trace 诊断、模块化优化、任务适配、Skill 转换和经验维护等局部环节；这些机制可以为当前 Method 提供组件和实验对照。 |
| 暂定判断 | 尚未发现与当前完整闭环同构的工作；“经过核验的外部方法知识 + 任务导向初始化 + trace 持续优化 + 自主探索”具有进一步研究价值。 |
| 不能提前声称 | 外部方法库一定是独立创新点；一定比 Meta-Harness 更快、更稳或上限更高；论文中的单项收益可以直接迁移或叠加。 |
| 下一步验证 | 先由四位同学在各自隔离的代码、H0、配置与运行目录中使用 `deepseek-v4-flash` 复现 Meta-Harness；核对四份 H0 起点和实验条件一致后，再比较无知识、原始文献、结构化方法知识和完整闭环。 |
