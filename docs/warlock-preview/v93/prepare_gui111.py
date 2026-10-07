"""Own distinct live-window preview realm detachment without window retirement."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v110';root=repo/'implementation/warlock-preview-provider-v111'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['uriCChecks']==66 and d['uriTraces']==24 and d['uriStates']==320 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() and n!='toolchain']
 return [n for n in names if n in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Native-issued retained renderer ticket transport. Native owns every ordinal and immutable ticket; renderer retains exact bytes, bounded ordered retries, delivery receipt and independent confirmation only. No duplicate Elm/native policy or effect settlement from delivery. Current legacy host activation unchanged. Qualify actual controlled C owner through JS transport and explicit Quint traces before typed realm/host activation.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS own freshGUI111 from held110. Implement bounded native-issued immutable renderer ticket outbox; current Native130 GUI110 legacy runtime passes2518/278/full cleanup and is PUBLIC79. Preserve native-assigned ordinals, exact wire bytes, original ordered prefix, unknown and independent confirmation. Actual WebKit/controlled host/Core activation remains next. No installed changes.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
