"""Derive native physical/actor quota retirement from the held purpose issuer."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v101';target=repo/'implementation/warlock-preview-provider-v102'
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
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(root),'parentManifestSHA256':sha(manifest),'purpose':'Release native job credits only after original physical/proof barriers and frontend confirmation, mark actor retirement only in the existing all-map transaction, validate actual retained actor readiness/final ACK purposes and release actor/binding credits only after original final effect and confirmation. C provider/reconciliation/outbox/WebKit follows.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS ownGUI102 actual native physical/job/actor/binding quota retirement, preserving original actual all-map retirement transaction and independent final delivery/front-end confirmation barriers. No metadata can assert physical cleanup. Held10170socket controls,15/23/299/four issuer model,bank/admission requalified,69Elm/nativeURI controls,95build; held10012originalsuites unchanged. Controlled C factory/routing, receiver reconciliation and native-assigned outbox/WebKit remain next before activation.'], 'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
