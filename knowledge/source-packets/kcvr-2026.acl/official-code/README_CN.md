# KCVR: 知识驱动的视频重建框架

**KCVR** (Knowledge-Centric Video Reconstruction) 是一个基于 **先规划-后生成** (Plan-then-Generate) 范式的教育视频摘要框架。本仓库包含论文投稿的实现代码。

## 概述

KCVR 通过以下步骤从教学视频中重建结构化教育摘要：
1. **规划阶段**：使用 SG-Planner 从领域知识图谱中提取知识子图
2. **微段生成**：使用目标感知解码生成片段级摘要
3. **宏段重建**：使用全局知识概览 (GKS) 将片段摘要融合为完整的视频摘要

## 项目结构

```
kcvr/
├── src/
│   ├── stage0_prep/          # 数据准备和规划
│   │   ├── sg_planner_core.py      # SG-Planner 核心实现
│   │   ├── 01_standardize_labels.py
│   │   ├── 02_cut_and_extract.py
│   │   ├── 05_generate_plans.py
│   │   └── ...
│   ├── stage1_micro/         # 微段级别训练和推理
│   │   ├── build_dataset_v2.py
│   │   ├── plan_utils.py
│   │   └── generate_splits.py
│   ├── stage2_macro/         # 宏段级别训练
│   │   └── build_dataset.py
│   ├── stage3_inference/     # 推理和评估
│   │   ├── infer_micro.py
│   │   ├── infer_macro.py
│   │   └── evaluate.py
│   ├── utils/                # 共享工具
│   │   ├── metric_utils.py   # KPC, LOC, ROUGE, BERTScore
│   │   ├── video_utils.py
│   │   └── csv_utils.py
│   └── evaluation/           # 评估脚本
│       └── eval_main.py
├── data/
│   ├── annotations/          # 标注数据
│   └── splits/               # 训练/验证/测试划分
├── knowledge_graph/           # 知识图谱资源
│   └── raw_csv/              # 图谱节点和关系
├── cache/                    # 中间文件
│   ├── frames/               # 提取的视频帧
│   └── plans/                # 生成的规划
├── experiments/              # 结果和预测
└── README.md
```

## 核心组件

### Stage 0: 规划阶段 (SG-Planner)
- **输入**：原始视频、知识图谱
- **输出**：每个片段的知识子图（规划）
- **关键文件**：`src/stage0_prep/sg_planner_core.py`, `src/stage0_prep/05_generate_plans.py`

### Stage 1: 微段生成
- **输入**：视频片段、规划、帧图像
- **输出**：带目标的片段级摘要
- **关键文件**：`src/stage1_micro/build_dataset_v2.py`, `src/stage1_micro/plan_utils.py`

### Stage 2: 宏段重建
- **输入**：微段摘要、全局知识概览 (GKS)
- **输出**：完整视频摘要
- **关键文件**：`src/stage2_macro/build_dataset.py`

### Stage 3: 推理和评估
- **推理**：使用微调模型生成预测
- **评估**：计算指标（ROUGE, BERTScore, C-F1, KPC, LOC）
- **关键文件**：`src/stage3_inference/infer_micro.py`, `src/stage3_inference/infer_macro.py`, `src/stage3_inference/evaluate.py`

## 评估指标

KCVR 使用以下评估指标：

- **ROUGE-1/2/L**：标准摘要指标
- **BERTScore**：基于 BERT 嵌入的语义相似度
- **C-F1**：概念 F1 分数（知识概念覆盖率）
- **KPC**：知识递进一致性（衡量对知识递进路径的遵循程度）
- **LOC**：学习目标覆盖率（衡量对学习目标的覆盖程度）

详见 `src/utils/metric_utils.py` 了解实现细节。

## 使用说明

### 1. 数据准备

```bash
# 标准化标注
python src/stage0_prep/01_standardize_labels.py

# 提取帧
python src/stage0_prep/02_cut_and_extract.py

# 生成规划
python src/stage0_prep/05_generate_plans.py
```

### 2. 构建训练数据集

```bash
# 微段级别数据集
python src/stage1_micro/build_dataset_v2.py

# 宏段级别数据集
python src/stage2_macro/build_dataset.py
```

### 3. 训练

训练使用 [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) 进行。参见 `LLaMA-Factory/examples/train_lora/` 中的训练配置文件。

### 4. 推理

```bash
# 微段级别推理
python src/stage3_inference/infer_micro.py \
    --model-path models/checkpoints/internvl3_kcvr_micro_v2_7subj_full \
    --dataset data/splits/v2_7subj_trainvaltest.json \
    --split test \
    --output-dir experiments/v7.4_run1/predictions

# 宏段级别推理
python src/stage3_inference/infer_macro.py \
    --model-path models/checkpoints/internvl3_kcvr_macro_v2_7subj_full \
    --micro-predictions experiments/v7.4_run1/predictions/predictions_micro.jsonl \
    --output-dir experiments/v7.4_run1/predictions
```

### 5. 评估

```bash
python src/stage3_inference/evaluate.py \
    --predictions experiments/v7.4_run1/predictions/predictions_micro.jsonl \
    --labels-root data/annotations/standard_labels/micro \
    --plans-root cache/plans/micro_plans \
    --kg-csv-root knowledge_graph/raw_csv \
    --output-dir experiments/v7.4_run1/metrics \
    --level micro
```

## 环境要求

- Python 3.8+
- PyTorch 2.0+
- transformers
- LLaMA-Factory
- rouge-score
- bert-score
- jieba
- 其他依赖（参见 `requirements.txt`）

## 引用

如果使用本代码，请引用我们的论文：

```bibtex
@article{kcvr2025,
  title={KCVR: Knowledge-Centric Video Reconstruction for Educational Video Summarization},
  author={...},
  journal={...},
  year={2025}
}
```

## 许可证

[在此指定您的许可证]

## 联系方式

[您的联系信息]

