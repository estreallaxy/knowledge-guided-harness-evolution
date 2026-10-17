# Exact source anchors

## Selected mechanism

To aid autoformalisation in scientific domains, we present FormalScience; a domain-agnostic human-in-the-loop agentic pipeline that enables a single domain expert (without deep formal language experience) to produce syntactically correct and semantically aligned formal proofs of informal reasoning for low economic cost.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.5; `paper/paper-acl2026.txt` marker `===== PDF p.5 =====` | framework |
| Results and ablations | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | analysis |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/qa/qa_prompt_generation.py:5` | `default_few_shot_prompt_generation` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/app/lean_prompts.py:18` | `load_qa_batches` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/app/lean_prompts.py:24` | `get_qa_batch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/app/lean_prompts.py:30` | `build_lean_prompt` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/qa/tests/test_qa_postprocessing.py:12` | `test_split_qas_markdown_parses_markdown_pairs_with_bold_headers` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/qa/tests/test_qa_postprocessing.py:29` | `test_postprocess_keeps_requested_trailing_batch_when_model_echoes_examples` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/qa/tests/test_qa_postprocessing.py:50` | `test_postprocess_deduplicates_identical_pairs_within_a_batch` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/app/tests/test_postprocessing_pipeline.py:30` | `_ok_compile` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/app/tests/test_postprocessing_pipeline.py:34` | `test_parse_boundary_response_accepts_fenced_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/app/tests/test_postprocessing_pipeline.py:56` | `test_parse_extraction_response_accepts_fenced_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/app/compile_lean.py:6` | `compile_lean` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/app/flatten_structured_proofs.py:16` | `_load_json` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/app/flatten_structured_proofs.py:27` | `_is_bad_comment` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/app/flatten_structured_proofs.py:34` | `_extract_comments` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/qa/qa_postprocessing.py:32` | `split_qas_markdown` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/qa/qa_postprocessing.py:66` | `_clean_block` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/qa/qa_postprocessing.py:76` | `_clean_qa_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/app/claude_generate_compile_loop.py:14` | `_ensure_import_paths` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `89b1e0ee60a346039107279dd109d00dfe8e8252`. Paper page numbers refer to the fixed local proceedings PDF.
