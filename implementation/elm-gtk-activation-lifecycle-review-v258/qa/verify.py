import hashlib, json, resource, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
owner = r.parent / 'elm-gtk-bootstrap-wire-v252'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(owner / 'component-manifest.json') == '085f45e556b8dd9ab645ffa01138aa0d1ff16b1194c7dba3e1f0ee0cdc68e0f4'
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
report = {'passed': True, 'sourceReviewPassed': False, 'nativeAcceptance': False, 'rows': count, 'ownerManifestSHA256': sha(owner / 'component-manifest.json'), 'blocker': 'Late activation after quiet scans is not included in authoritative exit-status accounting'}
out = r / 'qa' / ('verify-' + str(time.time_ns()))
out.mkdir()
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
files = {str(p.relative_to(r)): {'sha256': sha(p), 'size': p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name != 'component-manifest.json'}
(r / 'component-manifest.json').write_text(json.dumps({'schema': 1, 'sourceHeld': True, 'evidenceIntegrityPassed': True, 'sourceReviewPassed': False, 'nativeAcceptance': False, 'scope': 'Read-only held252 review with controlled actual-method late-activation witness', 'ownerManifestSHA256': report['ownerManifestSHA256'], 'files': files, 'verificationReport': str((out / 'report.json').relative_to(r))}, indent=2) + '\n')
print(json.dumps({'verifiedRows': count, 'manifestSHA256': sha(r / 'component-manifest.json'), 'sourceReviewPassed': False}))
