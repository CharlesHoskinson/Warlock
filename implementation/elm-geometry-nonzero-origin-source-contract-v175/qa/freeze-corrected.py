"""Verify and hold the read-only nonzero XDG origin proposal."""
import hashlib, json, resource, sys
from pathlib import Path
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
ledger = json.loads((ROOT / 'reviewed-inputs.json').read_text())
prior = json.loads((REPO / 'implementation/elm-geometry-constraint-coordinate-review-v155/reviewed-inputs.json').read_text())['files']
for rel, row in ledger['files'].items():
    p = REPO / rel
    assert sha(p) == row['sha256'], rel
    assert p.stat().st_size == row['size'], rel
    if 'capture' in row:
        capture = ROOT / row['capture']
        assert sha(capture) == row['sha256'], rel
        count = len(capture.read_text().splitlines())
        assert all(1 <= lo <= hi <= count for lo, hi in row['lineAnchors']), rel
    if str(p) in prior:
        assert row['sha256'] == prior[str(p)]['sha256'], rel
pair = REPO / 'implementation/elm-parent-first-anchor-pair-v90/qa/build-1791107369559431070/report.json'
data = json.loads(pair.read_text())
math = {}
for path, digest in data['dependencies'].items():
    if '/hyprutils/math/' in path:
        p = Path(path)
        assert sha(p) == digest, path
        math[path] = {'sha256': digest, 'size': p.stat().st_size}
lib = '/usr/lib/libhyprutils.so.0.14.2'
assert sha(Path(lib)) == data['linkedLibraries'][lib]
math[lib] = {'sha256': sha(Path(lib)), 'size': Path(lib).stat().st_size}
character = REPO / 'implementation/elm-geometry-conversion-edge-characterization-v166/component-manifest.json'
manifest = json.loads(character.read_text())
report = Path(manifest['selectedReport'])
assert sha(report) == manifest['selectedReportSHA256']
assert json.loads(report.read_text())['runs']['actual']['checks'] == 23
assert json.loads(report.read_text())['passed']
report_out = ROOT / 'qa/verification.json'
assert not report_out.exists()
report_out.write_text(json.dumps({'passed': True, 'scope': 'Source/capture/hash/line integrity and prior paired math evidence; no new conversion/native/policy tests', 'sources': len(ledger['files']), 'pairedMathDependencies': math, 'priorCharacterization': str(report), 'priorCharacterizationSHA256': sha(report), 'nativeAcceptance': False, 'policyAcceptance': False, 'modelAcceptance': False}, indent=2) + '\n')
target = ROOT / 'component-manifest.json'
assert not target.exists()
files = {str(p.relative_to(ROOT)): {'sha256': sha(p), 'size': p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p != target}
result = {'sourceHeld': True, 'evidenceIntegrityPassed': True, 'scope': 'Read-only proposed nonzero-origin transform contract; arithmetic characterized, GTK render/input and source/object provenance remain open', 'nativeAcceptance': False, 'policyAcceptance': False, 'modelAcceptance': False, 'files': files, 'reviewedInputs': ledger['files'], 'pairedMathDependencies': math}
target.write_text(json.dumps(result, indent=2) + '\n')
for rel, row in files.items():
    assert sha(ROOT / rel) == row['sha256'], rel
print(json.dumps({'passed': True, 'files': len(files), 'manifest': str(target), 'manifestSHA256': sha(target)}))
