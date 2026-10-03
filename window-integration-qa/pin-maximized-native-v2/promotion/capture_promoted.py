"""Promotion source inventory only; original runtime/test files untouched."""
from pathlib import Path
import hashlib,json,os,sys
B=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(B/'proposed'))
from capture_packet import inventory
from closure_union import union
original=Path('/home/hoskinson/window-behavior-spec/pin-maximized-collector-v1-proposal')
old=json.loads((original/'source-ready-inputs-final-v1.json').read_bytes())
assert hashlib.sha256((original/'source-ready-final-v1.json').read_bytes()).hexdigest()=='897b64e48757162fda9e349104f43b8df9e2b8d5a4b71a0b8505fbd602122fa7'
assert hashlib.sha256((original/'source-ready-inputs-final-v1.json').read_bytes()).hexdigest()=='35dea348f4836bfa7a2ca2cfe65c9481eb55ff11e9b6044c40e199eedc474310'
row=union(B,[old,inventory()],extra=[original/'source-ready-final-v1.json',original/'source-ready-inputs-final-v1.json',Path('/home/hoskinson/window-integration-qa/pin-max-pair-root-source-review-v1.json')])
assert all(row['inputs'].get(p)==sha and row['inputModes'].get(p)==old['inputModes'][p]for p,sha in old['inputs'].items())
assert all(row['symlinks'].get(p)==value for p,value in old['symlinks'].items())
assert all(row['directoryModes'].get(p)==value for p,value in old['directoryModes'].items())
p=B/'source-ready-inputs-promoted-v2.json'
with p.open('x')as out:json.dump(row,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
p.chmod(0o600)
ready=dict(result='PROMOTED_SOURCE_BUILD_PAIR_READY_FOR_ROOT_REVIEW',stage=str(B),sourceClosure=p.name,sourceClosureSHA256=hashlib.sha256(p.read_bytes()).hexdigest(),inputs=len(row['inputs']),links=len(row['symlinks']),directories=len(row['directoryModes']),originalPairReadySHA256='897b64e48757162fda9e349104f43b8df9e2b8d5a4b71a0b8505fbd602122fa7',originalPairClosureSHA256='35dea348f4836bfa7a2ca2cfe65c9481eb55ff11e9b6044c40e199eedc474310',coreSourceReadySHA256='0235a02ae77f5e144b93e036bf6013d0d0da0954130a184448a5ef4154b2373a',rootPairSourceReviewSHA256='0248bb790c24480a2d93e0e24a90b25ac120d6ef6f4b74c3baf0faa326479e5a',promotionMapping='promotion/mapping.json',onlyRebound='PAIR_READY selected probe path/input key/mode key',all31A3SourcesUnchanged=True,allFunctionalRuntimeAndTestSourcesUnchanged=True,nativeAuthorized=False,nativeAccepted=False,freezePerformed=False,rootOnlyNative=True)
p=B/'source-ready-promoted-v2.json'
with p.open('x')as out:json.dump(ready,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
p.chmod(0o600)
print(json.dumps(dict(path=str(p),readySHA256=hashlib.sha256(p.read_bytes()).hexdigest(),closureSHA256=ready['sourceClosureSHA256'],inputs=ready['inputs'],links=ready['links'],directories=ready['directories'])))
