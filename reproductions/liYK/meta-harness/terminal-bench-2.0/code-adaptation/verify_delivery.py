"""Verify portable delivery evidence with only the standard library."""
import ast
import hashlib
import json
from pathlib import Path


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    adaptation = Path(__file__).resolve().parent
    benchmark = adaptation.parent
    member = benchmark.parents[1]
    upstream = benchmark.parent / "code/reference_examples/terminal_bench_2/agents/baseline_kira.py"
    port = json.loads((adaptation / "port-verification.json").read_text())
    provenance = json.loads((adaptation / "provenance.json").read_text())
    assert sha256(upstream) == port["official_baseline_sha256"]
    assert sha256(adaptation / "historical-adaptation.diff") == provenance["patch_sha256"]
    for path, expected in provenance["historical_extra_source_files"].items():
        assert sha256(adaptation / path) == expected, path
    assert (adaptation / "agents/deepseek_candidate_003.py").read_bytes() == (
        adaptation / "historical-agents/deepseek_candidate_003.py"
    ).read_bytes()
    tree = ast.parse((adaptation / "agents/bailian_kira.py").read_text())
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "AgentHarness")
    methods = {node.name: node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for name, evidence in port["method_comparison"].items():
        digest = hashlib.sha256(ast.dump(methods[name], include_attributes=False).encode()).hexdigest()
        assert digest == evidence["ast_sha256"], name
    task_sets = []
    for baseline, expected in (("H0", (13, 9, 8, 36)), ("meta-harness", (17, 10, 3, 38))):
        summary = json.loads((member / baseline / "terminal-bench-2.0/results/summary.json").read_text())
        rows = summary["task_results"]
        ids = {row["task"] for row in rows}
        assert len(rows) == len(ids) == summary["denominator"] == 30
        actual = (
            sum(row["reward"] == 1 for row in rows),
            sum(row["reward"] == 0 for row in rows),
            sum(row["reward"] is None for row in rows),
            summary["total_attempts"],
        )
        assert actual == expected
        assert actual[:3] == tuple(summary[key] for key in ("successes", "zero_reward", "ungraded"))
        assert summary["metric"]["value"] == actual[0] / 30
        assert summary["metric"]["ungraded_in_denominator"]
        assert not summary["is_new_terminus_h0_result"]
        assert not summary["team_protocol_acceptance_verified"]
        assert not summary["heldout_generalization_verified"]
        if baseline == "meta-harness":
            assert sha256(adaptation / "agents/deepseek_candidate_003.py") == summary["candidate_sha256"]
        task_sets.append(ids)
    assert task_sets[0] == task_sets[1]
    print("PASS: two 30-task summaries, counts, snapshot, candidate and historical hashes, provider AST")


if __name__ == "__main__":
    main()
