"""Freeze the exact successful compiled replay closure; no native acceptance."""
import hashlib
import json
import resource
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
report_path = sorted((ROOT / 'qa').glob('replay-*/report.json'))[-1]
report = json.loads(report_path.read_text())
assert report['passed'] and not report.get('error')
for relative, digest in report['inputs'].items():
    assert sha(ROOT / relative) == digest, relative
    assert sha(report_path.parent / 'inputs' / relative) == digest, relative
manifest = {'passed': True, 'observedUTC': datetime.now(timezone.utc).isoformat(),
            'scope': report['scope'], 'wholeFeatureAccepted': False,
            'nativeAccepted': False, 'completedRequirementIds': [],
            'replayReport': {'path': str(report_path.relative_to(ROOT)), 'sha256': sha(report_path)},
            'elmChecks': report['checks'], 'files': report['inputs']}
(ROOT / 'qa/slice-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Frozen compiled Elm context-menu replay evidence; native integration remains open')
