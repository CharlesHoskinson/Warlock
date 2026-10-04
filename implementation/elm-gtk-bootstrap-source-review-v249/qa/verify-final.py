import hashlib, json, resource, stat, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
owner = r.parent / 'elm-gtk-role-native-v238'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = r / 'qa' / ('verify-' + str(time.time_ns()))
out.mkdir()
report = {'passed': False, 'nativeAcceptance': False}
try:
    initial = json.loads((r / 'initial-manifest.json').read_text())
    for name, value in initial['files'].items():
        p = r / name
        assert sha(p) == value['sha256'] and p.stat().st_size == value['size'], name
    m = json.loads((owner / 'component-manifest.json').read_text())
    assert m['sourceHeld'] is True
    count = 0
    for section, base in [('files', owner), ('externalFiles', None)]:
        entries = m.get(section, {})
        if isinstance(entries, dict):
            entries = [{'path': name, **(value if isinstance(value, dict) else {'sha256': value})} for name, value in entries.items()]
        for row in entries:
            p = base / row['path'] if base is not None else Path(row['path'])
            assert p.is_file() and sha(p) == row['sha256'], str(p)
            if 'size' in row:
                assert p.stat().st_size == row['size'], str(p)
            if 'mode' in row:
                assert stat.S_IMODE(p.stat().st_mode) == row['mode'], str(p)
            count += 1
    for name, target in m.get('symlinks', {}).items():
        p = owner / name
        assert p.is_symlink() and str(p.readlink()) == target, name
    (r / 'final').mkdir(exist_ok=True)
    sources = {}
    for p in sorted((owner / 'qa').glob('*.py')):
        (r / 'final' / p.name).write_bytes(p.read_bytes())
        sources[str(p)] = sha(p)
    report.update(passed=True, ownerManifestSHA256=sha(owner / 'component-manifest.json'), verifiedRows=count, sources=sources, scope='Current source closure and bounded diagnostic source review only; no GUI, no GTK01–08 acceptance')
except Exception as error:
    report['error'] = repr(error)
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
if not report['passed']:
    raise SystemExit(1)
files = {str(p.relative_to(r)): {'sha256': sha(p), 'size': p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name != 'component-manifest.json'}
(r / 'component-manifest.json').write_text(json.dumps({'schema': 1, 'sourceHeld': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'fullCampaignPassed': False, 'ownerManifestSHA256': report['ownerManifestSHA256'], 'files': files, 'verificationReport': str((out / 'report.json').relative_to(r))}, indent=2) + '\n')
print('reviewManifestSHA256=' + sha(r / 'component-manifest.json'))
