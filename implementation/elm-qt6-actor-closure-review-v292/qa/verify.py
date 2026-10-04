import hashlib, json, resource, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
owner = r.parent / 'elm-qt6-owned-actor-v285'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(owner / 'component-manifest.json') == 'e87f9fd7b164b3c0fc73857f26cecb3b2dd555bf3a3fc46caf07dc238f7e7a37'
m = json.loads((owner / 'component-manifest.json').read_text())
count = 0
for section, base in [('files', owner), ('externalFiles', None)]:
    entries = m[section]
    if isinstance(entries, dict):
        entries = [{'path': name, **(row if isinstance(row, dict) else {'sha256': row})} for name, row in entries.items()]
    for row in entries:
        p = base / row['path'] if base is not None else Path(row['path'])
        assert sha(p) == row['sha256'], str(p)
        if 'size' in row:
            assert p.stat().st_size == row['size'], str(p)
        count += 1
for name, target in m.get('symlinks', {}).items():
    assert (owner / name).is_symlink() and str((owner / name).readlink()) == target
freeze=json.loads((owner/'qa/freeze-1791149545974749970/report.json').read_text());assert freeze['passed'] and freeze['verifiedExternalFiles']==1096
assert [row['checks'] for row in freeze['reports']]==[6,16]
for item in freeze['reports']:
 p=Path(item['path']);assert sha(p)==item['sha256'];v=json.loads(p.read_text());assert v['passed'] and len(v['checks'])==item['checks']
 for source,expected in v.get('inputs',{}).items():
  if isinstance(expected,str):assert sha(Path(source))==expected,source
report = {'passed': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'rows': count, 'ownerManifestSHA256': sha(owner / 'component-manifest.json'), 'blocker': None}
out = r / 'qa' / ('verify-' + str(time.time_ns()))
out.mkdir()
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
files = {str(p.relative_to(r)): {'sha256': sha(p), 'size': p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name != 'component-manifest.json'}
(r / 'component-manifest.json').write_text(json.dumps({'schema': 1, 'sourceHeld': True, 'evidenceIntegrityPassed': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'scope': 'Read-only held285 owned Qt actor and synthetic process/decoder closure review', 'ownerManifestSHA256': report['ownerManifestSHA256'], 'files': files, 'verificationReport': str((out / 'report.json').relative_to(r))}, indent=2) + '\n')
print(json.dumps({'verifiedRows': count, 'manifestSHA256': sha(r / 'component-manifest.json'), 'sourceReviewPassed': True}))
