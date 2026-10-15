# Exact source anchors

## Selected mechanism

Environment-feedback loop generates and repairs domain/problem PDDL; Exploration Walk scores executability and guides tree refinement. The 66% vs. 29% comparison is produced without model training.

## Paper anchors

- p. 3: Method(s) Translate Problem Translate Domain No Human Intervention
- p. 3: evaluation, whereas we directly translate problem PDDL without any such assumptions. Guan et al.
- p. 3: approach delegates the entire plan generation process to an LLM instead of leveraging a dedicated
- p. 5: 4 Method
- p. 8: Algorithm 1 Generating Domain PDDL and Problem PDDL Using Environment Feedback
- p. 9: method with multiple response generations (nd = 10, np = 5). (5) P&D Tree + DomProp: Our
- p. 9: Results. Table 2 shows the final results on various environments. We consider a domain generation
- p. 44: limitations that aren’t acknowledged in the paper. The authors should use their best
- p. 46: method in Algorithm 1. For the data, the PDDL files are publicly available, and we provide
- p. 46: results?
- p. 49: limitations, etc.

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `src/domains.py`
- `src/evaluation.py`
- `src/intrinsic_planning.py`
- `src/main.py`
- `src/planning.py`
- `src/problem_domain_translation.py`
- `src/prompts.py`
- `reproduce.sh`
- `src/back_translate.py`
- `src/error_messages.py`
- `src/gen_pddl_template_pddl.py`
- `src/gpt_client.py`
- `src/pddl_utils.py`
- `src/utils.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Environment-feedback loop generates and repairs domain/problem PDDL; Exploration Walk scores executability and guides tree refinement. The 66% vs. 29% comparison is produced without model training.

## Symbol-level code anchors

- `src/domains.py:28` — `Domain`
- `src/evaluation.py:21` — `PlanRatings`
- `src/intrinsic_planning.py:242` — `run`
- `src/main.py:72` — `run`
- `src/planning.py:23` — `PlanningStrategy`
- `src/problem_domain_translation.py:20` — `generate_exact_n_problem_translation_candidates`
- `src/prompts.py:266` — `get_problem_translation_messages`
- `src/back_translate.py:151` — `back_translate_domains`
- `src/gen_pddl_template_pddl.py:67` — `generate_domain_templates`
- `src/gpt_client.py:21` — `GPTConfig`
- `src/pddl_utils.py:20` — `PDDLObj`
- `src/utils.py:14` — `postprocess`
