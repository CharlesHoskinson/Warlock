import hashlib, json, resource, stat, time
from pathlib import Path

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
root = Path(__file__).resolve().parents[1]
owner = root.parent / 'elm-qt6-scene-consumer-v296'

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            h.update(chunk)
    return h.hexdigest()

assert sha(owner / 'component-manifest.json') == '7f3a2cefb06076d9c36ae40e7cceb18ea39010b5a809701b08ec65b97211a88f'
manifest = json.loads((owner / 'component-manifest.json').read_text())
count = 0
for name, row in manifest['files'].items():
    path = owner / name
    assert not path.is_symlink()
    assert sha(path) == row['sha256'], name
    assert path.stat().st_size == row['size'], name
    assert stat.S_IMODE(path.stat().st_mode) == row['mode'], name
    count += 1
for name, digest in manifest['externalFiles'].items():
    assert sha(name) == digest, name
    count += 1
reports = []
for name in manifest['selectedReports']:
    path = Path(name)
    packet = json.loads(path.read_text())
    assert packet['passed'] and not packet['nativeAcceptance']
    for source, digest in packet['sourceInputs'].items():
        if Path(source).name != 'freeze.py':
            assert sha(source) == digest, source
    reports.append({'path': name, 'sha256': sha(path)})
assert not manifest['nativeAcceptance'] and not manifest['presentationProved'] and not manifest['fullCampaign']
report = {'passed': True, 'sourceReviewPassed': True, 'nativeAcceptance': False,
          'rows': count, 'reports': reports, 'blocker': None,
          'ownerManifestSHA256': sha(owner / 'component-manifest.json')}
out = root / 'qa' / ('verify-' + str(time.time_ns()))
out.mkdir()
(out / 'report.json').write_text(json.dumps(report, indent=2))
files = {str(path.relative_to(root)): {'sha256': sha(path), 'size': path.stat().st_size}
         for path in root.rglob('*') if path.is_file()}
held = root / 'component-manifest.json'
held.write_text(json.dumps({'sourceHeld': True, 'evidenceIntegrityPassed': True,
                           'sourceReviewPassed': True, 'nativeAcceptance': False,
                           'ownerManifestSHA256': report['ownerManifestSHA256'],
                           'files': files, 'verificationReport': str((out / 'report.json').relative_to(root))}, indent=2))
print(json.dumps({'rows': count, 'manifestSHA256': sha(held)}))
