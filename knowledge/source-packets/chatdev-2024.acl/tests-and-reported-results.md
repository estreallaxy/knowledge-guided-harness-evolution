# Tests and reported results

## Official verification entry points

- `tests/test_mem0_memory.py`
- `tests/test_memory_embedding_consistency.py`
- `tests/test_server_main_reload.py`
- `tests/test_attachment_upload_filename.py`
- `tests/test_websocket_send_message_sync.py`

## Published result anchors

- p. 6: Table 1: Overall performance of the LLM-powered software development methods, encompassing both single-agent
- p. 6: Table 3: Software statistics include Duration (time con-
- p. 6: Table 2: Pairwise evaluation results. sumed), #Tokens (number of tokens used), #Files (num-
- p. 7: Table 4: Ablation study on main components or mech- Security & Privacy

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | ACL 2024 |
| Official open-source implementation | https://github.com/OpenBMB/ChatDev at `4fb2db0ea90375ce1059f44fe03ffbd191a7a169` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
