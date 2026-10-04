"""Freeze orchestration evidence without asserting desktop acceptance."""
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

report_path = sorted((ROOT/'qa').glob('test-*/report.json'))[-1]
report = json.loads(report_path.read_text())
assert report['passed'] and not report.get('error')
assert all(check['passed'] for check in report['checks'])
for relative, digest in report['inputs'].items():
    assert sha(REPO/relative) == digest, relative
    assert sha(report_path.parent/'inputs'/relative) == digest, 'Frozen '+relative
files = {}
links = {}
manifest = ROOT/'qa/coordinator-manifest.json'
assert not manifest.exists(), 'Preserve frozen manifests; create a new derivative'
for path in sorted(ROOT.rglob('*')):
    if path == manifest:
        continue
    relative = str(path.relative_to(REPO))
    if path.is_symlink():
        links[relative] = str(path.readlink())
    elif path.is_file():
        files[relative] = sha(path)
companions = [REPO/'AGENTS.md', REPO/'docs/elm-roadmap/BUILD-LOOP.md',
              REPO/'implementation/elm-menu-lifecycle-v2/SCOPE.md']
companions.extend(sorted((REPO/'docs/elm-roadmap/delivery/build-loop-events').glob('*.json')))
for path in companions:
    files[str(path.relative_to(REPO))] = sha(path)
value = {'passed': True, 'observedUTC': datetime.now(timezone.utc).isoformat(),
         'scope': report['scope'], 'wholeSystemAccepted': False,
         'nativeGuiRun': False, 'completedRequirementIds': [],
         'checks': len(report['checks']),
         'report': {'path': str(report_path.relative_to(REPO)), 'sha256': sha(report_path)},
         'files': files, 'symlinks': links}
manifest.write_text(json.dumps(value, indent=2)+'\n')
print(json.dumps({'passed': True, 'checks': value['checks'], 'files': len(files),
                  'manifest': str(manifest)}))
