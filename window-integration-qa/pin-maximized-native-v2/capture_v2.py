"""Fresh source-only union of full frozen V1 plus V2 observational refinement."""
from pathlib import Path
import hashlib,json,os,sys
B=Path(__file__).resolve().parent
sys.path.insert(0,str(B/'proposed'))
from capture_packet import inventory
from closure_union import union
OLD=Path('/home/hoskinson/window-integration-qa/pin-maximized-native-v1')
old=json.loads((OLD/'frozen-inputs.json').read_bytes())
assert hashlib.sha256((OLD/'frozen-inputs.json').read_bytes()).hexdigest()=='bbcca0ea7a3501c2984156d99df54e3b5c5dfe8339b35a3a9deab79eecc95e37'
extra=[OLD/'frozen-inputs.json',OLD/'frozen-checkpoint.json',OLD/'source-ready-promoted-v2.json',OLD/'source-ready-inputs-promoted-v2.json',Path('/home/hoskinson/window-integration-qa/pin-max-promotion-root-source-review-v1.json'),Path('/home/hoskinson/window-integration-qa/pin-max-native14-root-failure-audit-v1.json')]
for base in [OLD/'attempt-1',B/'retained-v1/attempt-1']:
 for name in ['report.json','host/host-normal-closure.json','host/host-evidence.json','native/cases.json']:extra.append(base/name)
row=union(B,[old,inventory()],extra=extra)
assert all(row['inputs'].get(k)==v and row['inputModes'].get(k)==old['inputModes'][k]for k,v in old['inputs'].items())
assert all(row['symlinks'].get(k)==v for k,v in old['symlinks'].items())
assert all(row['directoryModes'].get(k)==v for k,v in old['directoryModes'].items())
p=B/'source-ready-inputs-final-v1.json'
fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
ready=dict(result='SOURCE_READY_FOR_ROOT_REVIEW',stage=str(B),sourceClosure=p.name,sourceClosureSHA256=hashlib.sha256(p.read_bytes()).hexdigest(),inputs=len(row['inputs']),links=len(row['symlinks']),directories=len(row['directoryModes']),ancestorManifestSHA256='bbcca0ea7a3501c2984156d99df54e3b5c5dfe8339b35a3a9deab79eecc95e37',conservation='conservation-v2.json',formal='formal-before-runtime-final.json',focusedCPU=26,inheritedA3CPU=43,coreSourceReadySHA256='0235a02ae77f5e144b93e036bf6013d0d0da0954130a184448a5ef4154b2373a',corePolicyBuild='59a1485d5f900db177414814bae9577898d687d17f2dc6a533ecec40a21590d3',runtimeRunnerUnchanged=True,original14Unchanged=True,normalHostAccepted=False,nativeAuthorized=False,freezePerformed=False,actualV1Retained=True)
p=B/'source-ready-v2.json';fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(ready,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
print(json.dumps(dict(path=str(p),SHA256=hashlib.sha256(p.read_bytes()).hexdigest(),**ready)))
