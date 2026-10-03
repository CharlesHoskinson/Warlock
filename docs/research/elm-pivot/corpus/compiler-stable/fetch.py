import concurrent.futures
import datetime
import hashlib
import json
import ast
import re
from pathlib import Path
from scrapling.fetchers import Fetcher

BASE = Path('/home/hoskinson/.cache/elm-pivot/compiler-stable')
records = []

def fetch(item):
    name, url, kind, expected_git = item
    response = Fetcher.get(url, timeout=45)
    raw = response.body
    if not isinstance(raw, bytes):
        raise TypeError('Scrapling response.body must preserve bytes')
    path = BASE / 'raw' / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    text = response.get_all_text(separator='\n') if kind == 'web-reference' else raw.decode('utf-8', errors='replace')
    extracted = BASE / 'text' / (name + '.txt')
    extracted.parent.mkdir(parents=True, exist_ok=True)
    extracted.write_text(text)
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    record = dict(requested_url=url, final_url=str(response.url), status=response.status,
        kind=kind, raw_path=str(path.relative_to(BASE)), extracted_path=str(extracted.relative_to(BASE)),
        byte_count=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
        extracted_sha256=hashlib.sha256(extracted.read_bytes()).hexdigest(),
        git_blob_sha1=blob, expected_git_blob_sha1=expected_git,
        git_blob_verified=(blob == expected_git) if expected_git else None,
        fetched_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        headers=dict(response.headers))
    if kind == 'web-reference':
        record['extracted_characters'] = len(text.strip())
        record['classification'] = 'needs-content-review'
    return record

tree_url = 'https://api.github.com/repos/elm/compiler/git/trees/0.19.2?recursive=1'
tree_record = fetch(('tree.json', tree_url, 'github-tree', None))
records.append(tree_record)
tree = json.loads((BASE / 'raw/tree.json').read_bytes())
if tree.get('truncated'):
    raise RuntimeError('Recursive source tree truncated')
items = []
for entry in tree['tree']:
    path = entry['path']
    if entry['type'] == 'blob' and (path.startswith('docs/') or (path.startswith('installers/') and Path(path).name.lower().startswith('readme'))):
        items.append((path, 'https://raw.githubusercontent.com/elm/compiler/0.19.2/' + path,
            'compiler-document' if path.startswith('docs/') else 'installer-readme', entry['sha']))
for route in ['docs', 'install', 'syntax']:
    items.append(('elm-lang-' + route + '.html', 'https://elm-lang.org/' + route, 'web-reference', None))
items.extend([
    ('elm-lang-docs-syntax.html', 'https://elm-lang.org/docs/syntax', 'web-reference', None),
    ('guide-install-elm.html', 'https://guide.elm-lang.org/install/elm.html', 'web-reference', None),
])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for record in pool.map(fetch, items):
        records.append(record)
        print(record['status'], record['raw_path'], record['byte_count'], flush=True)
for record in records:
    if record['kind'] != 'web-reference':
        continue
    if record['status'] != 200:
        record['classification'] = 'http-error-preserved'
        continue
    if not record['requested_url'].startswith('https://elm-lang.org/docs'):
        record['classification'] = 'server-rendered-substantive-guide'
        continue
    raw = (BASE / record['raw_path']).read_text()
    parts = []
    if record['requested_url'] == 'https://elm-lang.org/docs':
        for match in re.finditer(r'\bl\(lt,"600px",("(?:\\.|[^"\\])*")', raw):
            parts.append(ast.literal_eval(match.group(1)))
    else:
        for script in re.findall(r'<script\b[^>]*>(.*?)</script>', raw, re.S):
            for token in re.findall(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', script):
                if '\\n' not in token or len(token) < 180:
                    continue
                try:
                    value = ast.literal_eval(token)
                except (ValueError, SyntaxError):
                    continue
                if isinstance(value, str) and ('##' in value or '```' in value or '* [' in value):
                    parts.append(value)
    out = '\n\n'.join(parts)
    path = BASE / 'text' / (Path(record['raw_path']).name + '.embedded-markdown.txt')
    path.write_text(out)
    record.update(classification='spa-shell-with-substantive-embedded-markdown' if parts else 'spa-shell-only',
        embedded_markdown_path=str(path.relative_to(BASE)),
        embedded_markdown_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        embedded_markdown_characters=len(out),
        extraction_method='Static Markdown-bearing JavaScript string literals decoded with ast.literal_eval; no JavaScript execution; supplementary extraction')
(BASE / 'sources.json').write_text(json.dumps(dict(tag='0.19.2', tree_commit=tree['sha'], tree_truncated=tree.get('truncated',False), records=records), indent=2) + '\n')
if any((r['status'] != 200 and not (r['requested_url'] == 'https://elm-lang.org/syntax' and r['status'] == 404)) or r['git_blob_verified'] is False for r in records):
    raise RuntimeError('Source status or Git blob mismatch; inspect preserved manifest')
