"""Own fresh resume derivative; preserve held source and evidence."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v66';target=r/'implementation/warlock-preview-provider-v67';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=parent/'component-manifest.json';d=json.loads(manifest.read_text());assert d['passed'] and not target.exists()
for name,row in d['files'].items():assert sha(parent/name)==row['sha256'],name
shutil.copytree(parent,target,ignore=shutil.ignore_patterns('build-*','*check-*','component-manifest.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json','current-build.json'))
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),'purpose':'Original receiver epoch, retained resume intent cutoff across capacity retries, exact issued rejected-job registration; no cleanup gating or source eligibility promotion','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
event=loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(r)),['Previous status-only turn no new implementation progress; revalidated held66/source03e865c, all prior QA terminal. Fresh67 owns retained resume deadline/receiver guard/issued rejection registration. No external blocker. Preserve all original release gates and physical/journal/floor ownership; model/component/native scopes separate.'], 'progress',[str((target/'ANCESTRY.json').relative_to(r))]);print(json.dumps({'source':str(target),'checkpoint':str(event)}))
