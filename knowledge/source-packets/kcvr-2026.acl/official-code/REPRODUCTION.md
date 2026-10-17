# Reproducing Paper Results

This document provides step-by-step instructions for reproducing the experimental results reported in the paper.

## Overview

The paper reports results on:
- **In-Domain Evaluation**: 7 subjects (Biology, Chemistry, Math, Physics, Geography, Politics, Chinese)
- **Out-of-Domain Evaluation**: 3 subjects (Tech, History, English)
- **Ablation Studies**: 6 variants (B0-B6)
- **Robustness Tests**: ASR-Drop, ASR-Corrupt, Visual-Only

## Prerequisites

1. **Hardware Requirements**:
   - 4x NVIDIA A100 (80GB) or equivalent GPUs for full training
   - 1x GPU sufficient for inference and evaluation

2. **Software Requirements**:
   - Python 3.8+
   - CUDA 11.8+
   - See `requirements.txt` for full dependency list

3. **Data Requirements**:
   - Full dataset: 7 in-domain subjects + 3 OOD subjects
   - Example data (math subject, ~10%) is provided for quick verification
   - For full reproduction, contact authors for complete dataset

## Quick Verification (Using Example Data)

To quickly verify the code works with example data:

```bash
# 1. Verify data loading
python scripts/quick_verify.py --data-root data --kg-root knowledge_graph/raw_csv

# 2. Run inference on example data
python src/stage3_inference/infer_micro.py \
    --model-path [path_to_pretrained_model] \
    --dataset data/splits/example_split.json \
    --split test \
    --output-dir experiments/quick_test/predictions

# 3. Evaluate on example data
python src/stage3_inference/evaluate.py \
    --predictions experiments/quick_test/predictions/predictions_micro.jsonl \
    --labels-root data/annotations/standard_labels/micro \
    --plans-root cache/plans/micro_plans \
    --kg-csv-root knowledge_graph/raw_csv \
    --output-dir experiments/quick_test/metrics \
    --level micro
```

## Full Reproduction Steps

### Step 1: Data Preparation

```bash
# 1.1 Standardize labels
python src/stage0_prep/01_standardize_labels.py \
    --input-dir data/annotations/raw_labels \
    --output-dir data/annotations/standard_labels

# 1.2 Extract video frames
python src/stage0_prep/02_cut_and_extract.py \
    --videos-dir data/raw_videos \
    --output-dir cache/frames \
    --frames-per-segment 8

# 1.3 Generate knowledge plans
python src/stage0_prep/05_generate_plans.py \
    --labels-root data/annotations/standard_labels \
    --kg-csv-root knowledge_graph/raw_csv \
    --output-dir cache/plans
```

### Step 2: Dataset Building

```bash
# 2.1 Generate data splits (7 in-domain + 3 OOD)
python src/stage1_micro/generate_splits.py \
    --labels-root data/annotations/standard_labels \
    --output-file data/splits/v2_7subj_trainvaltest.json \
    --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 \
    --seed 42

# 2.2 Build micro-level training dataset
python src/stage1_micro/build_dataset_v2.py \
    --splits-file data/splits/v2_7subj_trainvaltest.json \
    --labels-root data/annotations/standard_labels/micro \
    --plans-root cache/plans/micro_plans \
    --kg-csv-root knowledge_graph/raw_csv \
    --output-dir trainsets/micro_sft_v2_7subj

# 2.3 Build macro-level training dataset
python src/stage2_macro/build_dataset.py \
    --micro-labels-root data/annotations/standard_labels/micro \
    --macro-labels-root data/annotations/standard_labels/macro \
    --plans-root cache/plans \
    --kg-csv-root knowledge_graph/raw_csv \
    --output-dir trainsets/macro_sft_v2_7subj
```

### Step 3: Model Training

**Note**: Full training requires significant computational resources. Pre-trained models can be provided upon request.

```bash
# 3.1 Micro-level training
cd LLaMA-Factory
llamafactory-cli train examples/train_lora/internvl3_kcvr_micro_v2_7subj_full.yaml

# 3.2 Macro-level training  
llamafactory-cli train examples/train_lora/internvl3_kcvr_macro_v2_7subj_full.yaml
```

Training configuration files are in `LLaMA-Factory/examples/train_lora/`.

### Step 4: Inference

```bash
# 4.1 Micro-level inference (In-Domain Test Set)
python src/stage3_inference/infer_micro.py \
    --model-path models/checkpoints/internvl3_kcvr_micro_v2_7subj_full \
    --dataset data/splits/v2_7subj_trainvaltest.json \
    --split test \
    --output-dir experiments/paper_results/in_domain/predictions

# 4.2 Macro-level inference
python src/stage3_inference/infer_macro.py \
    --model-path models/checkpoints/internvl3_kcvr_macro_v2_7subj_full \
    --micro-predictions experiments/paper_results/in_domain/predictions/predictions_micro.jsonl \
    --output-dir experiments/paper_results/in_domain/predictions

# 4.3 OOD inference
python src/stage3_inference/infer_micro.py \
    --model-path models/checkpoints/internvl3_kcvr_micro_v2_7subj_full \
    --dataset data/splits/v2_7subj_trainvaltest.json \
    --split ood \
    --output-dir experiments/paper_results/ood/predictions
```

### Step 5: Evaluation

```bash
# 5.1 In-Domain evaluation (Table 1)
python src/stage3_inference/evaluate.py \
    --predictions experiments/paper_results/in_domain/predictions/predictions_macro.jsonl \
    --labels-root data/annotations/standard_labels/macro \
    --plans-root cache/plans/macro_gks \
    --kg-csv-root knowledge_graph/raw_csv \
    --splits data/splits/v2_7subj_trainvaltest.json \
    --split test \
    --output-dir experiments/paper_results/in_domain/metrics \
    --level macro

# 5.2 OOD evaluation (Table 2)
python src/stage3_inference/evaluate.py \
    --predictions experiments/paper_results/ood/predictions/predictions_macro.jsonl \
    --labels-root data/annotations/standard_labels/macro \
    --plans-root cache/plans/macro_gks \
    --kg-csv-root knowledge_graph/raw_csv \
    --splits data/splits/v2_7subj_trainvaltest.json \
    --split ood \
    --output-dir experiments/paper_results/ood/metrics \
    --level macro
```

### Step 6: Baseline Comparisons

See `EXPERIMENTS.md` for detailed instructions on running baselines.

```bash
# Run all baselines
bash experiments/baselines/run_all_baselines.sh
```

### Step 7: Ablation Studies

```bash
# Run ablation experiments (B0-B6)
bash experiments/ablation/run_ablation_studies.sh
```

See `experiments/ablation/README.md` for detailed configuration of each variant.

### Step 8: Robustness Tests

```bash
# ASR-Drop (30% sentence removal)
bash experiments/robustness/asr_drop_30.sh

# ASR-Corrupt (domain-specific corruption)
bash experiments/robustness/asr_corrupt.sh

# Visual-Only (frames only, no transcript)
bash experiments/robustness/visual_only.sh
```

## Expected Results

### Table 1: In-Domain Results (Macro-Average)

Expected metrics ranges (may vary slightly due to random seeds):
- ROUGE-1: 47-49
- ROUGE-2: 21-23
- ROUGE-L: 44-46
- BERTScore: 0.84-0.85
- C-F1: 70-72
- KPC: 69-71
- LOC: 67-69

### Table 2: OOD Generalization

Expected improvements over baseline:
- KPC: +5-7 points
- LOC: +5-7 points
- C-F1: +5-7 points

### Table 3: Robustness

Expected degradation (relative to in-domain):
- ASR-Drop: -8% to -9% (KPC), -7% to -8% (LOC)
- ASR-Corrupt: -11% to -12% (KPC), -9% to -10% (LOC)

### Table 4: Ablation Studies

Expected component contributions:
- Planner (B2→B3): +0.8 KPC, +1.2 LOC
- KGVA (B3→B4): +1.7 C-F1, +1.8 KPC/LOC
- ACP-S3D (B4→B5): +2.7 KPC

## Troubleshooting

### Common Issues

1. **Out of Memory**: Reduce `cutoff_len` or `batch_size` in training configs
2. **Missing Dependencies**: Install all packages from `requirements.txt`
3. **Path Errors**: Ensure all paths are relative to project root
4. **Model Loading Errors**: Check model path and LLaMA-Factory version compatibility

### Getting Help

- Check `EXPERIMENTS.md` for detailed experiment configurations
- Review `DATA_README.md` for data format issues
- For full dataset access, contact authors

## Notes on Reproducibility

1. **Random Seeds**: All experiments use seed=42 for reproducibility
2. **Environment**: Results were obtained with PyTorch 2.0+, CUDA 11.8+
3. **Model Versions**: InternVL3-8B base model (specific version in configs)
4. **Data Version**: v2 dataset format (see `data/splits/v2_7subj_trainvaltest.json`)

## Citation

If you use this code or reproduce our results, please cite our paper.

