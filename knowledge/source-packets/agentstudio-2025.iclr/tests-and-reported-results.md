# Tests and reported results

## Official verification entry points

- `eval_agent_desiderata/README.md`
- `eval_online_benchmarks/README.md`
- `eval_agent_desiderata/processing/README.md`
- `eval_agent_desiderata/main.py`
- `eval_agent_desiderata/common.py`
- `eval_agent_desiderata/eval_base.py`
- `eval_agent_desiderata/eval_gui_grounding.py`
- `eval_agent_desiderata/eval_idm.py`
- `eval_agent_desiderata/eval_idmn2n.py`
- `eval_agent_desiderata/eval_success_detection.py`
- `eval_agent_desiderata/make_report.py`
- `eval_agent_desiderata/online_benchmark_analysis.py`
- `eval_agent_desiderata/re_caption_gui_grounding_data.py`
- `eval_agent_desiderata/split_subset.py`
- `tests/test_agents/test_agent.py`
- `tests/test_evaluators/test_filesystem.py`
- `tests/test_evaluators/test_gcalendar.py`
- `tests/test_evaluators/test_gdocs.py`
- `tests/test_evaluators/test_gdrive.py`
- `tests/test_evaluators/test_gforms.py`
- `tests/test_evaluators/test_gmail.py`
- `tests/test_evaluators/test_gsheets.py`
- `tests/test_evaluators/test_gslides.py`
- `tests/test_evaluators/test_joint_evaluation.py`
- `tests/test_evaluators/test_process.py`
- `tests/test_evaluators/test_qa.py`
- `tests/test_evaluators/test_telegram.py`
- `tests/test_evaluators/test_vscode.py`
- `tests/conftest.py`
- `eval_agent_desiderata/processing/process_grounding_data.py`

## Published result anchors

- p. 5: Table 1: Success rates (%) on AgentStudio overall benchmark tasks. Existing models can perform
- p. 6: Table 2: Distribution of failure modes for each model (%). Table 3: Active finish rate (%).
- p. 8: Table 5: Accuracy on IDMBench. Model performance drops significantly in IDM-Multiple.
- p. 9: Table 6: F1 score on CriticBench. More metrics can be found in Table 10 in Appendix A.
- p. 9: Table 10. These results indicate that existing models perform similarly on this task, with no significant
- p. 9: Table 6. In summary, while current VLMs show promise, their performance is still far from effective
- p. 9: Table 7: AgentStudio supports online interactions with real-world operating systems using the most
- p. 14: Table 8: Complete accuracy on GroundUI-1K.
- p. 14: Table 9: Edit Distance on IDM-Multiple (↓). The edit distance is the number of operations (insertion,
- p. 15: Table 10: Accuracy, F1 score, precision, and recall on CriticBench.

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ICLR 2025 |
| Official open-source implementation | https://github.com/ltzheng/agent-studio at `39959e230fecd6651e5700936432861ca7ef7016` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
