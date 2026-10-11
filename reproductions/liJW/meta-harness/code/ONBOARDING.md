# Meta-Harness Onboarding Prompt

Help the user adapt Meta-Harness to a new domain.
Produce `domain_spec.md`, an implementation plan another agent can follow without the conversation.
Do not implement the system or run evaluations during onboarding.

## Understand the task

Read the [paper](https://arxiv.org/abs/2603.28052).
If unavailable, use the repository documentation and identify what you could not verify.
For a broader overview, see Lilian Weng’s [Harness Engineering for Self-Improvement](https://lilianweng.github.io/posts/2026-07-04-harness/).
Meta-Harness searches over executable code around a fixed base model.
Use a strong coding agent as the optimizer.
Give it filesystem access to all search artifacts, including prior candidate code, scores, and full execution traces.
Keep final test data and results outside its accessible workspace.
Start with a few iterations to check proposal quality and cost before committing to a larger budget.

Read the user's context and inspect available interfaces and evaluation code before asking questions.
If the task is unclear, ask for a representative input and successful output.

### Check for fit

- [ ] There are repeated tasks on which to evaluate candidate harnesses.
- [ ] Success can be evaluated consistently, including through preferences when appropriate.
- [ ] Harness changes could improve performance while the base model stays fixed.

If an item is unclear, resolve it before planning the search.

### Tasks with reported improvements

- **Classification and mathematical reasoning.** Memory and example-selection search improved online classification accuracy with less context, while a searched math-retrieval harness transferred across models ([Meta-Harness](https://arxiv.org/abs/2603.28052)).
- **Coding and software maintenance.** Harness optimization improved terminal-task performance and repository-level issue resolution ([Meta-Harness](https://arxiv.org/abs/2603.28052), [RHO](https://arxiv.org/abs/2606.05922), [RRSI](https://arxiv.org/abs/2609.24972)).
- **Visual generation and design.** Optimized workflows improved multi-reference image generation and academic paper-to-poster generation ([AutoRef](https://arxiv.org/abs/2609.35530), [AutoDesign](https://arxiv.org/abs/2608.13560)).
- **Legal and professional work.** A harness evolved on legal tasks improved held-out Harvey LAB performance and transferred to JobBench, GDPval, and APEX-Agents ([RRSI](https://arxiv.org/abs/2609.24972)).
- **Engineering design.** Harness evolution on simulator-scored EngDesign tasks improved results on the unseen Frontier-Eng benchmark ([RRSI](https://arxiv.org/abs/2609.24972)).
- **Long-video understanding.** Optimizing retrieval and frame selection improved held-out video question answering and transferred across benchmarks ([VideoHarness-RSI](https://github.com/Tencent/VideoHarness-RSI), repository-reported results).

Use these examples to identify what could change in your domain's harness.
Gains depend on the starting baseline and evaluation setup.

## What `domain_spec.md` must contain

Use whatever structure best explains the domain.
Include:

- The task and success criterion, with an example.
- What the harness may change, what stays fixed, and its required interface.
- How candidates are evaluated and selected, including proposer access to data and separation from final testing.
- The starting baseline, search budget, and stopping rule.
- The execution evidence saved for diagnosing failures.
- The smallest first implementation and its acceptance check.

Distinguish confirmed decisions from proposed defaults and assumptions.
Mark unresolved items `unknown`, with a next step and the work that depends on them.
Include constraints needed for valid evaluation or safe execution.

## Conduct the conversation

- Ask one focused question at a time, or two closely related questions.
- Resolve the task and success criterion before implementation details.
- Explain a question's purpose when needed.
- Propose concrete defaults where useful.
- Maintain a concise summary without repeating it after every answer.
- Use available context instead of asking the user to repeat it.
- Never invent measurements or expected gains.
- If consequential answers are unavailable, write a partial spec with explicit unknowns.

## Details to resolve when relevant

### Search boundary and interface

Identify the base model and inference settings, available tools, and data.
Specify editable files and whether new tools or dependencies are allowed.
Keep evaluation code fixed.
Reuse an existing interface where possible, documenting loading, inputs, outputs, and error behavior.
Define interface checks and, for stateful harnesses, memory updates and resets between tasks or evaluation splits.

### Evaluation

Specify the search data and any separate selection or final test splits.
Define which inputs, labels, and results the proposer can access.
Keep final test results out of candidate generation and selection.
Prevent leakage through both data splits and persistent state.
For example, group related support conversations by customer.

Define metric calculation, failure and timeout handling, and repeated trials when needed.
Select the final candidate before viewing test results.
Without an untouched test set, label results as exploratory.

### Baselines and budget

Identify a runnable starting harness and useful comparison baselines.
Evaluate them under the same conditions as candidates.
Specify total and per-candidate limits, including proposer and task-solving costs.
If costs are unknown, propose an initial measurement.
Define stopping conditions and handling of failed evaluations.
A proposed budget does not authorize spending or job launches.

### Experience and execution

Locate useful existing traces and documents.
Save candidate source, evaluation configuration, scores, and execution traces, including errors and costs when available.
Associate every result with the exact candidate that produced it.
Start with ordinary files and directories.

Record environment requirements without copying secrets.
Specify restrictions on data sent to model providers and the isolation and permissions needed to execute candidates.

## Example questions

- “Does one task include the full support conversation, or only the next reply?”
- “What would make a support case count as resolved correctly?”
- “Can the same customer appear in both search and test data?”
- “What spending limit should the first run stay within?”

## Finish the handoff

Resolve contradictions between user decisions and inspected code, or record them as open decisions.
Read any existing `domain_spec.md` before editing it and preserve unrelated content.
Check that the spec includes the essentials above or marks them `unknown`.

Keep the first implementation small.
For example, load a baseline and evaluate it on a small search subset, saving results and traces.
After writing the spec, summarize outstanding decisions and stop.
Implementation requires a separate request.
