"""Own fresh actual Popup realm ports and transport adapter from held GUI113."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v113';root=repo/'implementation/warlock-preview-provider-v114';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['nativeElmOutboxChecks']==175 and d['fullBuildCommands']==103 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Connect actual Popup immutable PreviewPresenter to trusted native realm grant/event/quarantine/close ports and recovered native-issued transport. Preserve original legacy routes before any controlled grant, deny downgrade after controlled close, retain a single policy through transport-only recovery. Native alone wraps old/new epochs and issues tickets. Qualify real shared-host/WebKit/Core activation separately; no renderer may wrap a delayed bare native event under a new epoch or reset the Native grant.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,d['owner'],str(root.relative_to(repo)),['PROGRESS own freshGUI114 actual Popup typed native realm ports and recovered outbox adapter, preserving one existing policy, immutable native epoch wrappers and original legacy route until controlled enrollment. No renderer ordinals for controlled proposals, no downgrade or implicit bare-event rewrapping under replacement epoch. Parent113 PUBLIC82 0670a4500e3b668285b43e163adda958d1996f82/6439 blobs; Elm44/native175/Quint20/32/469/six variants/cold256/1549/full103/original permanent controls. Actual shared-host/WebKit/Core/full Elm recovery and full release remain open; no installed changes.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
