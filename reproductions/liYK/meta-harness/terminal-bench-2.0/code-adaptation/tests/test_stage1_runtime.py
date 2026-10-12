"""Check data-role boundaries and lossless failed-run evidence export."""
import asyncio
import contextlib
import io
import json
import tempfile
import unittest
import httpx
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import export_train
import launch
import propose
import runtime


class LaunchTests(unittest.TestCase):
    def test_dev_and_other_model_agent_cannot_enter_stage1_evaluation(self):
        with self.assertRaises(ValueError):
            launch.evaluation_command('agents.deepseek_kira:AgentHarness', [runtime.split()['dev'][0]], 'test')
        with self.assertRaises(ValueError):
            launch.evaluation_command('agents.qwen_kira:AgentHarness', ['regex-log'], 'test')
        command = launch.evaluation_command('agents.deepseek_kira:AgentHarness', ['regex-log'], 'test')
        self.assertIn('openai/deepseek-v4-flash-0731', command)
        self.assertNotIn('--timeout-multiplier', command)
        self.assertIn(str(runtime.DATA / 'train'), command)


class EvidenceTests(unittest.TestCase):
    def fixture(self, runs):
        job = runs / 'finished'
        job.mkdir()
        (job / 'result.json').write_text(json.dumps({'finished_at': '2026-10-11T00:00:00Z'}))
        tasks = sorted(runtime.split()['train'])
        provenance = {'model': runtime.configuration()[0]['model'], 'split': 'train',
                      'task_ids': tasks, 'split_sha256': runtime.digest(runtime.SHARED / 'split-v1.json'),
                      'source_sha256': runtime.sources('agents.deepseek_kira:AgentHarness')}
        (runs / 'finished-provenance.json').write_text(json.dumps(provenance))
        for index, task in enumerate(tasks):
            trial = job / (task + '__synthetic')
            (trial / 'agent').mkdir(parents=True)
            (trial / 'verifier').mkdir()
            (trial / 'config.json').write_text(json.dumps({'task': {'path': str(runtime.DATA / 'train' / task)}}))
            result = {'finished_at': '2026-10-11T00:00:00Z',
                      'verifier_result': {'rewards': {'reward': None if index == 0 else 0}},
                      'exception_info': {'exception_type': 'SyntheticError'} if index == 0 else None,
                      'agent_result': None}
            (trial / 'result.json').write_text(json.dumps(result))
            (trial / 'agent/trajectory.json').write_text(json.dumps({'steps': [
                {'metrics': {'prompt_tokens': 10, 'completion_tokens': 2}}]}))
            (trial / 'verifier/secret.txt').write_text('SYNTHETIC_HIDDEN_SENTINEL')
        return job

    def test_export_keeps_failed_usage_excludes_grader_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            runs = Path(directory)
            self.fixture(runs)
            with patch.object(runtime, 'RUNS', runs), patch.object(export_train, 'RUNS', runs):
                with contextlib.redirect_stdout(io.StringIO()):
                    export_train.export('finished', 'evidence')
                evidence = runs / 'evidence'
                runtime.validate_evidence(evidence)
                summary = json.loads((evidence / 'summary.json').read_text())
                self.assertEqual(summary['denominator'], 30)
                self.assertEqual(summary['ungraded'], 1)
                self.assertEqual(summary['all_attempt_input_tokens_observed'], 300)
                self.assertEqual(summary['all_attempt_output_tokens_observed'], 60)
                self.assertTrue(summary['usage_is_lower_bound'])
                self.assertFalse(any('verifier' in p.parts for p in evidence.rglob('*')))
                self.assertFalse(any('SYNTHETIC_HIDDEN_SENTINEL' in p.read_text()
                                     for p in evidence.rglob('*') if p.is_file()))
                (evidence / 'summary.json').write_text('{}')
                with self.assertRaises(ValueError):
                    runtime.validate_evidence(evidence)

    def test_incomplete_run_is_rejected_before_creating_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            runs = Path(directory)
            job = self.fixture(runs)
            (job / 'result.json').write_text(json.dumps({'finished_at': None}))
            with patch.object(export_train, 'RUNS', runs):
                with self.assertRaises(ValueError):
                    export_train.export('finished', 'evidence')
            self.assertFalse((runs / 'evidence').exists())

    def test_optimizer_preview_neither_calls_provider_nor_writes_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            runs = Path(directory)
            self.fixture(runs)
            with patch.object(runtime, 'RUNS', runs), patch.object(export_train, 'RUNS', runs):
                with contextlib.redirect_stdout(io.StringIO()):
                    export_train.export('finished', 'evidence')
                candidate = runtime.HERE / 'agents/deepseek_candidate_preview_test.py'
                args = SimpleNamespace(evidence=runs / 'evidence', parent='agents.deepseek_kira',
                                       name='deepseek_candidate_preview_test', execute=False)
                with patch.object(propose.httpx, 'AsyncClient', side_effect=AssertionError('No API in preview')):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(asyncio.run(propose.propose(args)), 0)
                self.assertFalse(candidate.exists())
                self.assertFalse(any(p.name.startswith('deepseek-proposer-') for p in runs.iterdir()))

    def test_optimizer_tool_round_preserves_reasoning_and_fixed_model(self):
        with tempfile.TemporaryDirectory() as directory:
            runs = Path(directory) / 'runs'
            runs.mkdir()
            adaptation = Path(directory) / 'adaptation'
            (adaptation / 'agents').mkdir(parents=True)
            (adaptation / 'agents/deepseek_kira.py').write_text('class AgentHarness: pass\n')
            self.fixture(runs)
            requests = []
            candidate_source = 'from agents.deepseek_kira import AgentHarness as H0\nclass AgentHarness(H0):\n    pass\n'

            def provider(request):
                value = json.loads(request.content)
                requests.append(value)
                if len(requests) == 1:
                    message = {'role': 'assistant', 'content': None, 'reasoning_content': 'complete synthetic reasoning',
                               'tool_calls': [{'id': 'call1', 'type': 'function', 'function': {
                                   'name': 'write_candidate', 'arguments': json.dumps({'source': candidate_source})}}]}
                else:
                    message = {'role': 'assistant', 'content': 'Synthetic test completed'}
                return httpx.Response(200, json={'choices': [{'message': message, 'finish_reason': 'stop'}],
                                                 'usage': {'prompt_tokens': 5, 'completion_tokens': 2}})

            client = httpx.AsyncClient
            with patch.object(runtime, 'RUNS', runs), patch.object(export_train, 'RUNS', runs):
                with contextlib.redirect_stdout(io.StringIO()):
                    export_train.export('finished', 'evidence')
                args = SimpleNamespace(evidence=runs / 'evidence', parent='agents.deepseek_kira',
                                       name='deepseek_candidate_synthetic', execute=True)
                with patch.object(propose, 'RUNS', runs), patch.object(propose, 'HERE', adaptation), \
                        patch.dict(propose.os.environ, {'BAILIAN_API_KEY': 'synthetic',
                                   'BAILIAN_OPENAI_COMPATIBLE': 'https://synthetic.invalid/v1'}), \
                        patch.object(propose.httpx, 'AsyncClient',
                                     side_effect=lambda **kwargs: client(transport=httpx.MockTransport(provider), **kwargs)):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(asyncio.run(propose.propose(args)), 0)
                self.assertEqual(len(requests), 2)
                self.assertEqual(requests[1]['messages'][-2]['reasoning_content'], 'complete synthetic reasoning')
                self.assertEqual((adaptation / 'agents/deepseek_candidate_synthetic.py').read_text(), candidate_source)
                for request in requests:
                    self.assertEqual(request['model'], 'deepseek-v4-flash-0731')
                    self.assertTrue(request['enable_thinking'])
                    self.assertNotIn('max_tokens', request)


if __name__ == '__main__':
    unittest.main()
