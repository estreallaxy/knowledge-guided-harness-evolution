# Exact source anchors

## Selected mechanism

Represent repository construction as a dependency-aware planning graph that schedules generation and validation steps.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.2; `paper/paper-iclr2026.txt` marker `===== PDF p.2 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.3; `paper/paper-iclr2026.txt` marker `===== PDF p.3 =====` | system |
| Results and ablations | PDF p.50; `paper/paper-iclr2026.txt` marker `===== PDF p.50 =====` | Analysis |
| Limitations or failure conditions | PDF p.44; `paper/paper-iclr2026.txt` marker `===== PDF p.44 =====` | limitations |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/zerorepo/code_gen/trae-agent/trae_agent/tools/docker_tool_executor.py:10` | `DockerToolExecutor` | Pinned implementation entry for the selected mechanism. |
| `official-code/zerorepo/rpg_encoder/rpg_agent/tools/search_code_by_features.py:65` | `FeatureSearchParam` | Pinned implementation entry for the selected mechanism. |
| `official-code/zerorepo/rpg_encoder/rpg_agent/tools/search_code_by_features.py:88` | `SearchCodeByFeatures` | Pinned implementation entry for the selected mechanism. |
| `official-code/CoderMind/scripts/rpg_agent/tools/search_code_by_features.py:66` | `FeatureSearchParam` | Pinned implementation entry for the selected mechanism. |
| `official-code/CoderMind/scripts/rpg_agent/tools/search_code_by_features.py:90` | `SearchCodeByFeatures` | Pinned implementation entry for the selected mechanism. |
| `official-code/CoderMind/scripts/rpg_agent/tools/search_code_snippets.py:69` | `CodeSearchParam` | Pinned implementation entry for the selected mechanism. |
| `official-code/CoderMind/scripts/rpg_agent/tools/search_code_snippets.py:104` | `SearchCodeSnippets` | Pinned implementation entry for the selected mechanism. |
| `official-code/zerorepo/rpg_encoder/rpg_agent/tools/search_code_snippets.py:67` | `CodeSearchParam` | Pinned implementation entry for the selected mechanism. |
| `official-code/zerorepo/rpg_encoder/rpg_agent/tools/search_code_snippets.py:101` | `SearchCodeSnippets` | Pinned implementation entry for the selected mechanism. |
| `official-code/CoderMind/scripts/rpg_agent/tools/search_node.py:88` | `FeatureSearchParam` | Pinned implementation entry for the selected mechanism. |
| `official-code/CoderMind/scripts/rpg_agent/tools/search_node.py:108` | `CodeSearchParam` | Pinned implementation entry for the selected mechanism. |
| `official-code/CoderMind/scripts/rpg_agent/tools/search_node.py:139` | `SearchNodeParam` | Pinned implementation entry for the selected mechanism. |
| `official-code/zerorepo/rpg_encoder/rpg_agent/tools/search_node.py:87` | `FeatureSearchParam` | Pinned implementation entry for the selected mechanism. |
| `official-code/zerorepo/rpg_encoder/rpg_agent/tools/search_node.py:106` | `CodeSearchParam` | Pinned implementation entry for the selected mechanism. |
| `official-code/zerorepo/rpg_encoder/rpg_agent/tools/search_node.py:136` | `SearchNodeParam` | Pinned implementation entry for the selected mechanism. |
| `official-code/zerorepo/code_gen/trae-agent/tests/tools/test_create.py:5` | `main` | Pinned implementation entry for the selected mechanism. |
| `official-code/zerorepo/code_gen/trae-agent/tests/tools/test_bash_tool.py:10` | `TestBashTool` | Pinned implementation entry for the selected mechanism. |
| `official-code/zerorepo/code_gen/trae-agent/tests/tools/test_mcp_tool.py:8` | `TestMCPTool` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `a4e6966c4ff59d84299bc56d6a47ae1f4f7b2885`. Paper page numbers refer to the fixed local proceedings PDF.
