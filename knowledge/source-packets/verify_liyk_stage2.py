"""Verify six current liYK base sources plus G-Memory, without executing upstream code."""
import argparse
import json
from pathlib import Path
import re
import urllib.request

from verify_liyk import PACKETS, compare_upstream, verify

HERE = Path(__file__).resolve().parent


def training_scope():
    """Check static-review membership, not the truth of no-training claims."""
    packets = ('reasoningbank-2509.25140', 'expel-2308.10144', 'agentrewind-2608.14380',
               'statefork-2609.38648', 'agentscope-2508.16279',
               'g-memory-2506.07398', 'agentdojo-2406.13352')
    errors, records = [], []
    for name in packets:
        data = json.loads((HERE / name / 'source-packet.json').read_text())
        mapping = json.loads((HERE / name / data['claim_evidence_map']).read_text())
        claims = {row['id']: row for row in mapping['claims']}
        review = data['selected_mechanism_training_review']
        selected = review['claim_ids']
        if len(selected) != len(set(selected)):
            errors.append(name + ': duplicate static-review identity')
        for uid in selected:
            if uid not in claims:
                errors.append(name + ': unknown selected claim: ' + uid)
        excluded = set(claims) - set(selected)
        if excluded != set(review.get('excluded_claim_ids', [])):
            errors.append(name + ': unrecorded or conflicting review exclusions')
        records.append({'packet': name, 'selected_claim_ids': selected,
                        'excluded_claim_ids': sorted(set(claims) - set(selected))})
    return {'packets': records, 'selected_claims': sum(len(row['selected_claim_ids']) for row in records),
            'excluded_claims': sum(len(row['excluded_claim_ids']) for row in records), 'errors': errors,
            'scope': 'Membership structure only; parameter-training semantics and team approval require review'}


def supplement(upstream=False, name='g-memory-2506.07398', selected_files=None):
    base = HERE / name
    data = json.loads((base / 'source-packet.json').read_text())
    paper, code = data['paper_version'], data['official_code_version']
    mapping = json.loads((base / data['claim_evidence_map']).read_text())
    errors = []
    revision = code['upstream_revision']
    if not re.fullmatch('[0-9a-f]{40}', revision):
        errors.append('Unpinned revision')
    if mapping['paper_version'] != paper['version']:
        errors.append('Paper version mismatch')
    if not (base / paper['pdf']).read_bytes().startswith(b'%PDF'):
        errors.append('Invalid PDF header')
    lines = (base / paper['text']).read_text().splitlines()
    pages = {int(m[1]): i + 1 for i, line in enumerate(lines) if (m := re.fullmatch(r'===== PDF p\.(\d+) =====', line))}
    ends = {page: pages.get(page + 1, len(lines) + 1) - 1 for page in pages}
    checked_ranges, comparisons = 0, []
    if len({claim['id'] for claim in mapping['claims']}) != len(mapping['claims']):
        errors.append('Duplicate claim IDs')
    for claim in mapping['claims']:
        if not claim.get('claim') or not claim.get('support_scope'):
            errors.append('Missing claim/support boundary')
        for anchor in claim['paper'].get('anchors', []):
            page = anchor['page']
            if page not in pages or not pages[page] <= anchor['text_line_start'] <= anchor['text_line_end'] <= ends[page]:
                errors.append('Paper page/range mismatch: ' + claim['id'])
        if not claim['paper'].get('anchors') and not claim['paper'].get('status'):
            errors.append('Missing paper boundary: ' + claim['id'])
        for anchor in claim['code_anchors']:
            path = base / anchor['file']
            if path.is_symlink() or not path.resolve().is_relative_to(base) or not path.is_file():
                errors.append('Invalid code path: ' + claim['id'])
                continue
            code_lines = path.read_text().splitlines()
            first, last = anchor['line_start'], anchor['line_end']
            if not 1 <= first <= last <= len(code_lines):
                errors.append('Code range mismatch: ' + claim['id'])
            elif not any(anchor['symbol'] in line for line in code_lines[first - 1:last]):
                errors.append('Code symbol mismatch: ' + claim['id'])
            relative = path.relative_to(base / code['local_path']).as_posix()
            expected = f'{code["repository"]}/blob/{revision}/{relative}#L{first}-L{last}'
            if anchor['fixed_url'] != expected:
                errors.append('Fixed URL mismatch: ' + claim['id'])
            checked_ranges += 1
    if upstream:
        repository = code['repository'].removeprefix('https://github.com/')
        if selected_files is None:
            selected_files = ('README.md', 'requirements.txt', 'mas/memory/mas_memory/GMemory.py', 'mas/memory/mas_memory/memory_base.py', 'mas/memory/common.py')
        for relative in selected_files:
            url = f'https://raw.githubusercontent.com/{repository}/{revision}/{relative}'
            row = {'file': relative, 'upstream_url': url}
            try:
                with urllib.request.urlopen(url, timeout=30) as response:
                    payload = response.read()
                row['status'] = 'equal' if (base / code['local_path'] / relative).read_bytes() == payload else 'different'
            except Exception as error:
                row.update(status='unknown', error=type(error).__name__ + ': ' + str(error))
            comparisons.append(row)
            if row['status'] != 'equal':
                errors.append('Upstream comparison failed: ' + relative)
    return {'packet': base.name, 'claims_checked': len(mapping['claims']),
            'code_ranges_checked': checked_ranges, 'errors': errors, 'upstream_files': comparisons,
            'human_review': 'pending', 'upstream_execution': 'not performed', 'h0_transfer': 'not performed'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', action='store_true')
    parser.add_argument('--current', action='store_true', help='Explicitly select the current seven-source scope (also the default); historical results remain in saved records')
    args = parser.parse_args()
    dojo_files = ('README.md', 'src/agentdojo/agent_pipeline/base_pipeline_element.py',
                  'src/agentdojo/agent_pipeline/agent_pipeline.py', 'src/agentdojo/agent_pipeline/tool_execution.py',
                  'src/agentdojo/agent_pipeline/pi_detector.py')
    result = {'foundation': verify(PACKETS[:-1]), 'supplement': supplement(args.upstream),
              'other_supplements': [supplement(args.upstream, 'agentdojo-2406.13352', dojo_files)],
              'selected_training_review': training_scope(),
              'scope': 'current six base sources plus G-Memory',
              'historical_reference_date': '2026-10-13'}
    if args.upstream:
        result['foundation']['upstream_content_comparison'] = compare_upstream(PACKETS[:-1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    remote = result['foundation'].get('upstream_content_comparison', {})
    raise SystemExit(bool(result['foundation']['errors'] or result['supplement']['errors']
                          or result['selected_training_review']['errors']
                          or any(row['errors'] for row in result['other_supplements'])
                          or remote.get('different') or remote.get('unknown')))
