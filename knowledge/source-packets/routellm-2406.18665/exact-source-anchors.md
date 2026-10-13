# Exact source anchors

Page number by`paper/paper-v1.pdf`(16 pages)`paper/paper-v1.txt`Yes.`--- PDF page N ---`Marking review.

# Papers

|Content to check|Exact Location|Scope of original support|
| --- | --- | --- |
|Problem-setting: Select between strong/weak models in reasoning|Abstract and § 1, PDF p.1|Routers make decisions at the request level; no multi-model cascades.|
|Main claim: cost down to **1/2 below** without sacrificing quality| Abstract,PDF p.1 |The paper is presented as >2x; as the model changes with the threshold.|
|Train router + data enhancement using** human preference data**| Abstract,PDF p.1;§2–§3,PDF p.2 |The preferred source of data is Chatbot Arena against the war.|
|Type 4 routers| §4(PDF pp.4–6) |Similarity weighting, matrix decomposition, BERT classification, causal language model; see also original.|
|Threshold/scaling parameters| §4,PDF p.5 |The paper stated that index scaling was the best and took gamma = 10.|
|Experiment Settings: Strong`gpt-4-1106-preview`Weak.`Mixtral 8x7B`, random route is contrasted| §5.1,PDF p.7 |For the definitions of the three indicators, CPC (50 per cent)/CPT (80 per cent) and APGR, see this section.|
|MT Bench Main result| Table 1,PDF p.7 |The table indicates 95 per cent of MT Bench 8.8 ≈ GPT-4.|
|MMLU Results| Table 2,PDF p.7 |The table indicates 92 per cent of 75 GPT-4 CPT (50 per cent).|
|GSM8K Results| Table 3,PDF p.8 |The table shows 87 per cent of 75 GPT-4 CPT (50 per cent).|
|Migration: route to model not present in training| Table 4,PDF p.8 |The paper advocated stronger generalization of routers; cross-model results were given in the table.|
|Cost estimates| §5,PDF p.9 |The paper is estimated at GPT-4 and Mixtral 8x7B per million token prices.|

# Official code

Line anchors are measured against the `official-code/` snapshot at revision `0b64fdafe049e596a3f5657c219329f24af24198`.

|Mechanism or evidence|Code Position|Role|
| --- | --- | --- |
|Route controller| `routellm/controller.py:41`(`Controller`) |External interface: Model names in`router-<name>-<threshold>`.|
|Model to Definition| `routellm/controller.py:36`(`ModelPair`),`:31`(`RoutingError`) |A strong/weak model is abnormal with route.|
|threshold calibration| `routellm/calibrate_threshold.py` |Command line calibration: A ratio threshold is applied to a given strong model.|
|Router achieved| `routellm/routers/similarity_weighted/`,`matrix_factorization/`,`causal_llm/`,`routers.py` |Three types of integrated interface to be achieved by open sources in the 4th class router.|
|OpenAI Compatibility Service| `routellm/openai_server.py` |Starts the local OpenAI compatible endpoint to replace the client without intrusion.|
|Checkpoint Configuration| `config.example.yaml` |Points to`routellm/*`weights on HuggingFace.|
|Evaluate scripts| `routellm/evals/benchmarks.py`,`evaluate.py` |Assessment portal (this snapshot is not included in its data catalogue).|
