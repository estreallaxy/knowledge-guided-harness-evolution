# Failure-guided Context Compression

## 什么时候使用

长轨迹造成上下文膨胀，且可获得不含封存测试集的成功/失败开发轨迹时使用。

## 机制

1. 在历史或观察超过阈值时压缩为状态摘要。
2. 对“完整上下文成功、压缩上下文失败”的开发轨迹分析丢失信息。
3. 更新压缩指南；必要时再蒸馏压缩器以降低运行成本。

## 本项目边界

压缩必须保留工具状态、已验证结果和未完成子目标；压缩策略只能用开发轨迹优化，并须与未压缩 H0 比较成功率、token、时延和旧任务退化。

## 直接运行

代码与依赖已保存在 [`code/`](code/)，运行时不需要再查论文或 GitHub。`demo` 用两条确定性的开发轨迹
跑完整的「朴素压缩 → 比较全量与压缩 → 由失败反推规则 → 再压缩」闭环，全程不联网、不需要模型：

```bash
cd reproductions/zhouMF/method-reproduction/acon-context-compression/code
python3 context_compression.py demo     # 离线自测，输出压缩率与缺失事实数
```

真实摘要文本（论文里由蒸馏后的压缩器产出）可走 live 路径：

```bash
export OPENAI_API_KEY=...
python3 context_compression.py summarize-live --model deepseek/deepseek-v4-flash
```

| 文件 | 用途 |
| --- | --- |
| [`code/context_compression.py`](code/context_compression.py) | 开发轨迹、压缩器、失败分析、规则修订循环、离线 demo、live 入口。 |
| [`code/requirements.txt`](code/requirements.txt) | 依赖清单；核心与自测仅用标准库，live 模式需要 `openai`。 |
| [`code/UPSTREAM.md`](code/UPSTREAM.md) | 上游仓库与固定 revision（AppWorld/OfficeBench + 蒸馏管线，未导入）。 |

## 来源与边界

固定论文与来源见 [source-packet: acon-2510.00615](../../../../knowledge/source-packets/acon-2510.00615/README.md)；上游代码版本与获取命令见
[code/UPSTREAM.md](code/UPSTREAM.md)。本地 demo 验证的是**规则修订机制与压缩/保留权衡**，
不是论文 AppWorld/OfficeBench 的 26–54% token 降幅；论文数值不能写成本地结果。
