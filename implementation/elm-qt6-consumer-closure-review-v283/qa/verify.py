import hashlib, json, resource, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = Path(__file__).resolve().parents[1]
owner = r.parent / 'elm-qt6-journal-consumer-v279'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(owner / 'component-manifest.json') == '94497439272da644ffd649c6ab081b4800ec691cfb449817fb261fa80ac36c74'
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
testPath=owner/'qa/test-1791148464886285381/report.json'
test=json.loads(testPath.read_text());assert test['passed'] and len(test['checks'])==48
assert sha(owner/'qa/journal.py')==test['sourceSHA256']==sha(testPath.parent/'journal.py')
assert sha(owner/'qa/test.py')==sha(testPath.parent/'test.py')
assert sha(testPath.parent/'enums.cpp')==test['enumSourceSHA256']
assert sha(testPath.parent/'enums')==test['enumBinarySHA256']
producer=owner.parent/'elm-qt6-role-journal-fixture-v250'
assert sha(producer/'component-manifest.json')=='c65966d9a136418a4b371278a554d3d830890f0d74b76950984857c0e4097983'
producerManifest=json.loads((producer/'component-manifest.json').read_text())
for name,row in producerManifest['files'].items():
 p=producer/name;assert sha(p)==row['sha256'] and p.stat().st_size==row['size'];count+=1
assert sha(producer/'native/qt-role-client.cpp')=='83e8a3f065262e3a05deed454619733dcac81b23384e0533ccae330524d29418'
report = {'passed': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'rows': count, 'ownerManifestSHA256': sha(owner / 'component-manifest.json'), 'blocker': None}
out = r / 'qa' / ('verify-' + str(time.time_ns()))
out.mkdir()
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
files = {str(p.relative_to(r)): {'sha256': sha(p), 'size': p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name != 'component-manifest.json'}
(r / 'component-manifest.json').write_text(json.dumps({'schema': 1, 'sourceHeld': True, 'evidenceIntegrityPassed': True, 'sourceReviewPassed': True, 'nativeAcceptance': False, 'scope': 'Read-only held279 synthetic Qt consumer/source and enum closure review', 'ownerManifestSHA256': report['ownerManifestSHA256'], 'files': files, 'verificationReport': str((out / 'report.json').relative_to(r))}, indent=2) + '\n')
print(json.dumps({'verifiedRows': count, 'manifestSHA256': sha(r / 'component-manifest.json'), 'sourceReviewPassed': True}))
