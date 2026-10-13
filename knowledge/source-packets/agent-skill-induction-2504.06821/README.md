# Inducing Programmatic Skills for Agentic Tasks

| 内容 | 位置 |
| --- | --- |
| 来源元数据 | [source-packet.json](source-packet.json) |
| 论文 v2 | [paper/paper-v2.pdf](paper/paper-v2.pdf) · [文本](paper/paper-v2.txt) |
| 官方核心代码 | [`official-code/`](official-code/)（`asi/induce/` 与 `asi/autoeval/`） |
| 论文与代码定位 | [exact-source-anchors.md](exact-source-anchors.md) |
| 配置和运行入口 | [configs-and-examples.md](configs-and-examples.md) |
| 测试与论文结果 | [tests-and-reported-results.md](tests-and-reported-results.md) |

## 快照状态

`official-code/` 已入库，固定 revision `377abe0623a37eaf7f03bdd26cb97bb5331acf47`
（2026-10-13 取得）。范围与排除项见 `source-packet.json` 的 `snapshot_scope`：

- 纳入：`asi/`（`induce/` 的 skill 归纳、`autoeval/` 的轨迹评估、`actions/` 的站点动作集、
  `agent.py`、`custom_action_set.py`、`config_files/` 等）与 `browsergym/`（WebArena 等环境入口）。
- 未纳入：WebArena/BrowserGym 的实际运行环境与站点数据、运行缓存、模型凭据。
- 许可证：仓库根 LICENSE 为 **CC BY-SA 4.0**（非软件常用许可证），迁移或再分发时需注意。
- `vendor-official-code.sh` 保留作快照来源记录；需要重建时可在有网络的终端执行。
- 上游未提供单元测试目录，测试入口记为未知。

本地 PDF 为公开 arXiv v2（COLM 2025 版本）；文中的页码锚点按该 PDF 计，
可用 `paper/paper-v2.txt` 的 `--- PDF page N ---` 标记复核。

## 与本地实验的关系

本包只保存论文与官方代码，不含本地运行结果。对「归纳出的 program 必须经执行验证才能复用」
这一机制的离线自测在 [`reproductions/zhouMF/method-reproduction/agent-skill-induction/`](../../../reproductions/zhouMF/method-reproduction/agent-skill-induction/)，
不构成对论文数值的复现。
