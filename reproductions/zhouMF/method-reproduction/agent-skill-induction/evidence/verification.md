# 核验记录

| 项目 | 状态 | 结论 |
| --- | --- | --- |
| 论文与发表 | 已核对 | arXiv:2504.06821v2 与 COLM 2025 版本一致。 |
| 核心机制 | 已核对 | ASI 在线诱导、程序验证、保存与复用 Skill。 |
| 上游代码 | 已定位 | 固定提交记录在 `code/UPSTREAM.md`；未执行 WebArena。 |
| 当前 H0 迁移 | 未运行 | 需实现 Terminal-Bench 环境适配与独立验证。 |
| 本地代码最小测试 | 已完成 | `python3 code/skill_induction.py demo` 通过（2026-10-12）：诱导出 `click(search); click(item); fill(rating,{rating}); click(submit)`，执行式验证入库、无验证候选被拒、换参数（rating=7）复用成功；假成功消融中 `prefix+tail` 显示成功而单独 `tail` 失败。未联网、未调用模型。 |
| demo 覆盖边界 | 部分 | 只覆盖机制：确定性最小 Web 环境 + 1 条开发 episode。未覆盖 LM 评估器、多站点泛化、论文 40.4/32.7 的数值。 |

不得将 WebArena 结果表述为当前 harness 的结果。
