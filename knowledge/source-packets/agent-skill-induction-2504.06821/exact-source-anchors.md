# Exact source anchors

页码按 `paper/paper-v2.pdf`（21 页）计。

## 论文

| 要核对的内容 | 精确位置 | 原文支持的范围 |
| --- | --- | --- |
| 计划表示（program）作为 skill 的核心主张 | Abstract，PDF p.1 | 主张 program 是有效的 skill 表示；给出 23.5% 与 11.3% 的说明，二者为**相对提升**，对应 Table 1 的 +7.7 与 +4.1 个百分点。 |
| 观测—动作循环与 episode 定义 | §2.1，PDF p.3 | 定义 τ、状态转移 T、终止条件与最大步数 H_max；不能推出跨站点可迁移。 |
| 用 LM 评估器过滤 episode 后再 induction | §2.2，PDF p.3 | 归纳只在 V_L(e)=1 的 episode 上进行；评估器是噪声来源。 |
| 与 AWM 的关键差异：skill 进动作空间而非记忆 | §2.2，PDF p.3，Figure 1 | A ∪ {d} → A 取代 M ∪ {d} → M；论文未证明该选择在所有 harness 上更优。 |
| Episode 清洗（去错误步骤、压缩 thought） | §2.3，PDF p.3 | thought 由每步 87.9 token 压到 13.4 token。 |
| 程序化 skill 的诱导与示例 | §2.3，PDF p.3–4，Figure 2 | 展示 `open_marketing_reviews()`、`search_reviews(...)` 的产生与轨迹改写。 |
| 执行式验证：改写轨迹前缀 + 截断尾部动作 | §2.3，PDF p.4 | 截断掉 skill 调用之后的尾部动作，避免"无论 skill 是否正确都返回正确答案"的假成功。 |
| 主结果（WebArena 六个站点） | §3.1–3.2，PDF p.5，Table 1 | ASI 40.4 vs vanilla 32.7 vs AWM 36.3（平均值）。 |
| 验证与表示形式的消融 | §3.3，PDF p.6，Table 3 | 拆开"执行式验证"与"程序表示"两个因素；四组取值见结果文件。 |
| 诱导成功率：程序比文本更严格 | §3.3，PDF p.6 | ASI 仅 15.6% 的 turn 通过验证，AWM 有 31.4% 的 turn 新增技能；用于归纳的 episode 分别为 58（ASI）与 70（AWM）。 |
| 组合式长任务中的效率收益 | §4，PDF p.8，Figure 3 | 单个组合任务中 ASI 用 4 步完成，AWM 用 27 步（论文记为缩短 85.2%）；样本量为 1，不能外推。 |
| 跨站点迁移设置 | §5，PDF p.8，Table 5 | 三组 sandbox→real 配对（OneStopMarket→Target、PostMill→Reddit、OpenStreetMap→GoogleMaps），每对取 10 条信息检索式查询。 |
| 常见 skill 复用与不兼容 skill 的更新 | §5，PDF p.8–9，Figure 4 | 展示 `search_product` 复用与 `sort_listings` 因页面行为变化而失效；支持"需要 +update 机制"的结论。 |
| 动作空间 | Appendix A.1，PDF p.14，Table 7 | 15 个原语动作；skill 只能在此之上组合。 |
| 三个 LM 组件的提示词（求解、评估、清洗、归纳） | Appendix A.2，PDF pp.14–16 | 复现所需提示词全文。 |
| 诱导与复用频次统计 | Appendix B.1，PDF p.16，Table 8 | 见表 8：42.5% 的用例至少复用 1 个 skill，skill 由 7.6% 的任务产生。 |
| 典型 skill 形态 | Appendix B.2，PDF p.16 | 串联常用原语（如 `search_product`）与使用高级编程原语两类。 |

## 官方代码

行号锚点按 `official-code/` 快照（revision `377abe0623a37eaf7f03bdd26cb97bb5331acf47`）计。

| 机制或证据 | 论文指向 | 作用 |
| --- | --- | --- |
| 上游仓库与 revision | <https://github.com/zorazrw/agent-skill-induction> @ `377abe0623a37eaf7f03bdd26cb97bb5331acf47` | 已入库（2026-10-13）。 |
| Skill 归纳主入口 | `asi/induce/induce_actions.py:88`（`induce_actions`） | 论文 §2.3 的 program 归纳；`:137`（`write_actions`）落盘 skill 与其测试。 |
| 执行式验证的落点 | `asi/induce/induce_actions.py:172`（`write_tests`） | 与论文「改写轨迹前缀 + 截断尾部动作」的执行式验证对应。 |
| Episode 清洗 | `asi/autoeval/evaluate_trajectory.py:25`（`remove_invalid_steps`）、`:62`（`extract_think_and_action`） | 论文 §2.3 的去错误步骤与 thought 压缩。 |
| 轨迹评估器 | `asi/autoeval/evaluator.py`、`clients.py`、`prompts.py` | 论文 §2.2 的 LM 评估器 V_L(e)。 |
| Skill 进入动作空间 | `asi/custom_action_set.py:30`（`CustomActionSet(HighLevelActionSet)`） | 论文 §2.2 的关键差异：A ∪ {d} → A 而不是进 memory。 |
| 站点动作集（原语动作） | `asi/actions/{shopping,admin,reddit,map,gitlab}.py` | 论文 Appendix A.1、Table 7 的 15 个原语动作在代码中的落地。 |
| Agent 主体 | `asi/agent.py:35`（`DemoAgent(Agent)`） | BrowserGym `Agent` 的 Skill 版实现。 |
| 提示词 | `asi/induce/prompt/`、`asi/autoeval/prompts.py` | 论文 Appendix A.2 的归纳/评估/清洗提示词。 |
| WebArena / BrowserGym 依赖 | `browsergym/`（随仓库一并快照） | 与 Terminal-Bench 接口不同，迁移需单独适配。 |

**已知缺口**：上游运行环境（WebArena 站点、BrowserGym 运行依赖）与模型凭据未纳入，
行号锚点已补但**接口行为未在本地执行验证**。

## 论文自身的不一致（提交前需注意）

| 位置 | 现象 |
| --- | --- |
| Abstract vs §3.2 vs Table 1 | Abstract 记"降低 10.7±15.3% 步数"，§3.2 写作"15.3% 和 10.6% 分别相对 vanilla 与 AWM"。按 Table 1 计算：5.0/5.6=10.7%（vs vanilla）、5.0/5.9=15.3%（vs AWM），即 Abstract 正确、§3.2 的对应关系写反。 |

