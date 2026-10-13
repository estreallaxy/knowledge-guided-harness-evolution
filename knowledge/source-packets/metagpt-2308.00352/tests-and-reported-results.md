# Tests and reported results

# Thesis reports

The following values are the result of the paper and are not the result of the rerun of the repository. Page number is PDF actual page.

|Experiment|Settings|Results (papers)|Location|
| --- | --- | --- | --- |
| HumanEval / MBPP | MetaGPT+GPT-4 Pass@1 | 85.9 / 87.7 |Fig.4 p.7 and text (no corresponding value table)|
|SoftwareDev Main result|70 Missions| Executability 3.75→；Tokens 31,255；Productivity 124.3；Human Revision Cost 0.83 | Table 1, p.8 |
|Absorption of enforceable feedback| HumanEval/MBPP Pass@1 |+4.2% and +5.4% (w/o feedback 81.7/82.3 → 85.9/87.7)| §4.4 p.9、Fig.4 p.7 |
|The number of characters disappears.| SoftwareDev |1 delegate: 1.0 / 10 reports / $ 0.915 → 4 Role: 4.0 / 2.5 / $1.385; #Lines 83 → 191| Table 3, p.9 |
|Cross-framework comparison|7 Tasks|MetaGPT 3.9 vs ChatDev 2.1, remaining 1.0| Table 4, p.24 |
|w/o Feedback Details|70 Task Avg|26,626.86 + 6,218 tokens, 516.71 s, $1.12, 3.36 minutes| Table 9, p.29 |

Reference note:

- 85.9 / 87.7 appears only in Fig. 4 column and body, without table; 81.7 / 82.3 of w/o feedback in Fig. 4 is pdftotext (compatible with § 4.4 + 4.2 / + 5.4 arithmetic).
- p.8 The text "503 seconds" corresponds to the w/o-feedback column, where MetaGPT is listed as 541 s in Table 1; do not mix when quoting.
- The paper does not contain a "move SOP" controlled digestion (multikey word Zero Impact Verification).

# Official check the entrance #

|Check Object|Official code|
| --- | --- |
|End-to-end generation (including QA feedback)|CLI`metagpt "Create a 2048 game"`or `generate_repo(...)`, product in`./workspace`|
|Test run and failed debugging| `official-code/metagpt/roles/qa_engineer.py:48-177`、`official-code/metagpt/actions/run_code.py:92-146`、`official-code/metagpt/actions/debug_error.py:48-74` |
|Test File Discard|WriterTest writes`{workspace}/tests/test_*.py`|

The HumanEval/MBPP assessment harness is not in this snapshot (zero hits) and must be obtained from`examples/benchmark`upstream.

# Current verification status

|Item|Status|
| --- | --- |
|PDF Parsable|Adopted, 29 pages.|
|Thesis anchor check with local full text|Adopted (Table 1/3/4/9, Fig.4 cross-checks with text; Fig.4 column labels are rotated text, two values are presumed and marked).|
|Official code version and core document|Fixed and saved.|
|Large data and complete benchmark environment|Not included in source package.|
|Official-to-end experiment rerun|Not yet implemented (dispension of modules such as snapshots, complete installation).|
|Proceed from moving to target Harness|Not yet validated.|
