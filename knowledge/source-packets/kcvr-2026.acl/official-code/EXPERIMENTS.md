# Experimental Setup and Configurations

This document describes the experimental setup for all results reported in the paper.

## Experimental Settings

### Dataset Splits

- **In-Domain Training**: 7 subjects (Biology, Chemistry, Math, Physics, Geography, Politics, Chinese)
- **In-Domain Test**: Same 7 subjects, held-out videos
- **OOD Test**: 3 subjects (Tech, History, English) - not seen during training
- **Split Ratios**: 70% train, 15% val, 15% test
- **Random Seed**: 42 (for reproducibility)

Split file: `data/splits/v2_7subj_trainvaltest.json`

### Training Configuration

#### Micro-Level Training
- **Base Model**: InternVL3-8B
- **Method**: LoRA fine-tuning
- **Learning Rate**: 2e-4
- **Batch Size**: 1 per device, gradient accumulation 8 (effective batch size 32)
- **Epochs**: 3
- **Max Length**: 3072 tokens
- **LoRA Rank**: 64

Config file: `LLaMA-Factory/examples/train_lora/internvl3_kcvr_micro_v2_7subj_full.yaml`

#### Macro-Level Training
- **Base Model**: InternVL3-8B (same as micro)
- **Method**: LoRA fine-tuning
- **Learning Rate**: 1e-4
- **Batch Size**: 1 per device, gradient accumulation 8
- **Epochs**: 2
- **Max Length**: 4096 tokens

Config file: `LLaMA-Factory/examples/train_lora/internvl3_kcvr_macro_v2_7subj_full.yaml`

## Baseline Methods

### 1. GPT-4o (Zero-Shot)

- **Implementation**: OpenAI API calls
- **Prompt**: Standard video summarization prompt (no knowledge graph)
- **Input**: Video frames (8 per segment) + transcript
- **Script**: `src/baselines/gpt4o_zero_shot.py`

**Key Settings**:
- Model: `gpt-4o`
- Temperature: 0.7
- Max tokens: 1024

### 2. InternVL-Chat (Zero-Shot)

- **Implementation**: InternVL3-8B without fine-tuning
- **Input**: Video frames + transcript (no planning)
- **Script**: `src/baselines/internvl_zero_shot.py`

**Key Settings**:
- Model: `models/base/InternVL3-8B`
- No LoRA adapters
- Same prompt format as training

### 3. InternVL-SFT (No Planning)

- **Implementation**: InternVL3-8B fine-tuned without knowledge planning
- **Training**: Same as micro-level training, but prompt excludes plan information
- **Script**: `src/baselines/internvl_sft_no_planning.py`

**Key Difference from Full Model**:
- Prompt: Only frames + transcript (no plan text)
- No SG-Planner output
- No knowledge graph guidance

### 4. VideoLLaMA2-SFT

- **Implementation**: VideoLLaMA2-7B fine-tuned on same dataset
- **Training**: Similar to InternVL-SFT baseline
- **Script**: `src/baselines/videollama2_sft.py`

**Note**: VideoLLaMA2 requires separate model download and setup.

### 5. Text-RAG Baseline

- **Implementation**: InternVL-SFT + Top-K knowledge concept definitions concatenated to prompt
- **Method**: Static retrieval (no dynamic planning)
- **Script**: `src/baselines/text_rag_baseline.py`

**Key Settings**:
- Top-K: 10 knowledge concepts
- Selection: Based on transcript keyword matching
- No visual attention (KGVA)

## Ablation Studies

### Component Ablation (Table 4)

Each variant builds upon the previous:

#### B0: Baseline (InternVL-SFT)
- No planning
- No visual attention
- No constraints
- **Config**: `experiments/ablation/configs/B0_baseline.yaml`

#### B1: + CTL Only
- Concept Trigger Layer for evaluation
- Not used in generation (only for metrics)
- **Config**: `experiments/ablation/configs/B1_ctl_only.yaml`

#### B2: + Text-RAG
- Top-K KC definitions in prompt
- No dynamic planning
- **Config**: `experiments/ablation/configs/B2_text_rag.yaml`

#### B3: + SG-Planner
- Contextual pruning
- Min-violation ordering
- Outputs subgraph + progression path
- **Config**: `experiments/ablation/configs/B3_planner.yaml`

#### B4: + KGVA
- Knowledge-Guided Visual Attention
- Cross-attention adapter with concept tokens
- **Config**: `experiments/ablation/configs/B4_kgva.yaml`

#### B5: + ACP-S3D
- Adaptive Constraint Planning
- Soft constrained decoding
- Fallback/retry logic
- **Config**: `experiments/ablation/configs/B5_acp_s3d.yaml`

#### B6: Full Model (+ GKS-Fusion)
- All components
- Global Knowledge Sketch for macro-level fusion
- **Config**: `experiments/ablation/configs/B6_full.yaml`

### Running Ablation Studies

```bash
# Run all ablation experiments
bash experiments/ablation/run_ablation_studies.sh

# Or run individually
bash experiments/ablation/B0_baseline.sh
bash experiments/ablation/B1_ctl_only.sh
# ... etc
```

## Robustness Tests

### 1. ASR-Drop (30% Sentence Removal)

- **Method**: Randomly remove 30% of sentence boundaries from transcript
- **Purpose**: Simulate transcription dropout
- **Script**: `experiments/robustness/asr_drop_30.sh`

**Expected Impact**:
- Baseline: -18% KPC, -17% LOC
- Full Model: -8% KPC, -7% LOC

### 2. ASR-Corrupt (Domain-Specific Corruption)

- **Method**: Reverse domain-specific conditions
  - Math: `a>1` ↔ `0<a<1`
  - Math: `monotone` ↔ `non-monotone`
- **Purpose**: Test robustness to ASR/OCR confusions
- **Script**: `experiments/robustness/asr_corrupt.sh`

**Expected Impact**:
- Baseline: -23% KPC, -20% LOC
- Full Model: -11% KPC, -10% LOC

### 3. Visual-Only (Frames Only)

- **Method**: Input restricted to frames only (no transcript)
- **Purpose**: Test VLM's inherent OCR-like capability
- **Script**: `experiments/robustness/visual_only.sh`

**Expected Results**:
- Baseline: KPC=42.1, C-F1=47.3
- Full Model: KPC=58.2, C-F1=62.8

## Evaluation Metrics

All metrics are computed using `src/utils/metric_utils.py`:

1. **ROUGE-1/2/L**: Standard n-gram overlap (F1-score)
2. **BERTScore**: Semantic similarity using BERT embeddings
3. **C-F1**: Concept F1-score (knowledge concept coverage)
4. **KPC**: Knowledge Progression Consistency
5. **LOC**: Learning Objective Coverage

See `src/utils/metric_utils.py` for implementation details.

### Statistical Aggregation

- **Macro-Average**: Average across subjects (each subject weighted equally)
- **Micro-Average**: Average across all samples (subject-weighted by sample count)

Paper reports **Macro-Average** to avoid bias from subject sample sizes.

## Result Files

All results are saved in `experiments/paper_results/`:

```
experiments/paper_results/
├── in_domain/
│   ├── predictions/
│   └── metrics/
│       ├── metrics.json
│       ├── metrics.csv
│       └── per_subject_metrics.json
├── ood/
│   ├── predictions/
│   └── metrics/
├── ablation/
│   ├── B0/
│   ├── B1/
│   └── ...
└── robustness/
    ├── asr_drop_30/
    ├── asr_corrupt/
    └── visual_only/
```

## Notes

1. **Reproducibility**: All experiments use fixed random seed (42)
2. **Hardware**: Results obtained with 4x A100 (80GB) GPUs
3. **Timing**: Full training takes ~3 days, inference takes ~2 hours
4. **Baseline Access**: Some baselines (GPT-4o) require API access

## Contact

For questions about experimental setup or to request pre-trained models, please contact the authors.

