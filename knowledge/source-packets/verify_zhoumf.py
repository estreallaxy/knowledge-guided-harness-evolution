"""校验 zhouMF 负责的 5 个 SourcePacket：结构、论文文本分页标记、代码行号锚点与凭据泄漏。

不联网、不执行上游代码。用法：python3 verify_zhouMF.py
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKETS = (
    'agent-skill-induction-2504.06821',
    'acon-2510.00615',
    'agentfold-2510.24699',
    'frugalgpt-2305.05176',
    'routellm-2406.18665',
)
REQUIRED_FIELDS = ('paper_version', 'official_code_version', 'exact_source_anchors',
                   'configs_and_examples', 'tests_and_reported_results')
PAPER_FIELDS = ('id', 'title', 'direction', 'version', 'published', 'authors', 'url', 'pdf', 'text')
CODE_FIELDS = ('repository', 'upstream_revision', 'retrieved_on', 'local_path',
               'snapshot_scope', 'license_status')
ANCHOR = re.compile(r'`([A-Za-z0-9_./-]+\.(?:py|sh|json|ya?ml))\s*:\s*(\d+)`')
SECRET_NAMES = {'.env', '.env.local'}


def verify_packet(name: str) -> dict:
    base = HERE / name
    errors, code_anchors, docs = [], 0, 0

    if not base.is_dir():
        return {'packet': name, 'errors': ['缺少目录'], 'code_anchors_checked': 0, 'docs_checked': 0}

    packet_file = base / 'source-packet.json'
    if not packet_file.is_file():
        return {'packet': name, 'errors': ['缺少 source-packet.json'],
                'code_anchors_checked': 0, 'docs_checked': 0}
    try:
        data = json.loads(packet_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        return {'packet': name, 'errors': [f'source-packet.json 解析失败: {exc}'],
                'code_anchors_checked': 0, 'docs_checked': 0}

    for field in REQUIRED_FIELDS:
        if not data.get(field):
            errors.append(f'缺少字段: {field}')
    paper = data.get('paper_version') or {}
    for field in PAPER_FIELDS:
        if not paper.get(field):
            errors.append(f'paper_version 缺字段: {field}')
    code = data.get('official_code_version') or {}
    for field in CODE_FIELDS:
        if not code.get(field):
            errors.append(f'official_code_version 缺字段: {field}')
    if code.get('upstream_revision') and len(str(code['upstream_revision'])) != 40:
        errors.append('upstream_revision 不是 40 位 commit')

    pdf = base / str(paper.get('pdf', ''))
    text = base / str(paper.get('text', ''))
    if not pdf.is_file():
        errors.append(f'缺少论文 PDF: {paper.get("pdf")}')
    elif not pdf.read_bytes().startswith(b'%PDF'):
        errors.append(f'PDF 头无效: {paper.get("pdf")}')
    if not text.is_file():
        errors.append(f'缺少论文文本: {paper.get("text")}')
    elif not re.search(r'^--- PDF page \d+ ---$', text.read_text(encoding='utf-8', errors='replace'), re.M):
        errors.append(f'论文文本缺少分页标记: {paper.get("text")}')

    for field in ('exact_source_anchors', 'configs_and_examples', 'tests_and_reported_results'):
        path = base / str(data.get(field, ''))
        if not path.is_file() or not path.read_text(encoding='utf-8').strip():
            errors.append(f'缺少或为空的说明文件: {field}')
        else:
            docs += 1

    local_code = base / str(code.get('local_path') or 'official-code')
    code_files = [p for p in local_code.rglob('*') if p.is_file()] if local_code.is_dir() else []
    if not code_files:
        errors.append('official-code/ 为空或不存在')
    for path in code_files:
        if path.name in SECRET_NAMES or path.suffix in {'.pem', '.key'}:
            errors.append(f'疑似凭据文件: {path.relative_to(base)}')

    anchors_file = base / str(data.get('exact_source_anchors', ''))
    if anchors_file.is_file():
        for relative, line in ANCHOR.findall(anchors_file.read_text(encoding='utf-8')):
            path = local_code / relative
            code_anchors += 1
            if not path.is_file():
                errors.append(f'锚点文件不存在: {relative}')
            elif int(line) > len(path.read_text(encoding='utf-8', errors='replace').splitlines()):
                errors.append(f'锚点行号越界: {relative}:{line}')

    return {'packet': name, 'direction': paper.get('direction'), 'errors': errors,
            'code_anchors_checked': code_anchors, 'docs_checked': docs,
            'official_code_files': len(code_files)}


def main() -> int:
    rows = [verify_packet(name) for name in PACKETS]
    result = {
        'packets': rows,
        'packets_checked': len(rows),
        'code_anchors_checked': sum(row['code_anchors_checked'] for row in rows),
        'errors': sum(len(row['errors']) for row in rows),
        'upstream_execution': '未知/未完成',
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
