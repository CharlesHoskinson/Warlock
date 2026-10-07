"""Preserve checkpoint-path failure and invoke original packager after build."""
import hashlib, json, pathlib, resource, runpy, sys
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
r = pathlib.Path('/home/hoskinson/omarchy-windows-parity')
base = pathlib.Path(__file__).parent
receipt = base / 'native175-premature-packaging-failure.json'
d = json.loads(receipt.read_text())
original = pathlib.Path(d['script'])
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(original) == d['scriptSHA256']
assert sha(pathlib.Path(d['confirmedBuild'])) == d['confirmedBuildSHA256']
assert not (r / 'implementation/warlock-client-provider-native-v175').exists()
failed = base / 'native175-retry-checkpoint-failure.json'
assert not failed.exists()
failed.write_text(json.dumps({
    'owner': d['owner'], 'scope': 'd2639f2c0fef4795b685c3e435504544',
    'scriptSHA256': sha(base / 'prepare_native175_after_confirmed_build.py'),
    'exitCode': 1, 'failure': 'Checkpoint referenced nonexistent Native175 slice before packaging.',
    'nativeRootAbsent': True, 'nativeLaunched': False,
    'correction': 'Checkpoint uses existing provider140 source; original packager unchanged.',
    'nativeAcceptance': False, 'fullReleaseAccepted': False
}, indent=2) + '\n')
sys.path.insert(0, str(r / 'implementation/elm-build-loop-v1'))
import loop
print(loop.write_checkpoint(r, d['owner'], 'implementation/warlock-preview-provider-v140',
    ['PROGRESS preserve premature packaging and nonexistent checkpoint-path failures before any source/native launch. Confirmed full119 hashes; invoke original unchanged Native175 packaging. Existing source slice used for checkpoint.'],
    'progress', [str(receipt.relative_to(r)), str(failed.relative_to(r))]))
runpy.run_path(str(original), run_name='__main__')
