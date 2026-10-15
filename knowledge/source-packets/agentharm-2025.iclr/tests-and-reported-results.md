# Tests and reported results

## Official verification entry points

- `benchmark/benign_tools/get_latest_emails.py`
- `benchmark/benign_tools/get_latest_posts_on_x.py`
- `benchmark/harmful_tools/get_latest_emails.py`
- `benchmark/harmful_tools/get_latest_posts_on_x.py`
- `benchmark/benign_tools/get_paypal_transactions.py`
- `benchmark/benign_tools/query_bing_search.py`
- `benchmark/benign_tools/query_google_search.py`
- `benchmark/benign_tools/query_onion_search.py`
- `benchmark/benign_tools/run_stable_diffusion_model.py`
- `benchmark/benign_tools/search_asset_libraries.py`
- `benchmark/benign_tools/search_hotels.py`
- `benchmark/benign_tools/search_web_hosting.py`
- `benchmark/benign_tools/verify_database_security.py`
- `benchmark/harmful_tools/get_paypal_transactions.py`
- `benchmark/harmful_tools/query_bing_search.py`
- `benchmark/harmful_tools/query_google_search.py`
- `benchmark/harmful_tools/query_onion_search.py`
- `benchmark/harmful_tools/run_stable_diffusion_model.py`
- `benchmark/harmful_tools/search_asset_libraries.py`
- `benchmark/harmful_tools/search_hotels.py`
- `benchmark/harmful_tools/search_web_hosting.py`
- `scorer.py`
- `benchmark/benign_tools/__init__.py`
- `benchmark/benign_tools/add_new_features.py`
- `benchmark/benign_tools/comment_on_mastodon.py`
- `benchmark/benign_tools/connect_vpn.py`
- `benchmark/benign_tools/convert_pdf_to_text.py`
- `benchmark/benign_tools/convert_text_to_pdf.py`
- `benchmark/benign_tools/create_ai_video.py`
- `benchmark/benign_tools/create_encryption_tool.py`

## Published result anchors

- p. 9: Table 2: Harm score for best-of-n sampling. We study the effect of best-of-n sampling (n = 5) using tem-
- p. 10: Table 3: Harm score with different prompting. We study the effect of three prompting techniques that are
- p. 15: Table 4: The default system prompt we used in our experiments.
- p. 16: Table 5: The prompt for the semantic refusal judge.
- p. 16: Table 6: The additional prompt for Llama-3.1 appended to the default system prompt shown in Table 4.
- p. 16: Table 7: The prompts that we use in the experiment from Table 3. We append these prompts to the default
- p. 17: Table 8: Refusals on agent vs. chat-only tasks. Comparison of refusal rates for GPT-4o and Claude models
- p. 18: Table 9: Main results on the public test set. All numbers on the benign behaviors are computed without any
- p. 19: Table 10: Main results on the private test set. We compute the results on a subset of models. Harm Score:

## Screening record

| Check | Result |
| --- | --- |
| Formal top-conference publication | 2025, ICLR |
| Official open-source implementation | https://github.com/UKGovernmentBEIS/inspect_evals at `d2d3aac91a37a8c7c8ed3de8b4e899c2594f24a9` |
| Training required for the selected harness mechanism | No |
| ExecutorLLM or OptimizerLLM weight update included | No |
| Datasets, model weights, generated runs, secrets, or hidden answers retained | No |
| Local end-to-end reproduction completed during ingestion | No; this packet preserves evidence and implementation material for later controlled reproduction. |

Reported numbers remain claims of the paper until independently reproduced under the project's common protocol.
