"""Derive native purpose-validated tickets from held actual admission integration."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v100';target=repo/'implementation/warlock-preview-provider-v101'
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
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(root),'parentManifestSHA256':sha(manifest),'purpose':'Native typed job-control issuer validates actual job/packet/terminal proofs before assigning immutable reserved ticket; confirmed retries remain distinguishable from new effects. C factory/physical actor release/reconciliation/outbox/WebKit integration follows.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS ownGUI101 native purpose-validated control tickets and bounded confirmed duplicate tombstones. Preserve actual Broker/proof authority, original immutable wire, single native namespace and unknown outcomes. Held100 actual admission40 socket controls,15/23/191/six compiled variants,95 build and12 original suites; no active WebKit/capture/release acceptance.'], 'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
