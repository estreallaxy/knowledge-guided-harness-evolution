# Exact source anchors

## Selected mechanism

To bridge this gap, we introduce collaborative memory, a paradigm that connects isolated semantics to enable the sharing of relational insights.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-acl2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.2; `paper/paper-acl2026.txt` marker `===== PDF p.2 =====` | approach |
| Experimental setup | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | 3.1 Experimental Setup |
| Results and ablations | PDF p.6; `paper/paper-acl2026.txt` marker `===== PDF p.6 =====` | results |
| Limitations or failure conditions | PDF p.10; `paper/paper-acl2026.txt` marker `===== PDF p.10 =====` | 6 Limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/src/memory/graph.py:10` | `UserItemGraph` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/encoder.py:10` | `FacetEncoder` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/encoder.py:119` | `TextBundleBuilder` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/packer.py:9` | `SnippetPacker` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/storage.py:11` | `MemoryStorage` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/pruner_llm_rules.py:11` | `LLMRulePruner` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/pruner_llm_rules.py:278` | `LLMRulePrunerAdapter` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/pruner.py:13` | `PrunerMLP` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/pruner.py:28` | `NeighborPruner` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/manager.py:9` | `MemRecManager` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/domain_rules/__init__.py:17` | `get_domain_rules` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/domain_rules/books_rules.py:9` | `BooksRules` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/domain_rules/goodreads_rules.py:9` | `GoodReadsRules` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/domain_rules/movietv_rules.py:9` | `MovieTVRules` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/memory/domain_rules/yelp_rules.py:9` | `YelpRules` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils.py:12` | `set_seed` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils.py:22` | `load_config` | Pinned implementation entry for the selected mechanism. |
| `official-code/src/utils.py:42` | `_substitute_env_vars` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `58d9031ed91c623b8034d2bf04f39aa937424c33`. Paper page numbers refer to the fixed local proceedings PDF.
