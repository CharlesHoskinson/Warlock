"""Exact original recovery-region comparison with explicit rebinding exceptions."""
import difflib
import hashlib
import json
import resource
import sys
import time
from pathlib import Path
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
root = Path(__file__).resolve().parents[1]
repo = root.parents[1]
out = root / 'qa' / ('compare-' + str(time.time_ns()))
out.mkdir()
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
lineage = repo / 'implementation/elm-gtk-recovery-oracle-lineage-v261/component-manifest.json'
assert sha(lineage) == '92f4fcba7051d3b22fa924f44e0a264700dfdea8bd2da1c5cc156dbb329a69bb'
packet = json.loads(lineage.read_text())
for path, expected in packet['externalFiles'].items():
    assert sha(path) == expected
def region(name):
    path = repo / 'implementation' / name / 'qa/native.py'
    body = path.read_text()
    begin = body.index('    # Reconnect occurs after a saved native MAX origin exists.')
    end = body.index("    report['scenarios'].append('GEOMETRY-MENU-10')", begin)
    return path, body[begin:body.index('\n', end)]
a_path, original = region('elm-geometry-family-menu-receipt-cleanup-native-v100')
b_path, rebound = region('elm-geometry-lifetime-retirement-native-v432')
normalized = rebound
config = ",'runtime':config['runtime'],'instance':config['instance']"
assert normalized.count(config) == 1
normalized = normalized.replace(config, '', 1)
diagnostic = next(line for line in normalized.splitlines(True)
                  if line.startswith("    report['retirementAddressDiagnostic']="))
assert normalized.count(diagnostic) == 1
normalized = normalized.replace(diagnostic, '', 1)
identity = "replacement['stableId']!=report['fixtureIdentity']['stableId']"
assert normalized.count(identity) == 1
normalized = normalized.replace(identity, "replacement['address']!=report['fixtureIdentity']['address']", 1)
assert normalized == original, 'Unexpected recovery operation/oracle/deadline change'
assert normalized.replace('deadline=time.monotonic()+6', 'deadline=time.monotonic()+7', 1) != original
diff = ''.join(difflib.unified_diff(original.splitlines(True), rebound.splitlines(True),
                                  fromfile=str(a_path), tofile=str(b_path)))
(out / 'region.diff').write_text(diff)
(out / 'compare.py').write_bytes(Path(__file__).read_bytes())
report = {'passed': True, 'nativeAcceptance': False, 'currentTupleQualified': False,
          'scope': 'Exact extracted08–10 region only, with explicit runtime/instance and stable-ID differences',
          'sourceSHA256': sha(__file__), 'lineageManifestSHA256': sha(lineage),
          'originalSource': str(a_path), 'originalSourceSHA256': sha(a_path),
          'reboundSource': str(b_path), 'reboundSourceSHA256': sha(b_path),
          'otherRegionBytesIdentical': True, 'deadlineMutationRejected': True,
          'wholeRunnerEquivalent': False}
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
manifest = root / 'component-manifest.json'
assert not manifest.exists()
files = {str(p.relative_to(root)): {'sha256': sha(p), 'size': p.stat().st_size}
         for p in sorted(root.rglob('*')) if p.is_file()}
manifest.write_text(json.dumps({'sourceHeld': True, 'evidenceIntegrityPassed': True,
    'nativeAcceptance': False, 'currentTupleQualified': False,
    'files': files, 'externalFiles': {str(lineage): sha(lineage),
    str(a_path): sha(a_path), str(b_path): sha(b_path)}, 'report': str(out / 'report.json')}, indent=2) + '\n')
print(json.dumps({'passed': True, 'report': str(out / 'report.json'),
                  'manifestSHA256': sha(manifest)}))
