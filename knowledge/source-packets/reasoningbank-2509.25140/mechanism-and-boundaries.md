# 成败推理经验提取、检索与追加

2026-10-12：按阶段一要求补齐机制接口与逐条来源；原始论文和代码未修改。

| 字段 | 机制说明 |
| --- | --- |
| 目标瓶颈 | 重复任务中丢弃历史成败经验，重复同类推理错误 |
| 作用模块 | 训练经验提取与执行前记忆检索 |
| 输入 | 当前任务query；已有经验/embedding缓存；完整轨迹；成功/失败判断；judge/extractor与embedding模型接口 |
| 触发条件 | 执行新任务前检索；一次任务结束后提取并追加。项目只允许train更新，dev/test前冻结是迁移设想。 |
| 必要步骤 | 按query与缓存经验算相似度，取相关experience及memory items；judge区分成功与失败，按不同指令从轨迹提炼可复用经验；将新memory items简单追加；后续任务检索并作为指导 |
| 状态变化 | 经验池和query embedding缓存追加；不含高级冲突消解/遗忘/压缩的已验证机制 |
| 预期输出 | 相关经验与memory items；扩展后的经验池；项目使用时另记提取成本 |
| 前提与限制 | 原论文在测试任务流持续学习；本项目dev/test冻结，不将原测试流更新照搬；固定代码检索experience后再取items；简单item级检索属于改编；judge/embedding真实运行和本地收益未知；系统收益不能归因于单条记忆 |

## 逐条机制、条件与限制的证据

| 主张 | 论文位置 | 固定代码 | 支持范围 |
| --- | --- | --- | --- |
| RB1：query检索top-k experience，相关memory作为执行指导 | PDF p.5，§3.2 / Fig.2 | [official-code/reasoning-bank/WebArena/memory_management.py:138](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L138-L170)（至170） | 论文机制与固定检索入口；不证明本地模型收益 |
| RB2：成功/失败用不同提取指令，生成经验条目 | PDF p.5，§3.2 memory extraction | [official-code/reasoning-bank/WebArena/induce_memory.py:123](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py#L123-L166)（至166） | 固定代码判别与模型调用分支；judge有效性未知 |
| RB3：整合是simple addition，代码追加jsonl而非高级维护 | PDF p.5，§3.2 memory consolidation | [official-code/reasoning-bank/WebArena/induce_memory.py:176](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py#L176-L186)（至186） | 原文追加机制与代码写入；不包含编辑/冲突解决 |
| RB4：检索另需query embedding且会写入缓存 | PDF p.22，Appendix A.2 memory retrieval | [official-code/reasoning-bank/WebArena/memory_management.py:172](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L172-L215)（至215） | 原文检索模型与固定缓存行为；缓存追加不等于memory item追加 |
| RB5：40.5→48.8是WebArena/Gemini系统结果 | PDF p.7，Table 1 | 对应原实验代码位置未知；不以固定片段证明论文数值 | 仅论文结果；固定代码与论文实验commit对应未知，不归因于单条经验 |

完整PDF文本行号、代码范围哈希及固定链接见 [机器可核对映射](claim-evidence-map.json)。

## 方法关系

- `expel-2308.10144`：互补/可替代的经验表示。ReasoningBank保存成败推理经验，ExpeL维护投票规则；可共享训练来源，但重复建议与检索开销须去重。状态：**迁移设想，组合收益未测**。对应证据：本包claims RB1–RB3；ExpeL claims EX1–EX2。

本地接入、组合收益、完整上游运行均没有因本次文档补充而变为已验证。
