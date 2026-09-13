#!/usr/bin/env python3
"""Local post validation, previews, public catalog and observed publication ledger."""
import argparse
import base64
from datetime import datetime, timezone
import fcntl
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote, quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from markdown_it import MarkdownIt

MD = MarkdownIt('commonmark', {'html': True}).enable('table')


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
    os.replace(tmp, path)


def config(path):
    p = Path(path).resolve()
    data = json.loads(p.read_text())
    for key in ['state_dir', 'notes_root', 'posts_dir']:
        data[key] = (p.parent / data[key]).resolve()
    return data


def canonical(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme.lower(), p.netloc.lower(),
                      quote(unicodedata.normalize('NFC', unquote(p.path)), safe='/@:-._~'), '', '')).rstrip('/')


def public_url(url, base):
    p = urlsplit(url)
    return (p.scheme == 'https' and p.netloc == urlsplit(base).netloc
            and bool(re.fullmatch(r'/(?:entry/[^?#]+|\d+)', p.path)) and not p.query and not p.fragment)


def fetch(url, limit=8_000_000):
    req = Request(url, headers={'User-Agent': 'PersonalBlogWorkflow/1.0'})
    with urlopen(req, timeout=25) as response:
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError('Response too large: ' + url)
        return data, response.url


def normalized(s):
    return re.sub(r'[^\w]', '', unicodedata.normalize('NFC', s).lower())


def catalog(args):
    cfg = config(args.config)
    articles, errors = {}, []
    for kind, suffix in [('sitemap', '/sitemap.xml'), ('rss', '/rss')]:
        try:
            payload, final = fetch(cfg['blog_url'] + suffix)
            if urlsplit(final).netloc != urlsplit(cfg['blog_url']).netloc:
                raise ValueError('Unexpected feed redirect')
            root = ET.fromstring(payload)
            if kind == 'sitemap':
                if not root.tag.endswith('urlset'):
                    raise ValueError('Expected a URL sitemap; sitemap indexes need explicit handling')
                for node in root:
                    fields = {e.tag.rsplit('}', 1)[-1]: e.text for e in node}
                    u = canonical(fields.get('loc') or '')
                    if public_url(u, cfg['blog_url']):
                        articles[u] = {'url': u, 'title': unquote(urlsplit(u).path.rsplit('/', 1)[-1]).replace('-', ' '),
                            'title_source': 'url_label', 'discovered_via': ['sitemap'], 'lastmod': fields.get('lastmod'),
                            'body_verified': False}
            else:
                for item in root.findall('./channel/item'):
                    u = canonical(item.findtext('link') or '')
                    if public_url(u, cfg['blog_url']):
                        a = articles.setdefault(u, {'url': u, 'discovered_via': [], 'body_verified': False})
                        a.update(title=item.findtext('title'), title_source='rss', category=item.findtext('category'))
                        a['discovered_via'].append('rss')
        except Exception as e:
            errors.append({'source': kind, 'error': str(e)})
    notes = []
    for file in sorted(cfg['notes_root'].glob('*.md')):
        content = file.read_text()
        m = re.search(r'^#\s+(.+)', content, re.M)
        title = m[1] if m else file.stem
        declared = re.findall(r'^>.*(?:블로그 발행본|발행 주소|발행 URL)\s*[:：]\s*(https?://\S+)', content, re.M)
        links = [{'url': canonical(u), 'status': 'found_in_public_catalog' if canonical(u) in articles else 'not_verified'} for u in declared]
        core = normalized(re.split(r'\s[—–]\s|:', title)[0])
        candidates = []
        for a in articles.values():
            at = normalized(a['title'] or '')
            if len(core) >= 4 and (core == at or at.startswith(core)):
                candidates.append({'url': a['url'], 'basis': 'title_similarity_only'})
        notes.append({'path': str(file.relative_to(cfg['notes_root'])), 'title': title,
                      'sha256': sha(file), 'declared_publications': links, 'candidates': candidates})
    out = {'version': 1, 'fetched_at': now(), 'blog_url': cfg['blog_url'],
           'complete': not errors, 'source_errors': errors, 'articles': list(articles.values()), 'notes': notes}
    target = cfg['state_dir'] / 'catalog.json'
    # A network failure must not replace a previous successful inventory with an empty one.
    if errors:
        target = cfg['state_dir'] / 'catalog-partial.json'
    write(target, out)
    rows = ['# TIL과 공개 글 연결', '', f'확인 시각: {out["fetched_at"]}', '',
            '유사 제목은 연결 후보다. 발행 완료나 본문 검증을 의미하지 않는다.', '',
            '| TIL | 명시된 발행 링크 | 제목 연결 후보 |', '|---|---|---|']
    for n in notes:
        declared = '<br>'.join(f'[{x["status"]}]({x["url"]})' for x in n['declared_publications']) or '—'
        candidate = '<br>'.join(f'[후보 {i+1}]({x["url"]})' for i, x in enumerate(n['candidates'])) or '—'
        rows.append(f'| {n["path"].replace("|", "&#124;")} | {declared} | {candidate} |')
    (target.parent / ('catalog-partial.md' if errors else 'catalog.md')).write_text('\n'.join(rows) + '\n')
    return {'ok': not errors, 'articles': len(articles), 'notes': len(notes),
            'notes_with_declared_links': sum(bool(n['declared_publications']) for n in notes),
            'notes_with_candidates': sum(bool(n['candidates']) for n in notes), 'output': str(target), 'errors': errors}


def tokens_of(text):
    result = MD.parse(text)
    return result, [child for token in result for child in (token.children or [])]


def lint(text, post=False):
    tokens, inline = tokens_of(text)
    errors, warnings = [], []
    lines = text.splitlines()
    for t in tokens:
        line = (t.map or [0])[0] + 1
        if t.type == 'fence':
            if not t.info.strip():
                errors.append(f'L{line}: code block needs a language label')
            last = re.sub(r'^(?:\s*> ?)+', '', lines[t.map[1] - 1]).strip() if t.map else ''
            if not re.fullmatch(re.escape(t.markup[0]) + '{' + str(len(t.markup)) + ',}', last):
                errors.append(f'L{line}: unclosed code fence')
        if post and t.type == 'heading_open' and t.tag == 'h1':
            errors.append(f'L{line}: keep the post title in post.json, not body H1')
        if t.type in {'html_inline', 'html_block'} and re.search(r'<\s*(script|iframe|object|embed)\b|\bon\w+\s*=', t.content, re.I):
            errors.append(f'L{line}: active HTML needs a separate reviewed asset')
        if t.type == 'table_open':
            raw = lines[t.map[0]:t.map[1]]
            counts = [len(re.split(r'(?<!\\)\|', row.strip().strip('|'))) for row in raw]
            if len(set(counts)) > 1:
                errors.append(f'L{line}: unequal table columns; escape literal pipes')
    prose = '\n'.join(t.content for t in inline if t.type == 'text')
    if post and re.search(r'\d~[-+]?\d', prose):
        warnings.append('Numeric tilde range: Tistory may render paired tildes as strikethrough; spell out the range')
    html_parts = '\n'.join(t.content for t in tokens + inline if t.type in {'html_inline', 'html_block'})
    if post and re.search(r'<\s*(?:img|a)\b', html_parts, re.I):
        errors.append('Use Markdown links and images so assets and destinations can be tracked')
    if re.search(r'\bTODO\b|\bFIXME\b|판독 불가|재확인 필요|\{\{[^}]+\}\}', prose + html_parts):
        errors.append('Unresolved placeholder in reader-facing content')
    if post and re.search(r'/Users/|file://|(?:GMS_KEY|API_KEY)\s*=\s*["\'][^<\s]', text):
        errors.append('Local/private path or assigned credential-like value in public content')
    if post and re.search(r'\$\$|\$[^$\n]*\\[A-Za-z]+[^$\n]*\$', prose):
        warnings.append('LaTeX detected: confirm actual Tistory math rendering or convert it')
    for t in inline:
        if t.type == 'html_inline' and re.search(r'<\s*(script|iframe|object|embed)\b|\bon\w+\s*=', t.content, re.I):
            errors.append('Active inline HTML needs separate review')
        if t.type == 'link_open':
            href = t.attrGet('href') or ''
            if post and not (href.startswith(('https://', 'http://', '#', 'mailto:'))):
                errors.append('Unpublished local link in post: ' + href)
            if href.startswith('#'):
                warnings.append('Verify heading anchor in the actual target renderer: ' + href)
            if re.search(r'\)[가-힣]', unquote(href)):
                errors.append('Likely malformed URL: ' + href)
        if t.type == 'image' and not t.content.strip():
            warnings.append('Image has no alternative text')
    return {'errors': list(dict.fromkeys(errors)), 'warnings': list(dict.fromkeys(warnings))}


def package(root):
    root = Path(root).resolve()
    meta = json.loads((root / 'post.json').read_text())
    text = (root / 'post.md').read_text()
    return root, meta, text


def content_hash(root):
    root, meta, text = package(root)
    h = hashlib.sha256(text.encode())
    h.update(json.dumps(meta, sort_keys=True, ensure_ascii=False).encode())
    for item in meta.get('images', []):
        f = root / item['path']
        if f.is_file():
            h.update(item['path'].encode()); h.update(f.read_bytes())
    return h.hexdigest()


def check_post(root):
    root, meta, text = package(root)
    report = lint(text, post=True)
    errors, warnings = report['errors'], report['warnings']
    for k in ['id', 'title', 'category', 'reader_question', 'contribution']:
        if not isinstance(meta.get(k), str) or not meta[k].strip():
            errors.append('Missing metadata: ' + k)
    if not isinstance(meta.get('tags'), list) or not all(isinstance(t, str) and t.strip() for t in meta.get('tags', [])):
        errors.append('tags must be an array of nonempty strings')
    if meta.get('intent') not in {'new', 'update'}:
        errors.append('intent must be new or update')
    if meta.get('intent') == 'update' and not str(meta.get('target_url') or '').startswith('https://'):
        errors.append('An update requires an observed target_url')
    _, inline = tokens_of(text)
    refs = [t.attrGet('src') for t in inline if t.type == 'image']
    listed = [x['path'] for x in meta.get('images', [])]
    if refs != listed:
        errors.append('Image manifest must match body image order (including repeated images)')
    for src in refs:
        p = (root / unquote(src)).resolve()
        if not p.is_relative_to(root) or not p.is_file() or not p.stat().st_size:
            errors.append('Missing/empty/outside-package image: ' + src)
    for record in meta.get('experiments', []):
        p = (root / record['path']).resolve()
        if not p.is_file() or sha(p) != record.get('sha256'):
            errors.append('Experiment result missing or changed: ' + record['path'])
        if record.get('script'):
            script = (root / record['script']).resolve()
            if not script.is_file() or sha(script) != record.get('script_sha256'):
                errors.append('Experiment script changed since the recorded run: ' + record['script'])
    note = meta.get('source_note')
    if note and not (root / note).is_file():
        errors.append('Missing source note: ' + note)
    if not meta.get('sources'):
        errors.append('At least one concrete source is required')
    for source in meta.get('sources', []):
        if not isinstance(source, dict) or not source.get('supports'):
            errors.append('Each source needs its concrete identity and supported claim')
            continue
        if source.get('kind') == 'public':
            u = urlsplit(source.get('url') or '')
            if u.scheme not in {'http', 'https'} or not u.netloc:
                errors.append('Public source must have an HTTP(S) URL')
        elif source.get('kind') == 'local':
            f = (root / source.get('path', '')).resolve()
            if not f.is_file() or sha(f) != source.get('sha256'):
                errors.append('Local source missing or changed: ' + source.get('path', ''))
        else:
            errors.append('Source kind must be public or local')
    if not meta.get('review', {}).get('technical'):
        warnings.append('Technical review has not been recorded')
    if not meta.get('review', {}).get('visual'):
        warnings.append('Visual review has not been recorded')
    report.update(ok=not errors, content_sha256=content_hash(root), checked_at=now())
    write(root / 'checks.json', report)
    return report


CSS = '''body{margin:0;background:#f3f5f9;color:#182231;font:17px/1.8 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif}main{max-width:840px;margin:40px auto;background:white;padding:48px;border-radius:18px}h1{font-size:34px;line-height:1.35}h2{margin-top:2.2em;font-size:25px}h3{font-size:21px}p,li{word-break:keep-all;overflow-wrap:anywhere}pre{background:#101827;color:#e8edf5;padding:22px;border-radius:10px;overflow:auto;font-size:14px;line-height:1.7}code{font-family:ui-monospace,Menlo,monospace}img{max-width:100%;height:auto}table{border-collapse:collapse;width:100%;display:block;overflow:auto;font-size:15px}th,td{border:1px solid #dbe1eb;padding:10px 15px}th{background:#edf2fb}a{color:#2459be}blockquote{border-left:4px solid #5b77c7;margin:25px 0;padding:8px 20px;background:#f5f7fc}.label{color:#586b89;font-size:13px;letter-spacing:.06em}@media(max-width:640px){main{margin:0;border-radius:0;padding:24px 18px}h1{font-size:27px}pre{padding:15px;font-size:12px}}'''


def preview(args):
    root, meta, text = package(args.directory)
    checked = check_post(root)
    if not checked['ok']:
        return checked
    page = '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    page += '<title>' + html.escape(meta['title']) + '</title><style>' + CSS + '</style><main>'
    page += '<div class="label">' + html.escape(meta['category']) + '</div><h1>' + html.escape(meta['title']) + '</h1>'
    page += MD.render(text) + '</main></html>'
    (root / 'preview.html').write_text(page)
    transfer = '<!doctype html><html lang="ko"><meta charset="utf-8"><title>티스토리 원고 복사</title><style>' + CSS + 'textarea{box-sizing:border-box;width:100%;min-height:70vh;font:15px/1.6 monospace}input{width:100%;font:22px sans-serif;padding:8px}</style><main><h1>티스토리 원고 복사</h1><p>제목과 본문을 각각 복사한다. 이미지는 원고의 해당 위치에서 업로드한다.</p>'
    transfer += '<label>발행 제목<input id="title" value="' + html.escape(meta['title'], quote=True) + '"></label><label>Markdown 본문<textarea id="markdown">' + html.escape(text) + '</textarea></label>'
    for i, item in enumerate(meta.get('images', [])):
        file = root / item['path']
        mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'webp': 'image/webp'}.get(file.suffix[1:].lower())
        if mime:
            transfer += '<figure><img id="upload-image-' + str(i) + '" alt="' + html.escape(item.get('purpose', ''), quote=True) + '" src="data:' + mime + ';base64,' + base64.b64encode(file.read_bytes()).decode() + '"><figcaption>' + html.escape(item['path']) + '</figcaption></figure>'
    transfer += '</main></html>'
    (root / 'editor-transfer.html').write_text(transfer)
    return {'ok': True, 'output': str(root / 'preview.html'), 'content_sha256': checked['content_sha256']}


class Article(HTMLParser):
    def __init__(self):
        super().__init__(); self.level = 0; self.active = None; self.text = []; self.images = []
        self.links = []; self.pre = 0; self.tables = 0; self.title = ''; self.found = False
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('property') == 'og:title':
            self.title = attrs.get('content', '')
        classes = set(attrs.get('class', '').split())
        if self.active is None and classes & {'tt_article_useless_p_margin', 'article_view', 'entry-content', 'contents_style'}:
            self.active = self.level; self.found = True
        if self.active is not None:
            if tag == 'img': self.images.append(attrs.get('src') or attrs.get('data-src') or '')
            if tag == 'a' and attrs.get('href'): self.links.append(attrs['href'])
            if tag == 'pre': self.pre += 1
            if tag == 'table': self.tables += 1
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.level += 1
    def handle_endtag(self, tag):
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.level = max(0, self.level - 1)
            if self.active is not None and self.level <= self.active: self.active = None
    def handle_data(self, data):
        if self.active is not None: self.text.append(data)


def verify_public(args):
    cfg = config(args.config)
    root, meta, text = package(args.directory)
    url = canonical(args.url)
    if not public_url(url, cfg['blog_url']): raise ValueError('Expected a public article URL on the configured blog')
    if meta.get('intent') == 'update' and canonical(meta['target_url']) != url:
        raise ValueError('Observed URL differs from the intended update target')
    checked = check_post(root)
    if not checked['ok']: return checked
    raw, final = fetch(url)
    parsed = Article(); parsed.feed(raw.decode('utf-8'))
    errors = []
    if canonical(final) != url: errors.append('Unexpected redirect')
    if not parsed.found: errors.append('No article body; HTTP 200 alone does not prove publication')
    if normalized(parsed.title) != normalized(meta['title']): errors.append('Title mismatch')
    tokens, _ = tokens_of(text)
    paras = []
    for i, t in enumerate(tokens):
        if t.type == 'paragraph_open' and i + 1 < len(tokens):
            children = tokens[i+1].children or []
            plain = ''.join(c.content for c in children if c.type in {'text', 'code_inline'})
            if len(normalized(plain)) > 35: paras.append(normalized(plain)[:80])
    selected = [paras[i] for i in sorted(set([0, len(paras)//2, len(paras)-1]))] if paras else []
    actual_text = normalized(' '.join(parsed.text))
    if not selected: errors.append('No representative paragraphs to verify')
    for sample in selected:
        if sample not in actual_text: errors.append('Representative paragraph missing: ' + sample[:30])
    expected = {'images': len(meta.get('images', [])), 'pre': sum(t.type in {'fence', 'code_block'} for t in tokens),
                'tables': sum(t.type == 'table_open' for t in tokens)}
    actual = {'images': len(parsed.images), 'pre': parsed.pre, 'tables': parsed.tables}
    for key in expected:
        if actual[key] != expected[key]: errors.append(f'{key} count mismatch: {actual[key]} vs {expected[key]}')
    internal = sorted({canonical(urljoin(url, u)) for u in parsed.links if public_url(canonical(urljoin(url, u)), cfg['blog_url'])})
    for u in internal:
        try:
            _, dest = fetch(u)
            if canonical(dest) != u: errors.append('Internal link redirected: ' + u)
        except Exception as e: errors.append('Internal link failed: ' + u + ' ' + str(e))
    report = {'ok': not errors, 'url': url, 'verified_at': now(), 'content_sha256': content_hash(root),
              'expected': expected, 'actual': actual, 'internal_links_checked': len(internal), 'errors': errors,
              'limits': 'Counts and text samples do not verify every sentence, image identity, placement, or visual rendering.'}
    write(root / 'public-verification.json', report)
    return report


def record_publication(args):
    cfg = config(args.config)
    root, meta, _ = package(args.directory)
    checked = check_post(root)
    if not checked['ok']: return checked
    u = canonical(args.url)
    parsed = urlsplit(u)
    if parsed.scheme != 'https' or parsed.netloc != urlsplit(cfg['blog_url']).netloc:
        raise ValueError('Publication URL must belong to the configured blog')
    if args.status == 'draft' and not re.fullmatch(r'/manage/post/\d+', parsed.path):
        raise ValueError('Draft needs a saved editor URL with an observed numeric post ID')
    if not args.observation.strip(): raise ValueError('A concrete UI observation is required')
    if args.status == 'published':
        if not public_url(u, cfg['blog_url']): raise ValueError('Expected public post URL')
        if meta.get('intent') == 'update' and canonical(meta['target_url']) != u:
            raise ValueError('Observed URL differs from the intended update target')
        verification = json.loads((root / 'public-verification.json').read_text())
        if not verification.get('ok') or verification['url'] != u or verification['content_sha256'] != checked['content_sha256']:
            raise ValueError('Public verification is missing, stale, or for another URL')
        if not all(meta.get('review', {}).get(k) for k in ['technical', 'visual']):
            raise ValueError('Record technical and visual review before marking published')
    event = {'post_id': meta['id'], 'status': args.status, 'url': u,
             'content_sha256': checked['content_sha256'], 'observed_at': now(), 'observation': args.observation}
    # Serialize read-modify-write, so simultaneous scheduled runs cannot lose or duplicate ledger entries.
    cfg['state_dir'].mkdir(parents=True, exist_ok=True)
    ledger = cfg['state_dir'] / 'publications.json'
    with (cfg['state_dir'] / '.ledger.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        events = json.loads(ledger.read_text()) if ledger.exists() else []
        identity = ['post_id', 'status', 'url', 'content_sha256']
        latest = next((e for e in reversed(events) if e['post_id'] == meta['id']), None)
        if latest and all(latest.get(k) == event[k] for k in identity):
            return {'ok': True, 'already_recorded': True, 'events': len(events)}
        events.append(event); write(ledger, events)
    return {'ok': True, 'event': event, 'events': len(events)}


def main():
    p = argparse.ArgumentParser(description=__doc__); sub = p.add_subparsers(dest='command', required=True)
    x = sub.add_parser('catalog'); x.add_argument('--config', required=True)
    x = sub.add_parser('lint-notes'); x.add_argument('file')
    for cmd in ['check', 'preview']:
        x = sub.add_parser(cmd); x.add_argument('directory')
    x = sub.add_parser('verify-public'); x.add_argument('directory'); x.add_argument('--config', required=True); x.add_argument('--url', required=True)
    x = sub.add_parser('record-publication'); x.add_argument('directory'); x.add_argument('--config', required=True)
    x.add_argument('--url', required=True); x.add_argument('--status', choices=['draft','published','publication_unknown'], required=True)
    x.add_argument('--observation', required=True)
    args = p.parse_args()
    try:
        if args.command == 'lint-notes':
            out = lint(Path(args.file).read_text()); out['ok'] = not out['errors']
        elif args.command == 'check': out = check_post(args.directory)
        else: out = globals()[args.command.replace('-', '_')](args)
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0 if out.get('ok', True) else 1
    except Exception as e:
        print(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False)); return 1


if __name__ == '__main__':
    sys.exit(main())
