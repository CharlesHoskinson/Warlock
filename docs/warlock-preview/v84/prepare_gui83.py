"""Preserve GUI82 C-fixture compile failure; correct new cleanup calls only."""
import hashlib, json, pathlib, resource, shutil, stat, sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-preview-provider-v82';target=repo/'implementation/warlock-preview-provider-v83'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
failure=next(parent.glob('qa/retirement-c-check-*/report.json'));failed=json.loads(failure.read_text())
assert not failed['passed'] and 'too few arguments' in failed['error'] and 'warlock_preview_bootstrap_close' in failed['error']
for name,value in failed['inputs'].items():assert sha(parent/name)==value,name
for name,value in failed['artifacts'].items():assert sha(failure.parent/name)==value,name
build=next(parent.glob('qa/build-*/report.json'));built=json.loads(build.read_text());assert built['passed'] and len(built['commands'])==95
for name,value in built['inputs'].items():assert sha(parent/name)==value,name
model=next(parent.glob('qa/retirement-decoder-check-*/report.json'));checked=json.loads(model.read_text());assert checked['passed'] and checked['namedScenarios']==13 and len(checked['coupledTraces'])==25 and checked['statesCompared']==439 and checked['unsafeMutantsDetected']==3
for name,value in checked['inputs'].items():assert sha(parent/name)==value,name
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
 'failure':'Current full95 native/Elm build and actual retirement decoder13/25/439states/3mutants pass. Separate new C fixture did not compile: omitted GError** on imported close and used nonexistent bootstrap_close instead of bootstrap_free. No C test process launched. Fresh83 changes only the new fixture cleanup calls; production decoder/query code unchanged.'},indent=2)+'\n')
def ignore(path,names):
 if pathlib.Path(path)==parent:return [name for name in names if name in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [name for name in names if (pathlib.Path(path)/name).is_dir() and name!='toolchain']
 return [name for name in names if name in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,target,ignore=ignore)
path=target/'native/retirement-observation-test.cpp';text=path.read_text()
old=' warlock_imported_clients_close(owner);warlock_preview_bootstrap_close(bootstrap);server.finish();'
new=' check(warlock_imported_clients_empty(owner) && warlock_imported_clients_close(owner,&error) && !error,"Exact original C empty/close");warlock_preview_bootstrap_free(bootstrap);server.finish();'
assert text.count(old)==1;text=text.replace(old,new);path.write_text(text)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),
 'purpose':'Unchanged actual typed native retirement decoder/query/C ABI. Correct only newly added C fixture cleanup calls after compile failure; retain failed82 and full95/decoder13/25/439states/3mutants. Native18/core16/GUI81 full121 campaign qualification remains separate. No original predicate or deadline change.',
 'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),
 ['PROGRESS native121 core16/plugin18/GUI81 held2458/276normal all2437fixed118+realretry controls. GUI82 full95 and typed decoder13/25/439states/3mutants pass; newCfixture failedcompile cleanupAPI names, no C run. Source82 heldfailed; fresh83 corrects fixturecalls only, production unchanged. Next currentfullcompile/Csocketguard suite/selected decoder traces, all original regressions, then same native observation path. Actual actor retirement stillopen.'],
 'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
