# Exact source anchors

## Selected mechanism

Allocate compression budgets with marginal information gain, then merge low-value tokens at a finer granularity.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | Method |
| Results and ablations | PDF p.8; `paper/paper-iclr2026.txt` marker `===== PDF p.8 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/eval_utils.py:5` | `normalize_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_utils.py:22` | `compute_exact` | Pinned implementation entry for the selected mechanism. |
| `official-code/eval_utils.py:25` | `compute_f1` | Pinned implementation entry for the selected mechanism. |
| `official-code/instruction_finetune.py:10` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/training_utils.py:9` | `InstructFTTokenizeFunction` | Pinned implementation entry for the selected mechanism. |
| `official-code/training_utils.py:52` | `DataCollatorForDynamicPadding` | Pinned implementation entry for the selected mechanism. |
| `official-code/training_utils.py:79` | `CustomTrainer` | Pinned implementation entry for the selected mechanism. |
| `official-code/ft_inference.py:14` | `setup_distributed` | Pinned implementation entry for the selected mechanism. |
| `official-code/ft_inference.py:32` | `barrier` | Pinned implementation entry for the selected mechanism. |
| `official-code/ft_inference.py:37` | `cleanup_distributed` | Pinned implementation entry for the selected mechanism. |
| `official-code/modeling_comi.py:17` | `parse_target_modules` | Pinned implementation entry for the selected mechanism. |
| `official-code/modeling_comi.py:29` | `build_lora_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/modeling_comi.py:41` | `ModelArguments` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d175a44eaf71084cb1ba2edc91e3f18944e971ad`. Paper page numbers refer to the fixed local proceedings PDF.
