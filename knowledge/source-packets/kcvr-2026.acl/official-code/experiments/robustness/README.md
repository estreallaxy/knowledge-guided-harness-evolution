# Robustness Tests

This directory contains scripts for robustness tests reported in Table 3 of the paper.

## Test Scenarios

### 1. ASR-Drop (30% Sentence Removal)

Simulates transcription dropout by randomly removing 30% of sentence boundaries from transcripts.

**Script**: `asr_drop_30.sh`

**Expected Impact**:
- Baseline: -18.2% KPC, -16.8% LOC
- Full Model: -8.3% KPC, -7.2% LOC

### 2. ASR-Corrupt (Domain-Specific Corruption)

Simulates ASR/OCR confusions in mathematical/scientific content by reversing domain-specific conditions.

**Examples**:
- Math: `a>1` ↔ `0<a<1`
- Math: `monotone` ↔ `non-monotone`

**Script**: `asr_corrupt.sh`

**Expected Impact**:
- Baseline: -22.5% KPC, -20.3% LOC
- Full Model: -11.4% KPC, -9.8% LOC

### 3. Visual-Only (Frames Only)

Tests VLM's inherent OCR-like capability by restricting input to frames only (no transcript).

**Script**: `visual_only.sh`

**Expected Results**:
- Baseline: KPC=42.1, C-F1=47.3
- Full Model: KPC=58.2, C-F1=62.8

## Running Robustness Tests

```bash
# Run all robustness tests
bash experiments/robustness/run_all_robustness.sh

# Or run individually
bash experiments/robustness/asr_drop_30.sh
bash experiments/robustness/asr_corrupt.sh
bash experiments/robustness/visual_only.sh
```

## Results

Results are saved to `experiments/paper_results/robustness/`:
- `asr_drop_30/metrics.json`
- `asr_corrupt/metrics.json`
- `visual_only/metrics.json`

Each result file contains:
- Metrics for baseline and full model
- Relative degradation (ΔKPC, ΔLOC)
- Per-subject breakdown

## Notes

- These tests use the same trained models as in-domain evaluation
- Only the input data is modified (transcript corruption or removal)
- Results show the model's robustness to input noise

