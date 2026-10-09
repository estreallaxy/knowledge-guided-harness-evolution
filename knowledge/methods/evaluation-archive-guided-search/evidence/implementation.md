# 实现依据

核对代码来源：[`ShengranHu/ADAS`](https://github.com/ShengranHu/ADAS)（官方实现）。

| 环节 | 论文/上游行为 | 关键位置 |
| --- | --- | --- |
| 评分存档 | 每次生成的设计在任务上评估打分，分数与设计一起存入不断增长的 archive | `{domain}/search.py` |
| 启发注入 | archive 作为后续生成的历史素材，meta agent 据此提出新设计 | 上游 meta agent 提示构建 |
| 自我反思与修复 | 生成流程含自我反思与 error-repair 步骤 | `{domain}/search.py` |
| 跨域迁移 | 发现的设计跨任务域、跨模型迁移后仍保持优势 | 论文 §Results（待 PDF 精读核对章节号） |

## 输入输出约定

```text
candidate design → task evaluation → (design, score, error_log, reflection)
                    ↓
              archive 滚动存档（成败都保留）
                    ↓
   top-k 成功 + 最近失败 → 注入下一轮生成提示 → 新候选
```

## 本仓库代码

[`../code/score_archive.py`](../code/score_archive.py) 按上述机制重新实现为与 harness 无关的骨架，而非复制上游代码。差异：成功与失败样例分开检索（便于消融各自贡献）；上游的 meta agent 提示构建与评估函数由调用方注入；不包含上游的领域任务代码。迁移到本研究优化闭环时，必须先把封存测试任务从存档可检索范围中排除，防止测试信息泄露进下一轮搜索。

上游仓库当前未复制进仓库；其运行依赖和可复现性仍需通过实际复现确认。
