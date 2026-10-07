"""Own fresh actual Popup realm ports and transport adapter from held GUI113."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v115';root=repo/'implementation/warlock-preview-provider-v116';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['nativeElmOutboxChecks']==206 and d['fullBuildCommands']==108 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Run the same retained Elm preview policy in a native-owned persistent JavaScriptCore worker, with exact owned context/thread, immutable input/output custody and no renderer authority or ordinal issuance. Couple original compiled policy to actual original C/Native synthetic peer while recreating renderer transport contexts. Native owns policy lifetime outside WebKit renderer loss; actual WebKit routing/visual projection, host input backpressure and delayed refusal outcomes remain separate activation gates.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,d['owner'],str(root.relative_to(repo)),['PROGRESS own freshGUI116 native-owned persistent JavaScriptCore Elm worker lifetime. Parent115 retained ingress/urgent quarantine boundaries98/native206/Quint ingress16/28/468/six variants and urgent6/18/406/two variants/cold256/3608/original1549/legacy45/native20+C34/full108 is held. One existing immutable Elm window policy stays authoritative; native module owns context/thread and exact input/output custody without renderer ordinals. Actual WebKit visual projection/stable URI/context refs, durable backpressure/retry, delayed expiry/revocation outcomes, capturedFD/Core/window/native/fullrelease gates remain open. No installed changes.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
