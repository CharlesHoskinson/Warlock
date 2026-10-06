"""Derive the held receiver component without modifying accepted evidence."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-preview-provider-v56'
target=repo/'implementation/warlock-preview-provider-v57'
manifest=parent/'component-manifest.json';data=json.loads(manifest.read_text())
assert data['passed'] and not target.exists()
for rel,row in data['files'].items():
 p=parent/rel;assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],rel
shutil.copytree(parent,target,ignore=shutil.ignore_patterns('build-*','check-*','metadata-check-*','catalog-check-*','delivery-check-*','component-manifest.json','elm-stuff','mutable-elm-home','__pycache__','ANCESTRY.json','current-build.json'))
(target/'ANCESTRY.json').write_text(json.dumps({'schema':1,'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'purpose':'Explicit trusted same-epoch native receipt subject growth. Preserve original subject/incarnation mapping, native journal, job and final ACK; atomic view/broker admission and refusal. Couple actual GIO drain/consumer fence/physical destruction to original terminal journal. No ordinary eligible capture or full release claim.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
checkpoint=loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),['Previous turn PROGRESS: publication52 remote e88c72b verified PUBLIC, local receipt0b9b4be. All publication handles terminal. Own fresh57 implementing explicit journal membership growth and atomic native view/broker admission. Qualify old/new terminal delivery through real physical drain and exact retained journal ACK, compile actual full GUI and selected coupled Quint; then exact owning native multi-entry campaign. Full release and original S09 thirteen remain open; preserve desktop/drafts/foreign five.'],'progress',['docs/warlock-preview/v70/report.json','docs/warlock-repository/v52/publication/delivery.json','implementation/warlock-preview-provider-v57/ANCESTRY.json'])
print(json.dumps({'source':str(target),'checkpoint':str(checkpoint)}))
