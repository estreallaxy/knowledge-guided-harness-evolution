from __future__ import annotations

import copy
import json
import math
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from .context import DEFAULT_LOG_DIR, get_current_session, record_uid_index
from .errors import InvalidBreakpointError, ReplayError
from .storage import (
    JsonlWriter,
    backtrack_events_path,
    backtrack_memory_path,
    backtrack_summaries_path,
    load_raw_records,
    next_fork_run_id,
    run_path,
)


BacktrackHistoryMode = Literal["deterministic", "llm-summary"]
BacktrackSelectionPolicy = Literal["agent-direct", "probabilistic-suffix"]
BacktrackMemoryPolicy = Literal["cumulative", "none"]
BacktrackContextPolicy = Literal["rollback", "preserve"]
BacktrackWorkspacePolicy = Literal["rollback", "preserve"]
DEFAULT_MEMORY_PREFIX = "Backtrack memory notebook from abandoned future branches:\n"
DEFAULT_CANDIDATE_LIMIT = 80
DEFAULT_SELECTION_POLICY: BacktrackSelectionPolicy = "agent-direct"
DEFAULT_SELECTION_TOP_K = 5
DEFAULT_SELECTION_DELTA = 0.7
DEFAULT_MEMORY_LIMIT = 20
DEFAULT_MEMORY_ITEM_CHAR_LIMIT = 900
DEFAULT_MEMORY_NOTEBOOK_CHAR_LIMIT = 8_000
_UNSET = object()
_SENSITIVE_OVERRIDE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "proxy_authorization",
    "access_token",
    "refresh_token",
    "id_token",
    "bearer_token",
    "client_secret",
    "secret",
    "password",
    "credential",
    "credentials",
}
_SENSITIVE_CONTAINER_KEYS = {
    "headers",
    "extra_headers",
    "default_headers",
    "http_headers",
}

ROLLBACK_CONTEXT_VISIBILITY_INSTRUCTIONS = (
    "At the beginning of a fork with backtrack memory, the abandoned branch's "
    "later messages and tool results are not visible except through that notebook. "
)
PRESERVE_CONTEXT_VISIBILITY_INSTRUCTIONS = (
    "At the beginning of a preserve-context fork, the abandoned branch's later "
    "messages and tool results remain visible by design. Their visibility is expected "
    "and does not mean that backtrack failed; this policy intentionally does not rewind "
    "agent messages. Treat filesystem claims in post-target observations as potentially "
    "stale until they are checked against the current controlled Git workspace. "
)
ROLLBACK_FUTURE_EVIDENCE_INSTRUCTIONS = (
    "Treat the notebook as the only carried evidence from the failed future branch; "
    "do not plan to inspect the old branch after the rewind. "
)
PRESERVED_STATE_EVIDENCE_INSTRUCTIONS = (
    "The Backtrack memory notebook carries explicit failure guidance, while the "
    "policy-preserved conversation or controlled Git workspace may also carry state "
    "from the failed future branch. Interpret that state using the policy-specific "
    "instructions below. "
)


BACKTRACK_TOOL_INSTRUCTIONS = (
    "Backtrack is a deliberate timeline fork escape hatch. Use it when the "
    "current execution path is shown by concrete external feedback or repeated "
    "failed repair evidence to be wrong, stuck, self-contradictory, or too "
    "expensive to repair in place. Do not use backtrack as an opening diagnostic "
    "before trying listed task tools and obtaining concrete failure evidence. "
    "Call backtrack_candidates first, then call backtrack_commit with a record_uid "
    "from those candidates when a rewind is the better next action. "
    "The candidate rendering mode and candidate count are controlled by the "
    "current run configuration; do not try to set tool parameters for them. "
    "Only use a top-level candidate record_uid returned by backtrack_candidates; "
    "those ids identify LLM decision records and are the only valid commit "
    "targets. Do not invent ids and do not use any tool/output ids from previews. "
    "After a failed verifier result, repair in place only once when the fix is "
    "obvious and local, such as one typo, one missing file, one known wrong path, "
    "one missing row, or one clearly wrong value. "
    "If the same verifier check, or the same semantic failure, appears again "
    "after a repair attempt, call backtrack_candidates before making more local "
    "edits. A same semantic failure means the same invariant, artifact, missing "
    "evidence, preservation requirement, malformed output, or error class is "
    "still failing even if the wording changed. Repeated failure means the "
    "current branch is likely structurally bad; do not keep rewriting the same "
    "artifact, guessing hidden prior state, or declaring the verifier wrong. "
    "Identify the first bad LLM decision: the planning, search-policy, "
    "data-source, or file-operation decision that introduced the strategy that "
    "now needs to be replaced. Commit to the closest returned LLM decision record "
    "before that bad decision, so the next fork can re-decide before entering the "
    "same strategy. Prefer the decision immediately before the first write, edit, "
    "move, destructive action, wrong source choice, wrong schema or manifest "
    "interpretation, wrong extraction/calculation/grouping strategy, or ignored "
    "preservation/provenance requirement that affected the repeatedly failing "
    "artifact or invariant. Before committing, check the candidate against the "
    "rewind boundary claimed in memory_summary. Inspect candidate tool_calls_preview: "
    "if memory says to rewind before a filesystem mutation, destructive/polluting "
    "file operation, or a specific move/write/edit/create boundary, do not choose "
    "a candidate at or after that relevant mutating decision; choose an earlier "
    "LLM record. If no returned candidate precedes the bad decision, choose the "
    "earliest returned candidate and state that limitation in selected_candidate_safety_check. "
    "If a later backtrack lands in the same repeated failure, choose an earlier "
    "root-cause decision next time. Before calling backtrack_commit, compare the "
    "memory_summary you plan to write with the Backtrack memory notebook already "
    "visible in the prompt. If the same failed_check or root_cause is already "
    "present, do not submit a semantically identical memory item. Instead, choose "
    "a different or earlier record_uid, name a concrete difference in the new "
    "strategy, or mark the previous diagnosis as uncertain and make the next fork "
    "re-check it. Changing only the order or count of read/list/search calls is "
    "not a concrete strategy difference if the first mutating action repeats the "
    "failed pattern. A strategy is meaningfully different only when it changes "
    "the first mutating action, delays mutation until required evidence or "
    "artifacts exist, or changes the source/schema/classification decision that "
    "made the previous mutation unsafe. "
    "Avoid rewinding to a later LLM turn that merely noticed the verifier "
    "failure, edited symptoms, called backtrack_candidates, or called "
    "backtrack_commit. "
    "Once backtrack_candidates has returned a candidate list for a stuck branch, "
    "treat that branch as commit-only: do not make more ordinary tool calls, do "
    "not verify again, do not call backtrack_candidates again, and do not stop. "
    "Call backtrack_commit. If backtrack_commit is rejected by policy because "
    "the target is too late, not a returned top-level candidate, or the memory "
    "is not executable, keep the same root-cause diagnosis and retry "
    "backtrack_commit with an earlier returned record_uid or a corrected "
    "memory_summary. "
    "The memory_summary passed to backtrack_commit is written for your past self: "
    "write it as structured operational memory with these fields: failed_check, "
    "observed_loop, why_local_repair_failed, root_cause, evidence_observed, "
    "assumptions_to_recheck, rewind_target_reason, "
    "selected_candidate_safety_check, do_not_repeat, corrected_strategy, "
    "do_not_call_before, must_satisfy_before_mutation, mutation_preflight, "
    "first_3_tool_calls, and success_invariant. Treat root_cause as a hypothesis "
    "supported by evidence, not an unquestionable fact. Never write a "
    "task-feasibility verdict into memory: do not state that a checkpoint, stage, "
    "or required artifact is impossible, infeasible, structurally blocked, or has "
    "no method. The verifier is the sole authority on feasibility; a checkpoint "
    "the verifier still reports as failed is pending, not impossible. Record any "
    "suspected limitation under assumptions_to_recheck together with its concrete "
    "evidence, so the next fork tests it with a real submission before treating "
    "it as fact. Judge candidate solutions only by verifier feedback, never by "
    "your own self-check: if the current branch holds a produced artifact that "
    "has not been submitted since it was last modified, submit it and read the "
    "verifier feedback before calling backtrack_commit. evidence_observed must "
    "quote the verifier's latest failure feedback verbatim and "
    "say what tool output, verifier feedback, or file content supports it; "
    "assumptions_to_recheck must name any uncertain source choice, schema "
    "interpretation, missing evidence, or tool-capability assumption the next "
    "fork should verify before relying on it. rewind_target_reason must name "
    "the concrete first bad LLM decision and confirm the selected record_uid is "
    "the closest returned LLM decision before that bad decision. "
    "selected_candidate_safety_check must confirm the selected record precedes "
    "the stated rewind boundary, or explicitly say no returned candidate does. "
    "observed_loop must say what repeated repair attempts happened; "
    "why_local_repair_failed must say why those repairs did not change the "
    "verifier outcome or remove the root cause. do_not_repeat and "
    "do_not_call_before are binding red-line constraints for the next fork, not "
    "background advice; name concrete tool calls or action classes that must not "
    "happen before their prerequisites are true, such as move_file before an "
    "original-layout manifest exists or create_directory for a verifier-rejected "
    "month. must_satisfy_before_mutation must list the evidence, artifact, or "
    "classification decision that must exist before any write_file, move_file, "
    "create_directory, edit, delete, or similarly mutating tool call. "
    "mutation_preflight must state the check the next fork should apply before "
    "its first mutating tool call. Include literal filenames, paths, commands, verifier "
    "keywords, or required evidence when known. Do not write vague memory such as "
    "'re-examine the source evidence'; write the operational correction, such as "
    "which search pattern to stop using and which file contents or paths to "
    "inspect instead. The memory must be executable with the tools currently "
    "listed for the agent. Assume the listed tools are sufficient for the task "
    "unless task instructions or concrete tool feedback prove otherwise. Do not "
    "use missing tool, no hashing tool, need runner/operator, or cannot complete "
    "with current tools as the final root_cause merely because a direct helper is "
    "not listed; write it as an assumption_to_recheck and search for an in-task "
    "or listed-tool path instead. Do not invent unavailable tools, shell/Python "
    "access, hashing helpers, external scripts, or human calculation. If the task "
    "needs exact arithmetic, indexing, hashes, or global classification and no "
    "direct compute helper is listed, corrected_strategy must still use existing "
    "read/write/list/search tools and visible task evidence, with "
    "verify_task_state only as a pass/fail check on concrete artifacts instead "
    "of guessing or repeatedly patching symptoms. "
    "If a verifier-checked field requires a cryptographic digest, exact transform, "
    "or other value that is not available from listed tools or existing task "
    "evidence, do not replace it with an empty field, blank field, unavailable "
    "marker, raw-content path, provenance token, external-review note, or "
    "conditional plan to use hidden environment capability. "
    "Instead, rewind to the earliest decision where the strategy should have "
    "searched for authoritative in-task evidence or avoided committing to that "
    "unavailable-value-dependent artifact. "
    "Do not write placeholder checksum values such as UNKNOWN or "
    "SHA256_UNAVAILABLE, do not claim unspecified environment utilities can "
    "compute values for you, and do not rely on the verifier to reveal hidden "
    "expected answers. Do not claim the LLM/model can internally compute "
    "cryptographic hashes or long exact transforms for arbitrary file contents. "
    "first_3_tool_calls must name real "
    "available tool calls, not hypothetical helper calls. "
    "After backtrack_commit, the current agent path is expected to stop; the runner "
    "replays to the chosen LLM record, injects the cumulative backtrack memory "
    "notebook, and continues on a new materialized timeline fork. "
    + ROLLBACK_CONTEXT_VISIBILITY_INSTRUCTIONS
    + ROLLBACK_FUTURE_EVIDENCE_INSTRUCTIONS
    + "In a backtracked fork, the Backtrack "
    "memory notebook is a binding operational constraint for this fork, not "
    "background context or optional advice; it overrides your default task-solving "
    "routine when they conflict. One exception: feasibility verdicts are never "
    "valid memory. If a notebook item claims a checkpoint, stage, or artifact is "
    "impossible, blocked, or has no method, treat that claim as an untested "
    "assumption to re-check with a real attempt and submission, not as a "
    "constraint; only the verifier's own feedback decides feasibility. Your first "
    "non-trivial actions after rewind must "
    "address the notebook directly. Do not resume the old workflow until you have "
    "satisfied the notebook's must_satisfy_before_mutation items or gathered the "
    "evidence required by corrected_strategy. Before any filesystem action in the "
    "new fork, identify the applicable memory item, restate the do_not_repeat "
    "constraint in your own words, and decide whether the diagnosis is stable "
    "enough to mutate. Before every mutating tool call (write_file, move_file, "
    "create_directory, edit, delete, or any task tool that changes state), apply "
    "the memory as a preflight gate: ask whether this action repeats the failed "
    "mutation pattern, whether the required evidence or artifact already exists, "
    "and whether the first mutating action is materially different from the "
    "abandoned branch. If a planned mutating action conflicts with do_not_repeat, "
    "do_not_call_before, failed_check, or mutation_preflight, do not call that "
    "tool yet; first gather the missing evidence, create the required prerequisite "
    "artifact, choose a non-mutating check, or backtrack again. If the memory "
    "indicates uncertain source choice, missing evidence, schema ambiguity, or "
    "tool-capability uncertainty, first re-check the relevant visible evidence "
    "before mutating files. If the memory identifies a concrete wrong mutation "
    "and a concrete replacement edit, you may mutate directly only when the "
    "replacement does not violate the notebook constraints. Choose a first action "
    "that implements corrected_strategy or gathers the evidence it requires, and "
    "only depart from the memory when new visible evidence in this fork proves it "
    "wrong."
)

PROBABILISTIC_SUFFIX_SELECTION_INSTRUCTIONS = (
    "This run uses probabilistic-suffix backtrack selection. After "
    "backtrack_candidates returns, do not call backtrack_commit. You must submit "
    "exactly required_estimate_count probability estimates to "
    "backtrack_commit_distribution. Read required_estimate_count from the "
    "candidate objects returned by backtrack_candidates. If returned_candidate_count "
    "equals required_estimate_count, include every returned candidate. If "
    "returned_candidate_count is larger, choose exactly required_estimate_count "
    "returned candidates. Assign each selected top-level candidate record_uid a "
    "non-negative probability estimate p. "
    "The estimates do not need to sum to 1; Replay normalizes them, sorts the "
    "selected candidates by trace order, computes suffix confidence "
    "S_i = sum(p_i..p_k), and commits to the latest selected candidate whose "
    "suffix confidence is at least delta={delta}. Include only candidates "
    "returned by backtrack_candidates. Use the record_uid field on the candidate "
    "objects; do not use ids from tool/output previews. If there are more returned "
    "candidates than required_estimate_count, choose the required_estimate_count "
    "candidates you judge most likely; do not default to the earliest returned "
    "candidates and do not require a contiguous prefix. If "
    "backtrack_commit_distribution returns a parameter error about estimate count "
    "or record_uid, do not call bash or backtrack_candidates; "
    "immediately retry backtrack_commit_distribution with the corrected estimates. "
    "Keep memory_summary operational in the same format required by direct "
    "backtrack memory."
)

PRESERVE_CONTEXT_BACKTRACK_INSTRUCTIONS = (
    "This run preserves agent context across backtrack. After backtrack_commit, "
    "the new fork keeps the current conversation context instead of rewinding "
    "the agent messages to the selected record_uid. The selected record_uid only "
    "chooses the controlled workspace restore point. Still choose a returned LLM "
    "record whose checkpoint restores the workspace to the earliest/closest state "
    "needed for a safe retry. Seeing messages or tool observations after the selected "
    "record_uid is expected in this mode and is not evidence that rewind failed. Do "
    "not backtrack again solely to remove those preserved messages or because they "
    "conflict with current files. First inspect the current controlled Git workspace; "
    "backtrack again only when new tool or verifier evidence shows that the strategy "
    "needs an earlier decision point."
)

PRESERVE_WORKSPACE_BACKTRACK_INSTRUCTIONS = (
    "This run preserves the workspace across backtrack. After an accepted backtrack, "
    "the new fork rewinds the agent LLM context to the selected record_uid, but "
    "the Git workspace is not restored to that record's checkpoint. The files "
    "remain in the current failed branch state. Use backtrack only as a context "
    "retry/decision retry under the current filesystem state, and do not assume "
    "polluting or destructive file changes have been undone. This preserved file "
    "state is expected and is not evidence that rewind failed. Do not backtrack again "
    "solely because files were not restored; backtrack again only for new concrete "
    "evidence that a different context decision point is needed."
)

BACKTRACK_TOOL_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "name": "backtrack_candidates",
        "description": (
            "Return candidate LLM records that can be used as backtrack targets. "
            "Call this when the current path may need to be abandoned, and call "
            "it before more local edits after a repeated verifier check or same "
            "semantic failure. Each returned item includes a record_uid plus "
            "decision and tool previews to help choose the LLM decision before the bad "
            "outcome while preserving enough useful context. The record_uid is the "
            "LLM decision that will be replayed/re-decided with backtrack memory; "
            "select the closest returned LLM decision before the first bad "
            "planning/search/data-source/file-operation decision. If the same "
            "failure repeats, pick an earlier root-cause predecessor instead of a "
            "late verification or repair turn. Only top-level candidate "
            "record_uid values are valid backtrack targets. In probabilistic "
            "selection mode, use the returned required_estimate_count and "
            "candidate record_uid fields to call backtrack_commit_distribution with "
            "exactly that many returned record_uid values. If there are more "
            "returned candidates than required estimates, choose the most likely "
            "candidates from anywhere in the returned list, not necessarily the "
            "earliest ones. Candidate count and rendering mode are fixed by the "
            "current run configuration."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": (
                        "Brief explanation of why the current path may need "
                        "backtracking. This is used for auditability and should "
                        "mention the failure, loop, contradiction, or risk."
                    ),
                },
            },
            "required": ["reason"],
            "additionalProperties": False,
        },
    },
    {
        "name": "backtrack_commit",
        "description": (
            "Commit to abandoning the current future branch and rewind to a prior "
            "LLM record. Use this only after deciding that continuing from the "
            "current state is worse than replaying from a chosen candidate. The "
            "record_uid should normally come from backtrack_candidates and names "
            "the closest returned LLM decision before the first bad decision to "
            "replace. Do not pass the bad decision itself when an earlier returned "
            "LLM predecessor exists. Do not pass a tool record id or a record id copied from a "
            "tool preview; pass only a top-level candidate record_uid. This call "
            "does not return a normal tool result: in "
            "SDK/runner-native mode it raises BacktrackRequested so the runner can "
            "stop the agent, create a materialized fork, inject the cumulative "
            "memory notebook, and re-exec."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "record_uid": {
                    "type": "string",
                    "description": (
                        "LLM record uid to rewind to, usually selected from "
                        "backtrack_candidates. The target must be kind='llm'; "
                        "tool record ids are not valid commit targets."
                    ),
                },
                "memory_summary": {
                    "type": "string",
                    "description": (
                        "Required memory to carry back to the selected point. Write "
                        "a concise but operational note for the past agent using "
                        "these fields: failed_check, observed_loop, "
                        "why_local_repair_failed, root_cause, evidence_observed, "
                        "assumptions_to_recheck, rewind_target_reason, "
                        "selected_candidate_safety_check, do_not_repeat, "
                        "corrected_strategy, do_not_call_before, "
                        "must_satisfy_before_mutation, mutation_preflight, "
                        "first_3_tool_calls, and "
                        "success_invariant. Treat root_cause as a hypothesis, not "
                        "an unquestionable fact; evidence_observed should name "
                        "the concrete verifier/tool/file evidence supporting it, "
                        "and assumptions_to_recheck should name uncertainties the "
                        "next fork must verify before relying on them. observed_loop "
                        "should summarize the "
                        "repeated attempts on the abandoned branch; "
                        "why_local_repair_failed should explain why those attempts "
                        "did not change the verifier outcome or remove the root cause. "
                        "rewind_target_reason must name the first bad LLM decision "
                        "and confirm that the selected record_uid is the closest "
                        "returned LLM decision before it. selected_candidate_safety_check "
                        "must confirm that the selected record precedes the stated "
                        "rewind boundary, or explicitly say no returned candidate does. If the "
                        "root cause is a filesystem mutation, destructive/polluting "
                        "file operation, or specific move/write/edit/create boundary, "
                        "do not choose a candidate at or after the relevant mutating "
                        "decision shown by tool_calls_preview. "
                        "do_not_repeat and do_not_call_before are binding red-line "
                        "constraints for the next fork, not optional advice. "
                        "must_satisfy_before_mutation must name the evidence, "
                        "artifact, or classification decision required before "
                        "write_file, move_file, create_directory, edit, delete, "
                        "or any other mutating action. mutation_preflight must "
                        "state how the next fork should check that its first "
                        "mutating action is not the same failed pattern again. "
                        "Changing only read/list/search ordering is not a concrete "
                        "strategy difference if the first mutating action repeats "
                        "the failed pattern. "
                        "Include literal filenames, paths, commands, verifier "
                        "keywords, or required evidence when known. Avoid vague "
                        "advice such as 're-examine evidence'; say exactly what to "
                        "stop doing and what to inspect or write instead. The plan "
                        "must be executable with the tools currently listed for the "
                        "agent. Compare this memory with any Backtrack memory "
                        "notebook already visible in the prompt; if the same "
                        "failed_check or root_cause is already present, do not "
                        "write a semantically identical memory item. Choose a "
                        "different or earlier record_uid, state a concrete strategy "
                        "difference, or mark the previous diagnosis uncertain and "
                        "re-check it in the next fork. Assume the listed tools are "
                        "sufficient unless task instructions or concrete tool "
                        "feedback prove otherwise. Do not use missing tool, no "
                        "hashing tool, need runner/operator, or cannot complete "
                        "with current tools as the final root_cause merely because "
                        "a direct helper is not listed. Do not invent unavailable "
                        "tools, shell/Python access, hashing helpers, external "
                        "scripts, LLM-internal hashing, "
                        "placeholder checksum values, verifier-as-answer-oracle "
                        "plans, human calculation, raw-content/path tokens in "
                        "checksum fields, empty checksum fields, external-review "
                        "notes, or conditional hidden-environment capability. "
                        "first_3_tool_calls must name real available tool calls."
                    ),
                },
                "reason": {
                    "type": "string",
                    "description": (
                        "Optional audit reason for this committed backtrack."
                    ),
                },
            },
            "required": ["record_uid", "memory_summary"],
            "additionalProperties": False,
        },
    },
)

BACKTRACK_DISTRIBUTION_TOOL_DEFINITION: dict[str, Any] = {
    "name": "backtrack_commit_distribution",
    "description": (
        "Commit to abandoning the current future branch by submitting a ranked "
        "probability distribution over candidate LLM records instead of one direct "
        "record_uid. Use this only after backtrack_candidates. Provide exactly "
        "required_estimate_count top-level candidate record_uid values from that "
        "backtrack_candidates result with non-negative probability estimates for "
        "each candidate being the first decision entry that caused the current "
        "deadlock or repeated failure. Replay normalizes "
        "the estimates, sorts them by trace order, computes suffix confidence "
        "S_i=sum(p_i..p_k), and rewinds to the latest selected candidate whose "
        "suffix confidence is at least the configured delta. This call does not "
        "return a normal tool result: in SDK/runner-native mode it raises "
        "BacktrackRequested so the runner can stop the agent, create a "
        "materialized fork, inject the cumulative memory notebook, and re-exec."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "estimates": {
                "type": "array",
                "description": (
                    "Exactly required_estimate_count candidate probabilities. "
                    "Include only top-level LLM record_uid values returned by the "
                    "last backtrack_candidates call, not tool/output preview ids."
                ),
                "items": {
                    "type": "object",
                    "properties": {
                        "record_uid": {
                            "type": "string",
                            "description": "Candidate LLM record uid returned by backtrack_candidates.",
                        },
                        "probability": {
                            "type": "number",
                            "minimum": 0,
                            "description": (
                                "Non-negative estimate p that this record is the "
                                "decision entry causing the current deadlock. "
                                "Values are normalized by Replay."
                            ),
                        },
                    },
                    "required": ["record_uid", "probability"],
                    "additionalProperties": False,
                },
                "minItems": 1,
            },
            "memory_summary": {
                "type": "string",
                "description": (
                    "Required memory to carry back to the selected point. Use the "
                    "same structured operational fields required by "
                    "backtrack_commit, including failed_check, observed_loop, "
                    "why_local_repair_failed, root_cause, evidence_observed, "
                    "assumptions_to_recheck, rewind_target_reason, "
                    "selected_candidate_safety_check, do_not_repeat, "
                    "corrected_strategy, do_not_call_before, "
                    "must_satisfy_before_mutation, mutation_preflight, "
                    "first_3_tool_calls, and success_invariant."
                ),
            },
            "reason": {
                "type": "string",
                "description": "Optional audit reason for this committed probabilistic backtrack.",
            },
        },
        "required": ["estimates", "memory_summary"],
        "additionalProperties": False,
    },
}


class BacktrackError(ReplayError):
    """Raised when a backtrack request cannot be built."""


@dataclass
class BacktrackRequested(Exception):
    record_uid: str
    memory_summary: str
    reason: str | None = None
    run_id: str | None = None
    log_dir: Path | None = None
    selection_metadata: dict[str, Any] | None = None

    def __str__(self) -> str:
        detail = f"Backtrack requested to {self.record_uid}"
        if self.reason:
            detail += f": {self.reason}"
        return detail


def backtrack_tool_instructions(
    selection_policy: BacktrackSelectionPolicy | None = None,
    context_policy: BacktrackContextPolicy | None = None,
    workspace_policy: BacktrackWorkspacePolicy | None = None,
) -> str:
    """Return the official guidance for exposing Replay backtrack tools."""

    resolved_context_policy = resolve_backtrack_context_policy(context_policy)
    resolved_workspace_policy = resolve_backtrack_workspace_policy(workspace_policy)
    instructions = BACKTRACK_TOOL_INSTRUCTIONS
    if resolved_context_policy == "preserve":
        instructions = instructions.replace(
            ROLLBACK_CONTEXT_VISIBILITY_INSTRUCTIONS,
            PRESERVE_CONTEXT_VISIBILITY_INSTRUCTIONS,
        )
    if resolved_context_policy == "preserve" or resolved_workspace_policy == "preserve":
        instructions = instructions.replace(
            ROLLBACK_FUTURE_EVIDENCE_INSTRUCTIONS,
            PRESERVED_STATE_EVIDENCE_INSTRUCTIONS,
        )
    if resolve_backtrack_selection_policy(selection_policy) == "probabilistic-suffix":
        for old, new in (
            (
                "Call backtrack_candidates first, then call backtrack_commit with a record_uid "
                "from those candidates when a rewind is the better next action.",
                "Call backtrack_candidates first, then call backtrack_commit_distribution with "
                "probability estimates over returned record_uid values when a rewind is the better next action.",
            ),
            (
                "Only top-level candidate record_uid values are valid for backtrack_commit.",
                "Only top-level candidate record_uid values are valid for backtrack_commit_distribution estimates.",
            ),
            (
                "Before calling backtrack_commit, compare the ",
                "Before calling backtrack_commit_distribution, compare the ",
            ),
            (
                "Call backtrack_commit. If backtrack_commit is rejected by policy because ",
                "Call backtrack_commit_distribution. If backtrack_commit_distribution is rejected by policy because ",
            ),
            (
                "The memory_summary passed to backtrack_commit is written for your past self:",
                "The memory_summary passed to backtrack_commit_distribution is written for your past self:",
            ),
            (
                "After backtrack_commit, the current agent path is expected to stop;",
                "After backtrack_commit_distribution, the current agent path is expected to stop;",
            ),
        ):
            instructions = instructions.replace(old, new)
        top_k = resolve_backtrack_selection_top_k(None)
        delta = resolve_backtrack_selection_delta(None)
        instructions = (
            instructions
            + "\n\n"
            + PROBABILISTIC_SUFFIX_SELECTION_INSTRUCTIONS.format(top_k=top_k, delta=delta)
        )
    if resolved_context_policy == "preserve":
        instructions = instructions + "\n\n" + PRESERVE_CONTEXT_BACKTRACK_INSTRUCTIONS
    if resolved_workspace_policy == "preserve":
        instructions = instructions + "\n\n" + PRESERVE_WORKSPACE_BACKTRACK_INSTRUCTIONS
    return instructions


def backtrack_tool_definitions(
    selection_policy: BacktrackSelectionPolicy | None = None,
) -> list[dict[str, Any]]:
    """Return neutral Replay backtrack tool definitions with JSON schemas."""

    policy = resolve_backtrack_selection_policy(selection_policy)
    definitions = [BACKTRACK_TOOL_DEFINITIONS[0]]
    if policy == "probabilistic-suffix":
        definitions.append(BACKTRACK_DISTRIBUTION_TOOL_DEFINITION)
    else:
        definitions.append(BACKTRACK_TOOL_DEFINITIONS[1])
    return copy.deepcopy(definitions)


def openai_backtrack_tool_definitions(
    selection_policy: BacktrackSelectionPolicy | None = None,
) -> list[dict[str, Any]]:
    """Return Replay backtrack tools in OpenAI chat/completions tool format."""

    return [
        {
            "type": "function",
            "function": definition,
        }
        for definition in backtrack_tool_definitions(selection_policy)
    ]


def mcp_backtrack_tool_definitions(
    selection_policy: BacktrackSelectionPolicy | None = None,
) -> list[dict[str, Any]]:
    """Return Replay backtrack tools in MCP-style list_tools format."""

    return [
        {
            "name": definition["name"],
            "description": definition["description"],
            "inputSchema": definition["parameters"],
        }
        for definition in backtrack_tool_definitions(selection_policy)
    ]


def backtrack_tool_functions() -> dict[str, Any]:
    """Return callables keyed by the official Replay backtrack tool names."""

    return {
        "backtrack_candidates": backtrack_candidates_for_agent,
        "backtrack_commit": backtrack_commit,
        "backtrack_commit_distribution": backtrack_commit_distribution_for_agent,
    }


def backtrack_candidates_for_agent(
    reason: str,
    **ignored_arguments: Any,
) -> list[dict[str, Any]]:
    """Agent-facing candidate tool.

    Candidate rendering mode and count are run policy, not agent policy. Keep
    the public Python API flexible for tests/offline inspection, but ignore any
    stale model-supplied mode/limit arguments at the tool boundary.
    """

    return backtrack_candidates(reason)


def backtrack_candidates(
    reason: str,
    mode: BacktrackHistoryMode | None = None,
    limit: int | None | object = _UNSET,
    *,
    run_id: str | None = None,
    log_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    """Return candidate LLM records that the current agent can backtrack to."""

    if not isinstance(reason, str) or not reason.strip():
        raise BacktrackError("backtrack_candidates requires a non-empty reason.")
    resolved_mode = resolve_backtrack_history_mode(mode)
    resolved_limit = resolve_backtrack_candidate_limit(limit)
    resolved_run_id, resolved_log_dir = resolve_current_trace(run_id=run_id, log_dir=log_dir)
    if resolved_limit is not None and resolved_limit < 1:
        remember_last_backtrack_candidates([], run_id=resolved_run_id, log_dir=resolved_log_dir)
        return []

    records = load_raw_records(run_path(resolved_log_dir, resolved_run_id))
    candidates = deterministic_candidates(records, limit=resolved_limit)

    if resolved_mode == "llm-summary":
        summaries = load_backtrack_summaries(resolved_log_dir, resolved_run_id)
        candidates = enrich_candidates_with_summaries(candidates, summaries)
    candidates = annotate_backtrack_candidates_for_selection(candidates)
    remember_last_backtrack_candidates(candidates, run_id=resolved_run_id, log_dir=resolved_log_dir)
    return candidates


def annotate_backtrack_candidates_for_selection(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    session = get_current_session()
    if session is None:
        return candidates
    if resolve_backtrack_selection_policy(None) != "probabilistic-suffix":
        return candidates
    top_k = resolve_backtrack_selection_top_k(None)
    returned_candidate_count = len(candidates)
    required_estimate_count = min(top_k, returned_candidate_count)
    candidate_record_uids = [
        str(candidate.get("record_uid"))
        for candidate in candidates
        if isinstance(candidate.get("record_uid"), str)
    ]
    for rank, candidate in enumerate(candidates, start=1):
        candidate["candidate_rank"] = rank
        candidate["returned_candidate_count"] = returned_candidate_count
        candidate["required_estimate_count"] = required_estimate_count
        candidate["distribution_instruction_ref"] = "See distribution_submit_instructions on the first candidate."
    if candidates:
        candidates[0]["distribution_submit_instructions"] = {
            "required_estimate_rule": (
                "Submit exactly required_estimate_count estimates to "
                "backtrack_commit_distribution. Read required_estimate_count from "
                "the returned candidates. If returned_candidate_count equals "
                "required_estimate_count, submit every returned record_uid; otherwise "
                "choose exactly required_estimate_count returned record_uid values."
            ),
            "candidate_selection_rule": (
                "When returned_candidate_count > required_estimate_count, inspect all "
                "returned candidates and choose the required_estimate_count record_uid "
                "values you judge most likely to be the first bad decision. Read each "
                "record_uid directly from its candidate object; do not default to the "
                "earliest returned candidates and do not require a contiguous prefix."
            ),
            "allowed_record_uids": candidate_record_uids,
            "estimate_item_format": {
                "record_uid": "<chosen returned record_uid>",
                "probability": "<non-negative number>",
            },
            "retry_instruction": (
                "If backtrack_commit_distribution rejects the estimate count or a record_uid, "
                "do not call bash or backtrack_candidates. Retry backtrack_commit_distribution "
                "using exactly required_estimate_count returned record_uid values."
            ),
        }
    return candidates


def remember_last_backtrack_candidates(
    candidates: list[dict[str, Any]],
    *,
    run_id: str,
    log_dir: Path,
) -> None:
    session = get_current_session()
    if session is None:
        return
    record_uids = [
        candidate.get("record_uid")
        for candidate in candidates
        if isinstance(candidate.get("record_uid"), str)
    ]
    session.last_backtrack_candidates = {
        "run_id": run_id,
        "log_dir": log_dir,
        "record_uids": record_uids,
    }


def last_backtrack_candidate_record_uids(
    *,
    run_id: str,
    log_dir: Path,
) -> list[str] | None:
    session = get_current_session()
    state = getattr(session, "last_backtrack_candidates", None) if session is not None else None
    if not isinstance(state, dict):
        return None
    if state.get("run_id") != run_id or state.get("log_dir") != log_dir:
        return None
    record_uids = state.get("record_uids")
    if not isinstance(record_uids, list):
        return None
    return [record_uid for record_uid in record_uids if isinstance(record_uid, str)]


def force_next_backtrack_distribution_retry() -> None:
    session = get_current_session()
    restrict = getattr(session, "restrict_next_tools", None) if session is not None else None
    if callable(restrict):
        restrict(["backtrack_commit_distribution"])


def is_backtrack_distribution_retry_error(exc: Exception) -> bool:
    if isinstance(exc, InvalidBreakpointError):
        return True
    if not isinstance(exc, BacktrackError):
        return False
    message = str(exc)
    retry_fragments = (
        "requires exactly",
        "accepts at most",
        "requires at least one probability estimate",
        "estimate #",
        "duplicate probability estimate",
        "probability for record_uid",
        "probability estimates must contain at least one positive value",
    )
    return any(fragment in message for fragment in retry_fragments)


def distribution_retry_suffix(candidate_record_uids: list[str] | None, required_count: int | None) -> str:
    parts = [
        "Next action is restricted to backtrack_commit_distribution; do not call bash or backtrack_candidates.",
    ]
    if required_count is not None:
        parts.append(f"Submit exactly {required_count} estimates.")
    if candidate_record_uids is not None:
        parts.append("Allowed record_uid values from the latest backtrack_candidates call: " + json.dumps(candidate_record_uids))
    return " ".join(parts)


_FEASIBILITY_VERDICT_PHRASES = (
    "impossible",
    "infeasible",
    "not feasible",
    "unsolvable",
    "unachievable",
    "not achievable",
    "no method exists",
    "no approach exists",
    "no way to",
    "structurally block",
    "structural block",
    "structurally impossible",
    "dead end",
    "dead-end",
    "give up",
    "hopeless",
    "cannot succeed",
    "cannot be done",
    "cannot be achieved",
    "cannot be completed",
    "cannot be satisfied",
)

MEMORY_VERDICT_REJECTION = (
    "memory_summary rejected: it contains a task-feasibility verdict ({phrase!r}). "
    "The verifier is the only authority on feasibility; a checkpoint the verifier "
    "still reports as failed is pending, not impossible. Rewrite the memory as "
    "operational facts only: quote the verifier's latest failure feedback verbatim "
    "in evidence_observed, list the concrete actions and edits already tried in "
    "observed_loop, and record the suspected limitation under assumptions_to_recheck "
    "so the next fork tests it with a real submission instead of inheriting it as "
    "fact. If the current branch holds an untested candidate artifact, submit it and "
    "read the verifier feedback before backtracking."
)

MEMORY_DUPLICATE_REJECTION = (
    "memory_summary rejected: it is near-identical (token overlap {overlap:.0%}) to "
    "an existing Backtrack memory notebook item. Re-submitting the same diagnosis "
    "does not change the next fork's behavior. Either choose an earlier or different "
    "record_uid with a materially different corrected_strategy (a different first "
    "mutating action), or, if the current branch holds an untested candidate "
    "artifact, submit it for verification instead of backtracking again."
)

MEMORY_DUPLICATE_OVERLAP_THRESHOLD = 0.75


def _memory_summary_tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9_./-]+", text.lower()) if len(token) > 2}


def find_feasibility_verdict(memory_summary: str) -> str | None:
    lowered = " ".join(memory_summary.lower().split())
    for phrase in _FEASIBILITY_VERDICT_PHRASES:
        if phrase in lowered:
            return phrase
    return None


def find_duplicate_memory_overlap(
    memory_summary: str,
    memory_items: list[dict[str, Any]],
    *,
    threshold: float = MEMORY_DUPLICATE_OVERLAP_THRESHOLD,
) -> float | None:
    new_tokens = _memory_summary_tokens(memory_summary)
    if not new_tokens:
        return None
    for item in memory_items:
        prior_tokens = _memory_summary_tokens(str(item.get("memory_summary") or ""))
        if not prior_tokens:
            continue
        overlap = len(new_tokens & prior_tokens) / len(new_tokens | prior_tokens)
        if overlap >= threshold:
            return overlap
    return None


def validate_memory_summary_discipline(
    memory_summary: str,
    *,
    run_id: str | None = None,
    log_dir: str | Path | None = None,
) -> None:
    """P3(c) 记忆纪律: 拒绝任务级可行性判决与近重复记忆, 报错引导改写。"""

    phrase = find_feasibility_verdict(memory_summary)
    if phrase is not None:
        raise BacktrackError(MEMORY_VERDICT_REJECTION.format(phrase=phrase))
    if run_id and log_dir is not None:
        try:
            memory_items = load_backtrack_memory(log_dir, run_id)
        except BacktrackError:
            return
        overlap = find_duplicate_memory_overlap(memory_summary, memory_items)
        if overlap is not None:
            raise BacktrackError(MEMORY_DUPLICATE_REJECTION.format(overlap=overlap))


def backtrack_commit(
    record_uid: str,
    memory_summary: str,
    reason: str | None = None,
    *,
    run_id: str | None = None,
    log_dir: str | Path | None = None,
) -> None:
    """Abort the current agent path and ask the runner to re-execute from a prior LLM."""

    if not isinstance(record_uid, str) or not record_uid.strip():
        raise BacktrackError("backtrack_commit requires a non-empty record_uid.")
    if not isinstance(memory_summary, str) or not memory_summary.strip():
        raise BacktrackError("backtrack_commit requires a non-empty memory_summary.")
    validate_memory_summary_discipline(memory_summary)

    resolved_run_id = run_id
    resolved_log_dir = Path(log_dir) if log_dir is not None else None
    try:
        resolved_run_id, resolved_log_dir = resolve_current_trace(run_id=run_id, log_dir=log_dir)
        records = load_raw_records(run_path(resolved_log_dir, resolved_run_id))
        record_uid = resolve_backtrack_target_record_uid(records, record_uid)
    except (BacktrackError, FileNotFoundError):
        pass
    if resolved_run_id and resolved_log_dir is not None:
        validate_memory_summary_discipline(
            memory_summary, run_id=resolved_run_id, log_dir=resolved_log_dir
        )

    raise BacktrackRequested(
        record_uid=record_uid,
        memory_summary=memory_summary,
        reason=reason,
        run_id=resolved_run_id,
        log_dir=resolved_log_dir,
    )


def backtrack_commit_distribution_for_agent(
    estimates: list[dict[str, Any]],
    memory_summary: str,
    reason: str | None = None,
    **ignored_arguments: Any,
) -> None:
    """Agent-facing probabilistic commit tool.

    Top-k and delta are run policy, not agent policy. Ignore any stale
    model-supplied tuning arguments at the tool boundary.
    """

    try:
        return backtrack_commit_distribution(
            estimates=estimates,
            memory_summary=memory_summary,
            reason=reason,
            require_candidate_context=True,
        )
    except Exception as exc:
        if is_backtrack_distribution_retry_error(exc):
            force_next_backtrack_distribution_retry()
        raise


def backtrack_commit_distribution(
    estimates: list[dict[str, Any]],
    memory_summary: str,
    reason: str | None = None,
    *,
    run_id: str | None = None,
    log_dir: str | Path | None = None,
    top_k: int | None = None,
    delta: float | None = None,
    require_candidate_context: bool = False,
) -> None:
    """Abort the current path using a normalized suffix-confidence selection."""

    if not isinstance(memory_summary, str) or not memory_summary.strip():
        raise BacktrackError("backtrack_commit_distribution requires a non-empty memory_summary.")
    validate_memory_summary_discipline(memory_summary)

    resolved_run_id, resolved_log_dir = resolve_current_trace(run_id=run_id, log_dir=log_dir)
    validate_memory_summary_discipline(
        memory_summary, run_id=resolved_run_id, log_dir=resolved_log_dir
    )
    records = load_raw_records(run_path(resolved_log_dir, resolved_run_id))
    candidate_record_uids = last_backtrack_candidate_record_uids(
        run_id=resolved_run_id,
        log_dir=resolved_log_dir,
    )
    if require_candidate_context and candidate_record_uids is None:
        raise BacktrackError(
            "backtrack_commit_distribution must be called after backtrack_candidates "
            "so Replay can enforce exactly required_estimate_count estimates. "
            "Call backtrack_candidates next; do not guess record_uid values."
        )
    try:
        selection = select_backtrack_target_by_suffix(
            records,
            estimates,
            top_k=top_k,
            delta=delta,
            candidate_record_uids=candidate_record_uids,
        )
    except (BacktrackError, InvalidBreakpointError) as exc:
        required_count = None
        if candidate_record_uids is not None:
            required_count = min(resolve_backtrack_selection_top_k(top_k), len(candidate_record_uids))
        suffix = distribution_retry_suffix(candidate_record_uids, required_count)
        if isinstance(exc, InvalidBreakpointError):
            raise InvalidBreakpointError(f"{exc} {suffix}") from exc
        raise BacktrackError(f"{exc} {suffix}") from exc

    raise BacktrackRequested(
        record_uid=str(selection["selected_record_uid"]),
        memory_summary=memory_summary,
        reason=reason,
        run_id=resolved_run_id,
        log_dir=resolved_log_dir,
        selection_metadata=selection,
    )


def select_backtrack_target_by_suffix(
    records: list[dict[str, Any]],
    estimates: list[dict[str, Any]],
    *,
    top_k: int | None = None,
    delta: float | None = None,
    candidate_record_uids: list[str] | None = None,
) -> dict[str, Any]:
    """Select the latest candidate whose normalized suffix confidence passes delta."""

    resolved_top_k = resolve_backtrack_selection_top_k(top_k)
    resolved_delta = resolve_backtrack_selection_delta(delta)
    if not isinstance(estimates, list) or not estimates:
        raise BacktrackError("backtrack_commit_distribution requires at least one probability estimate.")
    if len(estimates) > resolved_top_k:
        raise BacktrackError(
            f"backtrack_commit_distribution accepts at most {resolved_top_k} estimates, got {len(estimates)}."
        )
    required_estimate_count: int | None = None
    candidate_uid_set: set[str] | None = None
    if candidate_record_uids is not None:
        candidate_uid_set = set(candidate_record_uids)
        required_estimate_count = min(resolved_top_k, len(candidate_record_uids))
        if len(estimates) != required_estimate_count:
            raise BacktrackError(
                "backtrack_commit_distribution requires exactly "
                f"required_estimate_count={required_estimate_count} estimates, got {len(estimates)}."
            )

    llm_trace_indexes: dict[str, int] = {}
    for trace_index, record in enumerate(records):
        uid = record.get("record_uid")
        if record.get("kind") == "llm" and isinstance(uid, str):
            llm_trace_indexes[uid] = trace_index

    parsed_estimates: list[dict[str, Any]] = []
    seen_uids: set[str] = set()
    for input_index, item in enumerate(estimates):
        if not isinstance(item, dict):
            raise BacktrackError(f"estimate #{input_index + 1} must be an object.")
        record_uid = item.get("record_uid")
        if not isinstance(record_uid, str) or not record_uid.strip():
            raise BacktrackError(f"estimate #{input_index + 1} requires a non-empty record_uid.")
        if record_uid in seen_uids:
            raise BacktrackError(f"duplicate probability estimate for record_uid={record_uid!r}.")
        if record_uid not in llm_trace_indexes:
            raise InvalidBreakpointError(
                f"backtrack probability estimate target must be a known LLM record: {record_uid!r}."
            )
        if candidate_uid_set is not None and record_uid not in candidate_uid_set:
            raise InvalidBreakpointError(
                "backtrack probability estimate target must be one of the "
                f"record_uid values returned by backtrack_candidates: {record_uid!r}."
            )

        raw_value = item.get("probability", item.get("p"))
        try:
            raw_probability = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise BacktrackError(
                f"probability for record_uid={record_uid!r} must be a finite non-negative number."
            ) from exc
        if not math.isfinite(raw_probability) or raw_probability < 0:
            raise BacktrackError(
                f"probability for record_uid={record_uid!r} must be a finite non-negative number."
            )
        parsed_estimates.append(
            {
                "record_uid": record_uid,
                "raw_probability": raw_probability,
                "input_index": input_index,
                "trace_index": llm_trace_indexes[record_uid],
            }
        )
        seen_uids.add(record_uid)

    raw_probability_sum = sum(item["raw_probability"] for item in parsed_estimates)
    if raw_probability_sum <= 0:
        raise BacktrackError("probability estimates must contain at least one positive value.")

    parsed_estimates.sort(key=lambda item: item["trace_index"])
    selected: dict[str, Any] | None = None
    suffix_confidence = 0.0
    for item in parsed_estimates:
        item["probability"] = item["raw_probability"] / raw_probability_sum
    for item in reversed(parsed_estimates):
        suffix_confidence += item["probability"]
        item["suffix_confidence"] = suffix_confidence
        if selected is None and suffix_confidence + 1e-12 >= resolved_delta:
            selected = item

    if selected is None:
        selected = parsed_estimates[0]

    return {
        "selection_policy": "probabilistic-suffix",
        "top_k": resolved_top_k,
        "delta": resolved_delta,
        "required_estimate_count": required_estimate_count,
        "returned_candidate_count": len(candidate_record_uids) if candidate_record_uids is not None else None,
        "selected_record_uid": selected["record_uid"],
        "selected_trace_index": selected["trace_index"],
        "selected_suffix_confidence": selected["suffix_confidence"],
        "raw_probability_sum": raw_probability_sum,
        "estimates": parsed_estimates,
    }


def resolve_backtrack_history_mode(mode: BacktrackHistoryMode | None) -> BacktrackHistoryMode:
    if mode is None:
        session = get_current_session()
        mode = getattr(session, "backtrack_history_mode", "deterministic") if session is not None else "deterministic"
    if mode not in {"deterministic", "llm-summary"}:
        raise BacktrackError(f"Unsupported backtrack history mode: {mode!r}.")
    return mode


def resolve_backtrack_selection_policy(
    selection_policy: BacktrackSelectionPolicy | None,
) -> BacktrackSelectionPolicy:
    if selection_policy is None:
        session = get_current_session()
        selection_policy = (
            getattr(session, "backtrack_selection_policy", DEFAULT_SELECTION_POLICY)
            if session is not None
            else DEFAULT_SELECTION_POLICY
        )
    if selection_policy not in {"agent-direct", "probabilistic-suffix"}:
        raise BacktrackError(f"Unsupported backtrack selection policy: {selection_policy!r}.")
    return selection_policy


def resolve_backtrack_memory_policy(
    memory_policy: BacktrackMemoryPolicy | None,
) -> BacktrackMemoryPolicy:
    if memory_policy is None:
        session = get_current_session()
        memory_policy = (
            getattr(session, "backtrack_memory_policy", "cumulative")
            if session is not None
            else "cumulative"
        )
    if memory_policy not in {"cumulative", "none"}:
        raise BacktrackError(f"Unsupported backtrack memory policy: {memory_policy!r}.")
    return memory_policy


def resolve_backtrack_context_policy(
    context_policy: BacktrackContextPolicy | None,
) -> BacktrackContextPolicy:
    if context_policy is None:
        session = get_current_session()
        context_policy = (
            getattr(session, "backtrack_context_policy", "rollback")
            if session is not None
            else "rollback"
        )
    if context_policy not in {"rollback", "preserve"}:
        raise BacktrackError(f"Unsupported backtrack context policy: {context_policy!r}.")
    return context_policy


def resolve_backtrack_workspace_policy(
    workspace_policy: BacktrackWorkspacePolicy | None,
) -> BacktrackWorkspacePolicy:
    if workspace_policy is None:
        session = get_current_session()
        workspace_policy = (
            getattr(session, "backtrack_workspace_policy", "rollback")
            if session is not None
            else "rollback"
        )
    if workspace_policy not in {"rollback", "preserve"}:
        raise BacktrackError(f"Unsupported backtrack workspace policy: {workspace_policy!r}.")
    return workspace_policy


def resolve_backtrack_selection_top_k(top_k: int | None) -> int:
    if top_k is None:
        session = get_current_session()
        top_k = (
            getattr(session, "backtrack_selection_top_k", DEFAULT_SELECTION_TOP_K)
            if session is not None
            else DEFAULT_SELECTION_TOP_K
        )
    resolved = int(top_k)
    if resolved < 1:
        raise BacktrackError(f"backtrack selection top_k must be >= 1, got {resolved}.")
    return resolved


def resolve_backtrack_selection_delta(delta: float | None) -> float:
    if delta is None:
        session = get_current_session()
        delta = (
            getattr(session, "backtrack_selection_delta", DEFAULT_SELECTION_DELTA)
            if session is not None
            else DEFAULT_SELECTION_DELTA
        )
    resolved = float(delta)
    if not math.isfinite(resolved) or resolved <= 0 or resolved > 1:
        raise BacktrackError(f"backtrack selection delta must be in (0, 1], got {resolved}.")
    return resolved


def resolve_backtrack_candidate_limit(limit: int | None | object) -> int | None:
    if limit is _UNSET:
        session = get_current_session()
        session_limit = (
            int(getattr(session, "backtrack_max_candidates", DEFAULT_CANDIDATE_LIMIT))
            if session is not None
            else DEFAULT_CANDIDATE_LIMIT
        )
        return session_limit
    if limit is None:
        return None
    return int(limit)


def deterministic_candidates(
    records: list[dict[str, Any]],
    *,
    limit: int | None = DEFAULT_CANDIDATE_LIMIT,
) -> list[dict[str, Any]]:
    main_records = [
        record
        for record in records
        if record.get("kind") in {"llm", "tool"} and not _is_internal_replay_boundary(record)
    ]
    candidates: list[dict[str, Any]] = []

    for index, record in enumerate(main_records):
        if record.get("kind") != "llm":
            continue
        segment: list[dict[str, Any]] = []
        for next_record in main_records[index + 1 :]:
            if next_record.get("kind") == "llm":
                break
            segment.append(next_record)
        candidates.append(candidate_from_segment(record, segment))

    if limit is None:
        return candidates
    if limit < 1:
        return []
    return candidates[-limit:]


def _is_internal_replay_boundary(record: dict[str, Any]) -> bool:
    metadata = record.get("metadata")
    return isinstance(metadata, dict) and metadata.get("internal_replay_boundary") is True


def candidate_from_segment(
    llm_record: dict[str, Any],
    segment_records: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "record_uid": llm_record.get("record_uid"),
        "record_kind": "llm",
        "created_at": _record_created_at(llm_record),
        "decision_hint": _decision_hint(llm_record),
        "tool_calls_preview": _tool_calls_preview(llm_record),
        "tool_records_preview": [_tool_record_preview(record) for record in segment_records if record.get("kind") == "tool"],
        "source_mode": "deterministic",
    }


def build_backtrack_override_input(
    request: BacktrackRequested,
    *,
    run_id: str | None = None,
    log_dir: str | Path | None = None,
    memory_prefix: str = DEFAULT_MEMORY_PREFIX,
    memory_items: list[dict[str, Any]] | None = None,
    memory_limit: int | None = DEFAULT_MEMORY_LIMIT,
    memory_policy: BacktrackMemoryPolicy | None = None,
    context_policy: BacktrackContextPolicy | None = None,
    workspace_policy: BacktrackWorkspacePolicy | None = None,
) -> dict[str, Any]:
    resolved_memory_policy = resolve_backtrack_memory_policy(memory_policy)
    resolved_context_policy = resolve_backtrack_context_policy(context_policy)
    resolved_workspace_policy = resolve_backtrack_workspace_policy(workspace_policy)
    resolved_run_id, resolved_log_dir = resolve_current_trace(
        run_id=run_id or request.run_id,
        log_dir=log_dir or request.log_dir,
    )
    records = load_raw_records(run_path(resolved_log_dir, resolved_run_id))
    record = select_backtrack_context_record(records, request, resolved_context_policy)
    patched_input = replay_kwargs_from_record_input(
        record.get("input") if isinstance(record.get("input"), dict) else {}
    )
    messages = patched_input.get("messages")
    if not isinstance(messages, list):
        raise BacktrackError(
            f"Cannot build backtrack override for {request.record_uid}: input.messages is not a list."
        )
    patched_input["messages"] = strip_existing_backtrack_memory_messages(
        messages,
        memory_prefix=memory_prefix,
    )
    messages = patched_input["messages"]
    if resolved_memory_policy == "none":
        return patched_input
    notebook = memory_items
    if notebook is None:
        notebook = build_backtrack_memory_notebook(
            log_dir=resolved_log_dir,
            from_run=resolved_run_id,
            request=request,
        )
    memory_text = render_backtrack_memory_notebook(
        notebook,
        limit=memory_limit,
        memory_prefix=memory_prefix,
        context_policy=resolved_context_policy,
        workspace_policy=resolved_workspace_policy,
        target_record_uid=request.record_uid,
        context_source_record_uid=record.get("record_uid") if isinstance(record.get("record_uid"), str) else None,
    )
    messages.append(
        {
            "role": "system",
            "content": memory_text,
        }
    )
    return patched_input


def strip_existing_backtrack_memory_messages(
    messages: list[Any],
    *,
    memory_prefix: str = DEFAULT_MEMORY_PREFIX,
) -> list[Any]:
    return [
        message
        for message in messages
        if not is_backtrack_memory_message(message, memory_prefix=memory_prefix)
    ]


def is_backtrack_memory_message(
    message: Any,
    *,
    memory_prefix: str = DEFAULT_MEMORY_PREFIX,
) -> bool:
    if not isinstance(message, dict) or message.get("role") != "system":
        return False
    content = message.get("content")
    if not isinstance(content, str):
        return False
    return content.strip().startswith(memory_prefix.strip())


def replay_kwargs_from_record_input(input_record: dict[str, Any]) -> dict[str, Any]:
    patched_input = copy.deepcopy(input_record)
    patched_input.pop("provider", None)
    patched_input.pop("api", None)
    return patched_input


def prepare_backtrack_replay(
    request: BacktrackRequested,
    *,
    current_run_id: str | None = None,
    log_dir: str | Path | None = None,
    fork_run: str | None = None,
    memory_limit: int | None = DEFAULT_MEMORY_LIMIT,
    memory_policy: BacktrackMemoryPolicy | None = None,
    context_policy: BacktrackContextPolicy | None = None,
    workspace_policy: BacktrackWorkspacePolicy | None = None,
) -> dict[str, Any]:
    resolved_memory_policy = resolve_backtrack_memory_policy(memory_policy)
    resolved_context_policy = resolve_backtrack_context_policy(context_policy)
    resolved_workspace_policy = resolve_backtrack_workspace_policy(workspace_policy)
    run_id = current_run_id or request.run_id
    resolved_run_id, resolved_log_dir = resolve_current_trace(run_id=run_id, log_dir=log_dir or request.log_dir)
    records = load_raw_records(run_path(resolved_log_dir, resolved_run_id))
    context_record = select_backtrack_context_record(records, request, resolved_context_policy)
    context_source_record_uid = context_record.get("record_uid")
    memory_notebook = build_backtrack_memory_notebook(
        log_dir=resolved_log_dir,
        from_run=resolved_run_id,
        request=request,
    )
    patched_input = build_backtrack_override_input(
        request,
        run_id=resolved_run_id,
        log_dir=resolved_log_dir,
        memory_items=memory_notebook,
        memory_limit=memory_limit,
        memory_policy=resolved_memory_policy,
        context_policy=resolved_context_policy,
        workspace_policy=resolved_workspace_policy,
    )
    resolved_fork_run = fork_run or next_fork_run_id(resolved_log_dir, resolved_run_id)
    override_input_path = resolved_log_dir / f"{resolved_fork_run}.backtrack_override_input.json"
    override_input_path.parent.mkdir(parents=True, exist_ok=True)
    override_input_path.write_text(
        json.dumps(sanitize_backtrack_override_input_for_file(patched_input), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    metadata_path = resolved_log_dir / f"{resolved_fork_run}.backtrack_metadata.json"
    metadata = {
        "mode": "backtrack",
        "memory_summary": request.memory_summary,
        "reason": request.reason,
    }
    if resolved_memory_policy != "cumulative":
        metadata["memory_policy"] = resolved_memory_policy
    if resolved_context_policy != "rollback":
        metadata["context_policy"] = resolved_context_policy
        metadata["context_source_record_uid"] = context_source_record_uid
    if resolved_workspace_policy != "rollback":
        metadata["workspace_policy"] = resolved_workspace_policy
    if request.selection_metadata is not None:
        metadata["selection_metadata"] = request.selection_metadata
    metadata_path.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_backtrack_event(
        log_dir=resolved_log_dir,
        from_run=resolved_run_id,
        fork_run=resolved_fork_run,
        request=request,
    )
    write_backtrack_memory_notebook(
        log_dir=resolved_log_dir,
        run_id=resolved_fork_run,
        memory_items=[] if resolved_memory_policy == "none" else memory_notebook,
    )
    copy_prefix_backtrack_summaries(
        log_dir=resolved_log_dir,
        from_run=resolved_run_id,
        fork_run=resolved_fork_run,
        breakpoint_record_uid=request.record_uid,
    )
    return {
        "base_run": resolved_run_id,
        "breakpoint_record_uid": request.record_uid,
        "override_input_file": override_input_path,
        "backtrack_metadata_file": metadata_path,
        "fork_run": resolved_fork_run,
        "fork_log_mode": "materialized",
        "backtrack_memory_limit": memory_limit,
        "backtrack_memory_policy": resolved_memory_policy,
        "backtrack_context_policy": resolved_context_policy,
        "backtrack_workspace_policy": resolved_workspace_policy,
        "backtrack_context_source_record_uid": context_source_record_uid,
    }


def sanitize_backtrack_override_input_for_file(override_input: dict[str, Any]) -> dict[str, Any]:
    """Drop persisted secret-bearing kwargs while keeping runtime kwargs authoritative."""

    safe_input: dict[str, Any] = {}
    for key, value in override_input.items():
        if is_sensitive_override_key(key):
            continue
        if is_sensitive_container_key(key) and contains_sensitive_override_key(value):
            continue
        safe_input[key] = copy.deepcopy(value)
    return safe_input


def contains_sensitive_override_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            is_sensitive_override_key(key) or contains_sensitive_override_key(child)
            for key, child in value.items()
        )
    if isinstance(value, list):
        return any(contains_sensitive_override_key(child) for child in value)
    return False


def is_sensitive_override_key(key: Any) -> bool:
    normalized = str(key).strip().lower().replace("-", "_")
    return (
        normalized in _SENSITIVE_OVERRIDE_KEYS
        or normalized.endswith("_api_key")
        or normalized.endswith("_secret")
        or normalized.endswith("_password")
        or (normalized.endswith("_token") and not normalized.endswith("_tokens"))
    )


def is_sensitive_container_key(key: Any) -> bool:
    normalized = str(key).strip().lower().replace("-", "_")
    return normalized in _SENSITIVE_CONTAINER_KEYS


def load_backtrack_memory(log_dir: str | Path, run_id: str) -> list[dict[str, Any]]:
    path = backtrack_memory_path(Path(log_dir), run_id)
    if not path.exists():
        return []
    memory_items: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                item = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise BacktrackError(f"Invalid backtrack memory JSONL at {path}:{line_number}") from exc
            if isinstance(item, dict) and item.get("kind") == "backtrack_memory":
                memory_items.append(item)
    return memory_items


def build_backtrack_memory_notebook(
    *,
    log_dir: Path,
    from_run: str,
    request: BacktrackRequested,
) -> list[dict[str, Any]]:
    memory_items = load_backtrack_memory(log_dir, from_run)
    memory_items.append(backtrack_memory_item(from_run=from_run, request=request))
    return memory_items


def backtrack_memory_item(*, from_run: str, request: BacktrackRequested) -> dict[str, Any]:
    item = {
        "kind": "backtrack_memory",
        "run_id": from_run,
        "target_record_uid": request.record_uid,
        "memory_summary": request.memory_summary,
        "reason": request.reason,
        "created_at": iso_now(),
    }
    if request.selection_metadata is not None:
        item["selection_metadata"] = copy.deepcopy(request.selection_metadata)
    return item


def write_backtrack_memory_notebook(
    *,
    log_dir: Path,
    run_id: str,
    memory_items: list[dict[str, Any]],
) -> None:
    writer = JsonlWriter(backtrack_memory_path(log_dir, run_id), overwrite=True)
    try:
        for item in memory_items:
            copied = copy.deepcopy(item)
            copied["run_id"] = run_id
            writer.write(copied)
    finally:
        writer.close()


def render_backtrack_memory_notebook(
    memory_items: list[dict[str, Any]],
    *,
    limit: int | None = DEFAULT_MEMORY_LIMIT,
    memory_prefix: str = DEFAULT_MEMORY_PREFIX,
    context_policy: BacktrackContextPolicy = "rollback",
    workspace_policy: BacktrackWorkspacePolicy = "rollback",
    target_record_uid: str | None = None,
    context_source_record_uid: str | None = None,
    item_char_limit: int = DEFAULT_MEMORY_ITEM_CHAR_LIMIT,
    notebook_char_limit: int = DEFAULT_MEMORY_NOTEBOOK_CHAR_LIMIT,
) -> str:
    rendered_items = select_backtrack_memory_items(memory_items, limit=limit)
    lines = [memory_prefix.rstrip(), ""]
    policy_lines = backtrack_memory_policy_banner(
        context_policy=context_policy,
        workspace_policy=workspace_policy,
        target_record_uid=target_record_uid,
        context_source_record_uid=context_source_record_uid,
    )
    if policy_lines:
        lines.extend(policy_lines)
        lines.append("")
    if not rendered_items:
        return "\n".join(lines).rstrip()
    for index, item in enumerate(rendered_items, start=1):
        summary = str(item.get("memory_summary") or "").strip()
        if not summary:
            continue
        summary = _truncate(summary, limit=item_char_limit)
        detail = f"{index}. {summary}"
        target_record_uid = item.get("target_record_uid")
        reason = item.get("reason")
        if target_record_uid or reason:
            annotations = []
            if target_record_uid:
                annotations.append(f"target={target_record_uid}")
            if reason:
                annotations.append(f"reason={reason}")
            detail += f" ({'; '.join(annotations)})"
        lines.append(detail)
    rendered = "\n".join(lines).rstrip()
    if notebook_char_limit and len(rendered) > notebook_char_limit:
        return rendered[:notebook_char_limit].rstrip() + "\n...[backtrack memory truncated]"
    return rendered


def backtrack_memory_policy_banner(
    *,
    context_policy: BacktrackContextPolicy,
    workspace_policy: BacktrackWorkspacePolicy,
    target_record_uid: str | None = None,
    context_source_record_uid: str | None = None,
) -> list[str]:
    if context_policy == "rollback" and workspace_policy == "rollback":
        return []
    target_label = target_record_uid or "unknown"
    context_label = context_source_record_uid or "unknown"
    lines = [
        "Backtrack execution policy for this fork:",
        "",
        f"- Selected backtrack target: {target_label}. This is an internal Replay ID for the LLM decision selected by the accepted backtrack request.",
    ]
    if context_policy == "preserve":
        lines.append(
            f"- Conversation context source: {context_label}. This is the latest LLM record from the abandoned failed branch; agent messages were intentionally not rewound to {target_label}."
        )
    else:
        lines.append(
            f"- Conversation context state: agent messages were rewound to the input messages for target LLM record {target_label}."
        )
    if workspace_policy == "preserve":
        lines.append(
            "- Controlled Git workspace source: the failed branch at the moment backtrack was requested. "
            f"Files were intentionally not restored to the checkpoint for {target_label}."
        )
    else:
        lines.append(
            "- Controlled Git workspace state: restored to the recorded filesystem checkpoint immediately before "
            f"the tool calls produced by target LLM record {target_label} would execute."
        )
    lines.append(
        "The state combination above is intentional for this ablation policy and does not mean that backtrack failed."
    )
    if context_policy == "preserve":
        lines.append(
            "Messages and tool observations after the selected target remain visible by design, but their filesystem claims may be stale. Do not backtrack again solely to remove those messages or because they conflict with current files."
        )
    if workspace_policy == "preserve":
        lines.append(
            "Failed-branch files remain present by design. Do not backtrack again solely because those files were not restored to the target checkpoint."
        )
    lines.append(
        "First inspect the current controlled Git workspace. Backtrack again only when new tool or verifier evidence shows that the strategy needs a different decision point."
    )
    return lines


def select_backtrack_memory_items(
    memory_items: list[dict[str, Any]],
    *,
    limit: int | None = DEFAULT_MEMORY_LIMIT,
) -> list[dict[str, Any]]:
    valid_items = [
        item
        for item in memory_items
        if isinstance(item.get("memory_summary"), str) and item["memory_summary"].strip()
    ]
    if limit is None:
        return valid_items
    if limit <= 0:
        return []
    return valid_items[-limit:]


def compress_backtrack_memory_notebook(
    memory_items: list[dict[str, Any]],
    *,
    max_items: int = DEFAULT_MEMORY_LIMIT,
) -> list[dict[str, Any]]:
    """Future hook for LLM-based notebook compression."""

    return select_backtrack_memory_items(memory_items, limit=max_items)


def load_backtrack_summaries(log_dir: str | Path, run_id: str) -> list[dict[str, Any]]:
    path = backtrack_summaries_path(Path(log_dir), run_id)
    if not path.exists():
        return []
    summaries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                item = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise BacktrackError(f"Invalid backtrack summary JSONL at {path}:{line_number}") from exc
            if isinstance(item, dict) and item.get("kind") == "backtrack_summary":
                summaries.append(item)
    return summaries


def enrich_candidates_with_summaries(
    candidates: list[dict[str, Any]],
    summaries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    summaries_by_record_uid: dict[str, dict[str, Any]] = {}
    for summary in summaries:
        record_uid = summary.get("record_uid")
        summary_text = summary.get("summary")
        if isinstance(record_uid, str) and isinstance(summary_text, str) and summary_text.strip():
            summaries_by_record_uid[record_uid] = summary

    enriched: list[dict[str, Any]] = []
    for candidate in candidates:
        copied = dict(candidate)
        summary = summaries_by_record_uid.get(str(candidate.get("record_uid")))
        if summary is not None:
            summary_text = str(summary["summary"])
            copied.update(
                {
                    "decision_hint": _truncate(summary_text),
                    "summary": summary_text,
                    "summary_created_at": summary.get("created_at"),
                    "summary_model": summary.get("model"),
                    "summary_source_mode": summary.get("source_mode"),
                    "source_mode": "llm-summary",
                }
            )
        enriched.append(copied)
    return enriched


def copy_prefix_backtrack_summaries(
    *,
    log_dir: Path,
    from_run: str,
    fork_run: str,
    breakpoint_record_uid: str,
) -> int:
    copied_count = 0
    writer = JsonlWriter(backtrack_summaries_path(log_dir, fork_run), overwrite=True)
    try:
        for summary in load_backtrack_summaries(log_dir, from_run):
            if not is_prefix_backtrack_summary(summary, breakpoint_record_uid=breakpoint_record_uid):
                continue
            copied = copy.deepcopy(summary)
            copied["run_id"] = fork_run
            writer.write(copied)
            copied_count += 1
    finally:
        writer.close()
    return copied_count


def is_prefix_backtrack_summary(summary: dict[str, Any], *, breakpoint_record_uid: str) -> bool:
    breakpoint_index = record_uid_index(breakpoint_record_uid)
    record_index = record_uid_index(summary.get("record_uid"))
    end_before_index = record_uid_index(summary.get("end_before_record_uid"))
    if breakpoint_index <= 0 or record_index <= 0 or end_before_index <= 0:
        return False
    return record_index < breakpoint_index and end_before_index <= breakpoint_index


def write_backtrack_event(
    *,
    log_dir: Path,
    from_run: str,
    fork_run: str,
    request: BacktrackRequested,
) -> None:
    writer = JsonlWriter(backtrack_events_path(log_dir, from_run), overwrite=False)
    event = {
        "kind": "backtrack_event",
        "from_run": from_run,
        "fork_run": fork_run,
        "target_record_uid": request.record_uid,
        "memory_summary": request.memory_summary,
        "reason": request.reason,
        "created_at": iso_now(),
    }
    if request.selection_metadata is not None:
        event["selection_metadata"] = request.selection_metadata
    try:
        writer.write(event)
    finally:
        writer.close()


def resolve_current_trace(
    *,
    run_id: str | None = None,
    log_dir: str | Path | None = None,
) -> tuple[str, Path]:
    if run_id is not None:
        return run_id, Path(log_dir) if log_dir is not None else DEFAULT_LOG_DIR

    session = get_current_session()
    if session is None:
        raise BacktrackError("No active replay session; pass run_id and log_dir explicitly.")

    if hasattr(session, "fork_run") and getattr(session, "fork_run") is not None:
        return str(session.fork_run), session.log_dir
    if hasattr(session, "run_id"):
        return str(session.run_id), session.log_dir
    if hasattr(session, "base_run"):
        return str(session.base_run), session.log_dir

    raise BacktrackError("Could not resolve the current replay run.")


def find_llm_record(records: list[dict[str, Any]], record_uid: str) -> dict[str, Any]:
    for record in records:
        if record.get("record_uid") == record_uid:
            if record.get("kind") != "llm":
                raise InvalidBreakpointError(
                    "backtrack target must refer to an LLM record, "
                    f"but got kind={record.get('kind')!r}."
                )
            return record
    raise InvalidBreakpointError(f"backtrack target not found: {record_uid}")


def select_backtrack_context_record(
    records: list[dict[str, Any]],
    request: BacktrackRequested,
    context_policy: BacktrackContextPolicy,
) -> dict[str, Any]:
    target_record = find_llm_record(records, request.record_uid)
    if context_policy == "rollback":
        return target_record
    for record in reversed(records):
        if record.get("kind") == "llm":
            return record
    return target_record


def resolve_backtrack_target_record_uid(records: list[dict[str, Any]], record_uid: str) -> str:
    """Return an LLM uid, mapping an accidentally copied tool uid to its owner."""

    previous_llm_uid: str | None = None
    for record in records:
        uid = record.get("record_uid")
        kind = record.get("kind")
        if uid == record_uid:
            if kind == "llm":
                return str(record_uid)
            if kind == "tool" and previous_llm_uid:
                return previous_llm_uid
            raise InvalidBreakpointError(
                "backtrack target must refer to an LLM record, "
                f"but got kind={kind!r}."
            )
        if kind == "llm" and isinstance(uid, str):
            previous_llm_uid = uid
    raise InvalidBreakpointError(f"backtrack target not found: {record_uid}")


def _record_created_at(record: dict[str, Any]) -> Any:
    metadata = record.get("metadata")
    if isinstance(metadata, dict):
        return metadata.get("created_at")
    return None


def _decision_hint(record: dict[str, Any]) -> str:
    output = record.get("output")
    if not isinstance(output, dict):
        return ""
    content = output.get("content")
    if isinstance(content, str) and content:
        return _truncate(content)
    raw_response = output.get("raw_response")
    reasoning = _raw_reasoning_content(raw_response)
    if reasoning:
        return _truncate(reasoning)
    tool_calls_preview = _tool_calls_preview(record)
    return tool_calls_preview if tool_calls_preview else ""


def _raw_reasoning_content(raw_response: Any) -> str:
    if not isinstance(raw_response, dict):
        return ""
    choices = raw_response.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if not isinstance(message, dict):
        return ""
    reasoning = message.get("reasoning_content")
    return reasoning if isinstance(reasoning, str) else ""


def _tool_calls_preview(record: dict[str, Any]) -> str:
    output = record.get("output")
    tool_calls = output.get("tool_calls") if isinstance(output, dict) else None
    if not isinstance(tool_calls, list) or not tool_calls:
        return ""
    previews = []
    for tool_call in tool_calls:
        parsed = _tool_call_preview(tool_call)
        if parsed:
            previews.append(parsed)
    return _json_preview(previews)


def _tool_call_preview(tool_call: Any) -> dict[str, Any] | None:
    if not isinstance(tool_call, dict):
        return None
    if isinstance(tool_call.get("function"), dict):
        function = tool_call["function"]
        return {
            "name": function.get("name"),
            "arguments": function.get("arguments"),
        }
    return {
        "name": tool_call.get("name"),
        "arguments": tool_call.get("arguments", tool_call.get("args")),
    }


def _tool_record_preview(record: dict[str, Any]) -> dict[str, Any]:
    input_record = record.get("input") if isinstance(record.get("input"), dict) else {}
    error = record.get("error")
    return {
        "tool_name": input_record.get("tool_name"),
        "arguments_preview": _json_preview(input_record.get("arguments")),
        "status": "error" if error else "ok",
        "output_preview": _json_preview((record.get("output") or {}).get("value") if isinstance(record.get("output"), dict) else None),
        "error_preview": _json_preview(error),
        "effects_preview": _json_preview(record.get("effects")),
    }


def _json_preview(value: Any, *, limit: int = 400) -> str:
    if value is None:
        return ""
    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        text = repr(value)
    return _truncate(text, limit=limit)


def _truncate(value: str, *, limit: int = 400) -> str:
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    if limit <= 3:
        return text[:limit]
    return text[: limit - 3].rstrip() + "..."


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
