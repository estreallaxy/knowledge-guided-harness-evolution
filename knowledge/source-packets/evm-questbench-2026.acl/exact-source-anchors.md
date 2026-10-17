# Exact source anchors

## Selected mechanism

We introduce EVM-QuestBench, an execution-grounded benchmark for natural-language transaction-script generation on EVM-compatible chains.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.8; `paper/paper-acl2026.txt` marker `===== PDF p.8 =====` | architecture |
| Experimental setup | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | 4 Evaluation Setup |
| Limitations or failure conditions | PDF p.8; `paper/paper-acl2026.txt` marker `===== PDF p.8 =====` | failure analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/run_quest_bench.py:44` | `get_all_atomic_question_ids` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_quest_bench.py:57` | `get_all_composite_question_ids` | Pinned implementation entry for the selected mechanism. |
| `official-code/run_quest_bench.py:67` | `get_all_question_ids` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/quest_executor.py:21` | `QuestExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/validators/harvest_rewards_validator.py:12` | `HarvestRewardsValidator` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/validators/query_pending_rewards_validator.py:9` | `QueryPendingRewardsValidator` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/example_usage.py:17` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/check_setup.py:11` | `check_file_exists` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/check_setup.py:20` | `check_directory_exists` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/check_setup.py:29` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/parameter_generator.py:14` | `ParameterGenerator` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/parameter_generator.py:263` | `format_parameter_value` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/quest_controller.py:30` | `quick_anvil_health_check` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/quest_controller.py:67` | `QuestController` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/quest_env.py:18` | `QuestEnvironment` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/validators/erc20_permit_validator.py:11` | `ERC20PermitValidator` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/validators/query_nft_approval_status_validator.py:13` | `QueryNFTApprovalStatusValidator` | Pinned implementation entry for the selected mechanism. |
| `official-code/bsc_quest_bench/validators/query_nft_owner_validator.py:9` | `QueryNFTOwnerValidator` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `dd09c10b98d9d50d3c881df8b5f8412e9ad9728d`. Paper page numbers refer to the fixed local proceedings PDF.
