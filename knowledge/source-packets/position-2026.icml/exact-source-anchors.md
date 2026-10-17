# Exact source anchors

## Selected mechanism

Retain the multi-agent market environment, prompt-controlled collusion probes, behavior-based scoring, and representative-situation certification protocol; exclude activation-steering training.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.3; `paper/paper-icml2026.txt` marker `===== PDF p.3 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | approach |
| Results and ablations | PDF p.2; `paper/paper-icml2026.txt` marker `===== PDF p.2 =====` | results |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/environment/multiprompt_oligopoly.py:4` | `OligopolyGame` | Pinned implementation entry for the selected mechanism. |
| `official-code/r1_triopoly_tester.py:17` | `getActions` | Pinned implementation entry for the selected mechanism. |
| `official-code/r1_triopoly_tester.py:112` | `getAction` | Pinned implementation entry for the selected mechanism. |
| `official-code/r1_duopoly_tester.py:17` | `getActions` | Pinned implementation entry for the selected mechanism. |
| `official-code/r1_duopoly_tester.py:112` | `getAction` | Pinned implementation entry for the selected mechanism. |
| `official-code/chatgpt_duopoly_tester.py:49` | `is_successful_step` | Pinned implementation entry for the selected mechanism. |
| `official-code/chatgpt_duopoly_tester.py:54` | `load_resumable_steps` | Pinned implementation entry for the selected mechanism. |
| `official-code/chatgpt_duopoly_tester.py:78` | `extract_response_text` | Pinned implementation entry for the selected mechanism. |
| `official-code/environment/oligopoly.py:4` | `OligopolyGame` | Pinned implementation entry for the selected mechanism. |
| `official-code/steering/lib/data_loader.py:15` | `DataLoader` | Pinned implementation entry for the selected mechanism. |
| `official-code/steering/lib/data_loader.py:371` | `test_data_loader` | Pinned implementation entry for the selected mechanism. |
| `official-code/steering/lib/activation_extractor.py:16` | `ActivationExtractor` | Pinned implementation entry for the selected mechanism. |
| `official-code/steering/lib/activation_extractor.py:412` | `test_activation_extractor` | Pinned implementation entry for the selected mechanism. |
| `official-code/steering/lib/visualization.py:27` | `Visualizer` | Pinned implementation entry for the selected mechanism. |
| `official-code/steering/analyze_layers.py:21` | `load_metrics` | Pinned implementation entry for the selected mechanism. |
| `official-code/steering/analyze_layers.py:28` | `print_layer_summary` | Pinned implementation entry for the selected mechanism. |
| `official-code/steering/analyze_layers.py:141` | `compare_multiple_runs` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `2b76e15d3e7b15640590ae1216484802cabcf64d`. Paper page numbers refer to the fixed local proceedings PDF.
