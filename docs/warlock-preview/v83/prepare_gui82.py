"""Derive full GUI82 for strict typed native incarnation retirement observations."""
import hashlib, json, pathlib, resource, shutil, sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-preview-provider-v81'
target=repo/'implementation/warlock-preview-provider-v82'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
manifest=parent/'component-manifest.json';held=json.loads(manifest.read_text())
assert held['sourceHeld'] and held['passed'] and not target.exists()
for name,row in held['files'].items():assert sha(parent/name)==row['sha256'],name
def ignore(path,names):
 if pathlib.Path(path)==parent:return [name for name in names if name in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [name for name in names if (pathlib.Path(path)/name).is_dir() and name!='toolchain']
 return [name for name in names if name in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,target,ignore=ignore)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),
 'purpose':'Strict typed authenticated native permanent incarnation retirement decoder/query with monotonic sequence/frontier/native clock validation and exact receiver guard. No physical/terminal/actor removal from the observation alone; original single Elm policy/source and all deadline/replay/lifecycle checks retained.',
 'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),
 ['PROGRESS GUI82 assigned fresh from held81 for strict typed native18 retirement observation decoder/query. Native121 preflight underway after new conditional-retry audit qualified against actual118/120 and8unsafe evidence mutations. Preserve original full scope and native/Elm request floors; no actor erasure until exact proof/journal/reader/backend retirement. Next actual decoder/source compile and selected coupled cases while native121 qualifies current GUI81.'],
 'progress',[str((target/'ANCESTRY.json').relative_to(repo))]))
