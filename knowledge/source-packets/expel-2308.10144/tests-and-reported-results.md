# Express Report Results and Review Border

Fixed thesis`2308.10144v3`, original location: §4.1-4.3 / PDF pp. 3-5; Algorithms 1-3/p.6; Table 2/p.9; Table 3/p.10.

Table 2: on the first ALFWorld attempt, ReAct+Reflexion scores 40.3%, ExpeL retrieve-only scores 54.5%, and ExpeL+Reflexion scores 59.0%. The first-attempt column removes contributions from retries on the current task, although Reflexion is still used during training. The 59.0−54.5 gap supports the value of the rule component; the full 59.0−40.3 gap cannot be attributed solely to rule maintenance. The original work uses different models for rule extraction and execution, and the total offline refinement cost is unknown here.

A historical reconciliation between a fixed code and a local fit: Thesis term is UPVOTE/DOWNVOTE, fixed code agent/expel.py uses AGREE/REMOVE. Remove rules first REMOVE→AGREE→EDIT→ADD, text substring recognition already in place, list full when REMOVE minus 3 and in descending order. Local adaptation uses basic paper voting rules, stable ID and input order, without full table -3, upstream text resolution/reordering, and Reflexion sampling. Therefore, the code cannot be described as a recurrence or equivalent.

Results of implementation of official tests: unknown; complete upstream system not operational. The official entry in README is stored in [configuration and examples] (configs-and-examples.md). Previously, independent local adaptation passed 5 synthetic functional tests; these were neither official tests nor H0 migrations, returns or full dissertation.
