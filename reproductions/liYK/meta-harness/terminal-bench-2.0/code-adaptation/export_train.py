"""Freeze a finished 30-task train run for the DeepSeek optimizer.

Export scalar scores and agent trajectories only, never hidden verifier payloads.
Recovery selection is deliberately left to a separate documented review.
"""
import argparse
import json
import shutil
from pathlib import Path
from runtime import RUNS, SHARED, configuration, digest, split, validate_evidence


def export(job_name, output_name):
    job = RUNS / job_name
    if job.is_symlink() or job.resolve().parent != RUNS.resolve():
        raise ValueError('Job must be a direct personal run directory')
    job_result = json.loads((job / 'result.json').read_text())
    if not job_result.get('finished_at'):
        raise ValueError('Run is not finished')
    provenance = json.loads((RUNS / (job_name + '-provenance.json')).read_text())
    config, _ = configuration()
    allowed = sorted(split()['train'])
    if (provenance.get('model') != config['model'] or provenance.get('split') != 'train'
            or provenance['task_ids'] != allowed
            or provenance['split_sha256'] != digest(SHARED / 'split-v1.json')):
        raise ValueError('Only a complete fixed-model train run may be exported')
    rows, traces = [], []
    for trial in sorted(job.iterdir()):
        if not trial.is_dir():
            continue
        if trial.is_symlink():
            raise ValueError('Trial symlink is not allowed')
        task_config = json.loads((trial / 'config.json').read_text())
        task = Path(task_config['task']['path']).name
        if task not in allowed or any(row['task'] == task for row in rows):
            raise ValueError('Unexpected or repeated task; recovery requires independent review')
        result = json.loads((trial / 'result.json').read_text())
        if not result.get('finished_at'):
            raise ValueError('Trial has no terminal record')
        trace = trial / 'agent/trajectory.json'
        if trace.is_file() and (trace.is_symlink() or not trace.resolve().is_relative_to(trial.resolve())):
            raise ValueError('Trajectory escapes its trial')
        saved = json.loads(trace.read_text()) if trace.is_file() else {}
        agent = result.get('agent_result') or {}
        usage = {}
        for field, metric in [('n_input_tokens', 'prompt_tokens'), ('n_output_tokens', 'completion_tokens')]:
            trace_total = sum((step.get('metrics') or {}).get(metric) or 0 for step in saved.get('steps', []))
            usage[field] = max(agent.get(field) or 0, trace_total)
        usage['is_lower_bound'] = not all(agent.get(key) is not None for key in ('n_input_tokens', 'n_output_tokens'))
        rows.append({'task': task, 'trial': trial.name,
                     'reward': ((result.get('verifier_result') or {}).get('rewards') or {}).get('reward'),
                     'exception_type': (result.get('exception_info') or {}).get('exception_type'),
                     'usage': usage, 'finished_at': result['finished_at']})
        if trace.is_file():
            traces.append((task, trace))
    if sorted(row['task'] for row in rows) != allowed:
        raise ValueError('Missing training tasks')
    output = RUNS / output_name
    if output.resolve().parent != RUNS.resolve() or output.exists():
        raise ValueError('Evidence must be a new direct personal run directory')
    report = {'kind': 'stage1_train_evidence_v1', 'model': config['model'], 'split': 'train',
              'job': job_name, 'task_ids': allowed, 'denominator': 30,
              'successes': sum(row['reward'] == 1 for row in rows),
              'ungraded': sum(row['reward'] is None for row in rows),
              'all_attempt_input_tokens_observed': sum(row['usage']['n_input_tokens'] for row in rows),
              'all_attempt_output_tokens_observed': sum(row['usage']['n_output_tokens'] for row in rows),
              'usage_is_lower_bound': any(row['usage']['is_lower_bound'] for row in rows),
              'attempts': rows, 'actual_charge': None, 'source_sha256': provenance['source_sha256']}
    output.mkdir()
    (output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
    for task, trace in traces:
        target = output / 'tasks' / task
        target.mkdir(parents=True)
        shutil.copyfile(trace, target / 'trajectory.json')
    manifest = {**{key: report[key] for key in ('kind', 'model', 'task_ids', 'source_sha256')},
                'context_source_sha256': provenance['source_sha256'],
                'split_sha256': provenance['split_sha256'],
                'payload_sha256': {str(p.relative_to(output)): digest(p) for p in output.rglob('*') if p.is_file()}}
    (output / 'evidence-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    validate_evidence(output)
    print(json.dumps({'output': str(output), 'tasks': 30, 'successes': report['successes']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--job', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    export(args.job, args.output)
