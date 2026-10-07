"""Retain premature packaging failure; retry unchanged packaging after full build."""
import hashlib, json, pathlib, resource, runpy, sys
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = pathlib.Path('/home/hoskinson/omarchy-windows-parity')
base = pathlib.Path(__file__).parent
original = base / 'prepare_native175_cancelled_snapshot_normal.py'
root = r / 'implementation/warlock-client-provider-native-v175'
assert not root.exists()
build = r / 'implementation/warlock-preview-provider-v140/qa/build-1791399202008242593/report.json'
b = json.loads(build.read_text())
assert b['passed'] and len(b['commands']) == 119
assert all(c['exitCode'] == 0 for c in b['commands'])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for n, h in b['inputs'].items():
    assert sha(r / 'implementation/warlock-preview-provider-v140' / n) == h, n
receipt = base / 'native175-premature-packaging-failure.json'
assert not receipt.exists()
receipt.write_text(json.dumps({
    'owner': 'f6779148-8f5d-4bdf-8a0f-044184e486f2',
    'failedLauncherScope': '02e62c65bb0c4f099635b922e9ee214b',
    'script': str(original), 'scriptSHA256': sha(original),
    'failedAssertion': 'len(reports)==1', 'exitCode': 1,
    'cause': 'Packaging launched before dependent full build completed; no passing report existed.',
    'nativeRootAbsentBeforeRetry': True, 'nativeLaunchedOnFailedAttempt': False,
    'confirmedBuild': str(build), 'confirmedBuildSHA256': sha(build),
    'retryUsesUnchangedPackagingScript': True,
    'nativeAcceptance': False, 'fullReleaseAccepted': False
}, indent=2) + '\n')
sys.path.insert(0, str(r / 'implementation/elm-build-loop-v1'))
import loop
print(loop.write_checkpoint(r, 'f6779148-8f5d-4bdf-8a0f-044184e486f2',
    'implementation/warlock-client-provider-native-v175',
    ['PROGRESS preserve premature Native175 packaging assertion failure before any source copy or native launch. GUI140 full119 now confirmed terminal/pass/current input hashes. Fresh protected retry invokes unchanged original packaging; no oracle/source/deadline changes.'],
    'progress', [str(receipt.relative_to(r))]))
runpy.run_path(str(original), run_name='__main__')
