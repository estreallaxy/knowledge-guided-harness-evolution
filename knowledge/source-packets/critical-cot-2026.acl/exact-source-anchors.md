# Exact source anchors

## Selected mechanism

To bridge this gap, we propose Critical-CoT, a novel defense mechanism that conducts a two-stage fine-tuning (FT) on LLMs to develop critical thinking behaviors, enabling them to automatically identify potential backdoors and refuse to generate malicious reasoning steps.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | framework |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 5 Experiments |
| Results and ablations | PDF p.7; `paper/paper-acl2026.txt` marker `===== PDF p.7 =====` | Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-acl2026.txt` marker `===== PDF p.9 =====` | 7 Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/Critical-CoT_evaluation.py:16` | `get_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/Critical-CoT_evaluation.py:35` | `load_dataset_utils` | Pinned implementation entry for the selected mechanism. |
| `official-code/Critical-CoT_evaluation.py:48` | `eval_in_context_backdoor` | Pinned implementation entry for the selected mechanism. |
| `official-code/Critical-CoT_inference.py:7` | `get_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/Critical-CoT_inference.py:18` | `generate_inference_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/Critical-CoT_fine_tuning.py:27` | `get_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/Critical-CoT_fine_tuning.py:73` | `load_dataset_utils` | Pinned implementation entry for the selected mechanism. |
| `official-code/Critical-CoT_fine_tuning.py:80` | `reformat_dataset` | Pinned implementation entry for the selected mechanism. |
| `official-code/Critical-CoT_data_generation.py:19` | `get_args` | Pinned implementation entry for the selected mechanism. |
| `official-code/Critical-CoT_data_generation.py:37` | `load_dataset_utils` | Pinned implementation entry for the selected mechanism. |
| `official-code/Critical-CoT_data_generation.py:51` | `generate_dataset_defense_without_demos` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/utils.py:9` | `split_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/utils.py:36` | `normalize_float_answer` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/utils.py:39` | `str2bool` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/gsm8k_utils.py:5` | `preprocess_dataset` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/gsm8k_utils.py:19` | `poison_data` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/gsm8k_utils.py:52` | `gen_LLM_prompt_with_demos` | Pinned implementation entry for the selected mechanism. |
| `official-code/utils/MATH_utils.py:6` | `extract_boxed_answer` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `d84cad007fc429b9092503d0aac6d66b831690cf`. Paper page numbers refer to the fixed local proceedings PDF.
