# ExpeL reported results and review boundaries

Fixed paper `2308.10144v3`: §4.1–4.3 / PDF pp.3–5; Algorithms 1–3 / p.6; Table 2 / p.9; Table 3 / p.10.

Table 2 reports first-attempt ALFWorld success: ReAct+Reflexion 40.3%, ExpeL retrieve-only 54.5%, ExpeL+Reflexion 59.0%. The first-attempt column removes current-task retry contributions, although Reflexion is used during experience collection. The 59.0−54.5 contrast supports the rule component under that setup; the full 59.0−40.3 contrast cannot be attributed solely to rule maintenance. Rule extraction and execution use different models; total offline refinement cost is unknown here.

Historical adaptation comparison: the paper names UPVOTE/DOWNVOTE, while pinned `agent/expel.py` uses AGREE/REMOVE. The code processes REMOVE→AGREE→EDIT→ADD, matches rule text by substring, and applies a −3 behavior and descending order when the table is full. The historical local adaptation used basic paper voting rules, stable IDs and input order, without that full-table −3 behavior, upstream parsing/reordering or Reflexion sampling. It is not an equivalent upstream reproduction.

Official test execution and full upstream reproduction remain unknown/not performed. See [configuration and examples](configs-and-examples.md). A prior independent local adaptation passed 5 synthetic functional tests; this is a historical report, not a new run, official test, H0 migration or measured transfer benefit.
