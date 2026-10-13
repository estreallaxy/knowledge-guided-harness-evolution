# Configs and examples

## Paper experiment configuration

|set up|value|Location|
| --- | --- | --- |
| Benchmark |WebArena (six sites: Shop, Admin, Reddit, GitLab, Maps, Multi)| §3.1, PDF p.5 |
|environmental framework|BrowserGym, observed as webpage accessibility tree| §3.1, PDF p.5 |
|action space|WebArena defaults to 15 primitive actions| Appendix A.1, PDF p.14, Table 7 |
|Backbone model|`claude-3.5-sonnet`, used simultaneously for agent policy π, evaluator V and induction module I| §3.1, PDF p.5 |
|Evaluator|The paper comes with a program-based evaluator and is awarded 0/1 points.| §3.1, PDF p.5 |
|baseline|vanilla Claude + BrowserGym; AWM (text skill)| §3.1, PDF p.5 |
|Maximum number of steps|The paper is recorded as H_max, and no specific value is given.| §2.1, PDF p.3 |

**Note**: The paper does not give specific values for step upper limit, temperature, concurrency, retry and judgment timeout; these belong to`unknown`,
When migrating to this project, it must be fixed by itself and stated in the results, and cannot be claimed to be in the same condition as the paper.

## Official process entrance

The official repository pointed to by the paper: <https://github.com/zorazrw/agent-skill-induction>
(Fixed revision`377abe0623a37eaf7f03bdd26cb97bb5331acf47`).

```bash
git clone https://github.com/zorazrw/agent-skill-induction.git
git -C agent-skill-induction checkout 377abe0623a37eaf7f03bdd26cb97bb5331acf47
```

The snapshot has been archived (revision`377abe0623a37eaf7f03bdd26cb97bb5331acf47`, see`official-code/`).
The repository root README and run entry have been saved with the snapshot, but this package is not executed on the local machine, so no verified commands are given.
Before running, you need to complete: environment installation, WebArena/BrowserGym startup method, induction and verification script entry, and evaluation command;
The entry under`official-code/asi/`can be read directly from the repository root README and`asi/run_demo.py`.

## Copiable snippets from the paper

Table 7 (PDF p.14) lists all primitive actions, which can be directly used as an action space comparison table:

```
noop(wait_ms)  click(elem)  hover(elem)  fill(elem, value)
keyboard_press(key_comb)  scroll(x, y)  select_option(elem, options)
goto(url)  go_back()  go_forward()  new_tab()  tab_close()
tab_focus(index)  send_msg_to_user(text)  report_infeasible(reason)
```

The full text of the prompt words for the three LM components (episode evaluation, episode cleaning, and skill induction) is in
Appendix A.2 (PDF pp.14–16), when migrating, you can first use the paper prompts to clear the process, and then use the official code to check the differences.

## Local saving range

Save the PDF/full text of the paper, as well as the materials needed to understand and reproduce the mechanism in`official-code/`:
`asi/{induce,autoeval,actions}`, `asi/agent.py`, `asi/custom_action_set.py`,
`asi/config_files/generate_test_data.py`,`browsergym/`'s`core/`,`experiments/`source code,
and`browsergym/.../benchmark/metadata/*.csv`(evaluating task/split metadata loaded by name at runtime, no answer).

Not included: WebArena/BrowserGym runtime environment and site data, run cache, model credentials, and
`asi/config_files/test.json`,`test.raw.json`(embedded reference answers, belong to benchmark hidden answers, can be
`generate_test_data.py`regenerated). Therefore, this package does not contain answers that can be used directly to increase scores.
