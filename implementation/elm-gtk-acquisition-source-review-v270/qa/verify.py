import hashlib, json, resource, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
owner = r.parent / 'elm-gtk-native-acquisition-fix-v268'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(owner / 'component-manifest.json') == '8bfcda5de4bd6e0123a56d3a7b571d8d0ec9016a37aeedf467a23c3238bb9a17'
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
selected=['rapid-reap-1791146368520422717','reap-body-1791146368492202849','placement-1791146368512330077','cleanup-regression-1791146368524082762']
for name in selected:
 p=owner/'qa'/name/'report.json';v=json.loads(p.read_text());assert v['passed']
 for source,expected in v['inputs'].items():assert sha(Path(source))==expected
rapid=json.loads((owner/'qa'/selected[0]/'report.json').read_text());assert len(rapid['checks'])==8 and rapid['kernelAcquiredTotal']>0
for check in rapid['checks']:
 rows=[json.loads(line) for line in Path(check['journal']).read_text().splitlines()]
 owned=[x['identity'] for x in rows if x['kind']=='owned-child'];exits=[x for x in rows if x['kind']=='child-exit'];assert len(owned)==len(exits)==17
 assert len({(x['pid'],x['start']) for x in owned})==17
 assert sorted(x['exitCode'] for x in exits)==[0]*16+[7]
 assert len(rows[-1]['allWaitStatuses'])==17 and not rows[-1]['liveDescendants'] and rows[-1]['error'] is None
report = {'passed': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'rows': count, 'ownerManifestSHA256': sha(owner / 'component-manifest.json'), 'blocker': None}
out = r / 'qa' / ('verify-' + str(time.time_ns()))
out.mkdir()
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
files = {str(p.relative_to(r)): {'sha256': sha(p), 'size': p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name != 'component-manifest.json'}
(r / 'component-manifest.json').write_text(json.dumps({'schema': 1, 'sourceHeld': True, 'evidenceIntegrityPassed': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'scope': 'Read-only final268 acquisition and cleanup source review', 'ownerManifestSHA256': report['ownerManifestSHA256'], 'files': files, 'verificationReport': str((out / 'report.json').relative_to(r))}, indent=2) + '\n')
print(json.dumps({'verifiedRows': count, 'manifestSHA256': sha(r / 'component-manifest.json'), 'sourceReviewPassed': True}))
