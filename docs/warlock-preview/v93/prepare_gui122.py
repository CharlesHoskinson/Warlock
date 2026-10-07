"""Own the actual controlled host derivative; held source stays immutable."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v121';root=repo/'implementation/warlock-preview-provider-v122';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['normalOutputReservationUnderHeldProducerContractQualified'] and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
native=pathlib.Path(d['nativeBaselineManifest']);assert sha(native)==d['nativeBaselineManifestSHA256'];n=json.loads(native.read_text());assert n['passed'] and n['sourceHeld'] and n['nativeChecks']==2518 and n['normalOwnedExits']==278
for rel,row in n['files'].items():assert sha(native.parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [x for x in names if x in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [x for x in names if (pathlib.Path(path)/x).is_dir() and x!='toolchain']
 return [x for x in names if x in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':d['owner'],'parent':str(parent),'parentManifestSHA256':sha(m),'nativeBaselineManifest':str(native),'nativeBaselineManifestSHA256':sha(native),'purpose':'Actual QA-only controlled GTK/WebKit host route: presentation-only admission placeholder, single persistent native policy driver, native producer pause/retained exact inputs, fixed one-time pure renderer grant and native context-owned URI routing. Preserve original GTK admission, physical/terminal/confirmation and no-reset gates. Keep native opacity curtain closed until actual DOM/frame/physical reveal acceptance. No release or installed activation follows source preparation.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,d['owner'],str(root.relative_to(repo)),['PROGRESS ownGUI122 actual controlled host integration after held/publicGUI121 output custody. Native GTK admission must precede controlled factory/driver and fixed renderer grant; placeholder has presentation custody only and no window policy. Retain original producer results and pause further polling through WOULD_BLOCK; actual WebKit context owns scoped URI router. Bind callbacks to original manager/view/lease and current visual sequence. Physical native opacity curtain remains closed until actual DOM/frame/Wayland reveal qualification; decoder/RAF receipt alone is not that proof. Original legacy Native131GUI119/core16/plugin19/AQ1552518/278 stays baseline; no installed/draft/foreign changes. Uncertain live/process recovery, delayed never-issued proposals and full release gates remain open.'],'progress',[str(m.relative_to(repo)),str(native.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
