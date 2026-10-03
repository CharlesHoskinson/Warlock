"""Audit the QA promotion without launching a desktop or freezing sources."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import os
import stat
import sys
sys.path.insert(0, "/home/hoskinson/window-integration-qa/pin-maximized-native-v1/proposed")

QA = Path('/home/hoskinson/window-integration-qa')
BASE = QA / 'pin-maximized-native-v1'
ORIGINAL = Path('/home/hoskinson/window-behavior-spec/pin-maximized-collector-v1-proposal')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


ready_path = BASE / 'source-ready-promoted-v2.json'
assert digest(ready_path) == '0f0d7d5d192fc230c85d537bc40f9e6592030727a510a158c316b0a1c51432cc'
ready = json.loads(ready_path.read_bytes())
closure_path = BASE / ready['sourceClosure']
assert digest(closure_path) == ready['sourceClosureSHA256'] == '665c3d5c90d56ec146c4318985ce0666cf129f7989a278fdde8fea9ce048d4ff'
spec = importlib.util.spec_from_file_location('_root_pin_promotion_source_audit', BASE / 'proposed/run_native.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
current = runner.verify(closure_path)
old = json.loads((ORIGINAL / 'source-ready-inputs-final-v1.json').read_bytes())
for key in ['inputs', 'inputModes', 'symlinks', 'directoryModes']:
    assert all(current[key].get(path) == value for path, value in old[key].items()), key
mapping = json.loads((BASE / 'promotion/mapping.json').read_bytes())
changed = []
for row in mapping['allCopiedFiles']:
    before, after = Path(row['original']), Path(row['promoted'])
    assert digest(before) == row['sha256'] and stat.S_IMODE(before.stat().st_mode) == row['mode']
    if digest(after) != row['sha256'] or stat.S_IMODE(after.stat().st_mode) != row['mode']:
        changed.append(str(after.relative_to(BASE)))
assert set(changed) == {'PAIR_READY.json', 'proposed/freeze_packet.py'}, changed
assert (BASE / 'promotion/freeze_packet-before-snapshot-union.py').read_bytes() == (ORIGINAL / 'proposed/freeze_packet.py').read_bytes()
pair_before = json.loads((ORIGINAL / 'PAIR_READY.json').read_bytes())
expected = copy.deepcopy(pair_before)
previous_probe = expected['probe']
new_probe = str(BASE / 'readonly-probe/libqt-modal-probe.so')
expected['probe'] = new_probe
expected['inputs'][new_probe] = expected['inputs'].pop(previous_probe)
expected['inputModes'][new_probe] = expected['inputModes'].pop(previous_probe)
actual_pair = json.loads((BASE / 'PAIR_READY.json').read_bytes())
assert actual_pair == expected
assert digest(Path(new_probe)) == digest(Path(previous_probe)) == 'cb2828cd9ad93500e0e4ea26a3ec4272d6b8fcc7a0f666369c991adaa4f29762'
runner.pair_binding.read_pair(BASE / 'PAIR_READY.json')
for name in ['native_cases.py', 'input_episode.py', 'case_authority.py', 'output_readiness.py', 'private-controls.lua']:
    assert (BASE / name).read_bytes() == (ORIGINAL / name).read_bytes()
for name in ['candidate_host.py', 'host_observation.py', 'pair_binding.py', 'run_native.py', 'closure_union.py', 'capture_packet.py', 'private_output_host.py']:
    assert (BASE / 'proposed' / name).read_bytes() == (ORIGINAL / 'proposed' / name).read_bytes()

report = dict(result='pass', inputs=len(current['inputs']), links=len(current['symlinks']),
              directories=len(current['directoryModes']), retainedOriginalInputs=len(old['inputs']),
              retainedOriginalLinks=len(old['symlinks']), retainedOriginalDirectories=len(old['directoryModes']),
              copiedFiles=len(mapping['allCopiedFiles']), changed=changed,
              sourceReadySHA256=digest(ready_path), sourceClosureSHA256=digest(closure_path),
              originalRuntimeAndTestBodiesExact=True, selectedProbeBytesModesExact=True,
              pairMetadataRebindingExact=True, sourceOnlyFreezerUnionReviewed=True,
              normalClosureObservationRequired=True, sourceAndPromotionAccepted=True,
              nativeAuthorized=False, nativeAccepted=False,
              remaining=['Root freeze and exact frozen-source validation', 'Original14 native campaign',
                         'Separate native MAX/focus/scroll/transfer campaign'])
destination = QA / 'pin-max-promotion-root-source-review-v1.json'
with destination.open('x') as output:
    json.dump(report, output, indent=2)
    output.write('\n')
    output.flush()
    os.fsync(output.fileno())
print(json.dumps({**report, 'review': str(destination), 'reviewSHA256': digest(destination)}))
