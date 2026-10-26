# liYK: stage-two mechanism coverage and source-quality review

## Current PR scope (2026-10-26)

This source-materials PR covers six base sources: ReasoningBank and ExpeL (memory), AgentRewind and StateFork (session/environment state), and AgentScope and AgentDojo (extensions/lifecycle hooks), plus G-Memory as a memory supplement. AgentDojo is a current base-pair member, although the historical checks below added it as a supplement. New NORA changes are excluded; historical evidence may refer to NORA material already present on main. ACE, ASpec, MemEvolve, and PlugMem changes are outside this PR.

The dated evidence below is retained historical evidence from 2026-10-13, not a fresh seven-source result. Its original six-packet batch included NORA; adding G-Memory and AgentDojo produced eight packets, 29 claims, and 39 code ranges. Current PR scope does not rewrite those counts or imply new upstream runs, team acceptance, Method implementation, or H0 gains.

## Current seven-source checks (2026-10-26)

Run `python3 -B knowledge/source-packets/verify_liyk_stage2.py --current --upstream` for this PR. The current entry checks five base packets using the original schema, AgentDojo (the sixth base source) using its different schema, and the G-Memory supplement. Output grouping reflects schema compatibility, not source-admission roles. The seven sources contain 25 mapped claims and 35 code ranges; the membership check selects 24 claims and excludes RB5 as paper system-level support. All 43 selected upstream files matched the pinned versions in this run. These are static checks, not upstream execution or a new human decision. See the [current check record](liyk-base-source-validation-2026-10-26.json) and [personal conditional decision summary](liyk-personal-source-admission-2026-10-22.json).

Candidate-generation and evolution-control gaps below describe the 2026-10-13 batch only. Later supplement reviews are outside this PR; this batch does not claim that all later sources lack those mechanisms.

## Historical review (2026-10-13)

The review followed stage two of the team plan and the six screening criteria in the research plan. This is source organization, not Method implementation or a transfer-gain report.

After synchronizing `b638c977`, the knowledge index added a no-training integration requirement: selected mechanisms must not train/fine-tune ExecutorLLM, OptimizerLLM, or task-specific neural modules. The [selected-mechanism training-boundary review](liyk-stage2-training-boundaries.md) covers 27 selected mechanism/boundary claims across eight packets. RB5 system-level numbers and NO4 qualitative component-removal support (two claims) are not independent mechanisms or evidence about parameter training or individual mechanism gains. An independent agent identified the previous erroneous inclusion of NO4; the training-review count was corrected while retaining the original conclusions. G-Memory's `finetune_insights` calls an LLM to generate rule operations, and `backward` changes rule scores; conclusions do not rely on function names or generic upstream admission fields alone. Full dependency execution, human review, and transfer gains remain incomplete.

## Base coverage

| Direction | Two base sources | Historical verification status | Use boundaries |
| --- | --- | --- | --- |
| Long-term memory and experience reuse | ReasoningBank, ExpeL | Pinned materials, paper pages/text lines, code ranges/symbols, and version links passed structural checks; selected official code matched pinned upstream revisions byte for byte | ReasoningBank's original test-stream updates must not be used on this project's dev/test; ExpeL rule-maintenance differences remain; local gains unknown |
| Session and environment state management | AgentRewind, StateFork | Same as above | AgentRewind recording/workspace recovery is not a historical-file-copy demo; StateFork physical recovery requires its backend and is not automatically available in ordinary Docker |
| Extensions and lifecycle hooks | AgentScope, AgentDojo; NORA retained as conditional historical material | Same as above; AgentDojo module interfaces have precise mappings and upstream comparisons | Normal AgentScope post hooks do not guarantee exception cleanup; AgentDojo provides composable pipeline interfaces, not generic finally/recovery; NORA host wiring and real triggering remain unknown |

The six current base packets retain papers, official code, configuration examples, tests, and reported results, separating paper claims, pinned implementation behavior, and local status. Structural checks are not human acceptance; `team_review_status` remains `pending`, and complete upstream experiments and H0 transfer have not been performed. Other indexed sources require individual review; an index displaying `10 / 10` does not establish acceptance of this line.

The historical [G-Memory](g-memory-2506.07398/mechanism-and-boundaries.md) supplement added four claims covering three-level organization, retrieval, continual updates, and an implementation limitation. PDF pp.4–6 and six code ranges were checked; five core/configuration files matched pinned upstream bytes. It supplements memory, and cross-direction indexing does not establish lifecycle hooks. The original index incorrectly used section 5.4 Framework as the main method entry; sections 3 and 4.1–4.3 are the main method sections.

The historical [AgentDojo](agentdojo-2406.13352/mechanism-and-boundaries.md) addition checked extension interfaces: PDF p.5 section 3.2 and p.16 Figures 11–12; three claims, five code ranges, and five pinned upstream files. It provides checkable component contracts for the extensions direction only; this does not accept all indexed directions or resolve NORA's unknown host wiring. The relationship between the current revision and the 2024 paper's experiment revision is unknown; a complete installable snapshot and H0 transfer remain unverified. Its current base-pair role does not alter the historical batch structure.

## Historical four-stage mechanism coverage

| Stage | Traceable evidence | Mechanisms potentially reusable | Missing evidence or knowledge |
| --- | --- | --- | --- |
| Organization and retrieval | [ReasoningBank RB1/RB4](reasoningbank-2509.25140/claim-evidence-map.json), [ExpeL EX2](expel-2308.10144/claim-evidence-map.json), [G-Memory GM1/GM2](g-memory-2506.07398/claim-evidence-map.json) | Query-to-experience retrieval; rule/successful-trajectory representation; hierarchical graphs; embedding caches and retrieval prerequisites | Direct evidence for retrieving harness methods from optimization-task/trace conditions is unknown; transferring executor experience to the optimizer is a proposal |
| Candidate generation | [AgentScope AS1–AS3](agentscope-2508.16279/claim-evidence-map.json), [NORA NO1–NO4](nora-2605.02092/claim-evidence-map.json) | Editable hook interface contracts, host events, and structured handoff evidence | No verified knowledge-to-harness-patch generation mechanism in this line; public NORA host wiring is missing. Knowledge gap: evidence-constrained candidate generation and interface correctness |
| Evolution control | [StateFork SF1–SF4](statefork-2609.38648/claim-evidence-map.json), [AgentRewind AR1–AR3](agentrewind-2608.14380/claim-evidence-map.json) | Logical/physical state separation, context/workspace recovery, rollback resource boundaries | Execution-time branching/rollback does not establish optimizer candidate selection, acceptance, or stopping. Knowledge gap: direct validation of cross-candidate evolution control and cumulative budgets |
| Continual accumulation | [ReasoningBank RB2/RB3](reasoningbank-2509.25140/claim-evidence-map.json), [ExpeL EX1/EX3](expel-2308.10144/claim-evidence-map.json), [G-Memory GM3/GM4](g-memory-2506.07398/claim-evidence-map.json) | Success/failure experience extraction; append operations; rule addition/deletion/editing and voting; hierarchical updates/feedback; accounting for acquisition cost and retaining implementation limits | Conflict handling, forgetting, cross-benchmark transfer, and old-capability retention have not been validated on this line's H0 |

These entries identify traceable mechanisms and register gaps without equating executor experience mechanisms with empirical optimizer improvement. Further work collects/verifies sources only; no derived system is implemented before Method assignment and creation of its independent repository.

## Historical checks and results

The following commands identify the historical check entry points. The stage-two verifier now defaults to the current seven-source scope; the saved historical counts below are not regenerated by that current command.

```bash
python3 knowledge/source-packets/verify_liyk.py
python3 knowledge/source-packets/verify_liyk.py --upstream
python3 knowledge/source-packets/verify_liyk_stage2.py --upstream
```

On 2026-10-13, the original six-packet batch checked 50 pinned payloads, 22 claims, and 28 code ranges, with zero structural errors. Its 38 selected official files matched pinned upstream revisions, with no mismatches or unknown comparisons. The batch included NORA, not AgentDojo; see the [historical source-review record](liyk-stage2-source-review.json). No new end-to-end paper runs or model experiments were performed.

With the G-Memory and AgentDojo additions, the historical total was eight sources, 29 claims, 39 code ranges, and 48 selected official files matching pinned upstream bytes. Human review, official experiments, and H0 transfer remained incomplete.

Following `CONTRIBUTING.md`, locally computed file checksums were removed from the original six packets' metadata and anchor documents. Upstream Git revisions, original files, precise line numbers, and pinned links were retained. Content comparison used direct byte equality without saving local checksums; historical conclusions were not rewritten.

An independent agent accepted the limited static verification, including the NO4 count-correction closure; see the [independent review record](liyk-stage2-independent-review.json) for scope and remaining human-review requirements. This does not replace team approval, complete dependency execution, or H0 transfer.
