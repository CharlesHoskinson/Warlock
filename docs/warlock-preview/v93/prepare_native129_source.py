"""Own fresh native128 campaign derivative for actual Core19 resource metadata."""
import hashlib,json,pathlib,resource,shutil,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity');parent=repo/'implementation/warlock-client-provider-native-v128';root=repo/'implementation/warlock-client-provider-native-v129'
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
m=parent/'component-manifest.json';d=json.loads(m.read_text());assert d['sourceHeld'] and d['passed'] and d['nativeChecks']==2466 and d['normalOwnedExits']==277 and not root.exists()
for rel,row in d['files'].items():assert sha(parent/rel)==row['sha256'],rel
for name in ['warlock-preview-provider-v106','warlock-family-style-crop-capture-v19']:
 base=repo/'implementation'/name;held=json.loads((base/'component-manifest.json').read_text());assert held['sourceHeld'] and held['passed']
 for rel,row in held['files'].items():assert sha(base/rel)==row['sha256'],rel
 for rel,alias in held.get('directoryAliases',{}).items():assert (base/rel).is_symlink() and str((base/rel).resolve())==alias
def ignore(path,names):
 if pathlib.Path(path)==parent:return [n for n in names if n in {'component-manifest.json','ANCESTRY.json','__pycache__'}]
 if pathlib.Path(path)==parent/'qa':return [n for n in names if (pathlib.Path(path)/n).is_dir() or n=='preflight.json']
 return [n for n in names if n=='__pycache__']
shutil.copytree(parent,root,ignore=ignore)
shutil.copy2(repo/'implementation/warlock-family-style-crop-capture-v19/native-build-report.json',root/'native-build-report.json')
(root/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(m),'purpose':'Retain original native128/126 GUI92 campaign and every original oracle/deadline/teardown, with exact core16/plugin19 and additive real registry/scoped client-capture/resource/FD/lock checks. GUI92 runtime/probes remain retained sources, not current106 native acceptance. Held106 local ownership/Elm/current-host evidence stays separate. No installed changes.','nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(root.relative_to(repo)),['PROGRESS ownNative129 actual Core19 resource protocol/capture/FD qualification, retaining unchanged GUI92/native128 legacy campaign and original source evidence. Held106 local C/SCM_RIGHTS/GIO/Elm fixes and public73 separate; no native106 acceptance or installed changes. Review additive phase and exact preflight before serialized native launch. Original full release gates remain active.'],'progress',[str(m.relative_to(repo)),str((root/'ANCESTRY.json').relative_to(repo))]))
