"""Derive actual controlled C factory and ticket routing from held actor quotas."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v103';target=repo/'implementation/warlock-preview-provider-v104'
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
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(root),'parentManifestSHA256':sha(manifest),'purpose':'Retain exact native capture intent before effect invocation and actual export/backend ownership before local mapping/adoption can fail. Publish mapping pointer only after actual Broker ownership transfer, retaining it on post-transfer exceptions. No automatic Unknown acquisition replay or cleanup inference. Actual reconciliation/physical proof protocol and live-binding detachment remain next gates.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS ownGUI104 retain original native capture intent before invocation and exact backend export before local mapping/admission failures; allocation pointer only after actual Broker adoption and retained on post-transfer exception. Held103 controlled C10190/260/1041,five compiled variants,full95 and12 original suites published71. No Unknown replay or physical cleanup inference; actual reconciliation and live-window binding detachment still required before WebKit. Preserve all original real capture/release gates and GUI92/native128/core16/plugin18 runtime.'],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
