# Configurations and examples

## Environment and configuration evidence

| File | Role |
| --- | --- |
| `official-code/README-CN.md` | Dependency, configuration, or usage evidence. |
| `official-code/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/bridgegame/AI_competitors/bridge/round_1/demo1_AI/bridge_v1/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/bridgegame/AI_competitors/bridge/round_1/demo1_AI/bridge_v1/demo1.py` | Dependency, configuration, or usage evidence. |
| `official-code/bridgegame/AI_competitors/bridge/round_1/demo1_AI/bridge_v1/test_ai.py` | Dependency, configuration, or usage evidence. |
| `official-code/bridgegame/AI_competitors/bridge/round_1/demo2_AI/bridge_v1/demo2.py` | Dependency, configuration, or usage evidence. |
| `official-code/bridgegame/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/bridgegame/bridge/AI_example/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/bridgegame/bridge/AI_example/ai_http_server.py` | Dependency, configuration, or usage evidence. |
| `official-code/bridgegame/bridge_Arena/config.py` | Dependency, configuration, or usage evidence. |
| `official-code/bridgegame/bridge_magic/AI_example/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/bridgegame/bridge_magic/AI_example/smart_bridge_ai.py` | Dependency, configuration, or usage evidence. |
| `official-code/bridgegame/start_demo_competition.sh` | Dependency, configuration, or usage evidence. |
| `official-code/chessgame/AI_competitors/chess/round_1/demo1/README.md` | Dependency, configuration, or usage evidence. |
| `official-code/chessgame/AI_competitors/chess/round_1/demo1/demo1_ai.py` | Dependency, configuration, or usage evidence. |
| `official-code/chessgame/AI_competitors/chess/round_1/demo1/integration_test.py` | Dependency, configuration, or usage evidence. |
| `official-code/chessgame/AI_competitors/chess/round_1/demo1/test_ai.py` | Dependency, configuration, or usage evidence. |
| `official-code/chessgame/AI_competitors/chess/round_1/demo2/chess_ai.py` | Dependency, configuration, or usage evidence. |
| `official-code/chessgame/AI_competitors/chess/round_1/demo2/demo2_ai.py` | Dependency, configuration, or usage evidence. |
| `official-code/chessgame/README.md` | Dependency, configuration, or usage evidence. |

## Execution entries

| File | Use |
| --- | --- |
| `official-code/holdemgame/AI_examples/traditional/round1/ADK/demo1/test_ai.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/chessgame/chess_variant/AI_example/test_ai_client.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/holdemgame/AI_examples/traditional/round1/ADK/demo1/validate_ai.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/holdemgame/AI_examples/traditional/round1/ADK/demo2/demo2_ai.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/holdemgame/AI_examples/traditional/round1/ADK/demo1/demo1_ai.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/chessgame/AI_competitors/chess/round_1/demo1/integration_test.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/chessgame/AI_competitors/chess/round_1/demo1/test_ai.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/bridgegame/AI_competitors/bridge/round_1/demo1_AI/bridge_v1/test_ai.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |
| `official-code/gomokugame/AI_competitors/gomoku/round_1/demo1/gomoku_v1/test_ai.py` | Candidate official entry point; follow the pinned upstream instructions for external prerequisites. |

## Integration contract

| Input | Harness operation | Observable output |
| --- | --- | --- |
| Task, current state, and declared budget | Invoke the selected mechanism within its documented preconditions. | Candidate action, state update, retrieval result, schedule, or evaluation request. |
| Tool or environment response | Preserve the response and its provenance in the run trace. | Typed observation, error, timing, and resource evidence. |
| Candidate completion or stop condition | Freeze the resulting state and invoke the applicable verifier. | Score, diagnostic evidence, and a reproducible decision record. |

The snapshot supports mechanism inspection and adaptation. Full reproduction may require external models, datasets, services, or environments that are intentionally excluded.
