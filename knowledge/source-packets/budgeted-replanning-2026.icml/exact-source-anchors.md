# Exact source anchors

## Selected mechanism

Use trigger evidence, progress, latency, churn, safety, and remaining budget to control when replanning occurs and how much computation it receives. The rule-based BRACE controller is retained; the learned E-RECAP token predictor is excluded.

## Paper anchors

| Evidence target | Exact location | What it establishes |
| --- | --- | --- |
| Replanning bottleneck | PDF pp.1–2; markers `===== PDF p.1 =====` and `===== PDF p.2 =====` | Growing context produces heavy-tailed replanning latency and deadline violations. |
| Controller inputs and state | PDF p.3, Sections 3.1–3.2; marker `===== PDF p.3 =====` | Defines triggers, controller state, mode selection, token budget, and latency SLO. |
| Controller procedure | PDF p.6, Algorithm 1; marker `===== PDF p.6 =====` | Gives the high-level budgeted replanning loop. |
| Auditable accounting | PDF p.5, Section 3.4; marker `===== PDF p.5 =====` | Records phase timing, token use, trigger cause, selected mode, and SLO outcome. |
| Results and ablations | PDF pp.7–9, Section 4; markers `===== PDF p.7 =====` through `===== PDF p.9 =====` | Reports controller results, budget-matched comparisons, and stability ablations. |

## Official-code anchors

| Exact location | Symbol | Role in the selected mechanism |
| --- | --- | --- |
| `official-code/brace/controller.py:10` | `BraceHyperparams` | Declares SLO, progress, deadlock, cooldown, churn, and defer-control parameters. |
| `official-code/brace/controller.py:25` | `BraceState` | Carries controller state across replanning decisions. |
| `official-code/brace/controller.py:38` | `BraceDecision` | Returns mode, budgets, hazard flags, protected blocks, and rollback signal. |
| `official-code/brace/controller.py:54` | `BraceController` | Applies deterministic hazard, mode-selection, budgeting, and state-update rules. |
| `official-code/experiments/common/replan_schedule.py:50` | `build_trigger_dict` | Converts periodic, failure, and deadlock events into controller triggers. |
| `official-code/experiments/common/context_compress/strategies.py:32` | `select_history_tokens` | Enforces a token budget over replanning history. |
| `official-code/experiments/common/logging.py:58` | `RunContext` | Persists phase-level runtime evidence under the official schema. |
| `official-code/analysis/controller_field_coverage.py:72` | `audit_run` | Audits whether controller decisions and fields were recorded. |

All code locations refer to official revision `92e91e6e69aa2f5d16cec9ff24ec1b02827a862e`. Paper page numbers refer to the fixed local proceedings PDF.
