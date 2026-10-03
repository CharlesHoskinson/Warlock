#!/usr/bin/python3
"""Freeze only the exact root-reviewed B component and review provenance."""
import hashlib
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from qa_launch import require_qa_scope
require_qa_scope()
B = Path('/home/hoskinson/window-behavior-spec/pin-max-campaign-b-controller-v1-proposal')
QA = Path('/home/hoskinson/window-integration-qa')
def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert digest(B / 'SOURCE_READY.json') == 'c0a0d295bf69335a0fd442371f69e44c4169778df6fb8541c2dbcc64a73fc5a2'
assert digest(B / 'SOURCE_INPUTS.json') == '13d259af53cd2c927623ec1e670e2ac3f0c6183ccbd109e5924fbf3bcfe1367d'
review = QA / 'pin-max-campaign-b-controller-root-source-review-v1.json'
assert digest(review) == '278eba9674cea2fe159e3f24ca521984ca11ba857e7cdd4ce600a3f312550346'
sys.path.insert(0, str(B))
import capture_packet as capture
row = capture.inventory()
for path in [review, QA / 'review_pin_campaign_b_controller_v1.py', Path(__file__).resolve()]:
    metadata = capture.meta(path)
    row['inputs'][str(path)] = metadata['sha256']
    row['inputModes'][str(path)] = metadata['mode']
capture.publish(B / 'frozen-inputs.json', row)
print(dict(manifest=str(B / 'frozen-inputs.json'), sha256=digest(B / 'frozen-inputs.json'),
           inputs=len(row['inputs']), links=len(row['symlinks']), directories=len(row['directoryModes'])))
