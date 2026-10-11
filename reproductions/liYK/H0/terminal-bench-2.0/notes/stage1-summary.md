# 李永康 H0 Terminal Bench 2.0 阶段结果

固定 train 30 题：13 通过、9 零分、8 未评分，累计 36 次尝试。未评分进入 30 题分母；每题一个主记录，只有审阅过的基础设施替换参与主记录选择，额外尝试全部计入消耗。这不是 pass@2。

[配置](../configs/experiment.json) · [逐题摘要](../results/summary.json)

执行/优化使用百炼 deepseek-v4-flash-0731，评分采用任务原生时限；优化会话上限 2400 秒、不人为限输出/思考 token。正式 train 串行；4 CPU、8 GiB 的 Lima/Docker，linux/amd64。未显式设置 seed，费用账单未知。

历史个人 baseline 含供应商 hook 与 reasoning_content 兼容改动，不能称纯上游 H0；两个源码哈希已写入摘要，共同条件符合性仍待审阅。训练结果用于一次候选选择，不能称封存评估、统计显著改进或原论文数值复现。

旧路径下的原始运行、trace、冻结源码与账本保持原样；新目录只承载可提交摘要。未重新启动实验，也未修改隐藏评分器、共享 H0 或 benchmark。

## 2026-10-11 提交适配核对

历史 H0 指 Meta-Harness 的 KIRA 百炼适配版；新版 `H0/terminal-bench-2.0/code/` 是 Terminus，二者不是相同执行器。这组历史结果不能登记为新版 Terminus H0 的实验结果，也不能跨执行器作公平对照。
