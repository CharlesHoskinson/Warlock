"""Retain unlaunched119 preparation; align new QA with native refused schema."""
import ast, hashlib, json, pathlib, resource, shutil, stat, sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-client-provider-native-v119'
target=repo/'implementation/warlock-client-provider-native-v120'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert not list(parent.glob('qa/native-*/report.json')) and not target.exists()
preflight=parent/'qa/preflight.json';proof=json.loads(preflight.read_text());assert proof['passed'] and not proof['nativeLaunched']
for name,value in proof['inputs'].items():assert sha(pathlib.Path(name))==value,name
source=repo/'implementation/warlock-family-style-crop-capture-v18/native/authority.cpp'
assert '"kind\\\":\\\"refused' in source.read_text()
files={str(path.relative_to(parent)):{'kind':'file','sha256':sha(path),'size':path.stat().st_size,'mode':oct(stat.S_IMODE(path.stat().st_mode))} for path in sorted(parent.rglob('*')) if path.is_file() and '__pycache__' not in path.parts}
manifest=parent/'component-manifest.json';assert not manifest.exists()
manifest.write_text(json.dumps({'sourceHeld':True,'passed':False,'preflightPassed':True,
 'nativeLaunched':False,'status':'unlaunched-fixture-review','evidenceIntegrityPassed':True,'files':files,
 'nativeAcceptance':False,'fullReleaseAccepted':False,
 'reason':'Prelaunch review found new foreign/zero test expected kind:error, but preserved actual native refusal contract is kind:refused. Native119 was never launched. Fresh120 corrects only those two new expected discriminants; every original118 oracle remains exact.'},indent=2)+'\n')
def ignore(path,names):return [name for name in names if name in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path)==parent/'qa' and name.startswith(('native-','prepare-')))]
shutil.copytree(parent,target,ignore=ignore)
path=target/'qa/native.py';text=path.read_text()
assert text.count("foreign.get('kind')=='error'")==1 and text.count("zero.get('kind')=='error'")==1
text=text.replace("foreign.get('kind')=='error'","foreign.get('kind')=='refused'").replace("zero.get('kind')=='error'","zero.get('kind')=='refused'")
ast.parse(text);path.write_text(text)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Unlaunched119 source/preflight retained; correct only new retirement foreign/zero expected discriminants to the actual native refused schema. Owning core16/plugin18, GUI81, original118 controls/deadlines unchanged.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),
 ['PROGRESS native18 compiled and selected classifier8/20/438states/2mutants held. Prepared119 preflightpassed/unlaunched; prelaunchreview found two newexpectedrefusal discriminants wrong (error versus native refused). Source119 held unchanged, fresh120 corrects only those expectations before any native120 execution. Next preflight then serialized full campaign, preserving original118 oracles/ABI/deadlines. Native/fullrelease and actor erasure remainopen.'],
 'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
