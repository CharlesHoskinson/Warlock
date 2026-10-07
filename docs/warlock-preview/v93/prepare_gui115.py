"""Own fresh actual Popup realm ports and transport adapter from held GUI113."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v114';root=repo/'implementation/warlock-preview-provider-v115';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['nativeElmOutboxChecks']==192 and d['fullBuildCommands']==104 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Retain exact typed original Elm proposal intent before native issuance. Keep immutable ingress bookkeeping in the existing policy model; native-issued ticket fact removes only its exact same realm/body intent, never physical settlement. Preserve bounded capacity and atomic admission, trusted retries, all original lifecycle and native guards. Actual host routes, full Elm recovery and release qualification remain separate.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,d['owner'],str(root.relative_to(repo)),['PROGRESS own freshGUI115 retained original Elm proposal ingress before native ticket issuance. GUI114 PUBLIC83 exact native singleton ingress/packetizer/Popup compile: native192/codec43/Quint12/22 actualC traces/300 states/five variants/full104/resource4+scoped4. Retained ingress must use same immutable Elm policy, exact current native tickets, original purpose body and bounded admission; never conflate issuance with receipt/effect/physical settlement. Actual shared-host/WebKit/Core/full Elm recovery and original release gates open.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
