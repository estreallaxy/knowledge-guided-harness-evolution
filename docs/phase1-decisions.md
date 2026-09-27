# 第一阶段三项决定（2026-09-27，协议 v1）

这份文件固定**研究用的起点**，不宣称已经取得复现分数。先用下列配置做可运行性和成本试点；若不得不更改数据、模型或预算，记录为新协议版本，并在新版本下重跑所有对照。

| 项目 | 决定 | 已完成 / 尚待运行 |
| --- | --- | --- |
| 主 benchmark | [Terminal-Bench 2.0](https://github.com/harbor-framework/terminal-bench-2/tree/69671fbaac6d67a7ef0dfec016cc38a64ef7a77c)，任务仓库固定在 `69671fba...`；89 个 `task.toml` 目录的名称已保存至 [`task-ids.txt`](../benchmarks/terminal-bench-2.0/task-ids.txt)。 | 已核对 89 个唯一任务 ID；尚未运行 Docker/Harbor 任务。 |
| 划分 | [`split-v1.json`](../benchmarks/terminal-bench-2.0/split-v1.json)：train 30、dev 19、test 40。对 89 个 ID 按 `SHA256("kghe-tb2-v1-2026-09-27:" + task_id)` 排序后顺序切分；[`generate_split.py`](../benchmarks/terminal-bench-2.0/generate_split.py) 可复核。 | 划分已生成并检查互斥；**不是** AutoSaddler 原文的同一份随机划分，不能直接比较其论文分数。 |
| 评测器与环境 | Harbor `0.18.0`，与 Meta-Harness TB2 示例一致；从上述 Git 提交的[仓库快照](../benchmarks/terminal-bench-2.0/README.md)生成**本地任务目录**，用 Harbor `-p` 运行，避免注册表更新改变题目。Docker Linux，任务自带的原始测试脚本与资源声明保持不变。Python `>=3.12,<3.13`，其他依赖见 [`h0/pyproject.toml`](../harness/h0/pyproject.toml)。 | 固定提交的 89 题已在服务器准备；容器镜像 digest、Docker/Harbor 可运行性及 `uv.lock` 仍需在 smoke 后记录。服务器 `cc` 目前有 Docker 24.0.2 且可访问 daemon，但默认 Python 3.10.12、无 `uv` / Harbor，需先建立隔离的 Python 3.12 环境。 |
| 执行模型 | `anthropic/claude-opus-4-6`，运行参数 `temperature=0.7`，所有方法同一 API 路径、上下文和任务超时。保存每次实际返回的模型 ID、API 时间、错误和重试；若 API 拒绝该温度，统一改协议版本。 | 与 Meta-Harness TB2 参考脚本一致；尚未发起付费调用。 |
| 优化模型 | Meta-Harness 参考为 Claude Code + Opus。统一实验时固定 Claude Code CLI 版本，并显式指定 Opus 4.6；不使用随时间改变的 `opus` 别名。所有方法报告优化器 token、费用、时延。 | 需在服务器确认 CLI 和认证；不能把优化器能力变化误当作知识卡增益。 |
| 数据可见性 | 优化器只接触 train 的题目、完整 trace 和打分；dev 只给**聚合分数**作候选选择，test 仅最终评估。测试题、参考解、测试脚本及测试 trace 不进入优化器工作区或知识库。评测器可访问原测试脚本，执行 agent 不得读取答案/评分器。 | 89 题快照已在共享私有仓库，因此这是运行时隔离协议，不是对仓库成员的保密盲测；运行前需核验优化器的挂载和读取权限。 |
| 同条件预算 | **第一阶段试点**：每种优化方法最多 4 轮、每轮 1 个候选；每候选最多 train `30×1` + dev `19×2` = 68 次执行，优化期总上限 272 次；最终候选和未优化的 H0 各在 test `40×3` 次。Meta-Harness 与本方法采用相同执行预算上限，允许提前停止，但须报告真实次数与优化器成本。 | 这是可行性/成本试点预算，不声称等同论文的完整搜索预算。试点结束前确定正式论文预算并冻结新版本。 |
| 统计与日志 | 按题汇总各次二值成功率，再对题等权平均；同时报新增成功、原成功退化、95% 置信区间、token、墙钟时间、美元费用、失败/超时数。保留任务 ID、split、源码 commit、依赖锁、容器 digest、模型版本、原始 trace、候选差异和评测结果。 | 评分口径已定；结果尚无。 |

**划分的来源边界：**[AutoSaddler](https://arxiv.org/html/2608.23041) 采用 30/19/40 随机划分并在 40 题 test 上重跑 Meta-Harness，但其当前[开源仓库](https://github.com/microsoft/AutoSaddler)只提供 GAIA2 划分与适配，Terminal-Bench 适配标为待发布。这里复用划分规模，**不冒充其相同题目清单**。[Meta-Harness 公开 TB2 示例](https://github.com/stanford-iris-lab/meta-harness/tree/main/reference_examples/terminal_bench_2)默认在全部 89 题上搜索，故要把其控制器改为 train/dev 工作流后重跑，原文分数只能作背景参考。

## 共同 H0

选 [Meta-Harness 参考实现中的原始 `baseline_kira.py`](https://github.com/stanford-iris-lab/meta-harness/blob/44b9942127847f7421db70d8c7e48407f09a3c70/reference_examples/terminal_bench_2/agents/baseline_kira.py)（Terminus-KIRA）作共同 `H0`，固定上游提交 `44b9942127847f7421db70d8c7e48407f09a3c70`。源文件、原始 prompt、缓存辅助文件和依赖清单已复制到 [`harness/h0/`](../harness/h0/)；逐项与上游**Git blob** 核对一致，上游 MIT 许可证亦保留。`baseline_kira.py` 的 Git blob SHA-256：`e06b9273e2b900006a2072457dff2630ad04e589c48057d050219bdc791eb889`（Windows 工作区可能使用 CRLF，工作区文件哈希会不同）。

| 边界 | 内容 |
| --- | --- |
| 可修改的任务侧 harness | `agents/baseline_kira.py` 及由它引用的 prompt 模板；可修改系统指令、工具定义/调用、上下文摘要、终止检查、错误处理、信息记录与 Skill 接口。每个候选从 H0 复制生成自己的完整版本，不改原始 H0。 |
| 固定的实验侧 | Benchmark 题目、任务镜像、Harbor 运行器、评分器、数据划分、评测模型与给定预算；原始评测日志独立于候选可编辑 trace 保存。 |
| 容易混淆之处 | [`meta-harness-tbench2-artifact`](https://github.com/stanford-iris-lab/meta-harness-tbench2-artifact) 是搜索后得到的高分 harness，**不能作为 H0**，否则起点已经包含待比较方法的成果。`Terminus2` 是 KIRA 的运行接口/继承底座，不是这次选定的 H0 文件。 |

KIRA 已有终端执行循环、原生工具调用、提示词模板、上下文溢出后摘要、API/阻塞重试、任务完成确认和轨迹记录；因此可以在一个已工作的 agent 上研究多个 harness 模块，而无需先重新实现基础 agent。它目前**没有我们的论文方法库和专门的 Skill 选择器**，这些是后续候选改动，不偷放进 H0。不同优化方法都必须从相同的 H0 Git 版本开始。

## 首张知识标杆卡

选 [*How Well Do Agentic Skills Work in the Wild*](https://arxiv.org/abs/2604.04323) 的**任务相关 Skill refinement**机制。它给出问题、算法步骤、代码和 Terminal-Bench 2.0 对照，恰好能检查我们能否把一篇外部方法准确转成可检索卡。已下载[论文 PDF](../knowledge/sources/papers/2604.04323v1.pdf)，方法卡见 [`skill-usage-query-specific-refinement.md`](../knowledge/method-cards/skill-usage-query-specific-refinement.md)。这篇是 2026 年 4 月预印本，选择依据是机制与同 benchmark 的可核验证据，**不把发表状态当成权威背书**。

| 候选 | 本轮处理 | 按 2.1 指标判断 |
| --- | --- | --- |
| [Skill-Usage](https://arxiv.org/abs/2604.04323) | 首张卡 | 同一 TB2 的对照、可查代码、明确的有效与失效条件；接入 H0 仍需实测。 |
| [SkillWeaver](https://arxiv.org/abs/2606.18051) | 留作后续“组合/路由”卡 | 多 Skill 组合机制相关，但主要验证在作者新建的 CompSkillBench，尚无同一 H0/TB2 的直接证据。 |
| [Skill-Use](https://arxiv.org/abs/2608.04828) | 留作评测参考 | 清楚区分 Skill 触发、遵循与边界，可用于后续诊断；核心贡献是 benchmark，作为首张**方法**卡不合适。 |

它也揭示了研究边界：论文优化的是任务级 Skill，尚未证明“外部论文方法卡指导优化 agent 修改 H0”有效。标杆卡记录这种差异与失败例子；首次迁移实验只在 train/dev 上做，test 留待最终评估。首张卡需要师弟/师妹逐条核对 PDF 与代码后签名，才可标为“人工复核”。

## 运行前最后三个检查点

| 检查 | 成功标准 |
| --- | --- |
| 环境 smoke | 服务器以固定任务 checkout、Docker、Harbor `0.18.0` 运行 1 个 **train** 题；保存镜像 digest、CLI 版本和完整日志。 |
| H0 smoke | H0 可导入、运行、留下原始 trace；与上游校验和一致，先测 train 再测 dev。若必须修代码，形成 `H0-v2` 并让全部方法重跑。 |
| 基线适配 | Meta-Harness 的 89 题 `full` 和 hard 子集逻辑替换为本划分；候选只看 train，dev 仅用于选择。检查优化器实际工作区只挂载 train，且不能读取 test 的任务内容和评分。 |
