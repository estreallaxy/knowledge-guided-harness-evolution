# 李永康 meta-harness Terminal Bench 2.0 阶段结果

固定 train 30 题：17 通过、10 零分、3 未评分，累计 38 次尝试。未评分进入 30 题分母；每题一个主记录，只有审阅过的基础设施替换参与主记录选择，额外尝试全部计入消耗。这不是 pass@2。

[配置](../configs/experiment.json) · [逐题摘要](../results/summary.json)

执行/优化使用百炼 deepseek-v4-flash-0731，评分采用任务原生时限；优化会话上限 2400 秒、不人为限输出/思考 token。正式 train 串行；4 CPU、8 GiB 的 Lima/Docker，linux/amd64。未显式设置 seed，费用账单未知。

历史个人 baseline 含供应商 hook 与 reasoning_content 兼容改动，不能称纯上游 H0；两个源码哈希已写入摘要，共同条件符合性仍待审阅。训练结果用于一次候选选择，不能称封存评估、统计显著改进或原论文数值复现。

第一轮优化生成候选 003，耗时 256.54 秒，8 项针对候选的检查已通过。独立 dev 对照于用户收尾时取消：H0 19 个结果文件（10通过/2零分/7未评分），003 17 个结果文件（11通过/1零分/5未评分）；两路 root finished_at 为空，未完成 19 题成对评估。没有第二轮正式优化或 test。

旧路径下的原始运行、trace、冻结源码与账本保持原样；新目录只承载可提交摘要。未重新启动实验，也未修改隐藏评分器、共享 H0 或 benchmark。

## 2026-10-11 提交适配核对

历史 H0 指 Meta-Harness 的 KIRA 百炼适配版；新版 `H0/terminal-bench-2.0/code/` 是 Terminus，二者不是相同执行器。这组历史结果不能登记为新版 Terminus H0 的实验结果，也不能跨执行器作公平对照。

供应商接线已迁入 `code-adaptation/agents/` 的独立子类，官方 KIRA 文件保持原样。移植候选与历史候选文件字节一致；移植检查只使用合成响应和模拟 provider，不调用模型或 benchmark。移植后的真实任务运行、共同条件符合性与泛化收益仍未验证。入口与检查命令见[适配说明](../code-adaptation/README.md)。
