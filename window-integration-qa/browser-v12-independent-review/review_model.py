#!/usr/bin/env python3
"""Read-only refinement counterexamples; no runtime authority or process launch."""
from pathlib import Path
import hashlib
import json
import re

root = Path('/home/hoskinson/window-integration-qa/browser-files-flow-v12')
out = Path(__file__).resolve().parent
names = ['V12_CONTRACT.md', 'runtime_metrics.qnt', 'runtime_metrics_test.qnt',
         'metrics-formal-before-implementation.json', 'metrics_diagnostic.py',
         'retained-v11-failure/root-metrics-attribution.json']
before = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}
# The first model is now retained after the root's strengthened derivative.
# Replay its exact archived state instead of expecting current candidate schema.
model = root / 'metrics-first-model/runtime_metrics.qnt'
source = model.read_text()
schema = source.split('type Witness = {', 1)[1].split('}', 1)[0]
fields = re.findall(r'(\w+)\s*:\s*(bool|int|str)', schema)
assert dict(fields)['inode'] == 'bool'
assert dict(fields)['profile'] == 'bool'
assert dict(fields)['mount'] == 'bool'
assert dict(fields)['currentSnapshot'] == 'bool'
assert 'fdNumber' not in dict(fields)
assert re.search(r'w\s*==\s*before', source)

# Both concrete witnesses satisfy every abstract property. Projecting them to
# the current model loses an exact identity change; this is a refinement gap,
# not a failed allProps trace in the current (weaker) state space.
base = dict(rootPID=1847929, rootStart=77, fdNumber=7, device=84, inode=322538,
            mountID=346, profileInode=80, parentInode=81, rawMapsHash='batch-A',
            mappingLine='line-A', fullFlags=524290, target='owned-A')
changes = [dict(fdNumber=8), dict(inode=322539), dict(device=85),
           dict(mountID=347), dict(profileInode=82), dict(parentInode=83),
           dict(rawMapsHash='batch-B'), dict(mappingLine='line-B'),
           dict(fullFlags=2), dict(target='owned-B')]
abstract_good = {name: True if kind == 'bool' else None for name, kind in fields}
abstract_good.update(lifetime=77, fdCount=1, fdAccess=2, nlink=0, mode=384,
                     size=4194304, offset=0, length=4194304, permissions='rw-s')
examples = []
for change in changes:
    after = base | change
    assert base != after
    # No current Witness field carries any changed exact identity above.
    projected_before = dict(abstract_good)
    projected_after = dict(abstract_good)
    assert projected_before == projected_after
    examples.append(dict(changed=list(change), concreteBefore=base,
                         concreteAfter=after, abstractWitnessesEqual=True,
                         modelVerifyAndConfirmCanAcceptBoth=True))
after = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}
assert before == after
report = dict(result='historical-first-model-refinement-counterexamples',
              sourceStageOnly=True, rootSourcesUnchanged=True,
              sourceSHA256=before, historicalModelSHA256=hashlib.sha256(model.read_bytes()).hexdigest(), projectionCounterexamples=examples,
              counterexampleCount=len(examples), nativeExecuted=False,
              runtimeAuthorityGranted=False, modelInvariantViolationClaimed=False)
(out / 'historical-model-replay.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({key: report[key] for key in ('result', 'counterexampleCount',
                 'rootSourcesUnchanged', 'nativeExecuted')}))
