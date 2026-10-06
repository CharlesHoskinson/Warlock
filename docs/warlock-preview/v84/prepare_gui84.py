"""Hold the actual GUI83 receiver-fixture failure; use real unregister/register."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-preview-provider-v83'
target=repo/'implementation/warlock-preview-provider-v84'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(pattern,passed):
 paths=list(parent.glob(pattern));assert len(paths)==1,paths
 path=paths[0];proof=json.loads(path.read_text());assert proof['passed']==passed
 for name,value in proof['inputs'].items():assert sha(parent/name)==value,name
 for name,value in proof.get('artifacts',{}).items():assert sha(path.parent/name)==value,name
 return path,proof
build,built=verify('qa/build-*/report.json',True);assert len(built['commands'])==95
model,checked=verify('qa/retirement-decoder-check-*/report.json',True)
assert checked['namedScenarios']==13 and len(checked['coupledTraces'])==25 and checked['unsafeMutantsDetected']==3
failure,failed=verify('qa/retirement-c-check-*/report.json',False)
assert failed['commands'][-1]['name']=='valid' and failed['commands'][-1]['exitCode']!=0
assert 'Actual receiver replacement epoch' in failed['error']
files={}
for path in sorted(parent.rglob('*')):
 rel=path.relative_to(parent)
 if any(part in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for part in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not path.is_symlink(),path
 if path.is_file():files[str(rel)]={'kind':'file','sha256':sha(path),'size':path.stat().st_size,'mode':oct(stat.S_IMODE(path.stat().st_mode))}
manifest=parent/'component-manifest.json';assert not manifest.exists() and not target.exists()
manifest.write_text(json.dumps({'schema':1,'sourceHeld':True,'passed':False,'evidenceIntegrityPassed':True,'files':files,
 'buildReport':str(build),'retirementDecoderReport':str(model),'retirementCReport':str(failure),
 'nativeAcceptance':False,'fullReleaseAccepted':False,
 'failure':'Full95 and decoder13/25/439states/3mutants pass. New C fixture compiled, but registerView refuses an existing receiver as specified. Failed fixture attempted replacement without unregister; early exception skipped raw-pointer cleanup and ASan reported leaks. No accepted C boundary campaign. Fresh84 uses actual unregister then register and verifies fresh epoch; production unchanged.'},indent=2)+'\n')
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,target,ignore=ignore)
path=target/'native/retirement-observation-test.cpp';text=path.read_text()
old=' check(endpoint.registerView(reinterpret_cast<uintptr_t>(popup),native.binding(),{1,2}),"Actual receiver replacement epoch");'
new=' const auto originalEpoch=endpoint.registeredView(reinterpret_cast<uintptr_t>(popup))->epoch;\n endpoint.unregisterView(reinterpret_cast<uintptr_t>(popup));\n check(endpoint.registerView(reinterpret_cast<uintptr_t>(popup),native.binding(),{1,2}) && endpoint.registeredView(reinterpret_cast<uintptr_t>(popup))->epoch>originalEpoch,"Actual receiver replacement epoch");'
assert text.count(old)==1;path.write_text(text.replace(old,new))
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),
 'purpose':'Unchanged typed native retirement production decoder/query/C ABI. Correct new receiver fixture to use actual unregister/register and independently assert fresh epoch. Keep failed83 build/model/C/leak evidence. No original predicate, deadline or resource gate changed.',
 'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),
 ['PROGRESS GUI83 full95/decoder13/25/439states/3mutants pass; separate C fixture compiled but attempted register over existing receiver, fail + early cleanup leaks held. Fresh84 corrects fixture to actual unregister/register/fresh epoch; production unchanged. Native1212458/276 evidence committed83e294, publication59 live35851. Next compile84/C/model/regressions then actual native path and proof-safe actor turnover beyond256; full release remains open.'],
 'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
