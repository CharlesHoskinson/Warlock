"""Own distinct live-window preview realm detachment without window retirement."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v108';root=repo/'implementation/warlock-preview-provider-v109'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['bootstrapCChecks']==97 and d['bootstrapCoreDeathChecks']==47 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Distinct native preview binding-detachment proof/readiness/final processing/independent confirmation while actual native window remains Active. Preserve every original physical/backend/reader/terminal ACK and native receiver/borrowed delivery barrier. Keep permanent native incarnation retirement unchanged and use a distinct typed domain. Reopen same actual subject under fresh native realm without Native grant/session/frontend refresh; reject old events/tickets/URIs. No installed changes or Core/WebKit/native release acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS own freshGUI109 after held108. Implement distinct scoped binding detach with native-only physical/backend/reader/proof barriers, typed renderer readiness/final processing/confirmation and current native realm freshness. Native window remains Active; existing permanent-incarnation retirement is unchanged. Same subject reopens under next native epoch/receipt channel/opaque broker nonce on exact shared Native binding. Old bare binding events require explicit realm wrapper before shared-host activation; no general hello refresh or Unknown replay. GUI92/native129/core16/plugin19 bounded2517/278 remains separate.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
