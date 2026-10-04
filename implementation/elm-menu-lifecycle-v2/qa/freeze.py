"""Freeze separately scoped, successful V2 evidence and preserve all attempts."""
import hashlib
import json
import resource
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

REPORTS = {
    'compiledElm': 'qa/replay-1791082719169766540/report.json',
    'appliedElmMutations': 'qa/mutations-1791082755631851542/report.json',
    'sampledAbstractModel': 'qa/model-1791082868788532477/report.json',
    'historicalNativePackets': 'qa/historical-1791082974572663897/report.json',
}
reports = {}
for label, relative in REPORTS.items():
    path = ROOT / relative
    report = json.loads(path.read_text())
    assert report['passed'], relative
    for source, digest in report.get('inputs', {}).items():
        assert sha(ROOT / source) == digest, source
    for artifact, digest in report.get('artifacts', {}).items():
        assert sha(path.parent / artifact) == digest, artifact
    reports[label] = report

elm = reports['compiledElm']
model = reports['sampledAbstractModel']
historical = reports['historicalNativePackets']
assert elm['checks'] == 260 and elm['routerChecks'] == 47
assert model['stage'] == 'final' and model['namedScenarios'] == 29
assert model['invariantSamples'] == 2000 and model['unsafeGuardMutationDetected']
assert all(value > 0 for value in model['witnesses'].values())
assert historical['buildReport'] == REPORTS['compiledElm']
assert historical['buildReportSHA256'] == sha(ROOT / REPORTS['compiledElm'])
assert historical['nativeCommands'] == 2 and historical['nativeReceipts'] == 2
target = ROOT / 'qa/implementation-manifest.json'
assert not target.exists(), 'Frozen manifests are immutable'
files = {}
links = {}
for path in sorted(ROOT.rglob('*')):
    if path.is_symlink():
        links[str(path.relative_to(ROOT))] = str(path.readlink())
    elif path.is_file():
        files[str(path.relative_to(ROOT))] = {'sha256': sha(path), 'size': path.stat().st_size}
manifest = {
    'passed': True, 'observedUTC': datetime.now(timezone.utc).isoformat(),
    'scope': 'Bounded compiled menu/provider/receipt component, sampled abstraction and historical packet compatibility',
    'wholeFeatureAccepted': False, 'newNativeGuiAccepted': False,
    'completedRequirementIds': [],
    'reports': {label: {'path': relative, 'sha256': sha(ROOT / relative),
                        'scope': reports[label].get('scope')} for label, relative in REPORTS.items()},
    'compiledElmChecks': 307, 'namedAbstractScenarios': 29,
    'sampledAbstractTraces': 2000, 'modelWitnesses': model['witnesses'],
    'nativeObservationModelled': False,
    'remainingGates': ['native provider publication and authentication',
                       'shared controller integration and native qualification',
                       'reconciliation before exhausted-controller recovery',
                       'full right-click and roadmap acceptance'],
    'files': files, 'symlinks': links,
}
with target.open('x') as stream:
    stream.write(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'passed': True, 'manifest': str(target), 'files': len(files)}))
