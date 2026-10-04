"""Freeze the failed native floating-menu campaign without accepting its gates."""
import hashlib
import json
import resource
from pathlib import Path

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SOURCE = REPO / 'implementation/elm-shared-floating-menu-native-v152'
REPORT = SOURCE / 'qa/native-1791122705930103945/report.json'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
d = json.loads(REPORT.read_text())
assert d['passed'] is False and d['cleanupPassed'] is True
assert d['error'] == "AssertionError('floatingMenuHasMultipleActualEnabledActions')"
assert [c['name'] for c in d['checks'] if not c['passed']] == ['floatingMenuHasMultipleActualEnabledActions']
assert any(c['name'] == 'nativeClientsEmptyBeforePluginUnload' and c['passed'] for c in d['checks'])
for relative, digest in d['artifacts'].items():
    assert sha(REPORT.parent / relative) == digest, relative
preflight = json.loads((SOURCE / 'qa/preflight.json').read_text())
for path, digest in preflight['inputs'].items():
    assert sha(Path(path)) == digest, path
files = []
for directory in [ROOT, *[REPO / ('implementation/elm-shared-floating-menu-native-v' + str(n)) for n in (150, 151, 152)]]:
    for p in sorted(directory.rglob('*')):
        assert not p.is_symlink(), p
        if p.is_file():
            files.append(dict(path=str(p), size=p.stat().st_size, sha256=sha(p)))
destination = ROOT / 'component-manifest.json'
assert not destination.exists()
packet = dict(scope='Frozen failed native floating GTK menu campaign and rejected harness ancestors; no feature/native/release acceptance', nativeAcceptance=False, releaseAcceptance=False, report=str(REPORT), reportSHA256=sha(REPORT), cleanupPassed=True, failedGate='floatingMenuHasMultipleActualEnabledActions', files=files, externalClosure=preflight['inputs'])
destination.write_text(json.dumps(packet, indent=2) + '\n')
print(json.dumps(dict(frozen=True, files=len(files), manifest=str(destination), sha256=sha(destination))))
