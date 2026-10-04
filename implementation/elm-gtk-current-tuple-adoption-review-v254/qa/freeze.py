import hashlib, json, resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = r / 'qa/audit-1791142162065495829/report.json'
v = json.loads(report.read_text())
assert v['passed'] and not v['nativeAcceptance'] and v['currentGuiChecks'] == 473
for name, row in v['externalFiles'].items():
    p = Path(name)
    assert sha(p) == row['sha256'] and p.stat().st_size == row['size'], name
files = {str(p.relative_to(r)): {'sha256': sha(p), 'size': p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name != 'component-manifest.json'}
(r / 'component-manifest.json').write_text(json.dumps({'schema': 1, 'sourceHeld': True, 'evidenceIntegrityPassed': True, 'nativeAcceptance': False, 'scope': 'Current tuple read-only adoption review, not GTK qualification', 'files': files, 'externalFiles': v['externalFiles'], 'report': str(report.relative_to(r))}, indent=2) + '\n')
print(sha(r / 'component-manifest.json'))
