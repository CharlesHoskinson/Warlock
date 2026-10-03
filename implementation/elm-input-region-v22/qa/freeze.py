"""Freeze fixture and reviewed runner against the unchanged V20 native tuple."""
import hashlib
import json
from pathlib import Path
import resource

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT.parent / 'elm-surface-facts-v20'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
pair = CORE / 'qa/build-pair-manifest.json'
manifest = json.loads(pair.read_text())
assert manifest['passed']
for relative, digest in manifest['files'].items():
    assert sha(CORE / relative) == digest, relative
for artifact in manifest['nativePair'].values():
    assert sha(Path(artifact['path'])) == artifact['sha256']
paths = [ROOT / 'birth_fixture.py', ROOT / 'pointer_fifo.py', ROOT / 'qa/lifecycle_native.py', Path(__file__)]
output = {'scope': 'Fixture/runner source closure only; native acceptance pending',
          'nativePairManifest': str(pair), 'nativePairManifestSHA256': sha(pair),
          'files': {str(p.relative_to(ROOT)): sha(p) for p in paths}}
destination = ROOT / 'qa/source-manifest.json'
assert not destination.exists(), 'Preserve prior frozen packet'
destination.write_text(json.dumps(output, indent=2)+'\n')
print(destination)
