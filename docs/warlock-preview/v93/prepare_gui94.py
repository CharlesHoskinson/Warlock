"""Own bounded fair native retirement polling before WebKit activation."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
root=repo/'implementation/warlock-preview-provider-v93';target=repo/'implementation/warlock-preview-provider-v94'
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
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(root),'parentManifestSHA256':sha(manifest),'purpose':'One round-robin readiness candidate per native poll, with physical/proof/receiver checks before the fresh native query. No performance acceptance or actual WebKit activation.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS ownGUI94 fromheld93: bounded fair readiness polling, at most one candidate per call and no native IPC while original local physical/proof/receiver barriers remain. Explicit Quint/compiled native traces and actual socket/C receiver, terminal ACK, neighbor and loss controls required. Freeze no new S02 timing/resource budget; all original performance and full release gates remain. Next bounded reliable outgoing controls and actual WebKit host routing.'],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
