# 研究方案：以持续积累的方法知识增强任务导向的 harness 构建与优化

## 1. 研究动机与核心 idea

### 1.1 Motivation

1. Harness 的自动构建与演化依赖优化 agent 理解任务、分析执行轨迹、提出改进机制并将其正确实现，但通用编码能力并不必然转化为高效的 harness 优化能力。Trace 能揭示已发生的行为和失败，却不能完整提供可能的解决方案；
2. 模型已有的相关策略也可能未被当前上下文有效调用，使优化停留在有限的修改模式中。与此同时，外部论文与工程实践提供了可供借鉴的方法，但这些知识分散在不同描述和实现中，需要经过提炼、核验与适配，才能成为优化 agent 可使用的策略；
3. 实际任务对 skill、工具、上下文、记忆和容错的需求各不相同，成熟框架及单个方法的效果也不能直接等同于其迁移、组合后的收益，因此需要将任务需求与方法的适用条件、接口依赖和成本联系起来，支持从初始构建到后续优化的完整过程。

由此，本研究关注如何增强优化 agent 本身构建和改进 harness 的能力：持续吸收经过复核的外部方法知识，结合渐进式披露与自身实验经验，使其更有效地选择、适配和组合已有机制，同时保留独立提出、修改或拒绝方案的自由，避免知识引导固化探索。最终目标是在有限预算下提高有效改进的产生与实现效率，并通过执行反馈持续纠正方法选择和组合，检验多轮优化中的旧能力保留与未见任务收益。

### 1.2 核心 idea 与方法主线

**一句话 idea：通过持续吸收并核验外部方法知识、引导优化 agent 的自主探索和积累实验经验，增强其面向任务的 harness 构建与优化能力；先根据任务需求选择、适配和组合方法，再结合执行轨迹持续改进，并验证成本、能力保留与泛化效果。**

外部知识主要给优化 agent；执行 agent 使用优化后得到的代码、配置、工具和技能，不需要默认携带整套研究知识库。

**通用性要求：优化 agent 的流程应跨任务复用、高效且有效，执行 agent 的 harness 则根据任务演化。**

两个阶段相互连接：

1. **任务导向的初始构建**：任务需求 + 可编辑系统 + 方法知识 + 自主提案 → 候选初始 harness。
2. **证据驱动的持续优化**：当前 harness + trace + 历史实验 + 方法知识 + 自主提案 → 候选修改 → 验证 → 保留、修订或撤销。

两个知识来源相互补充：

- **外部研究知识**：论文和工程实践提供可能的机制、实现方式及适用条件。
- **内部探索经验**：优化 agent 自主提出假设，并从真实成功、失败和对照中积累经验。

核心研究问题是：**在固定执行模型、优化模型和资源约束下，能否让优化 agent 更善于提出和实现有效改进，并通过持续吸收外部知识与自主探索，改善任务适配、优化效率、能力保留和未见任务表现？**

## 2. Baseline 与 Benchmark

### 2.1 Baseline

| Baseline | 类型 | 官方实现 | 统一定位 |
| --- | --- | --- | --- |
| Benchmark H0 | 原始执行 harness | 随各 benchmark 固定 | 不经过自动优化的共同起点；按 benchmark 分别固定实现与版本。 |
| [GEPA](https://github.com/gepa-ai/gepa) | 自动优化器 | `gepa-ai/gepa` | 在相同 H0、数据划分、模型和评测器上运行。 |
| [Meta-Harness](https://github.com/stanford-iris-lab/meta-harness) | Harness 自动优化器 | `stanford-iris-lab/meta-harness` | 在相同 H0、数据划分、模型和评测器上运行。 |
| [AutoSaddler](https://github.com/microsoft/AutoSaddler) | Harness 自动优化器 | `microsoft/AutoSaddler` | 在相同 H0、数据划分、模型和评测器上运行。 |

H0 按 benchmark 定义：Terminal-Bench 2.0 使用固定版本的 Terminus 2；GAIA2 使用 Meta ARE 默认 agent；SWE-Bench Pro 使用 SWE-agent。若某篇 baseline 论文以不同 seed harness 起步，必须同时报告“论文原设置复现”和“统一 H0 对照”，不能把不同起点的结果直接比较。

### 2.2 统一模型配置

| 角色 | 模型 | API 模型标识 | 使用要求 |
| --- | --- | --- | --- |
| 执行模型（solver） | DeepSeek V4.1 Flash | `deepseek-flash` | 所有 baseline 与后续方法统一使用。 |
| 优化模型（proposer/optimizer） | DeepSeek V4.1 Flash | `deepseek-flash` | 与执行模型保持一致。 |

统一通过 DeepSeek 官方 API 调用，并在每次实验记录调用日期和 API 返回的实际模型版本。沙箱后端独立于模型配置，服务器复现默认使用本地 Docker。

### 2.3 Benchmark

| Benchmark | 论文 | 共享代码位置 |
| --- | --- | --- |
| Terminal-Bench 2.0 | [arXiv:2601.11868](https://arxiv.org/abs/2601.11868) | `benchmarks/terminal-bench-2.0/` |
| GAIA2 | [arXiv:2602.11964](https://arxiv.org/abs/2602.11964) | `benchmarks/gaia2/` |
| SWE-Bench Pro | [arXiv:2509.16941](https://arxiv.org/abs/2509.16941) | `benchmarks/swe-bench-pro/` |

共享 benchmark 保持只读。每位成员的 baseline 源码、benchmark 适配、配置、trace、运行状态、结果和复现说明全部放在 `reproductions/<成员>/<baseline>/<benchmark>/`；不得把个人实验产物写回根目录 `benchmarks/`。
