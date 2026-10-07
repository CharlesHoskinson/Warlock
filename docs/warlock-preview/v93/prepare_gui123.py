"""Own the actual controlled host derivative; held source stays immutable."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v122';root=repo/'implementation/warlock-preview-provider-v123';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and not d['passed'] and d['cpuBuildPassed'] and d['actualNativeGTKAdmissionObserved'] and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
native=repo/'implementation/warlock-client-provider-native-v132/component-manifest.json';n=json.loads(native.read_text());assert n['sourceHeld'] and not n['passed'] and n['privateSessionCleanupPassed']
for rel,row in n['files'].items():assert sha(native.parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [x for x in names if x in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [x for x in names if (pathlib.Path(path)/x).is_dir() and x!='toolchain']
 return [x for x in names if x in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'nativeBaselineManifest':str(native),'nativeBaselineManifestSHA256':sha(native),'purpose':'Fresh correction of held failed GUI122/Native132: persistent native-owned outer DOM mount survives Elm Browser.element replacement; forbid legacy imported wake in controlled route. Actual QA-only controlled GTK/WebKit host route: presentation-only admission placeholder, single persistent native policy driver, native producer pause/retained exact inputs, fixed one-time pure renderer grant and native context-owned URI routing. Preserve original GTK admission, physical/terminal/confirmation and no-reset gates. Keep native opacity curtain closed until actual DOM/frame/physical reveal acceptance. No release or installed activation follows source preparation.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS ownGUI123 after held failedGUI122/Native132 actual GTK/factory/native driver admission. Correct actual Elm mount replacement using native-owned persistent outer app container; initialize placeholder and pure receiver in separate child mounts, retain fixed one-time grant and original native custody. Also prevent legacy imported wake from scheduling a legacy producer on the controlled owner. Original scenario/deadlines/strict close unchanged. Full current CPU/build and serial actual probe next; physical curtain stays closed, actual reveal/recovery/full release open. Original Native1312518/278 baseline/installed/drafts/five foreign paths preserved.'],'progress',[str(m.relative_to(repo)),str(native.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
