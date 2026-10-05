"""Source closure for original lost-receipt pixel/input journeys on current GUI."""
import ast, hashlib, json, os, resource, stat, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs = {}
def check(path, digest):
    path = Path(path)
    assert path.is_file() and sha(path) == digest, str(path)
    inputs[str(path)] = digest
parent = REPO / 'implementation/elm-focus-recovery-renderer-held-v356/acceptance-manifest.json'
check(parent, 'a687a2efa8cffa5c141ea82efc7138a1c10ba44768e6febc2bb11d534cb96e3b')
held = json.loads(parent.read_text())
assert held['passed'] and held['currentRendererCohortNativeChecks'] == 40 and not held['fullReleaseAccepted']
for row in held['files']:
    path = REPO / row['path']
    assert stat.S_IMODE(path.lstat().st_mode) == row['mode']
    if 'symlink' in row:
        assert path.is_symlink() and os.readlink(path) == row['symlink']
    else:
        assert not path.is_symlink() and path.stat().st_size == row['size']
        check(path, row['sha256'])
base_review = REPO / 'implementation/elm-focus-recovery-renderer-native-v355/qa/preflight.json'
review = json.loads(base_review.read_text())
assert review['passed'] and review['pair'] == held['pair'] and review['originalStaticCheckCalls'] == 33
for path, digest in review['inputs'].items():
    check(path, digest)
check(base_review, sha(base_review))
previous = REPO / 'implementation/elm-namespaced-minimize-lost-v243/qa/native.py'
source = ROOT / 'qa/native.py'
expected = previous.read_text()
amendments = json.loads((ROOT / 'qa/source-amendments.json').read_text())
for before, after in amendments:
    assert before in expected
    expected = expected.replace(before, after)
assert source.read_text() == expected
old_tree = ast.parse(previous.read_text())
tree = ast.parse(source.read_text())
functions = lambda t: {n.name: n for n in ast.walk(t) if isinstance(n, ast.FunctionDef)}
old_functions, new_functions = functions(old_tree), functions(tree)
for name in ('pixels', 'input_state', 'key_recipient', 'native_minimized', 'application_state', 'click', 'window_facts'):
    assert ast.dump(old_functions[name], include_attributes=False) == ast.dump(new_functions[name], include_attributes=False), name
checks = lambda t: [n for n in ast.walk(t) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'check']
old_checks = checks(old_tree)
new_checks = checks(tree)
additions = {'actualPostRetirementReadsReleaseExactHistoricalUnknown', 'actualDurableReleaseAnchorsUnknownWithoutNativeOutcomeRelabel'}
name = lambda n: n.args[0].value if isinstance(n.args[0], ast.Constant) else ast.dump(n.args[0], include_attributes=False)
old_names = [name(n) for n in old_checks]
assert [name(n) for n in new_checks if name(n) not in additions] == old_names
assert len(new_checks) == len(old_checks) + 2 and {name(n) for n in new_checks if name(n) in additions} == additions
for old, new in zip(old_checks, [n for n in new_checks if name(n) not in additions]):
    if name(old) == 'replacementReceivesFreshlyBoundOriginalUnknownIntent':
        old = ast.parse("check('replacementReceivesFreshlyBoundOriginalUnknownIntent',uncertain['binding']==fresh_binding and uncertain['record']['intent']==old_request['intent'] and uncertain['record']['binding']==old_binding and uncertain['record']['status']=='Unknown',frame=uncertain)").body[0].value
    assert ast.dump(old, include_attributes=False) == ast.dump(new, include_attributes=False), name(old)
code = source.read_text()
assert "FAULT='unread'" in code
assert ("OPERATION='restore'" if 'restore-unread' in ROOT.name else "OPERATION='minimize'") in code
assert code.count('signal.pidfd_send_signal(renderer_fd,signal.SIGKILL,None,0)') == 2
assert 'def wait(fn,seconds=6):' in code and "if time.monotonic()>=until:raise RuntimeError('Unchanged observation deadline')" in code
assert "if loaded:wait(lambda:s.data('clients')==[])" in code
# Preserve the original oracle and strengthen final unload with an empty census.
assert "xwayland={enabled=false}" in code and 'ELM_WINDOW_RECOVERY_FAULT' in code
for name in ('inspection.py', 'sampling.py'):
    assert (ROOT / 'qa' / name).read_bytes() == (previous.parent / name).read_bytes()
    check(previous.parent / name, sha(previous.parent / name))
assert (ROOT / 'fixture.py').read_bytes() == (previous.parent.parent / 'fixture.py').read_bytes()
bus = REPO / 'implementation/elm-focus-recovery-renderer-native-v355/qa/bus_policy.py'
assert (ROOT / 'qa/bus_policy.py').read_bytes() == bus.read_bytes()
check(bus, sha(bus))
for path in (source, previous, ROOT / 'SPEC.md', ROOT / 'fixture.py', ROOT / 'qa/source-amendments.json', *sorted((ROOT / 'qa').glob('*.py'))):
    check(path, sha(path))
report = {'passed': True, 'sourceHeld': True, 'nativeAcceptance': False, 'fullReleaseAccepted': False, 'pair': held['pair'], 'originalStaticCheckCalls': len(old_checks), 'additiveStaticCheckCalls': 2, 'inputs': inputs, 'scope': 'Original243/244 namespaced minimize/restore withheld before carrier write/broker read, actual unchanged pixels/input/restart/no replay/explicit current-state action/second failure cancellation. Actual current349(same333)/Core205/594/AQ155; keyed C admission path, full Unknown DTO, fresh proof/read/durable release additions. Original check calls retained with strict DTO expansion only; PIDFD and absolute6s strengthened. No native result.'}
with (ROOT / 'qa/preflight.json').open('x') as stream:
    stream.write(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': True, 'inputs': len(inputs), 'originalStaticCheckCalls': len(old_checks), 'additiveStaticCheckCalls': 2}))
