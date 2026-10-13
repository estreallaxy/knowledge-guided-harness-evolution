# Exact source anchors

# Papers

|Content to check|Exact Location|Scope of original support|
| --- | --- | --- |
|ACI definition and motivation (LM is a new type of end user; shell missing small-session editing, no invalid editorial feedback)| §2,PDF p.2–3(Figure 1 p.1,Figure 2 p.2) | "we refer to the interface LM agents use to interact with computers as the agent-computer interface (ACI)";shell "fails to provide simple commands to edit a small file segment, and does not provide any feedback if the user makes an invalid edit". |
|ACI Four Design Principles|§ 2, PDF p.3 (numbered lists 1-4)|The commands are simple, well-functioning, well-received but concise, and guardrail inhibits error transmission ("Guardrails expert error promotion and Hasten response").|
|Windows file view:`open`100 rows, with line numbers, omitted line number tips,`scroll_up/down`,`goto` | §3 "File viewer",PDF p.4;Table 4 p.17;§A.1 p.18(Figure 10) |"The file Viewer submissions a window of at least 100 lines of the file at a time"; display full path, total number of lines, omitted lines and line numbers.|
|Edit command:`edit <start>:<end>`+ Replace text (single area, line range); automatically refresh view after editing; discarding editor and reporting error when defaulting| §3 "File editor",PDF p.4;§A.1 p.19–20(Figure 11 p.20) |"takes 3 reviewed arguments: the start line, end line, and replacement text"; "Invalid edits are identified, and the delegate is asked to try edifying the file again"; Lint output is rolled back (p.19). Note: The editor is a line range and not a line/replace ("search-and-replace" appears only as a description of sed in the No-edit baseline).|
|Feedback design: Visible hint when no output, format error retest template, old observation fold (last 5)| §3 "Context management",PDF p.4;§A.1 Figure 30/31 p.43,Figure 32 p.44 |"Your company ran properly and did not produce any output"; "observations preceding the last 5 are each contained into a single line".|
|Main result: SWE-bench full/lite, RAG / Shell-only / SWE-ent| §5 + Table 1,PDF p.5–6 | SWE-agent w/ GPT-4 Turbo 12.47%(full)/18.00%(Lite);Claude 3 Opus 10.46%/13.00%;Shell-only GPT-4 Turbo Lite 11.00%(w/o demo 7.33);RAG 1.31/3.79. |
|ACI component digestion (editor x search x window x context), SWE-bench Lite| §5.1 + Table 3,PDF p.5–6(Figures 5/6 p.7) |w/lining 18.0 vs action 15.0 vs No edit 10.3; Summarized 18.0 vs Iterative 12.0 vs No search 15.7; 100 Line 18.0 vs 300 Line 14.3 vs whole file 12.7; Last-5 18.0 vs Full resource 15.0 vs w/o demo 16.3.|
|Overscanning and per-repo/year breakdown| §B.1 Table 5 p.25;§B.2 Table 6–7 p.25–26 |GPT-4 Turbo Optimal 15.1% (T=0.0/window 100/Last-5, subset Dev 37); 0.0/200 under 2024-11 code only 9.2-10.8%; by repository django 26.32%, sympy 10.39%.|
|Restrictions/boundary| §E.3 Limitations & Future Work,PDF p.117–118;§A.1 p.19–20 | "The final SWE-agent configuration has a small toolkit";"the ACI development process and case studies are done manually";"the scope of SWE-agent is exclusively focused on programmatic tasks";guardrail "forces some edits to be done in a particular order". |

§ 3 p.3-4 and § A.1 p.20 refer to the results as "at most 50"/ "50 or Few" and the snapshot code is rejected at ** > 100**`official-code/config/commands/search.sh:41`Number of documents,`:102`The number of hits. It was a drift between the completion of the paper (mid-2024) and 2024-11 review.

# Official code

Report yourself.`__version__ = "0.7.0"`(`official-code/sweagent/__init__.py:5`I'm not sure. Note: This review has moved all commands to`config/commands/*.sh`, the Python side does not have an OpenCommand/ EditCommand class (`grep -rn 'OpenCommand|EditCommand|do_edit|lint' --include=*.py`Zero hits; followed-up path omitted in the same section`official-code/`Prefix.

|Mechanism or evidence|File & Line Number|Role|
| --- | --- | --- |
|Other Organiser`_print`Output`[File: … (N lines total)]`, line numbers, omitted line number tips, head/tail take`$WINDOW` | `official-code/config/commands/defaults.sh:1-13` |A 100-line window of § 3 + line number + lines above/ below.|
| `open`Command (line nomber, cross-border warning, directory/document without hint, through`_constrain_line`Centred`_print`) | `config/commands/defaults.sh:15-25, 39-80`(docstring 27-38) |ACI's open interface body;`WINDOW`See default value`config/default.yaml:88`. |
|Scroll/jump:`goto`,`scroll_down`,`scroll_up`Scrolling with alarms| `config/commands/defaults.sh:90-121`(goto),`123-140`(Calling)`145-170`(scroll) |Corresponding paper § 3 Window Moves with "Research First" Guide. Direction by Code`CURRENT_LINE ± (WINDOW-OVERLAP)`(: 151, :166) is the rule (scroll description of Table 4 p.17 is contrary to realization).|
|edit main process: flake8 selection code → backup → write back → lint difference → pass`_print`; printing two paragraphs and rolling back in case of error| `config/commands/edit_linting.sh:1-6`,`49`(`--select=F821,F822,F831,E111,E112,E113,E999,E902`, consistent with the paper p.19),`64-71`,`74-80`,`83-88`(Accept)`90-129`(Rejected,`:127` "Your changes have NOT been applied…") |§ 3/ § A.1 linting guardrail.|
| Command definitions, documentation comments, and runtime parsing (used to generate `{command_docs}`) | `sweagent/tools/commands.py:12-19`, `78-138` (`parse_bash_functions`), `172-227` (`ParseCommandDetailed`) | Supports the command documentation inserted into the prompt described in Appendix A.3. |
|Tool installation and status: command files in packaging`/root/commands`;env variables Export/OVERLAP/CURRENT_LINE/CURRENT_FILE) | `sweagent/tools/tools.py:53-79`(ToolConfig,`:78`Automatic`pip install flake8`),`138-215`(ToolHandler.install/_install_commands/_set_env_variables) |Thesis § A.3 Comand files / Envirronment variables.|
|Feedback & Retry: Format Error Template Append Temporary History Query;`exit_context/exit_cost`Exit Tag| `sweagent/tools/parsing.py:65-121`(ThoughtActionParser,`:75-84` error_message),`sweagent/agent/agents.py:415-431`(retry_after_format_fail),`452-494`(check_format_and_requery) |Corresponding Figure 32 and § 3 error retrying.|
|Main cycle & context management:`step()`/`run()`;old observations fold into one line`Old output omitted (n lines)`;`last_n_observations n:5` | `sweagent/agent/agents.py:621-668, 671-699`;`sweagent/agent/history_processors.py:31-53, 56-68`;`config/default.yaml:113-115`;`sweagent/environment/swe_env.py:163-205` |Thesis §3 History Collapse + Figure 31.|
|Run access and data set: CLI run / run-batch / run-replay;`SWEBenchInstances(flavor=lite/verified/full)` → HF `princeton-nlp/SWE-Bench[_Lite|_Verified]`;Docker mirror`swebench/sweb.eval.x86_64.<iid>:v1` | `sweagent/run/run.py:13-46`;`sweagent/run/run_batch.py:24-43, 78-100, 106-121`;`sweagent/run/batch_instances.py:203-243, 123-135`;`sweagent/environment/config/deployment.py:33-47` |§ 4 Dataset/test entry code matching.|

Line number is based on the`source-packet.json`fixed official code review.
