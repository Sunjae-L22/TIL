#!/usr/bin/env python3
"""Page-level PDF preparation and honest reading coverage. Python stdlib + Poppler."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    os.replace(tmp, path)


def pages(spec, total):
    if not spec:
        return list(range(1, total + 1))
    out = set()
    for part in spec.split(','):
        m = re.fullmatch(r'(\d+)(?:-(\d+))?', part.strip())
        if not m:
            raise ValueError('Invalid page range: ' + part)
        a, b = int(m[1]), int(m[2] or m[1])
        if a < 1 or b > total or a > b:
            raise ValueError('Page range outside source: ' + part)
        out.update(range(a, b + 1))
    return sorted(out)


def run(args):
    try:
        return subprocess.run(args, capture_output=True, check=True, timeout=120).stdout
    except FileNotFoundError:
        raise ValueError('Missing Poppler tool: ' + args[0]) from None


def load(workdir):
    root = Path(workdir).resolve()
    data = json.loads((root / 'manifest.json').read_text())
    if digest(data['source']['path']) != data['source']['sha256']:
        raise ValueError('Source changed. Prepare in a new workdir; old reading evidence is stale.')
    return root, data


def prepare(args):
    src, root = Path(args.pdf).resolve(), Path(args.workdir).resolve()
    info = run(['pdfinfo', str(src)]).decode()
    total = int(re.search(r'^Pages:\s+(\d+)', info, re.M)[1])
    selected = pages(args.pages, total)
    fingerprint = digest(src)
    manifest = root / 'manifest.json'
    if manifest.exists():
        _, data = load(root)
        if data['source']['sha256'] != fingerprint:
            raise ValueError('Workdir belongs to a different source. Choose another workdir.')
    else:
        data = {'version': 1, 'source': {'path': str(src), 'sha256': fingerprint,
                'pages': total}, 'selected_pages': [], 'pages': {}, 'created_at': now()}
    data['selected_pages'] = sorted(set(data['selected_pages']) | set(selected))
    (root / 'extracted').mkdir(parents=True, exist_ok=True)
    for n in selected:
        key = str(n)
        text_file = root / 'extracted' / f'{n:04}.txt'
        prior = data['pages'].get(key, {})
        if not (text_file.exists() and digest(text_file) == prior.get('text_sha256')):
            text_file.write_bytes(run(['pdftotext', '-f', str(n), '-l', str(n), '-layout', str(src), '-']))
        text = text_file.read_text()
        data['pages'][key] = {**prior, 'text_path': str(text_file.relative_to(root)),
            'text_sha256': digest(text_file), 'text_chars': len(text.strip()),
            'status': prior.get('status', 'extracted'),
            'reading_method': prior.get('reading_method'),
            'suggested_route': 'text-plus-visual' if len(text.strip()) >= 40 else 'visual'}
        write(manifest, data)
    return {'workdir': str(root), 'source_pages': total, 'selected_pages': selected,
            'visual_candidates': [n for n in selected if data['pages'][str(n)]['text_chars'] < 40]}


def render(args):
    root, data = load(args.workdir)
    chosen = pages(args.pages, data['source']['pages'])
    if not set(chosen) <= set(data['selected_pages']):
        raise ValueError('Prepare these pages before rendering them.')
    folder = root / 'pages'
    folder.mkdir(exist_ok=True)
    out = []
    for n in chosen:
        target = folder / f'{n:04}.png'
        prior = data['pages'][str(n)]
        cached = (target.exists() and prior.get('render_width') == args.width
                  and prior.get('image_sha256') == digest(target))
        if not cached:
            run(['pdftoppm', '-f', str(n), '-l', str(n), '-singlefile', '-scale-to-x',
                 str(args.width), '-scale-to-y', '-1', '-png', data['source']['path'], str(target.with_suffix(''))])
        prior.update(image_path=str(target.relative_to(root)), image_sha256=digest(target), render_width=args.width)
        write(root / 'manifest.json', data)
        out.append(str(target))
    return {'images': out}


def record(args):
    root, data = load(args.workdir)
    chosen = pages(args.pages, data['source']['pages'])
    if not set(chosen) <= set(data['selected_pages']):
        raise ValueError('Cannot mark unprepared pages.')
    if not args.note.strip():
        raise ValueError('Record what was checked or why a page was skipped/unresolved.')
    for n in chosen:
        item = data['pages'][str(n)]
        if args.status == 'covered' and args.method == 'text' and item['text_chars'] < 40:
            raise ValueError(f'Page {n} has little extracted text; inspect visually or record OCR.')
        if args.method == 'visual' and not item.get('image_path'):
            raise ValueError(f'Page {n} has no rendered image.')
    for n in chosen:
        data['pages'][str(n)].update(status=args.status, reading_method=args.method,
                                     note=args.note, reviewed_at=now())
    write(root / 'manifest.json', data)
    return {'recorded_pages': chosen, 'status': args.status}


def check(args):
    root, data = load(args.workdir)
    unfinished, corrupt, skipped = [], [], []
    for n in data['selected_pages']:
        item = data['pages'][str(n)]
        if item['status'] not in {'covered', 'skipped'}:
            unfinished.append(n)
        if item['status'] == 'skipped':
            skipped.append({'page': n, 'reason': item['note']})
        for kind in ['text', 'image']:
            if item.get(kind + '_path'):
                f = root / item[kind + '_path']
                if not f.is_file() or digest(f) != item[kind + '_sha256']:
                    corrupt.append({'page': n, 'artifact': kind})
    return {'ok': not unfinished and not corrupt, 'scope': data['selected_pages'],
            'source_pages': data['source']['pages'], 'unfinished': unfinished,
            'artifact_changes': corrupt, 'intentionally_skipped': skipped,
            'whole_source_covered': len(data['selected_pages']) == data['source']['pages'] and not unfinished and not corrupt}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare'); p.add_argument('pdf'); p.add_argument('--workdir', required=True); p.add_argument('--pages')
    p = sub.add_parser('render'); p.add_argument('workdir'); p.add_argument('--pages', required=True); p.add_argument('--width', type=int, default=1600)
    p = sub.add_parser('record'); p.add_argument('workdir'); p.add_argument('--pages', required=True)
    p.add_argument('--method', choices=['text', 'visual', 'ocr'], required=True)
    p.add_argument('--status', choices=['covered', 'skipped', 'unresolved'], required=True); p.add_argument('--note', required=True)
    p = sub.add_parser('check'); p.add_argument('workdir')
    args = ap.parse_args()
    try:
        result = globals()[args.command](args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('ok', True) else 1
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    sys.exit(main())
