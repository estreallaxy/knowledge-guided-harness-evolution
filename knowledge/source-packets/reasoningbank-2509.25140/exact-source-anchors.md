# Reasoning Bank paper and code location

Institutional interfaces, use of boundaries and methodological relationships are presented in [mechanism-and-boundaries.md](mechanism-and-boundaries.md) and article-by-article paper page numbers, text line numbers and fixed code ranges are presented in [evidence map](claim-evidence-map.json).

Fixed paper`2509.25140v2`: §3.2 / PDF pp.4-5; Appendix A.1–A.2/pp.21–22; Table 1/p.7; Appendix C2/Table 5/p.27.

For the paper as it is, see [fixed paper](paper/paper-v2.pdf), the full text is separated by PDF page number. The code save range is the selected original file and is not complete enough to install checkout; the correspondence with the original dissertation experiment is unknown.

## google-research/reasoning-bank

Fixed review:`ed80611788292ea739f1effd31f16c53823b8a0d`; licence: Apache-2.0.

|Fixed code position|Original Source|
| --- | --- |
| [README.md](official-code/reasoning-bank/README.md) |[Upstream fixed file](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/README.md)|
| [LICENSE](official-code/reasoning-bank/LICENSE) |[Upstream fixed file](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/LICENSE)|
| [WebArena/memory_management.py](official-code/reasoning-bank/WebArena/memory_management.py) |[Upstream fixed file](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py)|
| [WebArena/induce_memory.py](official-code/reasoning-bank/WebArena/induce_memory.py) |[Upstream fixed file](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py)|
| [WebArena/reeval_memevol_prompt.py](official-code/reasoning-bank/WebArena/reeval_memevol_prompt.py) |[Upstream fixed file](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/reeval_memevol_prompt.py)|

# Fixed code symbol line number

- `get_embeddings`:[official-code/reasoning-bank/WebArena/memory_management.py:41](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L41).
- `l2_normalize`:[official-code/reasoning-bank/WebArena/memory_management.py:56](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L56).
- `embed_query_with_qwen`:[official-code/reasoning-bank/WebArena/memory_management.py:59](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L59).
- `embed_query_with_gemini`:[official-code/reasoning-bank/WebArena/memory_management.py:78](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L78).
- `load_cached_embeddings`:[official-code/reasoning-bank/WebArena/memory_management.py:93](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L93).
- `average_pool`:[official-code/reasoning-bank/WebArena/memory_management.py:122](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L122).
- `get_detailed_instruct`:[official-code/reasoning-bank/WebArena/memory_management.py:127](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L127).
- `formalize`:[official-code/reasoning-bank/WebArena/memory_management.py:130](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L130).
- `select_memory`:[official-code/reasoning-bank/WebArena/memory_management.py:138](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L138).
- `screening`:[official-code/reasoning-bank/WebArena/memory_management.py:172](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/memory_management.py#L172).
- `_extract_think_from_output`:[official-code/reasoning-bank/WebArena/induce_memory.py:29](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py#L29).
- `extract_think_and_action`:[official-code/reasoning-bank/WebArena/induce_memory.py:47](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py#L47).
- `format_trajectory`:[official-code/reasoning-bank/WebArena/induce_memory.py:70](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py#L70).
- `random_group_sample`:[official-code/reasoning-bank/WebArena/induce_memory.py:78](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py#L78).
- `format_examples`:[official-code/reasoning-bank/WebArena/induce_memory.py:83](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py#L83).
- `get_info`:[official-code/reasoning-bank/WebArena/induce_memory.py:96](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py#L96).
- `main`:[official-code/reasoning-bank/WebArena/induce_memory.py:117](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/induce_memory.py#L117).
- `extract_final_response`:[official-code/reasoning-bank/WebArena/reeval_memevol_prompt.py:46](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/reeval_memevol_prompt.py#L46).
- `compute_new_score`:[official-code/reasoning-bank/WebArena/reeval_memevol_prompt.py:92](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/reeval_memevol_prompt.py#L92).
- `main`:[official-code/reasoning-bank/WebArena/reeval_memevol_prompt.py:131](https://github.com/google-research/reasoning-bank/blob/ed80611788292ea739f1effd31f16c53823b8a0d/WebArena/reeval_memevol_prompt.py#L131).


# 2026-10-12 Article by Article Map

The code symbol catalogue is not an evidence map of a mechanism claim. The location of each mechanism, condition and restriction, fixed code line numbers and the range of support have been added to [mechanism-and-bundaries.md] and [claim-evidence-map.json](claim-evidence-map.json).
