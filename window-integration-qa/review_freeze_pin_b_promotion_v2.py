#!/usr/bin/python3
"""Root review and freeze of a location-only private B derivative."""
from pathlib import Path
import datetime, difflib, hashlib, importlib.util, json, os, sys
sys.dont_write_bytecode = True
QA = Path('/home/hoskinson/window-integration-qa')
B = QA / 'pin-max-native-campaign-b-v2'
OLD = Path('/home/hoskinson/window-behavior-spec/pin-max-campaign-b-controller-v1-proposal')
from qa_launch import require_qa_scope
scope = require_qa_scope()
sys.path.insert(0, str(B))
import capture_final_promotion as capture
spec = importlib.util.spec_from_file_location('old_root_review', QA / 'review_pin_campaign_b_controller_v1.py')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
digest = review.digest
assert digest(B/'SOURCE_READY-v2.json') == 'a81b73bcbb26337c1223c5a4e77d4e5160e29eee043064e13d52e3d1c7847a79'
assert digest(B/'SOURCE_INPUTS-v2.json') == '71821827fc620bfa0d4542ae35dd9c9cd55f8043f43432a6d7750c4f07eb1e35'
assert digest(B/'PAIR_READY.json') == '754b35f50549c2ff87c3e19fa0fe1988662d6885f4abec3fb4546f41ddc728b6'
packet = json.loads((B/'SOURCE_INPUTS-v2.json').read_bytes())
review.verify(packet)
ancestor = json.loads((OLD/'frozen-inputs.json').read_bytes())
review.contains(packet, ancestor)
record = json.loads((B/'PROMOTION_RECORD.json').read_bytes())
assert record['allowedFileDeltas'] == ['capture_packet.py', 'PAIR_READY.json']
assert record['allOriginalRuntimeTestBodiesUnchanged'] is True
for row in record['copyRecords']:
    original, copied = Path(row['original']), Path(row['copy'])
    assert capture.initial.meta(original) == dict(sha256=row['sha256'], mode=row['mode'])
    if copied not in {B/'capture_packet.py', B/'PAIR_READY.json'}:
        assert capture.initial.meta(copied) == capture.initial.meta(original)
oldpair = json.loads((OLD/'PAIR_READY.json').read_bytes())
newpair = json.loads((B/'PAIR_READY.json').read_bytes())
for field, value in oldpair.items():
    if field in ['inputs','inputModes']:
        assert all(newpair[field].get(k) == v for k,v in value.items())
    else:
        assert newpair[field] == value, field
assert not (B/'ROOT_NATIVE_GRANT.json').exists()
assert not (B/'frozen-inputs.json').exists()
result = dict(schema='root-pin-b-location-review-v2', scope=scope,
    observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    files=len(packet['inputs']), links=len(packet['symlinks']), directories=len(packet['directoryModes']),
    wholeFailedAncestorFiles=len(ancestor['inputs']), allBytesModesLinksDirectoriesMatch=True,
    runtimeTestProofBodiesUnchanged=True, inheritedHostGuardUnchanged=True,
    reviewed='Complete location capture delta, final capture, actual source/location preflight and pair additions; prior full controller root review conserved.',
    approved='Freeze this exact derivative then one root private B01-B12 attempt after frozen actual location preflight.',
    nativeExecuted=False, fullCampaignBAccepted=False, fullParityAccepted=False)
out = QA/'pin-max-campaign-b-promotion-root-review-v2.json'
capture.initial.publish(out, result)
frozen = capture.inventory()
for path in [out, Path(__file__).resolve()]:
    meta = capture.initial.meta(path)
    frozen['inputs'][str(path)] = meta['sha256']
    frozen['inputModes'][str(path)] = meta['mode']
review.contains(frozen, packet)
review.verify(frozen)
capture.initial.publish(B/'frozen-inputs.json', frozen)
print(json.dumps(dict(result='pass', reviewSHA256=digest(out), manifestSHA256=digest(B/'frozen-inputs.json'),
    files=len(frozen['inputs']), links=len(frozen['symlinks']), directories=len(frozen['directoryModes']), nativeExecuted=False)))
