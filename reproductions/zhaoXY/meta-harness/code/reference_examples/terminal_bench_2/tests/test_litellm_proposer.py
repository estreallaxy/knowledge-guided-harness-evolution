"""Tests for the litellm-backed proposer.

Everything here runs offline: the LLM is stubbed, so no credentials and no
network are needed.  Run from the terminal_bench_2 directory:

    uv run python -m unittest -v tests.test_litellm_proposer
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import claude_wrapper
import litellm_proposer


def _tool_call(name, arguments, call_id="call_1"):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=arguments),
    )


def _response(content="", tool_calls=None, prompt_tokens=10, completion_tokens=5):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content, tool_calls=tool_calls)
            )
        ],
        usage=SimpleNamespace(
            prompt_tokens=prompt_tokens, completion_tokens=completion_tokens
        ),
    )


def _scripted(*responses):
    """Return a stub that yields the given responses in order."""
    queue = list(responses)

    def stub(**kwargs):
        if not queue:
            raise AssertionError("stub called more times than scripted")
        return queue.pop(0)

    return stub


class ProposerTestCase(unittest.TestCase):
    """Shared setup: a throwaway workspace and a clean proposer environment."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="proposer-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "agents").mkdir()
        (self.tmp / "prompt-templates").mkdir()
        (self.tmp / "scripts").mkdir()
        (self.tmp / "tests").mkdir()
        (self.tmp / "agents" / "baseline_kira.py").write_text("# H0\n")
        (self.tmp / "meta_harness.py").write_text("# outer loop\n")
        self.pending = self.tmp / "logs" / "pending_eval.json"

        # Snapshot the environment once; per-test tweaks go through the
        # `environ` argument of run_proposer so nothing leaks between tests.
        env_patcher = mock.patch.dict(os.environ, {}, clear=False)
        env_patcher.start()
        self.addCleanup(env_patcher.stop)
        for var in (
            "PROPOSER_MODEL",
            "PROPOSER_API_BASE",
            "PROPOSER_MAX_TURNS",
            "PROPOSER_TEMPERATURE",
            "PROPOSER_NUM_RETRIES",
            "DEEPSEEK_API_KEY",
            "OPENAI_API_KEY",
        ):
            os.environ.pop(var, None)

    def run_proposer(self, stub, environ=None, **overrides):
        """Run the proposer with a stubbed LLM.

        ``environ`` replaces the key-bearing environment for this run; passing
        ``environ={}`` exercises the missing-credential path.
        """
        if environ is None:
            environ = {"DEEPSEEK_API_KEY": "test-key"}
        kwargs = {
            "prompt": "propose something",
            "cwd": str(self.tmp),
            "log_dir": str(self.tmp / "logs" / "claude_sessions"),
            "name": "iter1",
            "timeout_seconds": 60,
            "max_turns": 10,
            "progress": False,
            "pending_eval_path": str(self.pending),
        }
        kwargs.update(overrides)
        # setUp has already stripped the proposer/key variables, so adding
        # `environ` on top is enough -- and avoids clearing PATH/HOME.
        with mock.patch.object(
            litellm_proposer, "litellm_completion", stub
        ), mock.patch.object(
            litellm_proposer, "_completion_cost", lambda response: 0.0
        ), mock.patch.dict(os.environ, environ, clear=False):
            result = litellm_proposer.run(**kwargs)
        # Guard against a test passing only because the session overshot its
        # scripted responses and died on the stub's own error.
        self.assertNotIn("stub called more times", result.stderr)
        return result

    def _evolve_args(self, run_name, skip_baseline=True):
        """Minimal args for run_evolve that stop right after the dir setup."""
        return SimpleNamespace(
            run_name=run_name,
            iterations=0,
            trials=2,
            fresh=False,
            skip_baseline=skip_baseline,
            skip_smoke=True,
            propose_only=False,
            full_eval=False,
            concurrent=1,
            propose_timeout=1,
        )


class PathSafetyTests(ProposerTestCase):
    def test_read_refuses_to_escape_workspace(self):
        ctx = litellm_proposer.ToolContext(evo_dir=self.tmp)
        for escape in ("../../etc/passwd", "/etc/passwd"):
            with self.assertRaises(litellm_proposer.ToolError):
                litellm_proposer._tool_read_file({"path": escape}, ctx)

    def test_write_refuses_h0_and_harness_files(self):
        ctx = litellm_proposer.ToolContext(evo_dir=self.tmp)
        forbidden = (
            "agents/baseline_kira.py",
            "agents/baseline_terminus2.py",
            "agents/__init__.py",
            "meta_harness.py",
            "scripts/run_eval.sh",
            "tests/test_meta_harness.py",
            "../outside.py",
        )
        for rel in forbidden:
            with self.assertRaises(litellm_proposer.ToolError, msg=rel):
                litellm_proposer._tool_write_file(
                    {"path": rel, "content": "nope"}, ctx
                )
        # nothing was actually written
        self.assertEqual((self.tmp / "agents" / "baseline_kira.py").read_text(), "# H0\n")
        self.assertFalse((self.tmp.parent / "outside.py").exists())

    def test_write_allows_candidates_and_templates(self):
        ctx = litellm_proposer.ToolContext(evo_dir=self.tmp)
        litellm_proposer._tool_write_file(
            {"path": "agents/candidate_a.py", "content": "x = 1\n"}, ctx
        )
        litellm_proposer._tool_write_file(
            {"path": "prompt-templates/candidate_a.txt", "content": "hi\n"}, ctx
        )
        self.assertTrue((self.tmp / "agents" / "candidate_a.py").is_file())
        self.assertTrue((self.tmp / "prompt-templates" / "candidate_a.txt").is_file())

    def test_write_allows_the_runs_pending_eval(self):
        ctx = litellm_proposer.ToolContext(
            evo_dir=self.tmp, pending_eval_path=self.pending
        )
        litellm_proposer._tool_write_file(
            {"path": str(self.pending), "content": "{}"}, ctx
        )
        self.assertTrue(self.pending.is_file())

    def test_write_refuses_pending_eval_of_another_run(self):
        ctx = litellm_proposer.ToolContext(
            evo_dir=self.tmp, pending_eval_path=self.pending
        )
        other = self.tmp / "logs" / "other-run" / "pending_eval.json"
        with self.assertRaises(litellm_proposer.ToolError):
            litellm_proposer._tool_write_file({"path": str(other), "content": "{}"}, ctx)


class ToolBehaviourTests(ProposerTestCase):
    def test_read_file_emits_claude_compatible_line_numbers(self):
        body = "\n".join(f"line {i}" for i in range(1, 11)) + "\n"
        (self.tmp / "sample.txt").write_text(body)
        ctx = litellm_proposer.ToolContext(evo_dir=self.tmp)

        out = litellm_proposer._tool_read_file({"path": "sample.txt"}, ctx)

        self.assertEqual(claude_wrapper._count_read_lines(out), 10)
        self.assertIn("line 1", claude_wrapper._clean_read_output(out))
        self.assertEqual(ctx.files_read["sample.txt"], {"reads": 1, "lines": 10})

    def test_read_file_honours_offset_and_limit(self):
        (self.tmp / "sample.txt").write_text(
            "\n".join(f"line {i}" for i in range(1, 21)) + "\n"
        )
        ctx = litellm_proposer.ToolContext(evo_dir=self.tmp)
        out = litellm_proposer._tool_read_file(
            {"path": "sample.txt", "offset": 5, "limit": 3}, ctx
        )
        self.assertEqual(claude_wrapper._count_read_lines(out), 3)
        self.assertIn("line 5", out)
        self.assertIn("more lines", out)

    def test_run_bash_strips_credentials_from_the_environment(self):
        ctx = litellm_proposer.ToolContext(evo_dir=self.tmp)
        with mock.patch.dict(os.environ, {"DEEPSEEK_API_KEY": "super-secret"}):
            out = litellm_proposer._tool_run_bash(
                {"command": "echo ${DEEPSEEK_API_KEY:-absent}"}, ctx
            )
        self.assertIn("absent", out)
        self.assertNotIn("super-secret", out)

    def test_bash_timeout_raises_tool_error(self):
        """The loop turns ToolError into an 'ERROR:' tool result, so a hung
        command costs one turn rather than the whole session."""
        ctx = litellm_proposer.ToolContext(evo_dir=self.tmp)
        with self.assertRaises(litellm_proposer.ToolError) as caught:
            litellm_proposer._tool_run_bash({"command": "sleep 5", "timeout": 1}, ctx)
        self.assertIn("timed out", str(caught.exception))

    def test_bash_reports_exit_code(self):
        ctx = litellm_proposer.ToolContext(evo_dir=self.tmp)
        out = litellm_proposer._tool_run_bash({"command": "exit 3"}, ctx)
        self.assertIn("[exit code: 3]", out)


class ProposerLoopTests(ProposerTestCase):
    def _write_pending_payload(self, name="cand_a"):
        return json.dumps(
            {"iteration": 1, "candidates": [{"name": name, "import_path": f"agents.{name}:AgentHarness"}]}
        )

    def test_successful_session_writes_pending_eval_and_logs(self):
        stub = _scripted(
            _response(
                tool_calls=[
                    _tool_call(
                        "write_file",
                        json.dumps(
                            {"path": "agents/cand_a.py", "content": "class A: pass\n"}
                        ),
                    )
                ]
            ),
            _response(
                tool_calls=[
                    _tool_call(
                        "write_file",
                        json.dumps(
                            {
                                "path": str(self.pending),
                                "content": self._write_pending_payload(),
                            }
                        ),
                        call_id="call_2",
                    )
                ]
            ),
        )
        result = self.run_proposer(stub)

        self.assertEqual(result.exit_code, 0, result.stderr)
        self.assertTrue(self.pending.is_file())
        self.assertEqual(len(result.tool_calls), 2)
        self.assertIn("agents/cand_a.py", result.files_written)

    def test_show_does_not_raise(self):
        """claude_wrapper.SessionResult.show() indexes token_usage directly."""
        stub = _scripted(_response(content="nothing to do"), _response(content="DONE"))
        result = self.run_proposer(stub)
        self.assertIn("input_tokens", result.token_usage)
        self.assertIn("output_tokens", result.token_usage)
        result.show()  # must not raise KeyError

    def test_token_usage_accumulates(self):
        stub = _scripted(
            _response(tool_calls=[_tool_call("list_dir", "{}")], prompt_tokens=100, completion_tokens=20),
            _response(content="DONE", prompt_tokens=7, completion_tokens=3),
        )
        result = self.run_proposer(stub)
        self.assertEqual(result.token_usage["input_tokens"], 107)
        self.assertEqual(result.token_usage["output_tokens"], 23)

    def test_missing_key_returns_config_error_without_calling_llm(self):
        def explode(**kwargs):
            raise AssertionError("litellm must not be called without a key")

        result = self.run_proposer(explode, environ={})
        self.assertEqual(result.exit_code, litellm_proposer.EXIT_CONFIG)
        self.assertIn("DEEPSEEK_API_KEY", result.stderr)

    def test_timeout_returns_124(self):
        def slow(**kwargs):
            import time as _t

            _t.sleep(0.15)
            return _response(tool_calls=[_tool_call("list_dir", "{}")])

        result = self.run_proposer(slow, timeout_seconds=0.05)
        self.assertEqual(result.exit_code, litellm_proposer.EXIT_TIMEOUT)
        self.assertIn("timed out", result.stderr)

    def test_max_turns_is_respected(self):
        stub = _scripted(*[_response(tool_calls=[_tool_call("list_dir", "{}")]) for _ in range(3)])
        result = self.run_proposer(stub, max_turns=3)
        self.assertEqual(result.exit_code, litellm_proposer.EXIT_NO_CANDIDATES)
        self.assertIn("max_turns", result.stderr)

    def test_malformed_arguments_do_not_kill_the_loop(self):
        stub = _scripted(
            _response(tool_calls=[_tool_call("list_dir", "{not json")]),
            _response(content="DONE"),
        )
        result = self.run_proposer(stub)
        self.assertEqual(len(result.tool_calls), 1)
        self.assertTrue(result.tool_calls[0].is_error)
        self.assertIn("not valid JSON", result.tool_calls[0].output)

    def test_text_only_turn_is_nudged_before_giving_up(self):
        stub = _scripted(
            _response(content="I will now write the candidate."),
            _response(
                tool_calls=[
                    _tool_call(
                        "write_file",
                        json.dumps(
                            {"path": str(self.pending), "content": self._write_pending_payload()}
                        ),
                    )
                ]
            ),
        )
        result = self.run_proposer(stub)
        self.assertEqual(result.exit_code, 0, result.stderr)
        self.assertTrue(self.pending.is_file())

    def test_pasted_json_block_is_salvaged(self):
        payload = self._write_pending_payload("salvaged")
        stub = _scripted(
            _response(content=f"I could not write the file.\n\n```json\n{payload}\n```")
        )
        result = self.run_proposer(stub)
        self.assertEqual(result.exit_code, 0, result.stderr)
        self.assertTrue(self.pending.is_file())
        self.assertEqual(
            json.loads(self.pending.read_text())["candidates"][0]["name"], "salvaged"
        )

    def test_log_session_layout_matches_the_claude_backend(self):
        stub = _scripted(
            _response(
                content="done",
                tool_calls=[
                    _tool_call(
                        "write_file",
                        json.dumps({"path": str(self.pending), "content": self._write_pending_payload()}),
                    )
                ],
            ),
            _response(content="DONE"),
        )
        log_dir = self.tmp / "logs" / "claude_sessions"
        result = self.run_proposer(stub, log_dir=str(log_dir))

        session_dirs = list(log_dir.iterdir())
        self.assertEqual(len(session_dirs), 1)
        session = session_dirs[0]
        self.assertTrue(session.name.endswith("_iter1"))
        self.assertTrue((session / "meta.json").is_file())
        self.assertTrue((session / "events.jsonl").is_file())
        meta = json.loads((session / "meta.json").read_text())
        self.assertEqual(meta["exit_code"], 0)
        self.assertEqual(meta["model"], litellm_proposer.DEFAULT_MODEL)
        self.assertTrue(list((session / "tools").glob("*.txt")))

    def test_llm_exception_is_reported_not_raised(self):
        def boom(**kwargs):
            raise RuntimeError("provider exploded")

        result = self.run_proposer(boom)
        self.assertEqual(result.exit_code, litellm_proposer.EXIT_NO_CANDIDATES)
        self.assertIn("provider exploded", result.stderr)


class ConfigTests(ProposerTestCase):
    def test_import_does_not_require_a_key(self):
        """Import-time key reads would break test collection."""
        self.assertTrue(hasattr(litellm_proposer, "run"))

    def test_model_resolution_defaults_to_deepseek(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PROPOSER_MODEL", None)
            os.environ.pop("PROPOSER_API_BASE", None)
            model, base = litellm_proposer._resolve_model()
        self.assertEqual(model, "deepseek/deepseek-v4-flash")
        self.assertIsNone(base)

    def test_api_base_switches_to_openai_compatible_routing(self):
        with mock.patch.dict(
            os.environ,
            {"PROPOSER_MODEL": "deepseek/deepseek-v4-flash", "PROPOSER_API_BASE": "http://proxy:8080/v1"},
        ):
            model, base = litellm_proposer._resolve_model()
        self.assertEqual(model, "openai/deepseek-v4-flash")
        self.assertEqual(base, "http://proxy:8080/v1")


class MetaHarnessWiringTests(ProposerTestCase):
    """The integration points in meta_harness.py, exercised without a network."""

    def test_propose_dispatches_to_litellm_by_default(self):
        import meta_harness

        with mock.patch.object(meta_harness, "PROPOSER_BACKEND", "litellm"), mock.patch.object(
            meta_harness, "propose_litellm", return_value=True
        ) as litellm_side, mock.patch.object(
            meta_harness, "propose_claude", return_value=False
        ) as claude_side:
            self.assertTrue(meta_harness.propose("p", 1))
        litellm_side.assert_called_once()
        claude_side.assert_not_called()

    def test_propose_backend_claude_still_uses_the_cli_path(self):
        import meta_harness

        with mock.patch.object(meta_harness, "PROPOSER_BACKEND", "claude"), mock.patch.object(
            meta_harness, "propose_litellm", return_value=False
        ) as litellm_side, mock.patch.object(
            meta_harness, "propose_claude", return_value=True
        ) as claude_side:
            self.assertTrue(meta_harness.propose("p", 1))
        claude_side.assert_called_once()
        litellm_side.assert_not_called()

    def test_propose_litellm_passes_the_run_pending_eval_path(self):
        import meta_harness

        with mock.patch.object(
            meta_harness.litellm_proposer,
            "run",
            return_value=SimpleNamespace(exit_code=0, stderr="", show=lambda: None),
        ) as runner:
            meta_harness.propose_litellm("p", 7, timeout=99)

        kwargs = runner.call_args.kwargs
        self.assertEqual(kwargs["pending_eval_path"], str(meta_harness.PENDING_EVAL))
        self.assertEqual(kwargs["name"], "iter7")
        self.assertEqual(kwargs["timeout_seconds"], 99)

    def test_runs_dir_relocates_the_evolution_artifacts(self):
        """RUNS_DIR must move run_evolve's output too, not just the import-time
        defaults: run_evolve used to reassign JOBS_DIR/LOGS_DIR from EVOLVE_DIR,
        which silently sent every evolution run to the code directory."""
        import importlib

        import meta_harness

        self.addCleanup(importlib.reload, meta_harness)
        with mock.patch.dict(os.environ, {"RUNS_DIR": str(self.tmp)}):
            importlib.reload(meta_harness)
            meta_harness.run_evolve(self._evolve_args("wiring-check"))

            self.assertEqual(meta_harness.JOBS_DIR, self.tmp / "jobs" / "wiring-check")
            self.assertEqual(meta_harness.LOGS_DIR, self.tmp / "logs" / "wiring-check")
            self.assertTrue(meta_harness.JOBS_DIR.is_dir())
            self.assertTrue(meta_harness.LOGS_DIR.is_dir())
            self.assertEqual(
                meta_harness.PENDING_EVAL,
                self.tmp / "logs" / "wiring-check" / "pending_eval.json",
            )

    def test_runs_dir_defaults_to_the_code_dir(self):
        """Unset RUNS_DIR keeps the original layout (EVOLVE_DIR/{logs,jobs})."""
        import importlib

        import meta_harness

        self.addCleanup(importlib.reload, meta_harness)
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("RUNS_DIR", None)
            importlib.reload(meta_harness)
            self.assertEqual(meta_harness.RUNS_DIR, meta_harness.EVOLVE_DIR)
            self.assertEqual(meta_harness.LOGS_DIR, meta_harness.EVOLVE_DIR / "logs")
            self.assertEqual(meta_harness.JOBS_DIR, meta_harness.EVOLVE_DIR / "jobs")


class CachedBaselineTests(ProposerTestCase):
    """The Phase 0 cache check must recognise real harbor job dirs.

    Upstream read the model from a top-level "model" / singular "agent.model",
    but harbor records it as agents[0].model_name, so every completed baseline
    was re-run (~$10 and hours per run) instead of being reused.
    """

    MODEL = "deepseek/deepseek-v4-flash"

    def test_reads_harbors_agents_list(self):
        import meta_harness

        cfg = {
            "n_attempts": 2,
            "agents": [
                {"name": "agents.baseline_kira:AgentHarness", "model_name": self.MODEL}
            ],
        }
        self.assertEqual(meta_harness._cached_model_name(cfg), self.MODEL)

    def test_keeps_the_shapes_upstream_handled(self):
        import meta_harness

        self.assertEqual(meta_harness._cached_model_name({"model": "m1"}), "m1")
        self.assertEqual(meta_harness._cached_model_name({"agent": {"model": "m2"}}), "m2")

    def test_unknown_shape_reads_as_empty(self):
        import meta_harness

        self.assertEqual(meta_harness._cached_model_name({}), "")
        self.assertEqual(meta_harness._cached_model_name({"agents": []}), "")
        self.assertEqual(meta_harness._cached_model_name({"agents": "oops"}), "")

    def _seed_baseline(self, runs, run_name, blob_name="kira-baseline-t2"):
        """Write a job dir shaped like harbor's, with one passing trial."""
        job = runs / "jobs" / run_name / blob_name
        (job / "some-task__AbCdEfG").mkdir(parents=True)
        (job / "config.json").write_text(
            json.dumps(
                {
                    "n_attempts": 2,
                    "agents": [{"model_name": self.MODEL}],
                }
            )
        )
        (job / "some-task__AbCdEfG" / "result.json").write_text(
            json.dumps({"verifier_result": {"rewards": {"reward": 1.0}}})
        )
        return job

    def test_harbor_shaped_cache_is_reused_instead_of_rerun(self):
        """The whole point of the fix: a matching job dir is not re-run."""
        import contextlib
        import importlib
        import io

        import meta_harness

        self.addCleanup(importlib.reload, meta_harness)
        runs = self.tmp / "runs"
        self._seed_baseline(runs, "evolve-1")

        def fake_run(import_path, job_name, **kwargs):
            # terminus2 has no cached dir, so it is the only one allowed to run.
            if "kira" in import_path:
                raise AssertionError("cached kira baseline was re-run")
            return runs / "jobs" / "evolve-1" / job_name, True

        with mock.patch.dict(
            os.environ, {"RUNS_DIR": str(runs), "HARBOR_MODEL": self.MODEL}
        ):
            importlib.reload(meta_harness)
            out = io.StringIO()
            with contextlib.redirect_stdout(out), mock.patch.object(
                meta_harness, "harbor_run", side_effect=fake_run
            ) as hb:
                meta_harness.run_evolve(self._evolve_args("evolve-1", skip_baseline=False))

        logged = out.getvalue()
        self.assertIn("cached", logged)
        self.assertIn("kira-baseline", logged)
        self.assertEqual(len(hb.call_args_list), 1)
        # The cached baseline's results still seed the frontier.
        frontier = json.loads(meta_harness.FRONTIER_VAL.read_text())
        self.assertEqual(frontier["some-task"]["pass_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
