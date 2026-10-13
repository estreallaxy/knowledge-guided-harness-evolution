# 实现依据

`code/skill_induction.py` 是论文机制的最小可运行实现，并把「程序」真正当作动作序列执行，
而不是像早期骨架那样只保存程序文本。

| 论文环节（§2.2–2.3） | 本仓库实现 | 说明 |
| --- | --- | --- |
| 只在评估器判定成功的 episode 上诱导 | `induce_program(episode, predicate)` | 调用方给定成功谓词，等价于论文的 `V_L(e)=1` 过滤。 |
| 从 episode 抽象出 program | `induce_program` 取「从初始状态起仍能达成目标的最短 suffix」 | 丢掉那些只因 episode 已过半才有用的动作；目标字段的字面值变成参数。 |
| 执行式验证（截断尾部） | `execution_verifier(binding, predicate)` | 只执行 program 本身，尾部动作被丢弃；program 必须独立达成目标才入库。 |
| 验证后入库 | `SkillLibrary.verify_and_add` | 未通过验证直接抛错，不写库。 |
| 检索与复用 | `SkillLibrary.retrieve` + `Skill.instantiate` | 轻量 token 重叠检索（论文用 LM）；复用即为新任务实例化参数。 |
| 动作空间 | `MiniWeb`（`goto/click/fill/submit`） | 论文动作空间是 WebArena 的 15 个原语（Table 7），这里只保留足以表达「多步 + 参数化」的最小子集。 |

安全边界：`execution_verifier` 只在 `MiniWeb` 上执行，不执行任意程序文本；真实接入时
执行环境与 verifier 由 harness 提供，外部知识层不绕过该边界。

**未实现（论文有、本地没有）**：LM 评估器过滤、thought 压缩（87.9→13.4 token）、
WebArena/BrowserGym 动作空间与站点、以及论文的 skill 呈现位置消融（memory vs actions）。
