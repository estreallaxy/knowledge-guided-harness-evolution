# Exact source anchors

## Selected mechanism

Run an iterative proposal, execution, measurement, and revision loop over executable scientific procedures.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.9; `paper/paper-iclr2026.txt` marker `===== PDF p.9 =====` | method |
| Results and ablations | PDF p.6; `paper/paper-iclr2026.txt` marker `===== PDF p.6 =====` | Results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/tusoai/prompts.py:15` | `_read_text_with_fallback` | Pinned implementation entry for the selected mechanism. |
| `official-code/tusoai/prompts.py:22` | `_read_package_text_with_fallback` | Pinned implementation entry for the selected mechanism. |
| `official-code/tusoai/prompts.py:30` | `_load_prompt_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/tusoai/optimization_prompts.py:4` | `_target_def_name` | Pinned implementation entry for the selected mechanism. |
| `official-code/tusoai/optimization_prompts.py:8` | `_target_contract` | Pinned implementation entry for the selected mechanism. |
| `official-code/tusoai/optimization_prompts.py:16` | `build_seed_base_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_fs_utils.py:9` | `test_copyfile_portable_copies_data_without_mode_updates` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_fs_utils.py:26` | `test_copytree_portable_swallows_copystat_metadata_errors` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_fs_utils.py:42` | `test_rmtree_portable_swallows_rmdir_metadata_errors` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_openai_models.py:13` | `test_named_openai_aliases_and_pricing` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_openai_models.py:32` | `test_named_model_context_and_cache_pricing` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_openai_models.py:59` | `test_openai_defaults_use_named_models_for_main_stages` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_claude_models.py:19` | `test_latest_claude_model_aliases_and_costs` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_claude_models.py:29` | `test_claude_provider_has_provider_compatible_defaults` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_claude_models.py:39` | `test_latest_claude_models_are_sent_to_messages_api` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_class_target_support.py:17` | `test_run_wiring_metadata_is_saved_to_dev_log` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_class_target_support.py:54` | `test_extract_and_replace_entire_class_preserves_function_replacement` | Pinned implementation entry for the selected mechanism. |
| `official-code/tests/test_class_target_support.py:100` | `test_class_targets_can_be_renamed_and_loaded_from_history_blocks` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `04a02f80bd3e84907e78654203642043de45e71f`. Paper page numbers refer to the fixed local proceedings PDF.
