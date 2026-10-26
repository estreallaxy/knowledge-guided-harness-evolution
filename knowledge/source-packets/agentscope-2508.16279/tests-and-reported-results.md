# AgentScope 1.0 reported results and review boundaries

Fixed paper `2508.16279v1`: §3.1.4 / PDF pp.10–11; pinned v1.0.0 `_agent_base.py` and `_agent_meta.py`.

The paper and pinned code establish pre/post interfaces associated with reply/observe/reasoning/acting/print. There is no isolated hook success-rate or cost ablation in this review. Framework performance cannot be attributed to callbacks. The selected two files primarily inspect reply/observe/print; other methods are not claimed to have been checked here.

Historical adaptation comparison: pinned `async_wrapper` runs instance hooks before class hooks, deep-copies pre arguments and post arguments/output, and executes post only after `original_func` returns normally. The local adaptation retained that behavior and added a generic wrapper/shared registry plus rebinding support. AgentScope was not installed. These are historical adaptation facts, not validation against a newer middleware interface or guaranteed finally/cleanup behavior.

Official test execution and full upstream reproduction remain unknown/not performed. See [configuration and examples](configs-and-examples.md). A prior independent local adaptation passed 5 synthetic functional tests; this is a historical report, not a new run, official test, H0 migration or measured transfer benefit.
