"""Copy verified liYK frozen train evidence and actual execution sources.

This is data migration only. Source snapshots and scores keep their original
meaning; current optimizer context is fingerprinted separately.
"""
import argparse
import json
import shutil
from pathlib import Path
from runtime import RUNS, SHARED, configuration, digest, sources, split, validate_evidence


def import_history(source, output_name):
    if source.is_symlink():
        raise ValueError('Historical evidence symlink is not allowed')
    source = source.resolve()
    original_personal = source.parent.parent
    if (source.parent.name != 'runs' or original_personal.name != 'meta-harness'
            or original_personal.parent.name != 'liYK'):
        raise ValueError('Only liYK personal frozen evidence may be imported')
    manifest = json.loads((source / 'evidence-manifest.json').read_text())
    report = json.loads((source / 'summary.json').read_text())
    config, _ = configuration()
    if (manifest.get('kind') != 'frozen_train_evidence_v1'
            or not manifest.get('formal_comparison_eligible')
            or manifest['task_ids'] != sorted(split()['train'])
            or manifest['split_sha256'] != digest(SHARED / 'split-v1.json')
            or report.get('model') != config['model']):
        raise ValueError('Historical evidence must be the frozen complete DeepSeek train set')
    actual = {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}
    if actual != set(manifest['payload_sha256']) | {'evidence-manifest.json'}:
        raise ValueError('Unexpected historical evidence payload')
    for relative, expected in manifest['payload_sha256'].items():
        p = source / relative
        if p.is_symlink() or not p.resolve().is_relative_to(source) or digest(p) != expected:
            raise ValueError('Historical evidence has changed')
        if (relative != 'summary.json' and
                not (relative.startswith('tasks/') and p.name in ('trajectory.json', 'trial_summary.json'))):
            raise ValueError('Unapproved historical payload type')
    for relative, expected in manifest['source_sha256'].items():
        p = original_personal / relative
        if p.is_symlink() or not p.resolve().is_relative_to(original_personal) or digest(p) != expected:
            raise ValueError('Historical execution source has changed')
    output = RUNS / output_name
    if output.resolve().parent != RUNS.resolve() or output.exists():
        raise ValueError('Destination must be a new direct personal run directory')
    output.mkdir(parents=True)
    for relative in manifest['payload_sha256']:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / relative, target)
    for relative in manifest['source_sha256']:
        target = output / 'execution-sources' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original_personal / relative, target)
    origin = {'historical_manifest_sha256': digest(source / 'evidence-manifest.json'),
              'historical_jobs': report['jobs'], 'selection_rule': report['selection_rule'],
              'actual_execution_source_sha256': manifest['source_sha256'],
              'current_code_has_not_produced_historical_scores': True,
              'optimizer_context': 'current H0 source; actual execution source snapshots available separately',
              'model': report['model'], 'new_model_calls': 0, 'new_benchmark_trials': 0}
    (output / 'origin.json').write_text(json.dumps(origin, indent=2) + '\n')
    portable = {'kind': 'stage1_train_evidence_v1', 'model': report['model'],
                'task_ids': manifest['task_ids'], 'split_sha256': manifest['split_sha256'],
                'source_sha256': manifest['source_sha256'],
                'context_source_sha256': sources(config['h0']),
                'payload_sha256': {str(p.relative_to(output)): digest(p)
                                   for p in output.rglob('*') if p.is_file()}}
    (output / 'evidence-manifest.json').write_text(json.dumps(portable, indent=2) + '\n')
    validate_evidence(output)
    print(json.dumps({'output': str(output), 'tasks': len(portable['task_ids']),
                      'successes': report['successes'], 'new_trials': 0}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    import_history(args.source, args.output)
