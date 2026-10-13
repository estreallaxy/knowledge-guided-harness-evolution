# Exact source anchors

# Papers

|Content to check|Exact Location|Scope of original support|
| --- | --- | --- |
|SOP Role Flow Line (Five Role Orders and Duties)| §3.1，PDF p.4–5（Fig.1 p.2、Fig.3 p.5） |Support: Five actors: Project Manager, Architect, Project Manager, Engineering, QA Engineering (p.4); "all actors to work in a regional manner" (p.5); PM Output PRD Architec Turn File Lists/Data Structures/ Interface Defenses Project Project Manager Distribution QA writing test.|
|Structured artifacts are transmitted as messages.|§3.1 p.5, §3.2 pp.5–6; Appendix B.2 pp.18–22 (Figs.7–9)|Support: “Communication through documents and roles” (p.6); the appendix shows Markdown/JSON artifacts for the PRD, system design, tasks, code, and unit tests.|
|Launch - Subscription Pool|§3.2 "Publish-Subscribe Mechanism" p. 6; Fig.2 left p.4|Support: Shared message tool releases structured messages, and the role is to subscribe to selection information (p. 6).|
|Executable feedback cycle|§ 3.3 p.6 (ln290-306); Fig.2 right p.4|Support: Engineeringer writes and runs a single test to debug if it does not pass, "maxium of 3 returns" (p.6).|
|Assessment: HumanEval / MBPP Pass@1| §1 p.2、§4.2 p.7；Fig.4 p.7 |Support: MetaGPT+GPT-4 "85.9% and 87.7% in Pass@1". Note: No corresponding numeric table, the figures appear only in the Fig.4 column and body; Table 7 (p. 25) is the GPT-4/3.5 variant experiment, which is not the source.|
|Evaluation: SoftwareDev Main result Table 1|Table 1 p.8; data set § 4.1 p.6-7, appendix C.1 p.23|Support: Executability 3.75 vs ChatDev 2.25; Tokens 31,255 vs 19,292; Production 124.3 vs 248.9; Human Review Post 0.83 vs 2.5; Time III column 762/503/541(ChatDev/w-o-FB/MetaGPT).|
|Absorption: enforceable feedback (Fig.4 + Table 9)| §4.4 p.9；Fig.4 p.7；Table 9 p.29 |Support: "+ 4.2% and + 5.4% in Pass@ 1 " ; Fig. 4 Last two columns (w/o feedback full) 85.9/ 87.7; exclusability 3.67 → 3.75; review 2.25 0.83.|
|Absorption: Role Number Table 3| §4.4 p.9；Table 3 p.9 |Support: Engineering individual (1 anent): Executobility 1.0, Reviews 10, $0.915 Full 4 roles: 4.0, 2.5, 1.385; #Lines 83 191.|
|Limits|Appendix D.1 p.25; § A.1 p.15|Support: "cannot fully charge to specific scenarios, such as as UI and front-end"; "interrupt the running process" for users; submary-based options do not change structured communication interfaces.|

Comment: The paper does not contain the controlled digestion of the SOP / Change Free Process - § 4.4 with only the number of roles and the implementable feedback; the baseline in the cross-frame comparison of Table 1/4 retains the respective process and does not constitute SOP removal control (`w/o SOP`, `without SOP`, `ablation.*SOP`, `free-flow` multi-keyfixed).

# Official code

(Excerpt`official-code/metagpt/`prefix omitted from the subsequent path in the same section.

|Mechanism or evidence|File & Line Number|Role|
| --- | --- | --- |
|Team assembly and running entrance| `official-code/metagpt/software_company.py:50-62`；`team.py:80-82, 89-93, 99-107, 122-138` |Three characters: →Engineer (n borg=5) → QaEngineer (run tests=True only); invest→run project release requirements; run loop env.run().|
|Five role subscription chain (flow line sequence)| `roles/product_manager.py:37-40`；`roles/architect.py:37-40`；`roles/project_manager.py:37-38`；`roles/engineer.py:91-92`；`roles/qa_engineer.py:44-45` |Seet actions/ watch: PM Watch [UserRequirement, PreparaeDocuments]; Architect {WritePRD}; PMgr [WriteDesign]; Engineering [WriteTasks, SummarizeCode...]; QA [SummarizeCode, WriterTest, RunCode, DebugError].|
|Structured artifact actions (PRD/design/tasks)| `actions/write_prd.py:61, 68-110`; `actions/design_api.py:39, 48-96`; `actions/project_management.py:32, 36-67` |WritePRD → PRD document; WriteDesign → system-design document plus Mermaid; WriteTasks → task-document interface.|
|Launch - Subscription: Environmental Distribution + Role Filter|`environment/base_env.py:175-195`(public message), `164-173` (add rules), `197-208` (run); `roles/role.py:305-309` [watch], `421-444` [observe, filter 433-434], `446-459` (public)|env press send to input role msg buffer; role filters news by`cause_by in watch`.|
|Structured Message|`schema.py:188-197`(Message field), `199-238` (validation/serializer)|Contact/instruct_content/cause_by/sent_from/send_toas a pool and subscription payload definition.|
|Executable feedback: QA writes run-test debugging| `roles/qa_engineer.py:48-93`（_write_test）、`95-127`（_run_code）、`129-142`（_debug_error）、`144-177`（_act）；`actions/run_code.py:92-118`（subprocess, timeout=10s）、`120-146`；`actions/debug_error.py:48-74` |Runs`python tests/…`, parses PASS/FAIL, rewrites and circulates LLM in case of failure (realization of §3.3 mechanism).|
|Engineer write code SumarizeCode QA| `roles/engineer.py:140-153`、`155-163`、`165-204`（send_to="Edward" :197）、`234-239`（_is_pass） |WriteCode→SummarrizeCode sent the control stream to QaEngineer after the decision was passed.|
|CLI and Configure Entry|`software_company.py:81-113`(typer), `131-157` (-init-config); `startup.py:9-10` (disused forward)|`metagpt "..."`CLI; for default configuration search path see`config2.py:98-112`.|

Line number is based on the`source-packet.json`fixed official code review.
