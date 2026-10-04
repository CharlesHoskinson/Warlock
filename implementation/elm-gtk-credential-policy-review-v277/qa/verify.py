import hashlib, json, resource, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
owner = r.parent / 'elm-gtk-activation-credentials-fix-v276'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(owner / 'component-manifest.json') == '95aecc9e6c640cc762f2776c6ad87c33edb82f6f926f546d4f6575f8875a5a32'
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
for reportPath in m['selectedCPUReports']:
 v=json.loads(Path(reportPath).read_text());assert v['passed'],reportPath
 for source,expected in v.get('inputs',{}).items():
  if isinstance(expected,str):assert sha(Path(source))==expected,source
post=owner/'qa/post-retirement-1791147770004575210'
for case in ['late-normal','late-fallback']:
 p=post/case/'activation-post-retirement.json';v=json.loads(p.read_text())
 assert v['passed'] is (case=='late-normal')
 if case=='late-normal':assert len(v['records'])==1 and v['records'][0]['terminal']['childExitCode']==0
assert "shutil.rmtree(runtime)  # Match inherited native host order before final proof." in (owner/'qa/post-retirement-test.py').read_text()
report = {'passed': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'rows': count, 'ownerManifestSHA256': sha(owner / 'component-manifest.json'), 'blocker': None}
out = r / 'qa' / ('verify-' + str(time.time_ns()))
out.mkdir()
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
files = {str(p.relative_to(r)): {'sha256': sha(p), 'size': p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name != 'component-manifest.json'}
(r / 'component-manifest.json').write_text(json.dumps({'schema': 1, 'sourceHeld': True, 'evidenceIntegrityPassed': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'scope': 'Read-only final276 credential and closed service-outcome source review', 'ownerManifestSHA256': report['ownerManifestSHA256'], 'files': files, 'verificationReport': str((out / 'report.json').relative_to(r))}, indent=2) + '\n')
print(json.dumps({'verifiedRows': count, 'manifestSHA256': sha(r / 'component-manifest.json'), 'sourceReviewPassed': True}))
