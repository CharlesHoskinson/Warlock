"""Own a fresh driver realm-lifecycle derivative; accepted GUI129 stays held."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=r/'implementation/warlock-preview-provider-v129'
root=r/'implementation/warlock-preview-provider-v130'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text())
assert d['sourceHeld'] and d['passed'] and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Retire an actually drained original C realm without deleting the single persistent Elm policy. Admit only a later original native epoch on the same binding with an empty issued namespace; replace realm-bound native outbox while transferring the same policy owner, never reconstructing window state or clearing permanent retirement chronology. Qualify actual C/JSC/FD two-realm lifecycle before wiring normal GTK/WebKit close/reopen. Existing host normal route remains unchanged until its separate native gate. No grant reset, changed deadlines, physical reveal or full release acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(r)),['PROGRESS PUBLIC95 c59722eb3c501552914859d58f8c5c70bdd8c21c/2001 exact owned blobs, PUBLIC and feature/elm branch verified; receipt5e59bb47962d5716b0fbc46271eebe3ec3fd03b4. Own fresh GUI130 from held SAFE129. Implement driver retire/reopen preserving exact same native-owned Elm policy and permanent chronology across original monotonic C epochs; replace only old drained grant-bound outbox. Actual C/JSC/sealed-FD two-realm and wrong-epoch/open-realm/refused-custody controls plus full119 build before actual GTK/WebKit lifecycle integration. Actual host reopen/physical reveal/recovery/full release stay open, accepted/failed packets and foreign/installed/drafts untouched.'],'progress',[str(m.relative_to(r)),str((root/'ANCESTRY.json').relative_to(r))]))
