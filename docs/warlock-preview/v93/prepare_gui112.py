"""Own distinct live-window preview realm detachment without window retirement."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v111';root=repo/'implementation/warlock-preview-provider-v112'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['nativeTicketRoundtripChecks']==93 and d['nativeOutboxStates']==463 and d['fullBuildCommands']==97 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Original native retained ticket/prefix recovery after renderer-context loss. Readonly bounded native recovery pages preserve original binding/epoch/reservation/issued/delivered/confirmed/frontiers and immutable ticket bytes without grant reset or new issuance. Rehydrate a new JS transport context only from complete consistent trusted original pages; delivery never settles effects/physical or Unknown. Actual WebKit/typed host activation separate.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS own freshGUI112 from held111. Implement readonly bounded native ticket/prefix recovery and fresh JS context rehydration on original native realm. Preserve original Native binding/epoch/issued/delivered/confirmed/native purpose quota/physical/Unknown barriers; no new issuance or reset. Pages contain at most one original ticket and refuse stale prefix/foreign epoch; complete consistency before first post. GUI111 C93/protocol47/Quint14/26/463/six/full97 held; publication80 running. Native130 current110 legacy2518/278/full cleanup remains PUBLIC79. Actual WebKit/Core host integration/full release remain open; no installed changes.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
