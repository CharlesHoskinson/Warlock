"""Protected syntax and immutable campaign comparison; never imports the runner."""
import ast
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
ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT.parents[1] / 'implementation/elm-geometry-effect-native-v55/qa/native.py'
OUT = ROOT / 'qa' / ('source-check-' + str(time.time_ns()))
OUT.mkdir(mode=0o700)
report = {'passed': False, 'nativeAcceptance': False,
          'scope': 'Exact original function and campaign AST comparison; original 96 checks and 7 pixel stages require fresh native execution'}
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(node):
    return ast.dump(node, include_attributes=False)
try:
    assert sha(ORIGINAL) == 'e30dc4d4703454b3d767ac4c40992ea4755f34b2edec91b0d3dba3723988c3ae'
    assert ORIGINAL.read_bytes() == (ROOT / 'qa/original-v55-native.py').read_bytes()
    runner = ROOT / 'qa/native.py'
    old, new = ast.parse(ORIGINAL.read_text()), ast.parse(runner.read_text())
    for path in sorted((ROOT / 'qa').glob('*.py')):
        ast.parse(path.read_text())
    old_functions = {n.name: dump(n) for n in old.body if isinstance(n, ast.FunctionDef)}
    new_functions = {n.name: dump(n) for n in new.body if isinstance(n, ast.FunctionDef)}
    assert old_functions == new_functions
    old_try = next(n for n in old.body if isinstance(n, ast.Try))
    new_try = next(n for n in new.body if isinstance(n, ast.Try))
    old_campaign = next(n for n in old_try.body if isinstance(n, ast.With))
    new_campaign = next(n for n in new_try.body if isinstance(n, ast.With))
    assert dump(old_campaign) == dump(new_campaign)
    assert [dump(n) for n in old_try.handlers] == [dump(n) for n in new_try.handlers]
    assert [dump(n) for n in old_try.finalbody] == [dump(n) for n in new_try.finalbody]
    assertions = [dump(n) for n in ast.walk(old_campaign) if isinstance(n, ast.Assert)]
    checks = [dump(n) for n in ast.walk(old_campaign) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'check']
    report.update(passed=True, runnerSHA256=sha(runner), originalSHA256=sha(ORIGINAL),
                  exactFunctions=list(old_functions), exactNativeCampaign=True,
                  exactTeardown=True, unchangedCampaignAssertions=len(assertions),
                  unchangedCampaignCheckCallsites=len(checks), originalNativeChecks=96,
                  originalPixelStages=7)
except Exception as error:
    report['error'] = repr(error)
report['inputs'] = {str(p): sha(p) for p in [ORIGINAL, *sorted((ROOT / 'qa').glob('*.py'))]}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'report': str(OUT / 'report.json'), 'error': report.get('error')}))
raise SystemExit(not report['passed'])
