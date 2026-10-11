# ExpeL 论文与代码定位

固定论文 `2308.10144v3`：§4.1–4.3 / PDF pp.3–5；Algorithms 1–3 / p.6；Table 2 / p.9；Table 3 / p.10。

论文原样 PDF 见 [固定论文](paper/paper-v3.pdf)，全文文本按 PDF 页码分隔。代码保存范围是选定原样文件，不是完整可安装 checkout；与论文原实验 commit 的对应关系未知。

## LeapLabTHU/ExpeL

固定 revision：`e41ec9a24823e7b560c561ab191441b56d9bcefc`；许可证：Apache-2.0。

| 固定代码位置 | 原始来源 | SHA256 |
| --- | --- | --- |
| [README.md](official-code/ExpeL/README.md) | [上游固定文件](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/README.md) | `761a26ab3d4ceb381663b44da1f68f670d1a3585cc04d602347e418eb8d5ccfc` |
| [LICENSE](official-code/ExpeL/LICENSE) | [上游固定文件](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/LICENSE) | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` |
| [insight_extraction.py](official-code/ExpeL/insight_extraction.py) | [上游固定文件](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/insight_extraction.py) | `3f6851932d6031ac43353e6428412069d6df53c3ecb08fcfb681c0dd8de10f3e` |
| [agent/expel.py](official-code/ExpeL/agent/expel.py) | [上游固定文件](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py) | `7db4e1be3c16dfca589eb2e194cfb4604be224dab32a04f7f03c4529b1dfcf74` |
| [configs/insight_extraction.yaml](official-code/ExpeL/configs/insight_extraction.yaml) | [上游固定文件](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/configs/insight_extraction.yaml) | `6708d53a211d1c22261bfaa050ef7e2f4667583852f052a4dc7ce42df02d8db7` |
| [configs/agent/expel.yaml](official-code/ExpeL/configs/agent/expel.yaml) | [上游固定文件](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/configs/agent/expel.yaml) | `8d0e75d5693d24267d54cf5857a721485c41b8eefbbea2c66353ea528a2781e0` |

## 固定代码符号行号

- `main`：[official-code/ExpeL/insight_extraction.py:46](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/insight_extraction.py#L46)。
- `ExpelAgent`：[official-code/ExpeL/agent/expel.py:20](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L20)。
- `parse_rules`：[official-code/ExpeL/agent/expel.py:665](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L665)。
- `retrieve_rule_index`：[official-code/ExpeL/agent/expel.py:683](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L683)。
- `is_existing_rule`：[official-code/ExpeL/agent/expel.py:689](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L689)。
- `update_rules`：[official-code/ExpeL/agent/expel.py:696](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L696)。
- `__init__`：[official-code/ExpeL/agent/expel.py:21](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L21)。
- `training`：[official-code/ExpeL/agent/expel.py:74](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L74)。
- `train`：[official-code/ExpeL/agent/expel.py:77](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L77)。
- `eval`：[official-code/ExpeL/agent/expel.py:80](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L80)。
- `next_task`：[official-code/ExpeL/agent/expel.py:83](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L83)。
- `task_critique`：[official-code/ExpeL/agent/expel.py:124](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L124)。
- `success_critique`：[official-code/ExpeL/agent/expel.py:152](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L152)。
- `failure_critique`：[official-code/ExpeL/agent/expel.py:173](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L173)。
- `_build_critique_prompt`：[official-code/ExpeL/agent/expel.py:202](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L202)。
- `prepare_new_eval`：[official-code/ExpeL/agent/expel.py:244](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L244)。
- `prompt_critique`：[official-code/ExpeL/agent/expel.py:248](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L248)。
- `run`：[official-code/ExpeL/agent/expel.py:273](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L273)。
- `create_rules`：[official-code/ExpeL/agent/expel.py:287](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L287)。
- `insert_before_task_prompt`：[official-code/ExpeL/agent/expel.py:404](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L404)。
- `insert_after_task_prompt`：[official-code/ExpeL/agent/expel.py:414](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L414)。
- `after_step`：[official-code/ExpeL/agent/expel.py:417](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L417)。
- `setup_vectorstore`：[official-code/ExpeL/agent/expel.py:420](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L420)。
- `update_dynamic_prompt_components`：[official-code/ExpeL/agent/expel.py:498](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L498)。
- `extend_rules`：[official-code/ExpeL/agent/expel.py:303](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L303)。
- `filtered_vectorstore`：[official-code/ExpeL/agent/expel.py:507](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L507)。
- `topk_docs`：[official-code/ExpeL/agent/expel.py:531](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L531)。
- `fewshot_doc_token_count`：[official-code/ExpeL/agent/expel.py:538](https://github.com/LeapLabTHU/ExpeL/blob/e41ec9a24823e7b560c561ab191441b56d9bcefc/agent/expel.py#L538)。
