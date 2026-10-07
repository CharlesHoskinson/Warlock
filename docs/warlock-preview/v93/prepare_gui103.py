"""Derive actual controlled C factory and ticket routing from held actor quotas."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v102';target=repo/'implementation/warlock-preview-provider-v103'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=root/'component-manifest.json';m=json.loads(manifest.read_text());assert m['passed'] and m['sourceHeld']
for rel,row in m['files'].items():assert sha(root/rel)==row['sha256'],rel
assert not target.exists()
def ignore(path,names):
 p=pathlib.Path(path)
 if p==root:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if p==root/'qa':return [n for n in names if (p/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(root,target,ignore=ignore)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(root),'parentManifestSHA256':sha(manifest),'purpose':'Actual opt-in C provider enrolls original receiver before admission, claims one namespace on actual native transport, issues strict purpose-validated original tickets and routes only native-owned contiguous packets; confirmations collect actual settled actor quotas. Legacy raw paths refuse controlled owners. Strict completed-actor close remains separate from live-binding detachment/reconciliation; renderer/WebKit activation follows.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS ownGUI103 actual controlled C provider/native-purpose ticket routing and original frontend confirmations; no WebKit activation yet. Native core plugin18 actual grantRegistry hello increments original frontend on authenticated repeat peer (authority.cpp499/grant-registry.hpp), so no assumed fresh grant. Same Native transport must claim one preview namespace and never reset it. Held1027809 metadata controls/260actors/1040prefix, actor15/23/316/four,job/bank/admission requalified,69Elm/nativeURI,95build. Explicit live-binding detachment/reconciliation remains distinct from permanent actor retirement and is required before full activation; preserve all original capturedFD/realwindow/runtime release gates.'], 'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
