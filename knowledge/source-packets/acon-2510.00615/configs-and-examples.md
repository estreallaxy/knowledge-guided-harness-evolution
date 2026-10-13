# Configs and examples

以下命令与路径取自 `official-code/README.md`（revision `d63f9ae18959dc7215ff62899c94c5e8c56847ae`），
未在本机执行。执行前请确认上游 README 未被更新，并遵守「凭据只走本地文件、不入库」。

## 运行前提

| 项目 | 要求 | 来源 |
| --- | --- | --- |
| Python | 3.11+ | 上游 README 徽章与 Installation 段 |
| 依赖 | `pip install -e .`（仓库根 `pyproject.toml`） | 上游 README |
| 外部环境 | AppWorld（`git lfs` + `pip install -e .` + `appworld install --repo` + `appworld download data`） | 上游 README Quickstart |
| 模型凭据 | OpenAI 兼容 key，写入 `configs/private_config.yaml` | 上游 README Configuration |
| 论文设置 | agent 与 compressor 用 **gpt-4.1 / gpt-4.1-mini**；蒸馏用 Qwen3/Phi-4 系列小模型 | 论文 Table 1/2/13 表注 |

## 上游示例命令（AppWorld + 历史压缩）

```bash
git clone https://github.com/StonyBrookNLP/appworld && cd appworld
git lfs install && pip install -e . && appworld install --repo && appworld download data

git clone https://github.com/microsoft/acon.git && cd acon
mv /path/to/appworld/data /path/to/acon/experiments/appworld
pip install -e .
# 在 configs/private_config.yaml 里放 openai_key

cd experiments/appworld
python run_all.py \
  --split train \
  --model_name gpt-4.1-mini \
  --tag baseline \
  --co_config_path configs/context_opt/gpt-4.1-mini_history.yaml
# 结果目录：experiments/appworld/outputs/gpt-4.1-mini_baseline/
```

指南优化与蒸馏的入口：`experiments/appworld/run_ctxopt_pipeline.py`（`main`），
提示模板在 `experiments/prompt_optimizer/`，OfficeBench 与 8-objective QA 的入口分别在其
`experiments/` 子目录（本快照未纳入 OfficeBench 的 26 MB 数据）。

## 配置片段

```yaml
# configs/private_config_dummy.yaml（上游原样，只有占位键）
openai_key: <YOUR_OPENAI_KEY_HERE>
```

## 未确认项（写为未知）

- 上游各实验的确切 seed、温度、并发与重试设置：论文未给，代码中未被本包逐一核对。
- `experiments/appworld/configs/context_opt/*.yaml` 与论文 Table 1 各行的对应关系：未逐一比对。
- OfficeBench 与 8-objective QA 的完整数据入口：本快照未纳入其数据目录。
