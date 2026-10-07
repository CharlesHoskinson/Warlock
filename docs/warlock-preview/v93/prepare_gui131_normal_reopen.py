"""Own the actual GTK/WebKit realm-lifecycle integration from held GUI130."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=r/'implementation/warlock-preview-provider-v130';root=r/'implementation/warlock-preview-provider-v131'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['cpuCPolicyRealmReuseQualified'] and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Connect original popup quarantine and strict original C/Bootstrap/physical/journal/confirmation retirement to the qualified same-policy later-native-epoch driver rebinding. Replace only an already-retired renderer document/view/manager; every new fixed grant initializes once in its original new context, preserving the same Native transport/Elm policy/permanent chronology. Keep native opacity0 and original producer/event/ticket/callback custody, navigation and snapshot ordinals. Qualify actual pointer close/reopen/current scoped images/private output and strict normal teardown; no physical reveal/reload/uncertain recovery or full release claim from preparation.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(r/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(r,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(r)),['PROGRESS previous goal turn made concrete progress: PUBLIC95 delayed snapshot and PUBLIC96 455421e67ebb431a32669e5dab23578a350dc99b/4053 exact owned blobs; public branch verified, receipt24497b0bd5480a9c7441f28d7114d77b1a63b2fa. Own fresh GUI131 from held130. Wire actual controlled host strict retire/new renderer-context/same-policy native epoch reopen; retain current29-control native regression then actual pointer two/three realm capture/URI/pixels/closed-curtain/strict teardown under original deadlines/core16/plugin19/AQ155. No Native grant/policy/model/custody reset; physical reveal/pressure/RSS/recovery/full release remain open. All held sources/foreign/installed/drafts preserved.'],'progress',[str(m.relative_to(r)),str((root/'ANCESTRY.json').relative_to(r))]))
