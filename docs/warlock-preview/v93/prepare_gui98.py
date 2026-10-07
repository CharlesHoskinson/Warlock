"""Own outgoing native control receipt primitive after held fair polling."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');root=repo/'implementation/warlock-preview-provider-v97';target=repo/'implementation/warlock-preview-provider-v98'
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
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(root),'parentManifestSHA256':sha(manifest),'purpose':'Native pre-admission receiver enrollment and actual Coordinator/Broker cleanup quota guard, before controlled provider/WebKit integration.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['PROGRESS ownGUI98: actual native receiver enrollment before jobs and guarded Coordinator/Broker job issuance with derived cleanup quotas. Native reserves capacity/remaining ordinal budget before physical admission, consumes only its own obligation quota, retains replay identity without new issuance and never uses reserved cleanup for speculative admission. Bank is transport bookkeeping, not physical proof or second policy. Derive actual ImportedClients job/actor/proof quotas and integrate issuer/outbox/admission afterward before WebKit activation. Held97 reservations11/23/397/4 and64 adversarial controls; publication68 complete. Preserve all original gates.'],'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo)),str((repo/'docs/warlock-preview/v93/OUTGOING-CONTROL-CONTRACT.md').relative_to(repo))]))
