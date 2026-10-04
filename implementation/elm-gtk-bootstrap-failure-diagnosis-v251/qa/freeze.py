import hashlib, json, resource, stat
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report = r / 'qa/diagnose-1791141707203919585/report.json'
v = json.loads(report.read_text())
assert v['passed'] and not v['nativeAcceptance'] and v['rawCallsMatched'] == 0 and v['normalizedCallsMatched'] == 4101
for name, row in v['evidenceSources'].items():
    p = Path(name)
    assert sha(p) == row['sha256'] and p.stat().st_size == row['size'], name
files = {str(p.relative_to(r)): {'sha256': sha(p), 'size': p.stat().st_size, 'mode': stat.S_IMODE(p.stat().st_mode)} for p in sorted(r.rglob('*')) if p.is_file() and p.name != 'component-manifest.json'}
(r / 'component-manifest.json').write_text(json.dumps({'schema': 1, 'sourceHeld': True, 'evidenceIntegrityPassed': True, 'nativeAcceptance': False, 'fullCampaignPassed': False, 'scope': 'Read-only diagnosis of preserved actual238 failure', 'files': files, 'externalEvidence': v['evidenceSources'], 'diagnosisReport': str(report.relative_to(r))}, indent=2) + '\n')
print(sha(r / 'component-manifest.json'))
