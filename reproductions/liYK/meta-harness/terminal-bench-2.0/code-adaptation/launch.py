"""Prepare data or preview/run a fixed DeepSeek training evaluation."""
import argparse
import hashlib
import importlib.util
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone

from runtime import (BENCHMARK, DATA, EXAMPLE, HERE, RUNS, SHARED, agent_name,
                     configuration, digest, execution_env, sources, split)


def preparation():
    spec = importlib.util.spec_from_file_location('prepare_dataset', SHARED / 'prepare_dataset.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluation_command(agent, tasks, job):
    config, _ = configuration()
    agent_name(agent)
    if not tasks or len(tasks) != len(set(tasks)) or set(tasks) - set(split()['train']):
        raise ValueError('Evaluation accepts distinct training task IDs only')
    command = [str(BENCHMARK / '.venv/bin/harbor'), 'run', '--agent', agent,
               '-p', str(DATA / 'train'), '-m', 'openai/' + config['model'],
               '-e', config['environment'], '-n', str(config['concurrency']),
               '--n-attempts', str(config['attempts_per_task']),
               '--jobs-dir', str(RUNS), '--job-name', job]
    for task in tasks:
        command.extend(['-i', task])
    return command


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('prepare', help='Prepare/verify private dataset copies; no model calls')
    sub.add_parser('check', help='Verify policy, data, agent imports and Docker connectivity')
    evaluate = sub.add_parser('evaluate', help='Print command; --execute starts a new run')
    evaluate.add_argument('--agent', default='agents.deepseek_kira:AgentHarness')
    evaluate.add_argument('--tasks', nargs='+', help='Default: one train smoke task')
    evaluate.add_argument('--train', action='store_true', help='All 30 training tasks')
    evaluate.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    config, _ = configuration()
    if args.action == 'prepare':
        return subprocess.call([sys.executable, str(SHARED / 'prepare_dataset.py'),
                                '--source', str(SHARED / 'dataset'), '--output', str(DATA)])
    if args.action == 'check':
        prep = preparation()
        manifest = json.loads((DATA / 'dataset-manifest.json').read_text())
        if manifest['split_sha256'] != digest(SHARED / 'split-v1.json'):
            raise ValueError('Prepared split is stale')
        prep.verify_output(DATA, manifest)
        for agent in (config['h0'], config['historical_candidate']):
            agent_name(agent)
            subprocess.run([sys.executable, '-m', 'meta_harness', '--validate-agent', agent],
                           cwd=HERE, env=execution_env(), check=True)
        subprocess.run(['docker', 'info', '--format', '{{.ServerVersion}}'], check=True)
        print('PASS: fixed DeepSeek policy, 30/19/40 private data, both agents and Docker; no model calls')
        return 0
    if args.train and args.tasks:
        parser.error('--train and --tasks are mutually exclusive')
    tasks = sorted(split()['train']) if args.train else (args.tasks or [config['smoke_task']])
    job = 'deepseek-stage1-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    command = evaluation_command(args.agent, tasks, job)
    print(shlex.join(command), flush=True)
    if not args.execute:
        return 0
    # Fully verify prepared copies before any run; preserve native timeouts.
    prep = preparation()
    manifest = json.loads((DATA / 'dataset-manifest.json').read_text())
    if manifest['split_sha256'] != digest(SHARED / 'split-v1.json'):
        raise ValueError('Prepared split is stale')
    prep.verify_output(DATA, manifest)
    env = execution_env()
    if not all(env.get(key) for key in config['credential_env']):
        raise ValueError('Missing required credential environment variables')
    if not (BENCHMARK / '.venv/bin/harbor').is_file():
        raise ValueError('Install the documented benchmark virtual environment first')
    import importlib.metadata
    docker_info = json.loads(subprocess.check_output(
        ['docker', 'info', '--format', '{{json .}}'], env=env, text=True))
    provenance = {'model': config['model'], 'split': 'train', 'task_ids': sorted(tasks),
                  'command': command, 'source_sha256': sources(args.agent),
                  'runner_sha256': digest(HERE / 'launch.py'),
                  'split_sha256': digest(SHARED / 'split-v1.json'),
                  'task_sha256': {task: manifest['task_sha256'][task] for task in tasks},
                  'dependencies': {name: importlib.metadata.version(name) for name in
                                   ('harbor', 'litellm', 'tenacity', 'python-dotenv', 'httpx')},
                  'docker_host': env.get('DOCKER_HOST', 'default'),
                  'docker_resources': {key: docker_info.get(key) for key in
                                       ('NCPU', 'MemTotal', 'Architecture', 'ServerVersion')},
                  'provider_endpoint_sha256': hashlib.sha256(
                      env['BAILIAN_OPENAI_COMPATIBLE'].encode()).hexdigest(),
                  'actual_charge': None, 'optimization_cost_included': False}
    RUNS.mkdir(parents=True, exist_ok=True)
    (RUNS / (job + '-provenance.json')).write_text(json.dumps(provenance, indent=2) + '\n')
    with (RUNS / (job + '-console.log')).open('w') as output:
        return subprocess.call(command, cwd=HERE, env=env, stdout=output, stderr=subprocess.STDOUT)


if __name__ == '__main__':
    raise SystemExit(main())
