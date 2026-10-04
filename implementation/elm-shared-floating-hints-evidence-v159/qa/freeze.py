"""Verify failed campaign and extract actual target protocol hints."""
import hashlib
import json
import re
import resource
from pathlib import Path

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SOURCE = REPO / 'implementation/elm-shared-floating-hints-native-v158'
REPORT = SOURCE / 'qa/native-1791123411132106707/report.json'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
campaign = json.loads(REPORT.read_text())
assert campaign['passed'] is False and campaign['cleanupPassed'] is True
assert campaign['error'] == "AssertionError('floatingMenuHasMultipleActualEnabledActions')"
for rel, digest in campaign['artifacts'].items():
    assert sha(REPORT.parent / rel) == digest, rel
preflight = json.loads((SOURCE / 'qa/preflight.json').read_text())
for path, digest in preflight['inputs'].items():
    assert sha(Path(path)) == digest, path
log_path = REPORT.parent / 'native-evidence/fixture.log'
log = log_path.read_text()
ids = re.findall(r'xdg_toplevel#(\d+)\.set_title\("ELM-AUTHORITY-FIXTURE"\)', log)
assert len(ids) == 1
target = ids[0]
surface = re.findall(r'xdg_surface#(\d+)\.get_toplevel\(new id xdg_toplevel#' + target + r'\)', log)
assert len(surface) == 1
minimum = re.findall(r'xdg_toplevel#' + target + r'\.set_min_size\((\d+), (\d+)\)', log)
maximum = re.findall(r'xdg_toplevel#' + target + r'\.set_max_size\((\d+), (\d+)\)', log)
origins = re.findall(r'xdg_surface#' + surface[0] + r'\.set_window_geometry\((-?\d+), (-?\d+), (\d+), (\d+)\)', log)
assert minimum and maximum and origins
assert all(tuple(map(int, v)) == (108, 42) for v in minimum)
assert all(tuple(map(int, v)) == (0, 0) for v in maximum)
assert all(tuple(map(int, v[:2])) == (0, 0) for v in origins)
diagnosis = dict(scope='Actual failed GTK protocol diagnostic only; no geometry/native/release acceptance', nativeAcceptance=False, releaseAcceptance=False, campaignPassed=False, cleanupPassed=True, report=str(REPORT), reportSHA256=sha(REPORT), fixtureLogSHA256=sha(log_path), targetTitle='ELM-AUTHORITY-FIXTURE', targetToplevel=target, targetSurface=surface[0], rawMinimum=list(map(int, minimum[-1])), rawMaximum=list(map(int, maximum[-1])), maximumMeaning='Zero means unbounded', geometryOrigin=[0, 0], geometryObservations=[list(map(int, row)) for row in origins])
destination = ROOT / 'diagnostic.json'
assert not destination.exists()
destination.write_text(json.dumps(diagnosis, indent=2) + '\n')
files = []
for directory in (ROOT, SOURCE):
    for p in sorted(directory.rglob('*')):
        assert not p.is_symlink(), p
        if p.is_file():
            files.append(dict(path=str(p), sha256=sha(p), size=p.stat().st_size))
manifest = ROOT / 'component-manifest.json'
assert not manifest.exists()
manifest.write_text(json.dumps(dict(scope=diagnosis['scope'], files=files, externalClosure=preflight['inputs'], nativeAcceptance=False, releaseAcceptance=False), indent=2) + '\n')
print(json.dumps(dict(frozen=True, files=len(files), rawMinimum=diagnosis['rawMinimum'], rawMaximum=diagnosis['rawMaximum'], manifestSHA256=sha(manifest))))
