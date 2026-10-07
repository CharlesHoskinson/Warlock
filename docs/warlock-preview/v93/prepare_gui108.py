"""Own next preview lifetime derivative without changing held GUI107."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v107';root=repo/'implementation/warlock-preview-provider-v108'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['realmCChecks']==111 and d['realmRaceChecks']==36 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Explicit preview lifetime continuation: safe original Bootstrap borrowed-receipt detach/reattach across strict owner close, followed by distinct live-window realm detachment and typed frontend realm freshness. Keep shared Native grant, every original physical/proof/actor/processing/independent-confirmation barrier and separate permanent incarnation retirement. No installed changes or native/WebKit acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS own freshGUI108 after held107. Review original Bootstrap receipt attachment lifetime and safe exact-owner close before reattachment; then distinct live-window binding detach/typed renderer realm delivery/current controlled Core/WebKit. No reset of shared Native binding/session/frontend, no fake window retirement, no weakened cleanup/unknown settlement. GUI92/native129/core16/plugin19 bounded2517/278 remains separate.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
