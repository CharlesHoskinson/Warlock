"""Hold the source-only native regression after protected CPU preflight."""
import hashlib
import json
import resource
import sys
from pathlib import Path
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
preflight_path = Path(sys.argv[1])
source_path = Path(sys.argv[2])
preflight, source = [json.loads(p.read_text()) for p in [preflight_path, source_path]]
assert preflight['passed'] and source['passed']
assert preflight['nativeAcceptance'] is False and source['nativeAcceptance'] is False
assert sha(ROOT / 'qa/native.py') == preflight['runnerSHA256'] == source['runnerSHA256']
for path, wanted in preflight['selectedInputs'].items():
    assert sha(path) == wanted, path
for relative, wanted in preflight['artifacts'].items():
    assert sha(preflight_path.parent / relative) == wanted, relative
for path, wanted in source['inputs'].items():
    assert sha(path) == wanted, path
host_root = ROOT.parents[1] / 'implementation/elm-geometry-staged-menu-native-v77'
host_manifest_path = host_root / 'qa/held-source-manifest.json'
host_manifest_sha = 'd5a9c11862d587175890cc814e852f1f73cb3481fa497883e7e4941236da6559'
assert sha(host_manifest_path) == host_manifest_sha
host_manifest = json.loads(host_manifest_path.read_text())
assert host_manifest['sourceHeld'] and host_manifest['evidenceIntegrityPassed']
for relative, row in host_manifest['files'].items():
    path = host_root / relative
    assert sha(path) == row['sha256'] and path.stat().st_size == row['size'], relative
destination = ROOT / 'qa/held-source-manifest.json'
files = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'size': p.stat().st_size}
         for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p != destination}
manifest = {'sourceHeld': True, 'evidenceIntegrityPassed': True,
            'nativeAcceptance': False, 'releaseAcceptance': False,
            'scope': 'CPU syntax/exact V55 campaign comparison and owning tuple preflight only; original 96 native checks and 7 pixel stages not yet rerun',
            'files': files, 'preflightReport': str(preflight_path),
            'preflightReportSHA256': sha(preflight_path),
            'sourceCheckReport': str(source_path), 'sourceCheckReportSHA256': sha(source_path),
            'hostManifest': str(host_manifest_path), 'hostManifestSHA256': host_manifest_sha,
            'selectedInputs': preflight['selectedInputs']}
destination.write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'passed': True, 'manifest': str(destination), 'sha256': sha(destination), 'files': len(files)}))
