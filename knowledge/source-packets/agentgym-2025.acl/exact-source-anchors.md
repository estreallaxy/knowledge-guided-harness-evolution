# Exact source anchors

## Selected mechanism

Uniform adapters over 14 environments, real-time concurrent interaction, trajectory capture, task-level feedback, and unified evaluation. Training algorithms and checkpoints are excluded.

## Paper anchors

- p. 1: evaluation of agents, and enables exploration works in several aspects: the number of environments,
- p. 1: results comparable to commercial models. We sets and a broad range of task instructions are es-
- p. 2: Evaluation Learning
- p. 2: framework, we include 7 real-world scenarios: web across multiple tasks, we further investigate their
- p. 3: framework, dataset, and methods. We hope on these trajectories, achieving promising perfor-
- p. 4: 4.2 Framework Architecture of AGENT G YM instruction sets or subsets (WA, ALF, Sci, AM, ST,
- p. 5: evaluation set size, trajectory set size (AGENT T RAJ and AGENT T RAJ-L), and the average interactive rounds of each
- p. 6: Method WS ALF TC Sci Baby MZ WD WT MV TL BD
- p. 7: implementation details. Prompts for each environ-
- p. 7: results in Table 3 demonstrate that, overall, closed-
- p. 7: Implementation Details. Experiments are con- ploring, receiving feedback, and learning in the
- p. 8: Method ALF-OOD Baby-OOD AM ST Model WS ALF TC Baby MZ WD

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `agentenv-alfworld/README.md`
- `agentenv-alfworld/pyproject.toml`
- `agentenv-babyai/README.md`
- `agentenv-babyai/pyproject.toml`
- `agentenv-lmrlgym/README.md`
- `agentenv-lmrlgym/pyproject.toml`
- `agentenv-sciworld/README.md`
- `agentenv-sciworld/pyproject.toml`
- `agentenv-searchqa/README.md`
- `agentenv-searchqa/pyproject.toml`
- `agentenv-sqlgym/README.md`
- `agentenv-sqlgym/pyproject.toml`
- `agentenv-textcraft/README.md`
- `agentenv-textcraft/pyproject.toml`
- `agentenv-tool/README.md`
- `agentenv-tool/pyproject.toml`
- `agentenv-tool/requirements.txt`
- `agentenv-webarena/README.md`
- `agentenv-webarena/pyproject.toml`
- `agentenv-webshop/README.md`
- `agentenv-webshop/pyproject.toml`
- `agentenv/pyproject.toml`
- `env-visualization/README.md`
- `env-visualization/package.json`
- `agentenv-tool/Toolusage/README.md`
- `agentenv-tool/Toolusage/requirements.txt`
- `agentenv-webarena/webarena/CITATION.cff`
- `agentenv-webarena/webarena/LICENSE`
- `agentenv-webarena/webarena/README.md`
- `agentenv-webarena/webarena/requirements.txt`
- `agentenv-webarena/webarena/setup.cfg`
- `agentenv-webarena/webarena/setup.py`
- `agentenv-webshop/webshop/LICENSE.md`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. ACL main long paper; environment/evaluation slice is separable from training.

## Symbol-level code anchors

- `env-visualization/README.md:29` — `BabyAIClient`
- `agentenv-searchqa/agentenv_searchqa/retriever.py:13` — `Encoder`
- `agentenv-searchqa/agentenv_searchqa/reward_score/qa_em.py:19` — `normalize_answer`
- `agentenv-searchqa/agentenv_searchqa/reward_score/qa_em_format.py:19` — `normalize_answer`
- `agentenv-searchqa/scripts/data_process/qa_search_test_merge.py:25` — `make_prefix`
- `agentenv-tool/agentenv_academia/academia_environment.py:12` — `AcademiaEnvServer`
- `agentenv-tool/agentenv_movie/movie_environment.py:13` — `MovieEnvServer`
- `agentenv-tool/agentenv_sheet/sheet_environment.py:13` — `SheetEnvServer`
- `agentenv-tool/agentenv_todo/todo_environment.py:12` — `clean_answer`
- `agentenv-tool/agentenv_weather/weather_environment.py:12` — `WeatherEnvServer`
- `agentenv-tool/Toolusage/toolusage/environment/academia_env.py:19` — `AcademiaEnv`
- `agentenv-tool/Toolusage/toolusage/environment/base_env.py:8` — `BaseEnvironment`
