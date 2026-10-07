"""Own native preview realm lifetime/freshness foundation for explicit detachment."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v106';root=repo/'implementation/warlock-preview-provider-v107'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Native-owned monotonic preview receiver realm/claim lifetime across endpoint replacement. Release only after original physical/proof/actor/processing/control close barriers; constructor rollback consumes rather than reuses epoch. Reject old tickets and legacy downgrade without whole Native hello/frontend/session reset. Foundation for distinct live-window preview detachment, not its completion or WebKit activation.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS ownGUI107 Native-owned preview realm lifetime/freshness before explicit live-window detachment. Held106 physical reader/adoption/Elm component and native129/Core19 resource49/2517/278 normal exits remain separate. Public74 verified806c609195d742d2a97e5d845c4c9cad1d45b2c7,602 owned blobs; local source3f40039fbec11bbacf5bafb33a17427cc13c3d68,receipt in progress. Preserve original Native binding/session/frontend and all independent close barriers; old event/ticket cannot address replacement. No installed changes.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
