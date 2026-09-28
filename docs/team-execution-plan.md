# 三阶段任务计划

阶段之间串行；每个阶段内三人并行。

```mermaid
flowchart LR
    A[阶段一：共同起点与知识收集] --> A1[周梦凡：H0]
    A --> A2[赵星源：Meta-Harness]
    A --> A3[王懿：结果汇总与知识复核]
    A1 --> B{验收一}
    A2 --> B
    A3 --> B
    B --> C[阶段二：优化闭环]
    C --> D{验收二}
    D --> E[阶段三：扩展验证]
```

## 阶段一：共同起点与知识收集

### 实验任务

| 负责人 | 任务 | 仓库相对路径 |
| --- | --- | --- |
| **周梦凡** | 编写 H0 配置并运行 Terminus-KIRA；与赵星源共同确定公共参数。 | 代码：`harness/h0/terminus-kira/`；入口：`agents.baseline_kira:AgentHarness`；配置：`experiments/configs/h0.yaml` |
| **赵星源** | 编写 Meta-Harness 配置并完成复现；与周梦凡共同确定公共参数。 | 代码：`optimizer/baselines/meta-harness/`；配置：`experiments/configs/meta-harness.yaml` |
| **王懿** | 设计统一结果字段，汇总两条实验线，检查缺失记录；复核三人的知识入库。 | `experiments/README.md`、`experiments/results/`、`knowledge/README.md`、`docs/research-plan.md` 2.1 |

### 论文收集任务

| 负责人 | 收集方向 | 数量 |
| --- | --- | --- |
| **周梦凡** | 指令与 Skill；上下文管理与压缩；长期记忆与经验复用；规划与任务进度管理；模型选择与资源分配 | **每个方向 2 篇** |
| **赵星源** | 工具与环境交互；容错与故障恢复；执行循环与调度；会话与环境状态管理；权限审批与运行隔离 | **每个方向 2 篇** |
| **王懿** | 子 Agent 与多 Agent 协作；扩展机制与生命周期钩子；运行观测、Trace 与集成接口；验证、评估与反馈 | **每个方向 2 篇** |

### H0 与 Meta-Harness 的统一配置

周梦凡维护 `h0.yaml`，赵星源维护 `meta-harness.yaml`。两人共同讨论并维护 `terminal-bench-2.0-common.yaml`；各自文件只写本方法特有参数。

| 配置项 | 统一要求 |
| --- | --- |
| 配置文件 | 公共参数由两人共同维护：`experiments/configs/terminal-bench-2.0-common.yaml`；周梦凡维护 `h0.yaml`；赵星源维护 `meta-harness.yaml`。 |
| Benchmark | `benchmarks/terminal-bench-2.0/`，使用同一 `split-v1.json` 和任务 ID。 |
| 初始 Harness | 均从 `harness/h0/terminus-kira/` 开始，不直接修改 H0。 |
| 执行模型 | 模型、provider、temperature、最大上下文和最大输出一致。 |
| 执行预算 | 每题最大 step、tool call、token、墙钟时间和重试次数一致。 |
| 运行设置 | 每题重复次数、并发数、Docker 环境和超时设置一致。 |
| 记录字段 | task ID、配置、trace、分数、token、费用、时延、异常和候选 harness 版本一致。 |
| Meta-Harness 额外成本 | 优化模型、搜索轮数、候选数和优化成本单独记录，不混入执行预算。 |
| 配置变更 | 公共参数须由周梦凡与赵星源商量后修改；影响公平性的参数变化后两条实验线一起重跑。 |

以下只是配置字段示例，具体字段、取值和默认值由周梦凡与赵星源讨论，并分别写入公共配置或各自配置。

| 配置部分 | 可讨论的字段示例 |
| --- | --- |
| Benchmark | 数据路径、split、任务范围、是否先跑 smoke task |
| H0 | harness 路径、Python 入口、prompt 路径、可编辑边界 |
| 执行模型 | provider、model、API 地址、temperature、上下文长度、最大输出 |
| 执行预算 | 最大 step、tool call、token、单题超时、重试次数 |
| 运行方式 | 重复次数、并发数、Docker 设置、缓存是否启用 |
| 记录方式 | trace 保存路径、逐题分数、token、费用、时延、异常、候选版本 |
| Meta-Harness | 优化模型、搜索轮数、每轮候选数、候选选择规则、优化预算 |
| 凭据 | 只配置环境变量名，不把 API key 或密码写入仓库 |

公共参数的讨论结果记录到 `experiments/configs/README.md`；未达成一致的字段先标记为“待定”，不要各自采用不同值。王懿只按确定后的配置汇总结果，不参与参数决定。

### 论文如何入库

1. 每篇论文建立 `knowledge/sources/<paper-id>/`，保存 PDF、GitHub 链接和来源说明。
2. 将论文与 GitHub 链接、负责人和进度同步到 `docs/research-plan.md` 的 2.1 表格。
3. 把各个方向的高价值方法写入 `knowledge/methods/<method>/README.md`。
4. 把可直接使用的代码放入 `knowledge/methods/<method>/code/`，并在 `knowledge/README.md` 登记。

现有 [`query-specific-skill-refinement`](../knowledge/methods/query-specific-skill-refinement/README.md) 计入“指令与 Skill”的第 1 篇，可继续重构。

## 阶段二与阶段三

| 阶段 | 负责人 | 任务 |
| --- | --- | --- |
| 二 | **周梦凡** | 根据任务和方法代码实现 `H0 → H1`。 |
| 二 | **赵星源** | 实现 `Trace → 诊断 → 修改 → 验证`。 |
| 二 | **王懿** | 接入方法代码，记录采用、拒绝与实验反馈。 |
| 三 | **周梦凡** | 扩充不同 harness 模块的方法与代码。 |
| 三 | **赵星源** | 运行 baseline、完整方法和关键消融。 |
| 三 | **王懿** | 检查未见任务、旧能力和总成本。 |

| 阶段验收 | 条件 |
| --- | --- |
| **验收一** | H0 与 Meta-Harness 在统一配置下稳定运行；2.1 每个方向登记 2 篇论文，并整理其中的高价值方法与可用代码。 |
| **验收二** | 从 H0 出发，跑通初始化和至少一轮 trace 优化。 |
| **最终验收** | 完成同条件 baseline、消融、封存测试、能力保留与成本分析。 |
