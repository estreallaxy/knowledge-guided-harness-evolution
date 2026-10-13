# Tests and reported results

# Thesis reports

The following values are the result of the paper and are not the result of the rerun of the repository. Page number is PDF actual page.

|Experiment|Settings|Results (papers)|Location|
| --- | --- | --- | --- |
|SWE-bench Main result| GPT-4 Turbo | full 12.47%($1.59),Lite 18.00%($1.67) | Table 1, p.6 |
|SWE-bench Main result| Claude 3 Opus | full 10.46%,Lite 13.00% | Table 1, p.6 |
|Shell-only / RAG Contrast| GPT-4 Turbo / Claude 3 Opus |Shell-only Lite 11.00 per cent (w/o demo 7.33 per cent); RG 1.31/2.6 per cent and 3.79/4.3 per cent| Table 1, p.6 |
|ACI component melts| SWE-bench Lite |Baseline (linking + Summarized + 100 rows + Last-5) = 18.0; after elimination of components 15.0/10, 12.0/15.7, 14.3/12.7, 15.0/16.3| Table 3, p.6 |
|Hyperscan|dev subset 37 cases|Optimal 15.1% (T=0.0/window 100/Last-5); Window 200 Significant variation| Table 5, p.25 |
|per-repo/ year| GPT-4 |django 26.32 per cent, psf/requests 33.33 per cent, sympy 10.39 per cent; no inter-year relevance| Table 6/7, p.26 |
|Error Type|Unsolved Track|Incorp/Overly Specific Total 52.0%, Failed Edit Recovery 23.4%; Automatic Aligning Rate 87%| Figure 8 p.8,Table 9 p.35 |
|Edit failure rate|Full Track|1185/2294 (51.7 per cent) with ≥1 lint failed editing; one final editing success 90.5 per cent and one failure down to 57.2 per cent| §5.2, p.8 |
| HumanEvalFix |CodeAct class contrast|Python 87.7 / JS 89.7 / Java 87.9 (median 88.3 per cent, summary 87.7 per cent)|Table 2 p.6, § 5 Text|
| pass@k | Lite |6 averages 17.94 per cent (±0.49), pass@6 32.67 per cent| Table 10, p.35 |

The difference between summary 12.5 per cent/87.7 per cent and text 12.47 per cent/88.3 per cent is derived from rounded to average calibre; the Lite 23 per cent of`README.upstream.md`is a subsequent calibre, which is 18.00 per cent later than the paper.

# Official check the entrance #

|Check Object|Official code|
| --- | --- |
|Bulk Run SWE-bench Example| `python -m sweagent.run.run run-batch --config <yaml>`(`sweagent/run/run.py:13-46`) |
|Track Playback|`run-replay`sub-command (ibid.)|
|Orbital products| `trajectories/<user>/<config>__<model>__<source>`(`official-code/sweagent/run/run_batch.py:33-43`) |

There are no SWE-bench measurements scripts (with external SWE-bench records) in this snapshot, and no official tests directory; end-to-end reruns are not carried out in the source package.

# Current verification status

|Item|Status|
| --- | --- |
|PDF Parsable|Adopted, page 118.|
|Thesis anchor check with local full text|Checked item by item (Table 1/3/5/6/7, § 5.2, § E.3; the drift of the 50 vs code > 100 for the search limit is indicated).|
|Official code version and core document|Fixed and saved (includes utils/, complete Import dependency).|
|Large data and complete benchmark environment|Source packages not included (no SWE-benchharness, no projects/demonstrations).|
|Official-to-end experiment rerun|Not implemented (no pyproject/demonstration track, not directly installed).|
|Proceed from moving to target Harness|Not yet validated.|
