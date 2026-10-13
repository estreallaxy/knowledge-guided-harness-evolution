# Tests and reported results

论文报告值，**不是本仓库复跑结果**。

> 数值来自 `paper/paper-v3.txt` 的文本提取，表格单元格折行/串列风险存在。
> 引用前请对照 `paper/paper-v3.pdf` 原文核对；本文件只登记可确证的数字。

## 核心主张（Abstract，PDF p.1；§1，PDF p.2）

| 主张 | 数值 | 说明 |
| --- | --- | --- |
| 峰值 token 下降 | **26–54%** | 跨 AppWorld / OfficeBench / 8-objective QA 的区间。 |
| 小模型作为长程 agent 的性能提升 | 最高 **+46%** | 缓解上下文干扰带来的收益，只针对小模型场景。 |
| 相对压缩基线 | 成功率更高 | 与 FIFO / Retrieval / LLMLingua / Prompting 等基线对照。 |

## Table 1（PDF p.6）AppWorld，agent gpt-4.1 / compressor gpt-4.1，Average(168)

列为 accuracy / steps / peak input tokens（10³）/ dependency（10⁶）。

| 方案 | Acc. | Steps | Peak | Dep. |
| --- | ---: | ---: | ---: | ---: |
| No compression | 56.0 | 16.14 | 49.93 | 5.96 |
| History: FIFO | 45.8 | 28.48 | 6.73 | 5.69 |
| History: Retrieval | 27.4 | 33.17 | 8.39 | 6.68 |
| History: LLMLingua | 39.3 | 24.42 | 7.50 | 6.37 |
| History: Prompting | 43.5 | 24.01 | 6.93 | 5.29 |
| History: **ACON UT** | 51.2 | 20.92 | 7.17 | 4.49 |
| History: **ACON UTCO** | **56.5** | 22.82 | 7.33 | 4.69 |
| Observation: **ACON UT** | 47.0 | 16.67 | 7.62 | 5.08 |
| Observation: **ACON UTCO** | 53.6 | 18.12 | 7.43 | 4.93 |

读法提醒：压缩把峰值 token 大幅压到个位数（10³），但 **steps 上升**（16.14 → 22.82），
即「省上下文」换来了更多轮交互；不要只引用 token 下降而不提步数变化。

## Table 2a（PDF p.7）OfficeBench，agent gpt-4.1 / compressor gpt-4.1

| 方案 | Acc. | Steps | Peak | Dep. |
| --- | ---: | ---: | ---: | ---: |
| No Compression | 76.84 | 11.52 | 7.27 | 4.43 |
| Prompting | 71.58 | 10.13 | 4.40 | 1.10 |
| **ACON UT** | 74.74 | 13.13 | 4.93 | 3.85 |
| **ACON UTCO** | 72.63 | 11.54 | 4.54 | 1.91 |

读法提醒：OfficeBench 上 ACON 的准确率**低于不压缩**（76.84 → 74.74/72.63），
论文只在效率—准确率权衡上主张优势。这一点在迁移前必须显式复核。

## Table 3（PDF p.9）优化器消融（AppWorld，gpt-4.1 agent，history compressor）

| 优化器配置 | Average Acc. |
| --- | ---: |
| o3 + 对比式反馈（默认） | 51.2 |
| o3 去掉对比式反馈 | 50.6（−0.6） |
| gpt-4.1 + 对比式反馈 | 47.6（−3.6） |
| gpt-5 + 对比式反馈 | 50.6（−0.6） |

## Table 4（PDF p.9）实际效率（AppWorld）

| 方案 | API 成本/题 | 单题时延 |
| --- | ---: | ---: |
| No Compression | $0.331 | 73.24s |
| ACON (history) | $0.285 | 87.68s |
| ACON (observation) | $0.272 | 101.92s |

读法提醒：成本下降约 14–18%，但时延上升 20–39%；「省钱」不等于「更快」。

## Table 13（PDF p.25）蒸馏压缩器（AppWorld Average Acc.）

| 压缩器 | Average Acc. |
| --- | ---: |
| Prompting（gpt-4.1-mini） | 39.3 |
| **ACON（gpt-4.1-mini）** | 47.6 |

## 当前核验状态

| 项目 | 状态 |
| --- | --- |
| PDF 可解析 | 已通过，57 页，提取到 `paper/paper-v3.txt`（含分页标记） |
| Abstract / §1 / §3 / §4 / §6 与 Table 1–4、13 | 已按本地文本核对，发现上述「steps 上升」「OfficeBench 准确率下降」两处需在引用时说明 |
| 论文自身口径 | 未发现内部冲突 |
| 官方端到端复跑 | **未执行**（需 AppWorld 数据与模型凭据） |
| 官方单元测试 | **未知**：上游仓库无 tests 目录 |
| 迁移到本 harness 的收益 | **未验证** |
