# Exact source anchors

## Selected mechanism

Probabilistic graphical state/belief tracking is inserted into prompted multi-agent interaction; the reported PGM enhancement improves tested models without updating weights.

## Paper anchors

- p. 4: Evaluation Setting in Figure 2, GPT-4 is used as
- p. 4: 3.3 Evaluation Metrics our benchmark calculates the ability as the ratio
- p. 9: results with PGM, GPT-4+PGM increases the Win tively. Lastly, we introduce Rationality from game

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `chatarena/chatbox_config.py`
- `chatarena/config.py`
- `config_release/competition_airportfee.json`
- `config_release/competition_as_chameleon.json`
- `config_release/competition_as_non_chameleon.json`
- `config_release/competition_as_non_undercover.json`
- `config_release/competition_as_undercover.json`
- `config_release/competition_prisoner.json`
- `config_release/competition_public_good.json`
- `arena_runner.py`
- `chatarena/environments/umshini/agents/__init__.py`
- `chatarena/environments/umshini/agents/content_moderation_bots.py`
- `chatarena/environments/umshini/agents/debate_bots.py`
- `chatarena/environments/umshini/agents/deception_bots.py`
- `run_competition_airportfee.py`
- `run_competition_chameleon.py`
- `run_competition_prisoner.py`
- `run_competition_public_good.py`
- `run_competition_undercover.py`
- `chatarena/agent.py`
- `prompts/airportfee_prompt.py`
- `prompts/chameleon_prompt.py`
- `prompts/prisoner_prompt.py`
- `prompts/public_good_prompt.py`
- `prompts/undercover_prompt.py`
- `chatarena/environments/__init__.py`
- `chatarena/environments/airportfee.py`
- `chatarena/environments/airportfee_pgm.py`
- `chatarena/environments/base.py`
- `chatarena/environments/chameleon_competition.py`
- `chatarena/environments/chameleon_competition_pgm.py`
- `chatarena/environments/prisoner.py`
- `chatarena/environments/prisoner_pgm.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Probabilistic graphical state/belief tracking is inserted into prompted multi-agent interaction; the reported PGM enhancement improves tested models without updating weights.

## Symbol-level code anchors

- `chatarena/chatbox_config.py:1` — `Config`
- `chatarena/config.py:8` — `Config`
- `arena_runner.py:43` — `run`
- `chatarena/environments/umshini/agents/content_moderation_bots.py:12` — `ContentDefender`
- `chatarena/environments/umshini/agents/debate_bots.py:7` — `BasicDebater`
- `chatarena/environments/umshini/agents/deception_bots.py:7` — `DeceptionDefender`
- `run_competition_airportfee.py:14` — `Competition_Airportfee`
- `run_competition_chameleon.py:11` — `Competition_Chameleon`
- `run_competition_prisoner.py:15` — `Competition_Prisoner`
- `run_competition_public_good.py:15` — `Competition_Public_Good`
- `run_competition_undercover.py:12` — `Competition_Under_Cover`
- `chatarena/agent.py:20` — `Agent`
