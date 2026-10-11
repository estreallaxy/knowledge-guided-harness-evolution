# 李永康来源包迁移

2026-10-11 按远端 SourcePacket 协议准备的六篇来源包；论文与选定官方代码固定版本，原始材料不改写。官方代码是原样选定片段，完整上游运行和 H0 迁移收益仍未验证。远端现有 Skill Usage 条目不由本次改动替换。

| 论文 | 方向 | 来源包 |
| --- | --- | --- |
| reasoningbank | 长期记忆与经验复用 | [reasoningbank-2509.25140](reasoningbank-2509.25140/source-packet.json) |
| expel | 长期记忆与经验复用 | [expel-2308.10144](expel-2308.10144/source-packet.json) |
| agentrewind | 会话与环境状态管理 | [agentrewind-2608.14380](agentrewind-2608.14380/source-packet.json) |
| statefork | 会话与环境状态管理 | [statefork-2609.38648](statefork-2609.38648/source-packet.json) |
| agentscope | 扩展机制与生命周期钩子 | [agentscope-2508.16279](agentscope-2508.16279/source-packet.json) |
| nora | 扩展机制与生命周期钩子 | [nora-2605.02092](nora-2605.02092/source-packet.json) |

每包包含固定 PDF、带页码文本、官方代码、source-packet.json 和三份来源说明。旧 sources/methods 与既有核验在本机保留；本次 PR 不提交旧目录或 Method 派生对象，也不修改 docs/research-plan.md。NORA 固定上游许可证未知，记录在来源包中，不能假定为开放再分发许可。

## 本地核验

从仓库根目录运行 `python3 knowledge/source-packets/validate_liyk_packets.py`，核对六份 PDF、六份页码文本、38 个固定官方代码文件及必需来源说明。PDF 在本目录的 `.gitattributes` 中标记为二进制；原始代码和文本的历史空白保留，不为通过格式检查而改写来源。此核验不执行上游项目，不证明论文或 H0 迁移收益。
