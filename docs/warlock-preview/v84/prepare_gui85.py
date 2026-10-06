"""Fresh active-subject registry derivative; leave the native122 owning tuple held."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-preview-provider-v84';target=repo/'implementation/warlock-preview-provider-v85'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=parent/'component-manifest.json';held=json.loads(manifest.read_text());assert held['sourceHeld'] and held['passed']
for rel,row in held['files'].items():assert sha(parent/rel)==row['sha256'],rel
assert not target.exists()
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,target,ignore=ignore)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),
 'purpose':'Replace dynamic C vector index identity with explicit bounded active entry membership and monotonic entry issuance. This is the serial foundation for the specified atomic multi-owner retirement. No actor removal is exposed before that transaction and Elm settlement contract are integrated. Current native122 uses heldGUI84/core16/plugin18; preserve all prior physical/journal/proof/counter/deadline gates.',
 'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
print(target)
