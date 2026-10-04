"""Freeze the successful production adapter closure, without GUI acceptance."""
import hashlib
import json
import resource
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

path = sorted((ROOT / 'qa').glob('replay-*/report.json'))[-1]
report = json.loads(path.read_text())
assert report['passed'] and not report.get('error')
for relative, digest in report['inputs'].items():
    assert sha(ROOT / relative) == digest, relative
    assert sha(path.parent / 'inputs' / relative) == digest, relative
for relative, digest in report.get('artifacts', {}).items():
    assert sha(path.parent / relative) == digest, relative
for relative, item in json.loads((ROOT / 'upstream.json').read_text())['files'].items():
    assert sha(REPO / item['source']) == item['sourceSHA256'], relative
    assert sha(ROOT / relative) == item['derivativeSHA256'], relative
    assert item['changed'] == (item['sourceSHA256'] != item['derivativeSHA256']), relative
mutation_reports = sorted((ROOT / 'qa').glob('mutations-*/report.json'))
mutation = None
if mutation_reports:
    mutation_path = mutation_reports[-1]
    mutation = json.loads(mutation_path.read_text())
    assert mutation['passed'] and not mutation.get('error')
    for relative, digest in mutation.get('inputs', {}).items():
        assert sha(ROOT / relative) == digest, relative
target = ROOT / 'qa/implementation-manifest.json'
assert not target.exists(), 'Frozen manifests are immutable'
files = {}
links = {}
for candidate in sorted(ROOT.rglob('*')):
    relative = str(candidate.relative_to(ROOT))
    if candidate.is_symlink():
        links[relative] = str(candidate.readlink())
    elif candidate.is_file():
        files[relative] = {'sha256': sha(candidate), 'size': candidate.stat().st_size}
manifest = {
    'passed': True, 'observedUTC': datetime.now(timezone.utc).isoformat(),
    'scope': 'Compiled production MenuBridge/NativeProvider/TaskbarShell external fixtures and shared app compatibility',
    'wholeFeatureAccepted': False, 'newNativeGuiAccepted': False,
    'completedRequirementIds': [],
    'report': {'path': str(path.relative_to(ROOT)), 'sha256': sha(path)},
    'checks': report.get('checks'),
    'mutationReport': None if mutation is None else {'path': str(mutation_path.relative_to(ROOT)), 'sha256': sha(mutation_path)},
    'remainingGates': ['merge into latest shared controller candidate',
                       'context-menu mode, gesture origin and lease/focus handling',
                       'atomic popup closure plus native command',
                       'lost broker receipt journal/recovery policy',
                       'full native roadmap, right-click and release acceptance'],
    'files': files, 'symlinks': links,
}
with target.open('x') as stream:
    stream.write(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'passed': True, 'manifest': str(target), 'files': len(files)}))
