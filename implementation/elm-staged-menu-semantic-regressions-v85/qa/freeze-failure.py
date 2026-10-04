"""Preserve failed CPU semantic regression evidence, without acceptance."""
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
REPORT = ROOT / 'qa/replay-1791107849175752252/report.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r = json.loads(REPORT.read_text())
assert r['passed'] is False
assert r['stagedSuites']['menu']['casesPassed'] == 78
assert r['stagedSuites']['refresh']['casesPassed'] == 21
assert r['stagedSuites']['geometry']['casesPassed'] == 52
assert r['stagedSuites']['geometry']['failedCases'] == ['taskbar-origin Unknown prevents geometry namespace bypass']
for relative, wanted in r['artifacts'].items():
    assert sha(REPORT.parent / relative) == wanted, relative
for relative, wanted in r['sourceInputs'].items():
    assert sha(Path(r['sourceRoot']) / relative) == wanted, relative
for relative, wanted in r['qaInputs'].items():
    assert sha(ROOT / relative) == wanted, relative
destination = ROOT / 'qa/failed-source-manifest.json'
files = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'size': p.stat().st_size}
         for p in sorted(ROOT.rglob('*')) if p.is_file() and not p.is_symlink() and p != destination}
manifest = {'sourceHeld': True, 'evidenceIntegrityPassed': True,
            'semanticAcceptance': False, 'nativeAcceptance': False, 'releaseAcceptance': False,
            'scope': 'Held failed full staged semantic campaign; no expected-green exemptions',
            'report': str(REPORT), 'reportSHA256': sha(REPORT), 'files': files,
            'originalFailedIdentity': 'taskbar-origin Unknown prevents geometry namespace bypass',
            'stagedResults': r['stagedSuites'], 'productionSource': r['sourceRoot']}
destination.write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'passed': True, 'failurePreserved': True, 'manifest': str(destination),
                  'sha256': sha(destination), 'files': len(files)}))
