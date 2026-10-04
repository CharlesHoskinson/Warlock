"""Hold actual historical oracle audit without conferring new acceptance."""
import hashlib
import json
import resource
import sys
from pathlib import Path
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
root = Path(__file__).resolve().parents[1]
manifest = root / 'component-manifest.json'
assert not manifest.exists()
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
report_path = root / 'qa/audit-1791144620244152851/report.json'
report = json.loads(report_path.read_text())
assert report['passed'] and not report['nativeAcceptance'] and not report['currentTupleQualified']
assert all(row['passed'] for row in report['checks'])
assert sha(root / 'qa/audit.py') == report['sourceSHA256']
external = {}
for row in report['records']:
    for path, digest in [(row['source'], row['sourceSHA256']),
                         (row['historicalReport'], row['reportSHA256'])]:
        assert sha(path) == digest
        external[path] = digest
files = {str(p.relative_to(root)): {'sha256': sha(p), 'size': p.stat().st_size}
         for p in sorted(root.rglob('*')) if p.is_file()}
manifest.write_text(json.dumps({'sourceHeld': True, 'evidenceIntegrityPassed': True,
    'nativeAcceptance': False, 'currentTupleQualified': False,
    'scope': 'Original100 and rebound432 actual historical08/09/10 oracle lineage only',
    'files': files, 'externalFiles': external, 'report': str(report_path)}, indent=2) + '\n')
print(json.dumps({'passed': True, 'manifest': str(manifest), 'sha256': sha(manifest)}))
