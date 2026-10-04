"""Verify and hold bounded owning-code characterization evidence."""
import hashlib
import json
import resource
from pathlib import Path

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def check(path, row):
    if isinstance(row, str):
        assert sha(path) == row, path
    else:
        assert sha(path) == row['sha256'] and path.stat().st_size == row['size'], path
        if 'resolved' in row:
            assert str(path.resolve()) == row['resolved'], path
edge = REPO / 'implementation/elm-geometry-conversion-edge-characterization-v166'
manifest = edge / 'component-manifest.json'
assert sha(manifest) == '2a24176b9c4e3b1e07b8c424d69bd14be0beb8e09800d01aecbf267f638f5341'
packet = json.loads(manifest.read_text())
assert packet['sourceHeld'] and packet['evidenceIntegrityPassed']
assert packet['nativeAcceptance'] is False and packet['checks'] == 23
for rel, row in packet['files'].items():
    check(edge / rel, row)
for path, row in packet['externalClosure'].items():
    check(Path(path), row)
for rel, row in packet['ancestorInventory'].items():
    check(Path(packet['ancestorRoot']) / rel, row)
review = REPO / 'implementation/elm-window-bound-hints-review-v166/qa/review-1791124740256767174/report.json'
assert sha(review) == '3d714f47d47754c136cb8392cc7ec24360d108cbfbc28ccebea819ad7204f1ee'
d = json.loads(review.read_text())
assert d['passed'] is True and all(row['passed'] for row in d['checks'])
for group in ('compilerDependencies', 'linkedLibraries', 'artifacts'):
    for path, row in d[group].items():
        check(Path(path), row)
actual = REPO / 'implementation/elm-window-bound-hints-characterization-v165/qa/characterization-1791124527444957441/report.json'
assert json.loads(actual.read_text())['checks'] == 13
assert json.loads(actual.read_text())['passed'] is True
helper_review = REPO / 'implementation/elm-geometry-size-policy-integration-review-v163/qa/review-1791124329570836574/report.json'
assert json.loads(helper_review.read_text())['passed'] is True
directories = [ROOT, edge, Path(packet['ancestorRoot']), review.parents[2], helper_review.parents[2],
               REPO / 'implementation/elm-window-bound-hints-characterization-v164',
               REPO / 'implementation/elm-window-bound-hints-characterization-v165']
files = []
for directory in directories:
    for p in sorted(directory.rglob('*')):
        assert not p.is_symlink(), p
        if p.is_file():
            files.append(dict(path=str(p), size=p.stat().st_size, sha256=sha(p)))
destination = ROOT / 'component-manifest.json'
assert not destination.exists()
destination.write_text(json.dumps(dict(scope='Bounded owning-code CPU characterization only; no policy/model/native/release acceptance', conversionCases=23, boundHintCases=13, nativeAcceptance=False, modelAcceptance=False, files=files, conversionManifestSHA256=sha(manifest), hintReviewSHA256=sha(review)), indent=2) + '\n')
print(json.dumps(dict(frozen=True, files=len(files), manifestSHA256=sha(destination))))
