# Exact source anchors

## Selected mechanism

Declarative policy worksheet, explicit dialogue-state machine, deterministic runtime, and narrow LLM calls for parsing/realization. User-study and logic-task results test this hybrid harness.

## Paper anchors

- p. 6: Algorithm 1 in Appendix A outlines the agent policy. fail to retain information in a conversation and han-
- p. 7: 6 Evaluation on the StarV2 Benchmark AT-SGD XXL 53.1 51.5 81.1
- p. 7: 6.1 Results beats using only GPT-4 Turbo in all domains.
- p. 7: 7 Evaluation on Real User Studies
- p. 8: Evaluation Metrics: We use four evaluation met- Additionally, the higher Execution Accuracy of
- p. 10: Limitations We use Cursor/Co-pilot for code suggestion
- p. 14: Algorithm 1 Genie Agent Policy

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `README.md`
- `pyproject.toml`
- `web/README.md`
- `src/webapp/requirements.txt`
- `experiments/domain_agents/course_enroll/test_runtime.py`
- `experiments/domain_agents/course_enroll/config.yaml`
- `experiments/domain_agents/course_enroll/test_policy.py`
- `experiments/domain_agents/investment_agent/config.yaml`
- `experiments/domain_agents/investment_agent/test_policy.py`
- `experiments/agents/plane_search/__init__.py`
- `experiments/agents/plane_search/api.py`
- `experiments/agents/plane_search/common.py`
- `experiments/agents/plane_search/custom_suql.py`
- `experiments/agents/plane_search/spreadsheet.py`
- `src/worksheets/agent/config.py`
- `experiments/agents/apartment_search/__init__.py`
- `experiments/agents/apartment_search/api.py`
- `experiments/agents/apartment_search/common.py`
- `experiments/agents/apartment_search/custom_suql.py`
- `experiments/agents/apartment_search/spreadsheet.py`
- `experiments/agents/hotel_search/__init__.py`
- `experiments/agents/hotel_search/api.py`
- `experiments/agents/hotel_search/common.py`
- `experiments/agents/hotel_search/custom_suql.py`
- `experiments/agents/hotel_search/spreadsheet.py`
- `experiments/agents/plane_book/__init__.py`
- `experiments/agents/plane_book/api.py`
- `experiments/agents/plane_book/common.py`
- `experiments/agents/plane_book/custom_suql.py`
- `experiments/agents/plane_book/spreadsheet.py`
- `experiments/domain_agents/course_enroll/course_enroll.py`
- `experiments/domain_agents/course_enroll/course_enrollment.json`
- `experiments/domain_agents/investment_agent/investment_agent.py`
- `experiments/domain_agents/ticket_submission/services_general_info_chunked.json`
- `experiments/domain_agents/ticket_submission/ticket_submission.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. Declarative policy worksheet, explicit dialogue-state machine, deterministic runtime, and narrow LLM calls for parsing/realization. User-study and logic-task results test this hybrid harness.

## Symbol-level code anchors

- `README.md:101` — `course_detail_to_individual_params`
- `experiments/domain_agents/investment_agent/test_policy.py:12` — `main`
- `experiments/agents/plane_search/api.py:5` — `plane_search`
- `experiments/agents/plane_search/custom_suql.py:10` — `suql_runner`
- `src/worksheets/agent/config.py:11` — `OpenAIModelConfig`
- `experiments/agents/apartment_search/api.py:5` — `apartment_search_result`
- `experiments/agents/apartment_search/custom_suql.py:10` — `suql_runner`
- `experiments/agents/hotel_search/api.py:5` — `hotel_search`
- `experiments/agents/hotel_search/custom_suql.py:10` — `suql_runner`
- `experiments/agents/plane_book/api.py:5` — `check_availability`
- `experiments/agents/plane_book/custom_suql.py:10` — `suql_runner`
- `experiments/domain_agents/course_enroll/course_enroll.py:24` — `course_detail_to_individual_params`
