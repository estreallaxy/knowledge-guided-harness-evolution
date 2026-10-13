# Configs and examples

以下内容取自 `official-code/`（revision `2b23e6acbd4b39f71912816640dcc59e45aa4b5e`），**未在本机执行**。

## 运行前提

| 项目 | 要求 | 来源 |
| --- | --- | --- |
| 安装 | `pip install git+https://github.com/stanford-futuredata/FrugalGPT`（仓库根 `setup.py`） | 上游 README |
| 供应商凭据 | 多家商业 LLM API 的 key（论文用 12 个 API / 5 家供应商） | 论文 Table 1；本包不含凭据 |
| 价格表 | `config/serviceinfo.json`、`config/serviceidmap.json` | 需按**当前**价格重填，论文价格已过时 |
| 数据 | HEADLINES 等数据集（上游通过 wget 下载） | 上游 README；本快照未纳入 `data/` |

## 上游示例命令

```bash
git clone https://github.com/stanford-futuredata/FrugalGPT && cd FrugalGPT
pip install git+https://github.com/stanford-futuredata/FrugalGPT

wget https://github.com/lchen001/DataHolder/releases/download/v0.0.1/HEADLINES.zip
unzip HEADLINES.zip -d strategy/
wget -P db/ https://github.com/lchen001/DataHolder/releases/download/v0.0.1/HEADLINES.sqlite
wget -P db/ https://github.com/lchen001/DataHolder/releases/download/v0.0.1/qa_cache.sqlite

# 按需运行 examples/ 下的 tradeoff 笔记本
jupyter notebook examples/FrugalGPT_gen_tradeoff_HEADLINES.ipynb
```

官方也提供免 API key 的 Colab 演示笔记本；不装环境也能先跑通概念。

## 配置片段

```json
// config/serviceinfo.json（节选：按输入/输出 token 计价的字段）
"textsynth": {
  "gptneox_20B": { "cost_input": 0.0000014, "cost_output": 0.000035, "cost_fixed": 0, "fixed_size": 0 }
}
```

## 未确认项（写为未知）

- cascade 的默认阈值与「升级/不升级」判定细节：论文给的 0.37 是 HEADLINES 上的个例，代码默认值未核对。
- 打分器的训练配置（模型、数据量、超参）：`src/FrugalGPT/scoring.py` 与 notebook 中的设置未逐一核对。
- 与论文 Table 3 对应的 cost-to-reach-accuracy 计算脚本入口：未定位。
