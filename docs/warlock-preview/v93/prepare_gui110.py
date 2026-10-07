"""Own distinct live-window preview realm detachment without window retirement."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v109';root=repo/'implementation/warlock-preview-provider-v110'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['detachmentCChecks']==77 and d['detachmentCohortChecks']==66 and d['detachmentStates']==715 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Lifetime-safe native URI read capability and stable WebKit routing before controlled preview realm replacement. Exact owning shared state, creator/receiver/epoch binding, destruction revocation and opaque token freshness without raw Endpoint callbacks. Preserve every original physical/backend/reader/terminal ACK and native receiver/borrowed delivery barrier. Keep permanent native incarnation retirement unchanged and use a distinct typed domain. Reopen same actual subject under fresh native realm without Native grant/session/frontend refresh; reject old events/tickets/URIs. No installed changes or Core/WebKit/native release acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS own freshGUI110 after held109. Implement safe weak native read capability capturing exact Endpoint lifetime/binding/receiver/epoch under original Shared lock; stale callbacks deny after destruction/replacement even if physical readers retain storage. Stable trusted WebKit router must not hold raw Endpoint across controlled close. Preserve original Broker/native-time/nonce/reader/physical barriers; shared-host activation remains separate. Native GUI92/native129/core16/plugin19 remains2517/278/full cleanup. No installed/main desktop/draft changes.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
