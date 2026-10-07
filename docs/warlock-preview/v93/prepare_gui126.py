"""Own the actual controlled host derivative; held source stays immutable."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-preview-provider-v125';root=repo/'implementation/warlock-preview-provider-v126';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['normalControlledHostClosureQualified'] and d['cpuBuildPassed'] and d['actualNativeGTKAdmissionObserved'] and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
native=repo/'implementation/warlock-client-provider-native-v135/component-manifest.json';n=json.loads(native.read_text());assert n['sourceHeld'] and n['passed'] and n['normalControlledHostClosureQualified'] and n['privateSessionCleanupPassed']
for rel,row in n['files'].items():assert sha(native.parent/rel)==row['sha256'],rel
def ignore(path,names):
 if pathlib.Path(path)==parent:return [x for x in names if x in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [x for x in names if (pathlib.Path(path)/x).is_dir() and x!='toolchain']
 return [x for x in names if x in {'__pycache__','elm-stuff'}]
shutil.copytree(parent,root,ignore=ignore)
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'nativeBaselineManifest':str(native),'nativeBaselineManifestSHA256':sha(native),'purpose':'Fresh derivative of held bounded controlled GUI125/Native135. Add actual QA-only loaded-image observation and native-current projection gating before the existing private WebKit snapshot. Reuse the original native-issued URI/size validation and independent pixel oracle. Preserve one persistent native Elm policy, original GTK/native grants, deadlines, effects, actor/journal/confirmation custody and strict normal closure. Native curtain remains closed: rendered-image pixels do not authorize physical reveal or full release acceptance.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS ownGUI126 after bounded actual GUI125/Native13516checks8normalexits published PUBLIC92. Add actual QA-only loaded-image observer on pure renderer and native-current projection gating before original private WebKit snapshot, then same original16 actual scenario checks plus independent original pixel oracle/current native URI and dimensions. Preserve original Native/Core/GTK/Elm/epoch/deadline6/strict closure, native opacity curtain0; pixels are separate from frame/physical reveal. All failure evidence and legacy2518/278 preserved. Next current full build then serial Native136. Installed/drafts/foreign untouched.'],'progress',[str(m.relative_to(repo)),str(native.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
