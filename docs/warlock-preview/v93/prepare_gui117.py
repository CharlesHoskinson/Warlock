"""Own fresh typed visual projection from the held native-owned single policy."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v116';root=repo/'implementation/warlock-preview-provider-v117';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['nativeElmOutboxChecks']==207 and d['fullBuildCommands']==110 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Project the same authoritative retained Elm preview policy into typed visual data, sharing original rendering and concealment decisions without another window model in the renderer. Preserve original policy transitions, native ownership, issuance, settlement, backpressure and source-scoped evidence. Actual controlled host activation, durable native input/ticket custody, WebKit/Core/process recovery and delayed refusal liveness remain separate.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,d['owner'],str(root.relative_to(repo)),['PROGRESS own freshGUI117 typed visual projection from heldGUI116 persistent native-owned optimized Elm policy. Parent207 actual C/JSC controls,37 lifetime/13 pre-grant faults/48 backpressure/Quint8/20/405/three native variants/full110 are held. Share original immutable policy render/concealment decisions through a typed visual DTO without exposing jobs/resources or adding a second window policy. Refactor only view projection helpers; preserve original window/lifecycle transitions and physical/receipt authority. Compile and couple visual projection to actual worker before controlled Popup/host activation. All original native/WebKit/Core/resource/process/full release gates remain open; no installed changes.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
