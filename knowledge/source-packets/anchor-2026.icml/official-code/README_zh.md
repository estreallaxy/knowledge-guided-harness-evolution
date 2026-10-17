# ANCHOR: Calibrated Probabilities from LLM Outputs

ANCHOR 是一个三阶段框架，将大语言模型 (LLM) 的原始输出转化为校准后的概率值。

> [English Version](README.md)

## 目录

- [项目结构](#项目结构)
- [环境配置](#环境配置)
- [配置文件](#配置文件)
- [数据集](#数据集)
- [运行流程](#运行流程)
  - [Stage 1: 因子空间构建](#stage-1-因子空间构建-factor-space-construction)
  - [Stage 2: 上下文感知映射](#stage-2-上下文感知映射-context-aware-mapping)
  - [Stage 3: 概率推理](#stage-3-概率推理-probabilistic-inference)
  - [评估](#评估)
- [FactCheck 数据集流程](#factcheck-数据集流程-xsum)
- [Baseline 方法](#baseline-方法)
- [常见问题](#常见问题)

---

## 项目结构

```
ANCHOR/
├── README.md
├── README_zh.md
├── requirements.txt
├── data/                          # 数据集目录
│   ├── common2sense.json          # 主数据集
│   ├── common2sense_human_annotation.csv   # 人工标注 (用于评估)
│   ├── common2sense_human_annotation.json
│   ├── xsum.json                  # FactCheck 数据集
│   ├── plasma.json / today.json / cnn.json / covid.json / expertqa.json
│   └── ...
└── code/
    ├── utils/
    │   ├── config.py              # ⬅ 全局配置 (API Key、模型路径等)
    │   ├── utils.py               # LLM 调用封装
    │   ├── prompt_shots.py        # Prompt 模板 (common2sense)
    │   ├── prompt_shots_fact_check.py  # Prompt 模板 (FactCheck)
    │   └── response_parse_utils.py    # 响应解析工具
    ├── run/
    │   ├── iterative_factor_gen.py              # Stage 1
    │   ├── hierarchical_condition_mapping.py    # Stage 2
    │   ├── casual_bayesian_train.py             # Stage 3
    │   ├── evaluate_nb_cbn.py                   # 评估脚本
    │   ├── compute_nb_cbn.py                    # F1 分数计算
    │   ├── iterative_factor_gen_fact_check.py   # Stage 1 (FactCheck)
    │   ├── hierarchical_condition_mapping_fact_check.py  # Stage 2 (FactCheck)
    │   ├── scenario_analysis.py / scenario_inference.py / scenario_train.py  # BIRD baseline
    │   └── results/               # 输出目录 (自动创建)
    ├── baselines/                 # Baseline 方法
    └── evaluation/                # BIRD 评估脚本
```

---

## 环境配置

### 1. 创建 Conda 环境

```bash
conda create -n anchor python=3.10 -y
conda activate anchor
```

### 2. 安装依赖

```bash
cd ANCHOR
pip install -r requirements.txt
```

> **注意:**
> - `requirements.txt` 已包含所有必要依赖 (`httpx`, `nltk`, `sentence-transformers>=5.0.0` 等)。
> - 如果你只使用远程 API (如 gpt-4o-mini)，不需要安装 `vllm`。若需要本地部署模型，请额外安装: `pip install vllm==0.6.3`。

### 3. 下载嵌入模型

Stage 1 和 Stage 2 需要 `all-MiniLM-L6-v2` 句向量模型用于因子聚类和 KNN 检索。

```bash
# 方式一: 使用 Python 下载到指定路径
python -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model.save('/your/local/path/all-MiniLM-L6-v2')
print('Model saved successfully.')
"

# 方式二: 使用 huggingface-cli
pip install huggingface_hub
huggingface-cli download sentence-transformers/all-MiniLM-L6-v2 --local-dir /your/local/path/all-MiniLM-L6-v2
```

下载后，将路径填写到 `code/utils/config.py` 中的 `MiniLM_L6_PATH`。

---

## 配置文件

运行前必须编辑 `code/utils/config.py`：

```python
# 嵌入模型本地路径
MiniLM_L6_PATH = '/your/local/path/all-MiniLM-L6-v2'

# 数据集选择: common2sense, plasma, today, cnn, xsum, covid, expertqa
dataset_name = "common2sense"

# 数据与输出目录 (相对于 code/run/)
dataset_file_dic = "../../data/"
save_file_dic = "./results/"

# LLM API 配置 (OpenAI 兼容接口)
model_name = 'gpt-4o-mini'
base_url = 'https://your-api-endpoint/v1'
api_key = 'your-api-key-here'
```

> **提示:** 支持任何 OpenAI 兼容的 API 端点，包括 OpenAI 官方、Azure OpenAI、本地 vLLM 服务等。

---

## 数据集

| 数据集 | 文件名 | 说明 |
|--------|--------|------|
| Common2Sense | `common2sense.json` | 常识推理场景 (主数据集，216 条) |
| XSum | `xsum.json` | 事实核查场景 (FactCheck) |
| PLASMA | `plasma.json` | 常识推理场景 |
| Today | `today.json` | 常识推理场景 |
| CNN | `cnn.json` | 新闻场景 |
| COVID | `covid.json` | COVID 相关场景 |
| ExpertQA | `expertqa.json` | 专家问答场景 |

---

## 运行流程

> **重要:** 三个阶段**必须按顺序执行**，因为每个阶段的输出是下一个阶段的输入。
>
> **工作目录:** 所有命令均从 `code/run/` 目录执行。
>
> **PYTHONPATH:** 必须设置 `PYTHONPATH` 指向 `code/` 目录，以便正确导入 `utils` 模块。

```bash
# 进入运行目录
cd ANCHOR/code/run

# 确保输出目录存在
mkdir -p results
```

### Stage 1: 因子空间构建 (Factor-Space Construction)

通过反向溯因 (reverse abduction) 迭代生成因子，并使用 UMAP + HDBSCAN 进行层次聚类。

```bash
PYTHONPATH=.. python iterative_factor_gen.py \
    --start 0 \
    --end 5 \
    --cluster
```

**参数说明:**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--start` | 0 | 起始数据索引 |
| `--end` | 1000 | 结束数据索引 (设为 5 可快速测试) |
| `--target` | 40 | 每个场景的目标因子数量 |
| `--batch` | 5 | 每轮生成因子批量大小 |
| `--rounds` | 10 | 最大迭代轮数 |
| `--cluster` | 否 | 启用聚类剪枝 (推荐启用) |
| `--model_name` | config 中配置 | 使用的 LLM 模型名称 |
| `--dataset_name` | config 中配置 | 数据集名称 |

**输出文件:**
```
results/{dataset}_{model}_{start}_{end}_factors.json
```

**说明:** 后续阶段默认会查找 `{dataset}_{model}_0_1000_factors_processed_lowercased.json`。如果你使用的 `--end` 参数不是 1000，需要创建符号链接：

```bash
# 示例: 如果 --end 5，则创建软链接
cd results
ln -sf {dataset}_{model}_0_5_factors.json {dataset}_{model}_0_1000_factors_processed_lowercased.json
cd ..
```

---

### Stage 2: 上下文感知映射 (Context-Aware Mapping)

使用层次 KNN 检索从因子库中为每个条件匹配相关因子，通过 LLM 投票和自反思进行筛选。

```bash
PYTHONPATH=.. python hierarchical_condition_mapping.py \
    --start 0 \
    --end 5 \
    --K1 3 \
    --K2 5 \
    --num_prompts 3 \
    --enable_self_reflection \
    --max_retries 5
```

**参数说明:**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--start` | 0 | 起始数据索引 |
| `--end` | 1000 | 结束数据索引 |
| `--K1` | 3 | 检索的顶层聚类数量 |
| `--K2` | 5 | 每个聚类中检索的因子数量 |
| `--num_prompts` | 3 | LLM 投票轮数 |
| `--vote_ratio` | 0.5 | 投票阈值比例 |
| `--alpha` | 0.5 | 聚类名称 vs 因子内容的权重 |
| `--max_retries` | 5 | LLM 响应解析最大重试次数 |
| `--enable_self_reflection` | 是 | 启用自反思步骤 |
| `--disable_self_reflection` | - | 禁用自反思步骤 |

**输入文件:**
```
results/{dataset}_{model}_0_1000_factors_processed_lowercased.json   # Stage 1 的输出
```

**输出文件:**
```
results/{dataset}_{model}_{start}_{end}_condition_mapping.json
```

**说明:** 后续阶段默认查找 `{dataset}_{model}_0_1000_condition_mapping.json`。如有需要，创建符号链接：

```bash
cd results
ln -sf {dataset}_{model}_0_5_condition_mapping.json {dataset}_{model}_0_1000_condition_mapping.json
cd ..
```

---

### Stage 3: 概率推理 (Probabilistic Inference)

构建朴素贝叶斯 (NB) 和因果贝叶斯网络 (CBN)，通过 LLM 识别潜在变量并初始化参数，计算校准概率。

```bash
PYTHONPATH=.. python casual_bayesian_train.py \
    --start 0 \
    --end 5 \
    --max_retries 5
```

**参数说明:**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--start` | 0 | 起始数据索引 |
| `--end` | 1000 | 结束数据索引 |
| `--max_retries` | 20 | LLM 响应解析最大重试次数 |
| `--mapping_type` | `pruned_cluster` | 映射类型 (`pruned_cluster` / `init_cluster` / `uncluster`) |
| `--use_cot` | `_cot_v1_` | CoT 提示变体 |
| `--factor_prob_type` | `llm_` | 因子概率来源 |
| `--latent_prob_type` | `llm` | 潜在变量概率来源 |
| `--SMOOTH_ALPHA` | 0.5 | 平滑参数 |
| `--ablation` | `false` | 消融实验模式 (默认关闭) |

**输入文件:**
```
results/{dataset}_{model}_0_1000_condition_mapping.json   # Stage 2 的输出
```

**输出文件:**
```
results/{dataset}_{model}_{model}_bn_compare_add_both{use_cot}{factor_prob_type}{latent_prob_type}_{mapping_type}.json
```

例如: `common2sense_gpt-4o-mini_gpt-4o-mini_bn_compare_add_both_cot_v1_llm_llm_pruned_cluster.json`

---

### 评估

评估需要人工标注数据 (`data/common2sense_human_annotation.csv` 和 `data/common2sense_human_annotation.json`)。

> **注意:** `evaluate_nb_cbn.py` 中有一个硬编码路径 `common2sense_qwen2.5-2b_0_1000_factors.json`，如果你使用不同模型，需要修改此路径或创建相应的软链接。

```bash
# Step 1: 运行评估脚本 (生成比较结果)
PYTHONPATH=.. python evaluate_nb_cbn.py \
    --start 0 \
    --end 5

# Step 2: 计算 F1 分数
# 需要修改 compute_nb_cbn.py 中的 filename 变量指向 Step 1 的输出文件
PYTHONPATH=.. python compute_nb_cbn.py
```

---

## FactCheck 数据集流程 (XSum)

XSum 等事实核查数据集使用专用脚本，流程与上述类似：

```bash
# Stage 1: 因子生成
PYTHONPATH=.. python iterative_factor_gen_fact_check.py \
    --dataset_name xsum \
    --start 0 \
    --end 5 \
    --cluster

# 创建软链接 (如有需要)
cd results
ln -sf xsum_gpt-4o-mini_0_5_factors.json xsum_gpt-4o-mini_0_1000_factors.json
cd ..

# Stage 2: 条件映射
PYTHONPATH=.. python hierarchical_condition_mapping_fact_check.py \
    --dataset_name xsum \
    --start 0 \
    --end 5 \
    --enable_self_reflection \
    --max_retries 5

# Stage 3: 使用主脚本 (修改 config.py 中的 dataset_name 为 xsum)
PYTHONPATH=.. python casual_bayesian_train.py \
    --dataset_name xsum \
    --start 0 \
    --end 5 \
    --max_retries 5
```

---

## Baseline 方法

BIRD baseline 方法位于 `code/run/` 下的 `scenario_*.py` 和 `code/baselines/` 目录：

```bash
# BIRD 方法
PYTHONPATH=.. python scenario_analysis.py
PYTHONPATH=.. python scenario_inference.py
PYTHONPATH=.. python scenario_train.py
```

其他 baseline 方法请参考 `code/baselines/` 目录中的脚本。评估脚本位于 `code/evaluation/` 目录。

---

## 常见问题

### 1. `ModuleNotFoundError: No module named 'utils'`

确保设置了 `PYTHONPATH`：

```bash
PYTHONPATH=.. python <script_name>.py
```

### 2. `OSError: [Errno 24] Too many open files`

httpx 连接池已在 `utils.py` 中配置限制。如果仍遇到此问题，可以增大系统文件描述符限制：

```bash
ulimit -n 65536
```

### 3. `sentence_transformers` 加载模型失败

确保:
- 使用 `sentence-transformers>=5.0.0`
- 模型已下载到 `config.py` 中 `MiniLM_L6_PATH` 指定的路径
- 路径是一个包含 `config.json` 的目录

### 4. Stage 间数据文件名不匹配

各阶段默认查找 `_0_1000_` 命名模式的文件。如果你的 `--start`/`--end` 参数不同，需要创建符号链接（参见各阶段说明）。

### 5. API 调用超时或失败

- 代码内置了自动重试机制
- 可通过 `--max_retries` 调整重试次数
- 确保 `config.py` 中的 `base_url` 和 `api_key` 正确

---

## 完整快速复现流程 (5 条数据)

以下是使用 common2sense 数据集快速复现全流程的命令序列：

```bash
# 0. 安装依赖并配置
pip install -r requirements.txt
# 编辑 code/utils/config.py 设置 API Key、模型路径等

# 1. 进入运行目录
cd code/run
mkdir -p results

# 2. Stage 1: 因子生成
PYTHONPATH=.. python iterative_factor_gen.py --start 0 --end 5 --cluster

# 3. 创建软链接 (Stage 2 需要)
cd results
ln -sf common2sense_gpt-4o-mini_0_5_factors.json common2sense_gpt-4o-mini_0_1000_factors_processed_lowercased.json
cd ..

# 4. Stage 2: 条件映射
PYTHONPATH=.. python hierarchical_condition_mapping.py --start 0 --end 5 --enable_self_reflection --max_retries 5

# 5. 创建软链接 (Stage 3 需要)
cd results
ln -sf common2sense_gpt-4o-mini_0_5_condition_mapping.json common2sense_gpt-4o-mini_0_1000_condition_mapping.json
cd ..

# 6. Stage 3: 概率推理
PYTHONPATH=.. python casual_bayesian_train.py --start 0 --end 5 --max_retries 5

# 7. 评估 (可选, 需要人工标注数据)
PYTHONPATH=.. python evaluate_nb_cbn.py --start 0 --end 5
```

> **预计运行时间 (5 条数据):**
> - Stage 1: ~15–30 分钟 (取决于 API 速度)
> - Stage 2: ~15–25 分钟
> - Stage 3: ~5–10 分钟
> - 总计: ~35–65 分钟
