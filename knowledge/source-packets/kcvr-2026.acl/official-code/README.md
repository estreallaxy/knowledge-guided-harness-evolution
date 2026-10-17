# KCVR: Knowledge-Centric Video Reconstruction

This repository contains the implementation code for KCVR, a framework for educational video summarization based on the Plan-then-Generate paradigm.

## Overview

KCVR generates structured educational summaries from instructional videos through a three-stage pipeline:
1. Planning: Extract knowledge subgraphs using SG-Planner
2. Micro-generation: Generate segment-level summaries
3. Macro-reconstruction: Fuse segments into full-video summaries

## Project Structure

- `src/stage0_prep/`: Data preparation and knowledge planning
- `src/stage1_micro/`: Micro-level (segment) training
- `src/stage2_macro/`: Macro-level (full video) training  
- `src/stage3_inference/`: Inference and evaluation scripts
- `src/utils/`: Shared utilities (metrics, video processing, etc.)
- `data/`: Annotations and data splits
- `knowledge_graph/`: Knowledge graph files (CSV format)
- `cache/`: Intermediate files (plans, frames)

## Key Components

- **Stage 0**: Data preparation and knowledge planning
- **Stage 1**: Micro-level (segment) training and inference
- **Stage 2**: Macro-level (full video) training
- **Stage 3**: Inference and evaluation scripts

## Metrics

The framework evaluates summaries using:
- ROUGE-1/2/L
- BERTScore
- Concept-F1 (C-F1)
- Knowledge Progression Consistency (KPC)
- Learning Objective Coverage (LOC)

## Quick Start

### Quick Verification (Using Example Data)

To quickly verify the code works:

```bash
# Verify data loading and basic functionality
python scripts/quick_verify.py --data-root data --kg-root knowledge_graph/raw_csv
```

### Full Reproduction

For full reproduction of paper results, see **[REPRODUCTION.md](REPRODUCTION.md)** for detailed step-by-step instructions.

**Quick Summary**:
1. **Data Preparation**: Run scripts in `src/stage0_prep/` to process videos and generate plans
2. **Dataset Building**: Build training datasets using scripts in `src/stage1_micro/` and `src/stage2_macro/`
3. **Training**: Train models using LLaMA-Factory (see `REPRODUCTION.md` for details)
4. **Inference**: Use scripts in `src/stage3_inference/` for inference and evaluation

See `DATA_README.md` for data format details and example data.
See `EXPERIMENTS.md` for detailed experimental configurations.

## Requirements

See `requirements.txt` for dependencies. Main requirements:
- Python 3.8+
- PyTorch 2.0+
- transformers
- LLaMA-Factory
- rouge-score, bert-score, jieba

## Data

Example data for the `math` subject (~10% of full dataset) is provided:
- Knowledge graph: `knowledge_graph/raw_csv/`
- Annotations: `data/annotations/standard_labels/micro/math/`
- Plans: `cache/plans/micro_plans/math/`

See `DATA_README.md` for detailed data format description.

## Reproducing Paper Results

This repository contains all code and configurations needed to reproduce the results reported in the paper:

- **Table 1 (In-Domain)**: See `REPRODUCTION.md` Step 5.1
- **Table 2 (OOD)**: See `REPRODUCTION.md` Step 5.2
- **Table 3 (Robustness)**: See `experiments/robustness/README.md`
- **Table 4 (Ablation)**: See `experiments/ablation/README.md`

**Important Notes**:
- Full reproduction requires the complete dataset (contact authors if needed)
- Training requires significant computational resources (4x A100 GPUs recommended)
- Pre-trained models can be provided upon request
- Example data allows verification of code functionality without full dataset

## Documentation

- **[REPRODUCTION.md](REPRODUCTION.md)**: Step-by-step reproduction guide
- **[EXPERIMENTS.md](EXPERIMENTS.md)**: Detailed experimental setup and configurations
- **[DATA_README.md](DATA_README.md)**: Data format and structure
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)**: Code organization

