# Tests and reported results

以下数值均为**论文报告值**，不是本仓库复跑结果。

## Table 1（PDF p.5）WebArena 成功率

| 模型 | 方法 | # Steps | SR | Shop | Admin | Reddit | GitLab | Maps | Multi |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT | Vanilla | - | 12.3 | 13.9 | 10.4 | 6.6 | 15.0 | 15.6 | 8.3 |
| GPT | AWM | 5.9 | 35.5 | 32.1 | 29.1 | 54.7 | 35.0 | 42.2 | 18.8 |
| Claude | Vanilla | 5.6 | 32.7 | 32.6 | 36.8 | 36.8 | 26.1 | 38.5 | 20.8 |
| Claude | AWM | 5.9 | 36.3 | 34.8 | 39.0 | 51.9 | 28.9 | 39.4 | 18.8 |
| Claude | **ASI（本文）** | 5.0 | **40.4** | 40.1 | 44.0 | 54.7 | 32.2 | 43.1 | 20.8 |

口径提醒：Abstract 的"23.5% / 11.3%"是相对提升（40.4/32.7、40.4/36.3），
绝对差分别为 **+7.7** 与 **+4.1** 个百分点。引用时勿把相对值写成百分点。

## Table 3（PDF p.6）消融：验证与表示形式

| 归因 | 表示 | 呈现位置 | 成功率 |
| --- | --- | --- | ---: |
| 无执行式验证 | text | memory | 32.6 |
| 有执行式验证 | program | memory | 36.4 |
| 有执行式验证 | text | memory | 39.0 |
| 有执行式验证 | program | actions（= ASI） | 40.1 |

结论边界：拆开两个因素后，验证带来 +3.8（32.6→36.4），
表示形式与呈现位置的组合再带来 +3.7（36.4→40.1）；论文据此称 program 格式不适合放入 memory。

## Table 8（PDF p.16）诱导与复用频次

| 站点 | 尝试归纳 | 归纳成功 | 复用用例 | 总用例 |
| --- | ---: | ---: | ---: | ---: |
| shopping | 21 | 8 | 96 | 180 |
| admin | 38 | 15 | 108 | 156 |
| reddit | 24 | 11 | 14 | 105 |
| map | 13 | 10 | 80 | 109 |
| gitlab | 25 | 11 | 10 | 175 |

论文据此称 42.5% 的用例至少复用一个 skill，且 skill 由 7.6% 的任务产生。

## 其他报告值

| 结论 | 数值 | 位置 |
| --- | --- | --- |
| 归纳质量：通过执行式验证的比例 | ASI 15.6% / AWM 31.4% 的 turn | §3.3，PDF p.6 |
| thought 压缩 | 87.9 → 13.4 token/step | §2.3，PDF p.3 |
| 组合任务步数 | ASI 4 步 vs AWM 27 步（论文记 85.2%） | §4，PDF p.8，Figure 3 |
| 跨站点迁移 | 三组 sandbox→real 配对，每对 10 条查询 | §5，PDF p.8，Table 5 |

## 当前核验状态

| 项目 | 状态 |
| --- | --- |
| PDF 可解析 | 已通过，21 页，全文已提取为 `paper/paper-v2.txt`（含 `--- PDF page N ---` 分页标记，便于复核页码锚点）。 |
| Abstract、§2、§3、Table 1/3/7/8、§4–5 | 已与本地全文逐页核对。 |
| 论文自身口径冲突 | 已发现 1 处：步数降低的对应关系（Abstract 与 §3.2 不一致）。 |
| 官方代码版本与核心文件 | **已取得**（revision `377abe0623a37eaf7f03bdd26cb97bb5331acf47`，2026-10-13），核心文件见 `exact-source-anchors.md` 的代码锚点表。 |
| 官方单元测试 | **未知**：上游无 tests 目录。 |
| WebArena / BrowserGym 运行环境 | 运行环境与站点数据未纳入；已纳入 `browsergym/` 的机制源码与 `benchmark/metadata/*.csv` 元数据。 |
| benchmark 测试材料 | `browsergym/.../benchmark/metadata/*.csv`（仅 task/split 元数据，无答案）已随机制代码纳入；`asi/config_files/test.json`、`test.raw.json`（含 `reference_answers` 与评分规则）**未入库**。 |
| 本地文件哈希 | 不记录（本包不保存本地计算的 MD5/SHA 值）。 |
| 官方端到端实验复跑 | 尚未执行。 |
| 迁移到目标 Harness 的收益 | 尚未验证；且上游依赖 WebArena，与 Terminal-Bench 接口差异较大。 |

