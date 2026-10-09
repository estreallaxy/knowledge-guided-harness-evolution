# 实验配置协议

个人配置已经迁移到各自的完整复现工作区，本目录只保存跨实验的字段约定，不保存任何成员的运行配置。

| 成员 | 配置目录 | 应维护的文件 |
| --- | --- | --- |
| 周梦凡 | `../../reproductions/zhouMF/meta-harness/configs/` | `terminal-bench-2.0.yaml`、`h0.yaml`、`meta-harness.yaml` |
| 赵星源 | `../../reproductions/zhaoXY/meta-harness/configs/` | `terminal-bench-2.0.yaml`、`h0.yaml`、`meta-harness.yaml` |
| 王懿 | `../../reproductions/wangY/meta-harness/configs/` | `terminal-bench-2.0.yaml`、`h0.yaml`、`meta-harness.yaml` |
| 李永康 | `../../reproductions/liYK/meta-harness/configs/` | `terminal-bench-2.0.yaml`、`h0.yaml`、`meta-harness.yaml` |
| 李嘉旺 | `../../reproductions/liJW/meta-harness/configs/` | `terminal-bench-2.0.yaml`、`h0.yaml`、`meta-harness.yaml` |

五份配置须使用相同的 benchmark 划分、内容一致但路径独立的 H0、`deepseek-v4-flash`、实验预算和记录字段。凭据只通过环境变量提供，不写入仓库。
