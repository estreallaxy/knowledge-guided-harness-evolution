"""Verify six liYK pinned SourcePackets without model or upstream execution."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import re
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
PACKETS = ('reasoningbank-2509.25140', 'expel-2308.10144', 'agentrewind-2608.14380',
           'statefork-2609.38648', 'agentscope-2508.16279', 'nora-2605.02092')


def verify(packets=PACKETS):
    result = []
    for name in packets:
        base = HERE / name
        data = json.loads((base / 'source-packet.json').read_text())
        errors, count, claim_count, range_count = [], 0, 0, 0
        fields = ('paper_version', 'official_code_version', 'exact_source_anchors',
                  'configs_and_examples', 'tests_and_reported_results')
        for field in fields:
            if not data.get(field):
                errors.append('Missing field: ' + field)
        paper = data['paper_version']
        if not paper.get('authors') or not paper.get('published_at') or not paper.get('source_url'):
            errors.append('Incomplete paper metadata')
        files = [paper['local_pdf'], paper['local_text']]
        for upstream in data['official_code_version']:
            if len(upstream.get('revision', '')) != 40 or not upstream.get('scope'):
                errors.append('Unpinned/unspecified code revision')
            files.extend(entry['file'] for entry in upstream['files'])
        for relative in files:
            path = base / relative
            count += 1
            if (path.is_symlink() or not path.resolve().is_relative_to(base)
                    or not path.is_file() or not path.stat().st_size):
                errors.append('Missing, empty or escaped payload: ' + relative)
        for field in ('exact_source_anchors', 'configs_and_examples', 'tests_and_reported_results'):
            path = base / data[field]
            if not path.is_file() or not path.read_text().strip():
                errors.append('Missing explanation: ' + field)
        for anchor in data.get('code_symbol_anchors', []):
            lines = (base / anchor['file']).read_text().splitlines()
            line = anchor['line']
            if line < 1 or line > len(lines) or anchor['symbol'] not in lines[line - 1]:
                errors.append('Code symbol anchor mismatch: ' + anchor['symbol'])
        for field in ('mechanism_and_boundaries', 'claim_evidence_map'):
            relative = data.get(field)
            if not relative or not (base / relative).is_file():
                errors.append('Missing mechanism evidence: ' + field)
        map_path = base / data.get('claim_evidence_map', 'claim-evidence-map.json')
        if map_path.is_file():
            mapping = json.loads(map_path.read_text())
            if mapping.get('paper_version') != paper['version']:
                errors.append('Claim map paper version mismatch')
            text_lines = (base / paper['local_text']).read_text().splitlines()
            starts = {int(match[1]): index + 1 for index, line in enumerate(text_lines)
                      if (match := re.fullmatch(r'--- PDF page (\d+) ---', line))}
            ends = {page: starts.get(page + 1, len(text_lines) + 1) - 1 for page in starts}
            claims = mapping.get('claims', [])
            claim_count = len(claims)
            if not claims or len({claim['id'] for claim in claims}) != claim_count:
                errors.append('Missing or duplicate claims')
            for claim in claims:
                if not claim.get('claim') or not claim.get('support_scope'):
                    errors.append('Missing claim or support scope: ' + claim['id'])
                origin = claim.get('paper', {})
                anchors = origin.get('anchors', [origin] if 'page' in origin else [])
                for anchor in anchors:
                    page = anchor['page']
                    if (origin.get('pdf') != paper['local_pdf']
                            or origin.get('text') != paper['local_text']
                            or page not in starts
                            or not starts[page] <= anchor['text_line_start']
                            <= anchor['text_line_end'] <= ends[page]):
                        errors.append('Paper range/page mismatch: ' + claim['id'])
                if not anchors and not origin.get('status'):
                    errors.append('Missing paper evidence boundary: ' + claim['id'])
                code_anchors = list(claim.get('code_anchors', []))
                if 'file' in claim.get('code', {}):
                    code_anchors.append(claim['code'])
                for anchor in code_anchors:
                    relative = anchor['file']
                    path = base / relative
                    upstreams = [upstream for upstream in data['official_code_version']
                                 if any(entry['file'] == relative for entry in upstream['files'])]
                    if (len(upstreams) != 1 or path.is_symlink()
                            or not path.resolve().is_relative_to(base) or not path.is_file()):
                        errors.append('Unpinned claim code: ' + claim['id'])
                        continue
                    lines = path.read_text().splitlines()
                    first, last = anchor['line_start'], anchor['line_end']
                    if not 1 <= first <= last <= len(lines):
                        errors.append('Invalid claim code range: ' + claim['id'])
                        continue
                    upstream = upstreams[0]
                    repository = upstream['repository'].removeprefix('https://github.com/').removesuffix('.git')
                    expected_url = (f'https://github.com/{repository}/blob/{upstream["revision"]}/'
                                    f'{relative.split("/", 2)[2]}#L{first}-L{last}')
                    if anchor['fixed_url'] != expected_url:
                        errors.append('Claim fixed URL mismatch: ' + claim['id'])
                    if anchor.get('symbol') and not any(anchor['symbol'] in line for line in lines[first - 1:last]):
                        errors.append('Claim symbol missing from code range: ' + claim['id'])
                    range_count += 1
                if (not code_anchors and not claim.get('code_status')
                        and not claim.get('code', {}).get('status')):
                    errors.append('Missing code evidence boundary: ' + claim['id'])
            for relation in mapping.get('relations', []):
                if not (HERE / relation['other'] / 'source-packet.json').is_file():
                    errors.append('Missing related source: ' + relation['other'])
        if not (base / paper['local_pdf']).read_bytes().startswith(b'%PDF'):
            errors.append('Invalid PDF header')
        result.append({'packet': name, 'direction': data['direction'], 'pinned_payloads_checked': count,
                       'symbol_anchors_checked': len(data.get('code_symbol_anchors', [])),
                       'claims_checked': claim_count, 'claim_code_ranges_checked': range_count,
                       'errors': errors, 'upstream_execution': 'not performed / unknown',
                       'team_review': data['validation']['team_review_status']})
    return {'packets': result, 'payloads_checked': sum(row['pinned_payloads_checked'] for row in result),
            'claims_checked': sum(row['claims_checked'] for row in result),
            'claim_code_ranges_checked': sum(row['claim_code_ranges_checked'] for row in result),
            'errors': sum(len(row['errors']) for row in result), 'new_model_calls': 0}


def compare_upstream(packets=PACKETS):
    """Compare selected payload bytes against pinned upstream Git files, without digests."""
    entries = []
    for name in packets:
        base = HERE / name
        data = json.loads((base / 'source-packet.json').read_text())
        for upstream in data['official_code_version']:
            repository = upstream['repository'].removeprefix('https://github.com/').removesuffix('.git')
            for entry in upstream['files']:
                relative = entry.get('upstream_path') or entry['file'].split('/', 2)[2]
                url = f'https://raw.githubusercontent.com/{repository}/{upstream["revision"]}/{relative}'
                entries.append((name, base / entry['file'], url))

    def compare(entry):
        name, path, url = entry
        row = {'packet': name, 'file': str(path.relative_to(HERE / name)), 'upstream_url': url}
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = response.read()
            row['status'] = 'equal' if path.read_bytes() == payload else 'different'
        except Exception as error:
            row.update(status='unknown', error=type(error).__name__ + ': ' + str(error))
        return row

    with ThreadPoolExecutor(max_workers=6) as pool:
        rows = list(pool.map(compare, entries))
    return {'files': rows, 'equal': sum(row['status'] == 'equal' for row in rows),
            'different': sum(row['status'] == 'different' for row in rows),
            'unknown': sum(row['status'] == 'unknown' for row in rows),
            'scope': 'Selected official code bytes only; no model calls or upstream execution'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', action='store_true', help='Also compare selected bytes with fixed Git revisions')
    args = parser.parse_args()
    result = verify()
    if args.upstream:
        result['upstream_content_comparison'] = compare_upstream()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    remote = result.get('upstream_content_comparison', {})
    raise SystemExit(bool(result['errors'] or remote.get('different') or remote.get('unknown')))
