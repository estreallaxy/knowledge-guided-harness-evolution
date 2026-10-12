"""Personal, train-only runtime paths and immutable evidence checks."""
import hashlib
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK = HERE.parent
PERSONAL = BENCHMARK.parent
REPOSITORY = BENCHMARK.parents[3]
EXAMPLE = PERSONAL / 'code/reference_examples/terminal_bench_2'
SHARED = REPOSITORY / 'benchmarks/terminal-bench-2.0'
RUNS = BENCHMARK / 'runs'
DATA = BENCHMARK / 'data/tb2-split-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configuration():
    config = json.loads((BENCHMARK / 'configs/launch.json').read_text())
    policy = json.loads((BENCHMARK / 'configs' / config['policy']).read_text())
    if config['model'] != 'deepseek-v4-flash-0731' or policy['model'] != config['model']:
        raise ValueError('Execution and optimization must use the fixed DeepSeek model')
    if (config['split'] != 'train' or config['attempts_per_task'] != 1
            or config['concurrency'] != 1 or config['optimizer_timeout_seconds'] != 2400
            or config['task_timeout'] != 'benchmark_native'
            or config['output_and_thinking_token_cap'] is not None
            or policy['enable_thinking'] is not True
            or policy['socket_timeout_seconds'] != 2400):
        raise ValueError('Launch configuration differs from the recorded stage-one conditions')
    return config, policy


def split():
    value = json.loads((SHARED / 'split-v1.json').read_text())
    groups = [value[key] for key in ('train', 'dev', 'test')]
    if [len(x) for x in groups] != [30, 19, 40] or len(set(sum(groups, []))) != 89:
        raise ValueError('Invalid frozen task partition')
    return value


def agent_name(value):
    if value != 'agents.deepseek_kira:AgentHarness' and not re.fullmatch(
            r'agents\.deepseek_candidate_[a-z0-9_]+:AgentHarness', value):
        raise ValueError('Only the fixed DeepSeek H0 or a personal candidate is allowed')
    if not (HERE / value.split(':')[0].replace('.', '/')).with_suffix('.py').is_file():
        raise ValueError('Missing personal agent module')
    return value


def sources(agent):
    paths = [EXAMPLE / 'agents/baseline_kira.py', EXAMPLE / 'anthropic_caching.py',
             EXAMPLE / 'prompt-templates/terminus-kira.txt',
             HERE / 'agents/__init__.py', HERE / 'agents/bailian_kira.py',
             HERE / 'agents/deepseek_kira.py', HERE / agent.split(':')[0].replace('.', '/'),
             BENCHMARK / 'configs/deepseek-api.json', BENCHMARK / 'configs/launch.json']
    paths[-3] = paths[-3].with_suffix('.py')
    # Preserve the full inheritance chain of a generated personal candidate.
    import ast
    pending = list(paths)
    known = set(paths)
    while pending:
        path = pending.pop()
        if path.suffix != '.py':
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and (node.module or '').startswith('agents.deepseek_candidate_'):
                ancestor = (HERE / node.module.replace('.', '/')).with_suffix('.py')
                if ancestor not in known:
                    known.add(ancestor)
                    paths.append(ancestor)
                    pending.append(ancestor)
    return {str(p.relative_to(PERSONAL)): digest(p) for p in set(paths)}


def execution_env():
    env = dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join((str(HERE), str(EXAMPLE)))
    env['LITELLM_LOG'] = 'ERROR'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def validate_evidence(directory, check_sources=True):
    if directory.is_symlink():
        raise ValueError('Evidence symlink is not allowed')
    directory = directory.resolve()
    if not directory.is_relative_to(RUNS.resolve()) or directory.is_symlink():
        raise ValueError('Evidence must be inside this benchmark personal runs directory')
    manifest = json.loads((directory / 'evidence-manifest.json').read_text())
    config, _ = configuration()
    if (manifest.get('kind') != 'stage1_train_evidence_v1'
            or manifest['model'] != config['model']
            or manifest['task_ids'] != sorted(split()['train'])
            or manifest['split_sha256'] != digest(SHARED / 'split-v1.json')):
        raise ValueError('Evidence is not the complete fixed DeepSeek training set')
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    if actual != set(manifest['payload_sha256']) | {'evidence-manifest.json'}:
        raise ValueError('Unexpected or missing evidence payload')
    for relative, expected in manifest['payload_sha256'].items():
        p = directory / relative
        if p.is_symlink() or not p.resolve().is_relative_to(directory) or digest(p) != expected:
            raise ValueError('Evidence payload changed or escaped')
    if check_sources:
        if not manifest.get('context_source_sha256'):
            raise ValueError('Missing optimizer context source fingerprints')
        for relative, expected in manifest['context_source_sha256'].items():
            p = PERSONAL / relative
            if p.is_symlink() or not p.resolve().is_relative_to(PERSONAL) or digest(p) != expected:
                raise ValueError('Evidence execution source changed')
    return manifest
