"""Fixed DeepSeek proposer with train-only file tools and persistent raw history.

Only explicit training artifacts are exposed. No shell tool, secrets, test data,
or benchmark verifier files are available to the proposer. This implements the
read-history/write-candidate part; candidate evaluation is a separate Harbor run.
"""
import argparse
import ast
import asyncio
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from runtime import (BENCHMARK, EXAMPLE, HERE, RUNS, configuration, digest, split, validate_evidence)

class ArtifactTools:
    def __init__(self, history: Path, candidate: Path, family='deepseek', parent='agents.deepseek_kira'):
        self.candidate = candidate
        self.files = {}
        self.files['source/agents/baseline_kira.py'] = EXAMPLE / 'agents/baseline_kira.py'
        self.files['source/prompt-templates/terminus-kira.txt'] = EXAMPLE / 'prompt-templates/terminus-kira.txt'
        for name in ('agents/bailian_kira.py', 'agents/deepseek_kira.py'):
            self.files['source/' + name] = HERE / name
        if parent != 'agents.deepseek_kira':
            self.files['source/' + parent.replace('.', '/') + '.py'] = HERE / (parent.replace('.', '/') + '.py')
        # History is a specific training job, not the entire runs directory.
        for path in history.rglob('*'):
            if (path.is_file() and not path.is_symlink()
                    and path.suffix in ('.json', '.txt', '.log')
                    and path.name not in ('config.json', 'exception.txt')
                    and 'verifier' not in path.parts):
                self.files['history/' + path.relative_to(history).as_posix()] = path

    def call(self, name, arguments):
        if name == 'list_files':
            return sorted(self.files)
        if name == 'read_file':
            path = self.files[arguments['path']]
            lines = path.read_text(errors='replace').splitlines()
            start = max(1, int(arguments.get('start_line', 1)))
            count = max(1, min(400, int(arguments.get('line_count', 200))))
            return {'total_lines': len(lines), 'text': '\n'.join(
                f'{i+start}: {line}' for i, line in enumerate(lines[start-1:start-1+count]))}
        if name == 'write_candidate':
            source = arguments['source']
            tree = ast.parse(source)
            if not any(isinstance(node, ast.ClassDef) and node.name == 'AgentHarness' for node in tree.body):
                raise ValueError('Candidate must define AgentHarness')
            # Reject memorized task identifiers; general mechanisms only.
            partition = split()
            if any(task in source for group in ('train', 'dev', 'test') for task in partition[group]):
                raise ValueError('Candidate contains a benchmark task identifier')
            if len(source.encode()) > 262144:
                raise ValueError('Candidate source is unexpectedly large')
            self.candidate.write_text(source)
            return {'written': self.candidate.name, 'syntax_valid': True}
        raise ValueError('Unknown tool')


def tool(name, description, properties, required):
    return {'type': 'function', 'function': {'name': name, 'description': description,
        'parameters': {'type': 'object', 'properties': properties, 'required': required}}}


TOOLS = [
    tool('list_files', 'List all available source and training history files.', {}, []),
    tool('read_file', 'Read a file in numbered pages. Continue reading as needed.',
         {'path': {'type': 'string'}, 'start_line': {'type': 'integer'}, 'line_count': {'type': 'integer'}}, ['path']),
    tool('write_candidate', 'Save the candidate Python file; may revise it later.',
         {'source': {'type': 'string'}}, ['source']),
]


async def propose(args):
    family = 'deepseek'
    config, policy = configuration()
    history = args.evidence.resolve()
    manifest = validate_evidence(history)
    parent = args.parent
    if parent != 'agents.deepseek_kira' and not re.fullmatch(r'agents\.deepseek_candidate_[a-z0-9_]+', parent):
        raise ValueError('Parent must be a personal DeepSeek agent')
    if not (HERE / (parent.replace('.', '/') + '.py')).is_file():
        raise ValueError('Parent source is missing')
    parent_key = BENCHMARK.name + '/code-adaptation/' + parent.replace('.', '/') + '.py'
    if parent_key not in manifest['context_source_sha256']:
        raise ValueError('Parent source is not part of the frozen optimizer context')
    candidate = HERE / 'agents' / (args.name + '.py')
    if candidate.exists():
        raise ValueError('Refusing to overwrite an existing candidate')
    if not args.execute:
        print(json.dumps({'action': 'preview_only', 'model': policy['model'],
                          'evidence': str(history), 'candidate': str(candidate),
                          'optimizer_timeout_seconds': 2400}, indent=2))
        return 0
    credentials = {key: os.environ.get(key) for key in config['credential_env']}
    if not all(credentials.values()):
        raise ValueError('Missing required credential environment variables')
    run = RUNS / ('deepseek-proposer-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    run.mkdir(parents=True)
    formal = True
    access = ArtifactTools(history, candidate, family, parent)
    messages = [{'role': 'system', 'content': (
        'You are a harness optimization coding agent. Inspect the available source, scores, '
        'and complete execution history using file tools; diagnose general failure modes or '
        'efficiency opportunities. Write one modest reusable candidate as a Python subclass '
        f'of {parent}.AgentHarness. Preserve provider, model, thinking, time limits, '
        'and complete reasoning_content for tool-call continuation. '
        'Hard constraint: never remove, truncate, replace, or filter reasoning_content '
        'from outbound requests or stored messages. Do not propose reasoning-history '
        'pruning. This field is provider-specific and may be required on inbound '
        'tool continuations; being absent from the base OpenAI schema does not make '
        'it response-only. Also, zero cache counts in Harbor do not prove no API '
        'caching: the usage extractor may not support this provider. '
        'tool schema, and grading boundaries. Do not hardcode task names, answers, or '
        'task-specific solutions. Do not read secrets or modify the environment or evaluator. '
        'You may add generic prompt or control-flow improvements. If no supported improvement '
        'exists, explain that honestly; do not manufacture one. After saving, summarize your '
        'hypothesis and expected benefit. '
        + ('This is the bounded formal search on all 30 training tasks; consider failure '
           'patterns across tasks and avoid fitting one trace. Read summary.json and '
           'inspect complete relevant trajectories in pages. Score improvements are '
           'unproven until independent evaluation. '
           if formal else 'This is a single-task infrastructure pilot, not evidence of general improvement. ')
        + 'You have at most 40 minutes total, including API waits.')},
        {'role': 'user', 'content': 'Inspect the training evidence and write one candidate if justified. Start by listing the available files.'}]
    report = {'model': policy['model'], 'deadline_seconds': 2400, 'history': str(history),
              'candidate': str(candidate), 'status': 'running', 'usage': [], 'cost_status': 'unpriced',
              'scope': 'formal_train' if formal else 'single_task_pilot', 'parent': parent,
              'request_errors': [],
              'evidence_manifest_sha256': digest(history / 'evidence-manifest.json'),
              'context_source_sha256': manifest['context_source_sha256'],
              'optimizer_source_sha256': digest(Path(__file__)),
              'actual_charge': None}
    started = time.monotonic()
    events = run / 'events.jsonl'
    def log(event):
        with events.open('a') as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + '\n')
    async def loop():
        async with httpx.AsyncClient(timeout=2400) as client:
            while True:
                for retry_index in range(5):
                    try:
                        response = await client.post(credentials['BAILIAN_OPENAI_COMPATIBLE'].rstrip('/') + '/chat/completions',
                            headers={'Authorization': 'Bearer ' + credentials['BAILIAN_API_KEY']},
                            json={'model': policy['model'], 'messages': messages, 'tools': TOOLS,
                                  'enable_thinking': policy['enable_thinking']})
                        response.raise_for_status()
                        break
                    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                        status = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None
                        if status is not None and status != 429 and status < 500:
                            raise
                        event = {'type': 'request_error', 'error_type': type(exc).__name__,
                                 'http_status': status, 'retry_index': retry_index}
                        log(event)
                        report['request_errors'].append(event)
                        if retry_index == 4:
                            raise
                        await asyncio.sleep(min(60, 10 * 2 ** retry_index))
                result = response.json()
                choice = result['choices'][0]
                msg = choice['message']
                log({'type': 'response', 'response': result})
                report['usage'].append(result.get('usage', {}))
                if choice['finish_reason'] == 'length':
                    raise ValueError('Provider output limit reached')
                messages.append(msg)
                if not msg.get('tool_calls'):
                    report['summary'] = msg.get('content')
                    report['status'] = 'candidate_ready' if candidate.exists() else 'no_candidate'
                    return
                for call in msg['tool_calls']:
                    try:
                        value = access.call(call['function']['name'], json.loads(call['function']['arguments']))
                    except (ValueError, KeyError, TypeError, SyntaxError) as exc:
                        value = {'error': type(exc).__name__}
                    log({'type': 'tool', 'name': call['function']['name'], 'result': value})
                    messages.append({'role': 'tool', 'tool_call_id': call['id'], 'content': json.dumps(value, ensure_ascii=False)})
    try:
        await asyncio.wait_for(loop(), timeout=config['optimizer_timeout_seconds'])
    except asyncio.TimeoutError:
        report['status'] = 'timed_out'
    except Exception as exc:
        report['status'] = 'failed'
        report['error_type'] = type(exc).__name__
    report['elapsed_seconds'] = round(time.monotonic() - started, 2)
    (run / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'run': str(run), **report}, ensure_ascii=False, indent=2))
    return 0 if report['status'] in ('candidate_ready', 'no_candidate') else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--parent', default='agents.deepseek_kira')
    parser.add_argument('--name', required=True)
    parser.add_argument('--execute', action='store_true', help='Call the model; default is preview only')
    args = parser.parse_args()
    if not re.fullmatch(r'deepseek_candidate_[a-z0-9_]+', args.name):
        parser.error('Candidate name must use deepseek_candidate_ followed by lowercase letters/digits/underscores')
    raise SystemExit(asyncio.run(propose(args)))
