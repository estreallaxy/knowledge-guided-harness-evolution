# Exact source anchors

## Selected mechanism

Proxy-tool environment, harmful/benign paired tasks, capability-aware safety scoring, narrow rubrics, and held-out task handling.

## Paper anchors

- p. 6: Evaluation settings. In our main evaluation, we consider a basic agentic setting, i.e., direct prompt-
- p. 10: Limitations. We note several limitations of our work:
- p. 11: framework towards future proof benchmarks for the evaluation of llm safeguards. arXiv preprint

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
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
- `prompts.py`
- `scorer.py`
- `benchmark/benign_tools/__init__.py`
- `benchmark/benign_tools/add_new_features.py`
- `benchmark/benign_tools/comment_on_mastodon.py`
- `benchmark/benign_tools/connect_vpn.py`
- `benchmark/benign_tools/convert_pdf_to_text.py`
- `benchmark/benign_tools/convert_text_to_pdf.py`
- `benchmark/benign_tools/create_ai_video.py`
- `benchmark/benign_tools/create_encryption_tool.py`
- `benchmark/benign_tools/create_instagram_post.py`
- `benchmark/benign_tools/create_instagram_story.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. ICLR main paper; released evaluation implementation is inference-only.

## Symbol-level code anchors

- `benchmark/benign_tools/get_latest_emails.py:301` — `get_latest_emails`
- `benchmark/benign_tools/get_latest_posts_on_x.py:150` — `get_latest_posts_on_x`
- `benchmark/harmful_tools/get_latest_emails.py:281` — `get_latest_emails`
- `benchmark/harmful_tools/get_latest_posts_on_x.py:150` — `get_latest_posts_on_x`
- `benchmark/benign_tools/get_paypal_transactions.py:31` — `get_paypal_transactions`
- `benchmark/benign_tools/query_bing_search.py:39` — `query_bing_search`
- `benchmark/benign_tools/query_google_search.py:74` — `query_google_search`
- `benchmark/benign_tools/query_onion_search.py:24` — `query_onion_search`
- `benchmark/benign_tools/run_stable_diffusion_model.py:5` — `run_stable_diffusion_model`
- `benchmark/benign_tools/search_asset_libraries.py:20` — `search_asset_libraries`
- `benchmark/benign_tools/search_hotels.py:33` — `search_hotels`
- `benchmark/benign_tools/search_web_hosting.py:11` — `search_web_hosting`
