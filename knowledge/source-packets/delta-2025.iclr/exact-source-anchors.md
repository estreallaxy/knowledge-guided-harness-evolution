# Exact source anchors

## Selected mechanism

Maintain proper-noun records, bilingual summaries, short-term exemplars, and retrieval-based long-term context; update each memory after every segment.

## Paper anchors

- p. 1: method. Furthermore, D ELTA improves pronoun and context-dependent transla-
- p. 2: results (Kim et al., 2019; Maruf et al., 2021; Fernandes et al., 2021). These studies can be separated
- p. 3: method directs LLMs to retrieve key information across varying granularities and spans, and store
- p. 5: framework of D ELTA is illustrated in Figure 1, the algorithm of D ELTA is detailed in Algorithm 1,
- p. 6: Algorithm 1: The Overall Framework of D ELTA
- p. 7: method are not aligned at the sentence level with the source text, we do not report the sCOMET
- p. 8: Ablation Study Table 4 presents an ablation study in the En ⇒ Zh direction using
- p. 10: method avoids sentence omissions and reduces GPU memory consumption, in contrast to main-

## Official-code anchors

The following retained paths are the primary implementation and verification entry points. They are pinned by the upstream Git revision in `source-packet.json`.

- `LICENSE`
- `README.md`
- `requirements.txt`
- `demo/readme.md`
- `demo/requirements.txt`
- `eval_consistency/run_eval.sh`
- `demo/run_gpt.sh`
- `demo/run_qwen.sh`
- `eval_consistency/eval_probability_en_to.py`
- `eval_consistency/eval_probability_to_en.py`
- `eval_consistency/show_wrong_entities.py`
- `eval_consistency/src_tgt_tokenize_en_to.py`
- `eval_consistency/src_tgt_tokenize_to_en.py`
- `infer/run_infer_gpt.sh`
- `infer/run_infer_qwen.sh`
- `demo/DelTA.py`
- `demo/postprocess.py`
- `demo/preprocess.py`
- `infer/infer_gpt.py`
- `infer/infer_qwen.py`
- `infer/post_process.py`

## Evidence boundary

The acceptance and transfer decision is limited to the inference-time mechanism described above. The GPT/API path is inference-only and separable from local-model serving. The paper reports consistency/quality gains and official code exposes memory prompts, retrieval, online updates, and evaluation.

## Symbol-level code anchors

- `eval_consistency/eval_probability_en_to.py:26` — `list_insert`
- `eval_consistency/eval_probability_to_en.py:25` — `list_insert`
- `eval_consistency/show_wrong_entities.py:6` — `main`
- `eval_consistency/src_tgt_tokenize_en_to.py:13` — `sentence_tokenize`
- `eval_consistency/src_tgt_tokenize_to_en.py:13` — `sentence_tokenize`
- `demo/DelTA.py:7` — `get_unique_filename`
- `demo/postprocess.py:4` — `extract_hyp`
- `demo/preprocess.py:10` — `detect_encoding`
- `infer/infer_gpt.py:30` — `invoke_embedding`
- `infer/infer_qwen.py:23` — `invoke_chat`
