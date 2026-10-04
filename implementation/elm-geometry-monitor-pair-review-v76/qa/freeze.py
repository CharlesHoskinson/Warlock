"""Record the held read-only V75 review packet without changing its upstream."""
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
PAIR = ROOT.parents[1] / 'implementation/elm-geometry-monitor-owning-pair-v75'
REPORT = ROOT / 'qa/review-1791106672284100816/report.json'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
report = json.loads(REPORT.read_text())
assert report['passed'] and report['nativeAcceptance'] is False
for relative, row in report['pairInventory'].items():
    path = PAIR / relative
    assert path.is_file() and not path.is_symlink()
    assert sha(path) == row['sha256'] and path.stat().st_size == row['size'], relative
assert set(report['pairInventory']) == {str(p.relative_to(PAIR)) for p in PAIR.rglob('*') if p.is_file() and not p.is_symlink()}
for path, wanted in report['verified'].items():
    assert sha(Path(path)) == wanted, path
destination = ROOT / 'qa/held-source-manifest.json'
files = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'size': p.stat().st_size}
         for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p != destination}
manifest = {'sourceHeld': True, 'evidenceIntegrityPassed': True,
            'nativeAcceptance': False, 'releaseAcceptance': False,
            'scope': 'Independent V75/V73 byte integrity review only; V30 AQ runtime maps and actual menu campaign remain required',
            'report': str(REPORT), 'reportSHA256': sha(REPORT), 'files': files,
            'pairRoot': str(PAIR), 'pairFiles': report['pairInventory']}
destination.write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'passed': True, 'manifest': str(destination), 'sha256': sha(destination),
                  'reviewFiles': len(files), 'pairFiles': len(report['pairInventory'])}))
