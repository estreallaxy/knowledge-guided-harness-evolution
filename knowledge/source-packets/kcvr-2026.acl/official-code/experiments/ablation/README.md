# Ablation Studies

This directory contains scripts and configurations for running ablation studies reported in Table 4 of the paper.

## Ablation Variants

Each variant (B0-B6) builds upon the previous one:

- **B0**: Baseline (InternVL-SFT, no planning)
- **B1**: + CTL Only (for evaluation)
- **B2**: + Text-RAG (static knowledge retrieval)
- **B3**: + SG-Planner (dynamic knowledge planning)
- **B4**: + KGVA (Knowledge-Guided Visual Attention)
- **B5**: + ACP-S3D (Adaptive Constraint Planning)
- **B6**: Full Model (+ GKS-Fusion)

## Running Ablation Studies

### Option 1: Run All Ablations

```bash
bash experiments/ablation/run_ablation_studies.sh
```

This will run all variants sequentially and save results to `experiments/paper_results/ablation/`.

### Option 2: Run Individual Variants

```bash
# Baseline
bash experiments/ablation/B0_baseline.sh

# With CTL
bash experiments/ablation/B1_ctl_only.sh

# ... etc
```

## Configuration Files

Each variant has a corresponding configuration file in `experiments/configs/ablation/`:

- `B0_baseline.yaml`: No planning, no visual attention
- `B1_ctl_only.yaml`: CTL enabled for evaluation only
- `B2_text_rag.yaml`: Text-RAG enabled
- `B3_planner.yaml`: SG-Planner enabled
- `B4_kgva.yaml`: KGVA enabled
- `B5_acp_s3d.yaml`: ACP-S3D enabled
- `B6_full.yaml`: All components enabled

## Expected Results

See Table 4 in the paper for expected metric values. Key insights:

1. **Planner (B2→B3)**: +0.8 KPC, +1.2 LOC
2. **KGVA (B3→B4)**: +1.7 C-F1, +1.8 KPC/LOC
3. **ACP-S3D (B4→B5)**: +2.7 KPC (largest single jump)

## Notes

- Each ablation requires re-training the model with the corresponding configuration
- Training time: ~3 days per variant on 4x A100 GPUs
- Results are saved in `experiments/paper_results/ablation/{B0-B6}/`

