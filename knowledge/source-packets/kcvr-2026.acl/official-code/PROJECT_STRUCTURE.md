# Project Structure

This document describes the code organization and directory structure of KCVR.

## Directory Structure

```
kcvr/
├── README.md                 # 英文项目说明
├── README_CN.md              # 中文项目说明
├── requirements.txt          # Python依赖包
├── PROJECT_STRUCTURE.md      # 本文件：项目结构说明
│
├── src/                      # 源代码目录
│   ├── stage0_prep/         # Stage 0: 数据准备和规划
│   │   ├── sg_planner_core.py      # SG-Planner 核心算法
│   │   ├── 01_standardize_labels.py    # 标注标准化
│   │   ├── 02_cut_and_extract.py       # 视频切分和帧提取
│   │   ├── 03_convert_bge_m3_to_safetensors.py  # 向量模型转换
│   │   ├── 04_standardize_knowledge_graph.py     # 知识图谱标准化
│   │   ├── 05_generate_plans.py                  # 生成知识规划
│   │   ├── 06_audit_plans.py                    # 规划审核
│   │   └── 07_build_alias.py                    # 别名表构建
│   │
│   ├── stage1_micro/         # Stage 1: 微段级别训练
│   │   ├── build_dataset_v2.py      # 构建微段训练数据集
│   │   ├── plan_utils.py            # 规划序列化工具
│   │   └── generate_splits.py       # 生成数据划分
│   │
│   ├── stage2_macro/         # Stage 2: 宏段级别训练
│   │   └── build_dataset.py         # 构建宏段训练数据集
│   │
│   ├── stage3_inference/     # Stage 3: 推理和评估
│   │   ├── infer_micro.py           # 微段推理
│   │   ├── infer_macro.py           # 宏段推理
│   │   └── evaluate.py              # 评估脚本
│   │
│   ├── utils/                # 共享工具模块
│   │   ├── metric_utils.py          # 指标计算（KPC, LOC, ROUGE, BERTScore）
│   │   ├── video_utils.py           # 视频处理工具
│   │   └── csv_utils.py             # CSV处理工具
│   │
│   └── evaluation/           # 评估相关脚本
│       ├── eval_main.py             # 主评估入口
│       ├── validate_gt_vs_asr.py    # GT vs ASR 验证
│       └── t5_eval_metrics_matrix.py # T5 指标矩阵评估
│
├── data/                     # 数据目录（示例结构）
│   ├── annotations/          # 标注数据
│   │   ├── raw_labels/       # 原始标注
│   │   └── standard_labels/  # 标准化标注
│   └── splits/               # 数据划分文件
│
├── knowledge_graph/          # 知识图谱资源
│   └── raw_csv/              # 图谱CSV文件（节点和关系）
│
├── cache/                    # 缓存目录（中间文件）
│   ├── frames/               # 提取的视频帧
│   ├── plans/                # 生成的规划
│   └── ocr_results/         # OCR结果
│
└── experiments/              # 实验结果目录
    └── [experiment_name]/    # 具体实验
        ├── predictions/      # 预测结果
        └── metrics/          # 评估指标
```

## Key Modules

- **Stage 0**: Data preparation, video processing, knowledge planning
- **Stage 1**: Micro-level dataset building and training
- **Stage 2**: Macro-level dataset building and training
- **Stage 3**: Inference and evaluation
- **Utils**: Metrics computation (ROUGE, BERTScore, C-F1, KPC, LOC)

## Workflow

1. **Data Preparation**: Process videos, standardize labels, generate plans
2. **Dataset Building**: Build training datasets for micro and macro levels
3. **Training**: Train models using LLaMA-Factory
4. **Inference & Evaluation**: Generate predictions and compute metrics

See individual script files for usage details.

## Notes

- All paths are relative to project root
- Requires LLaMA-Factory and dependencies (see `requirements.txt`)
- Example data for `math` subject is provided (~10% of full dataset)

