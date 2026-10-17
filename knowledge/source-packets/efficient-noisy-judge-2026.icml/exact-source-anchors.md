# Exact source anchors

## Selected mechanism

Large language models (LLMs) are increasingly used as automatic evaluators of generative AI outputs, a paradigm often referred to as "LLM-as-a-judge." In practice, LLM judges are imperfect predictions for the underlying truth and can exhibit systematic, non-random errors.

## Paper anchors

| Evidence target | Exact location | Anchor |
| --- | --- | --- |
| Selected mechanism | PDF p.1; `paper/paper-icml2026.txt` marker `===== PDF p.1 =====` | Mechanism-specific discussion |
| Method or system design | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | method |
| Results and ablations | PDF p.6; `paper/paper-icml2026.txt` marker `===== PDF p.6 =====` | 5.3. Results |
| Limitations or failure conditions | PDF p.9; `paper/paper-icml2026.txt` marker `===== PDF p.9 =====` | 7. Discussion |

## Official-code anchors

| Exact location | Symbol | Role |
| --- | --- | --- |
| `official-code/reproduce/llm_judge_eval.py:47` | `extract_text_from_content` | Pinned implementation entry for the selected mechanism. |
| `official-code/reproduce/llm_judge_eval.py:69` | `get_prompt_and_responses` | Pinned implementation entry for the selected mechanism. |
| `official-code/reproduce/llm_judge_eval.py:103` | `call_judge` | Pinned implementation entry for the selected mechanism. |
| `official-code/docs/lightswitch.js:28` | `bsSetupThemeToggle` | Pinned implementation entry for the selected mechanism. |
| `official-code/docs/pkgdown.js:31` | `changeTooltipMessage` | Pinned implementation entry for the selected mechanism. |
| `official-code/docs/pkgdown.js:116` | `searchFuse` | Pinned implementation entry for the selected mechanism. |
| `official-code/docs/deps/jquery-3.6.0/jquery-3.6.0.js:106` | `DOMEval` | Pinned implementation entry for the selected mechanism. |
| `official-code/docs/deps/jquery-3.6.0/jquery-3.6.0.js:135` | `toType` | Pinned implementation entry for the selected mechanism. |
| `official-code/docs/deps/jquery-3.6.0/jquery-3.6.0.js:506` | `isArrayLike` | Pinned implementation entry for the selected mechanism. |

All code locations refer to official revision `632a89565883be25d94d38b7cd3ca78d62a491f4`. Paper page numbers refer to the fixed local proceedings PDF.
