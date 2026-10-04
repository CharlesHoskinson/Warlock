import hashlib, json, resource, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
owner = r.parent / 'elm-gtk-privileged-helper-drain-v282'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(owner / 'component-manifest.json') == '5619425ec3a4b2d60fb26072d7fd5fbef44e6b2fefda90b3419e4bf37c392233'
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
assert len(m['selectedCPUReports'])==15
for reportPath in m['selectedCPUReports']:
 v=json.loads(Path(reportPath).read_text());assert v['passed'],reportPath
 for source,expected in v.get('inputs',{}).items():
  if isinstance(expected,str):assert sha(Path(source))==expected,source
drain=json.loads((owner/'qa/drain-1791149240032075778/report.json').read_text())
assert drain['passed'] and drain['credentialPolicyInjected'] is True and len(drain['checks'])==3
checks={row['name']:row for row in drain['checks']}
normal=checks['privileged-wait'];assert normal['actualHelperExitCode']==0 and not normal['helperSignalled'] and normal['terminal']['error'] is None and len(normal['terminal']['allWaitStatuses'])==2
timeout=checks['privileged-timeout'];assert timeout['elapsed']<3 and not timeout['helperSignalledBySupervisor'] and timeout['terminal']['liveDescendants'] and timeout['terminal']['error'] and not timeout['positiveCleanup']
error=checks['repeated-signal-error'];assert error['terminal']['error'] and not error['terminal']['liveDescendants'] and len(error['terminal']['allWaitStatuses'])==2 and not error['helperSignalled']
report = {'passed': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'rows': count, 'ownerManifestSHA256': sha(owner / 'component-manifest.json'), 'blocker': None}
out = r / 'qa' / ('verify-' + str(time.time_ns()))
out.mkdir()
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
files = {str(p.relative_to(r)): {'sha256': sha(p), 'size': p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name != 'component-manifest.json'}
(r / 'component-manifest.json').write_text(json.dumps({'schema': 1, 'sourceHeld': True, 'evidenceIntegrityPassed': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'scope': 'Read-only final282 bounded privileged wait/reap and terminal source review', 'ownerManifestSHA256': report['ownerManifestSHA256'], 'files': files, 'verificationReport': str((out / 'report.json').relative_to(r))}, indent=2) + '\n')
print(json.dumps({'verifiedRows': count, 'manifestSHA256': sha(r / 'component-manifest.json'), 'sourceReviewPassed': True}))
