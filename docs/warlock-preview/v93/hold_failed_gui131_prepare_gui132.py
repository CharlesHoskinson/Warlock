"""Hold the exact compiler-refused candidate and fix syntax in a fresh derivative."""
import hashlib,json,pathlib,resource,shutil,stat,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v131';root=r/'implementation/warlock-preview-provider-v132'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
build=parent/'qa/build-1791389971721122202/report.json';d=json.loads(build.read_text());assert not d['passed'] and d['commands'][-1]['name']=='host-compile' and d['commands'][-1]['exitCode']==1
assert 'misleading-indentation' in (build.parent/'host-compile.stderr').read_text()
for n,h in d['inputs'].items():assert sha(parent/n)==h,n
model_reports=list(parent.glob('qa/host-realm-lifecycle-model-*/report.json'));assert len(model_reports)==1;model=model_reports[0];q=json.loads(model.read_text());assert q['passed'] and q['namedScenarios']==9 and q['invariantSamples']==200
for n,h in q['inputs'].items():assert sha(parent/n)==h,n
for n,h in q['artifacts'].items():assert sha(model.parent/n)==h,n
files={}
for p in sorted(parent.rglob('*')):
 rel=p.relative_to(parent)
 if any(x in {'elm-stuff','mutable-elm-home','elm-home','__pycache__'} for x in rel.parts) and 'toolchain' not in rel.parts:continue
 assert not p.is_symlink(),p
 if p.is_file():files[str(rel)]={'kind':'file','sha256':sha(p),'size':p.stat().st_size,'mode':oct(stat.S_IMODE(p.stat().st_mode))}
m=parent/'component-manifest.json';assert not m.exists();m.write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','sourceHeld':True,'passed':False,'cpuBuildPassed':False,'nativeLaunched':False,'nativeAcceptance':False,'fullReleaseAccepted':False,'modelNamedScenarios':9,'modelInvariantSamples':200,'scope':'Actual host lifecycle candidate refused by unchanged Werror at misleading indentation in the same-policy pointer guard. No native GUI launched. Nine named context/realm lifecycle scenarios and200 invariant samples pass independently; they do not qualify compilation or native behavior. Preserve exact source and compiler/model evidence; a fresh derivative only brackets the existing error guard.','reports':{'failedBuild':{'path':str(build),'sha256':sha(build)},'hostLifecycleModel':{'path':str(model),'sha256':sha(model)}},'files':files},indent=2)+'\n')
assert not root.exists()
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
p=root/'native/controlled-preview-host.h';s=p.read_text();old='            if(!error || !*error)g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Original persistent policy owner changed on native realm reopen");return FALSE;'
assert s.count(old)==1;s=s.replace(old,'            if(!error || !*error){g_set_error_literal(error,G_IO_ERROR,G_IO_ERROR_FAILED,"Original persistent policy owner changed on native realm reopen");}\n            return FALSE;');p.write_text(s)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'acceptedFoundation':str(r/'implementation/warlock-preview-provider-v130/component-manifest.json'),'purpose':'Fresh compiler syntax correction only: bracket existing same-policy error guard to satisfy original Werror. Preserve actual native GUI close/reopen/context replacement implementation, original Native/Elm policy/custody/deadlines, safe opacity0 and all failed/model evidence. Full119 and actual normal/current-image/reopen/stale/strict cleanup gates next.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(r)),['PROGRESS heldfailedGUI131 Werror misleading-indentation in original persistent-policy pointer guard, no native launch. Quint context/realm9named200samples pass separately. Own fresh GUI132 with only bracketed guard syntax fix; actual native close/reopen/fixed-grant context replacement/current epoch snapshots implemented from held130 foundation, same Native/Elm policy/physical/journal/confirmation custody and original deadlines. Full119/current model then actual unchanged29/13 and two/three normal/pending-intent realm native qualification; no opacity opening/reset/installed changes. Full release/physical reveal/reload/uncertain recovery/resource gates remain open.'],'progress',[str(m.relative_to(r)),str((root/'ANCESTRY.json').relative_to(r))]))
